from antlr4 import CommonTokenStream, InputStream, ParseTreeWalker

import crocodsl.func as func

from .field import _Field
from .gram.GramLexer import GramLexer
from .gram.GramListener import GramListener
from .gram.GramParser import GramParser


def IDENT(x):
    """A no-op to return the input of a function."""
    return x


# Escape codes are the same ones used in JSON:
# https://github.com/antlr/grammars-v4/blob/master/json/JSON.g4#L42
# Any character not listed in this map will be printed literally into the
# string. This is the desired behavior for characters like quotes and slashes
# that need to be escaped, so they are not included in this map. It's also a
# good fallback for escaping characters that don't need to be escaped.
ESCAPE = {
    "n": "\n",  # newline
    "r": "\r",  # carriage return
    "t": "\t",  # tab
    "b": "\b",  # backspace
    "f": "\f",  # form feed
}
"""A map of character values for escape codes."""


class _Args:
    """Wrapper for a function's arguments."""

    def __init__(self, *x):
        self.args = x


class ExprCompiler(GramListener):
    """Compile an Expression by walking the parse tree."""

    def __init__(self, debug=False):
        super().__init__()
        # The ops/args dicts store for each context a function to be called
        # to produce some object in the language (see `func` and `field`).
        # Values get popped as they are evaluated. (This is secretly a stack.)
        self.operators = {}
        self.arguments = {}
        self.root = None
        self.debug = debug

    def enterParens(self, ctx):
        op = func.Not if ctx.NOT() else IDENT
        self._enterNode(ctx, op, [])

    def exitParens(self, ctx):
        self._leaveNode(ctx)

    def enterLogical(self, ctx):
        op = getattr(func, ctx.op.text)
        self._enterNode(ctx, op, [])

    def exitLogical(self, ctx):
        self._leaveNode(ctx)

    def enterCompare(self, ctx):
        op = getattr(func, ctx.op.text)
        self._enterNode(ctx, op, [])

    def exitCompare(self, ctx):
        self._leaveNode(ctx)

    def enterArray(self, ctx):
        self._enterNode(ctx, lambda *x: list(x), [])

    def exitArray(self, ctx):
        self._leaveNode(ctx)

    def enterLiteral(self, ctx):
        self._enterNode(ctx, IDENT, [])

    def exitLiteral(self, ctx):
        self._leaveNode(ctx)

    def enterNull(self, ctx):
        self._enterNode(ctx, lambda: None, [])

    def exitNull(self, ctx):
        self._leaveNode(ctx)

    def enterBoolean(self, ctx):
        self._enterNode(ctx, lambda x: x == "True", [ctx.BOOL().getText()])

    def exitBoolean(self, ctx):
        self._leaveNode(ctx)

    def enterString(self, ctx):
        # Strip first and last character, which are the enclosing quotes.
        raw_str = ctx.getText()[1:-1]

        # Interpret escape sequences
        s = ""
        escaped = False
        for char in raw_str:
            if escaped:
                # Get the escaped character, falling back to the original
                # character if there isn't a predefined code.
                s += ESCAPE.get(char, char)
                escaped = False
                continue
            elif char == "\\":
                escaped = True
                continue
            else:
                s += char
                continue

        self._enterNode(ctx, IDENT, [s])

    def exitString(self, ctx):
        self._leaveNode(ctx)

    def enterInt(self, ctx):
        self._enterNode(ctx, int, [ctx.getText()])

    def exitInt(self, ctx):
        self._leaveNode(ctx)

    def enterFloat(self, ctx):
        self._enterNode(ctx, float, [ctx.getText()])

    def exitFloat(self, ctx):
        self._leaveNode(ctx)

    def enterFunction(self, ctx):
        opName = ctx.NAME().getText()
        op: func._Expression | None = None
        try:
            op = func.FUNCTION_REGISTRY[opName]
        except KeyError:
            try:
                op = getattr(func, opName)
            except AttributeError as e:
                raise SyntaxError(f"Function '{opName}' is not defined") from e

        self._enterNode(ctx, op, [])

    def exitFunction(self, ctx):
        self._leaveNode(ctx)

    def enterAttribute(self, ctx):
        self._enterNode(
            ctx, _Field, [attr.NAME().getText() for attr in ctx.nested_attr().attr()]
        )

    def exitAttribute(self, ctx):
        self._leaveNode(ctx)

    def enterArgs(self, ctx):
        self._enterNode(ctx, _Args, [])

    def exitArgs(self, ctx):
        self._leaveNode(ctx)

    def _enterNode(self, ctx, f, args):
        self.operators[ctx] = f
        self.arguments[ctx] = args

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise SyntaxError(f"Syntax error at {line}:{column}: {msg}")

    def _leaveNode(self, ctx):
        # Get the node's operation and arguments.
        # Normally these objects can be discarded in this step since they will
        # never be seen again, but keep them in case of debugging.
        if self.debug:
            op = self.operators[ctx]
            args = self.arguments[ctx]
        else:
            op = self.operators.pop(ctx)
            args = self.arguments.pop(ctx)

        # Evaluate!
        value = op(*args)

        # If this is a nested value, add it to the parent's arguments.
        # Otherwise this must be the root node.
        has_parent = ctx.parentCtx in self.operators
        if has_parent:
            if isinstance(value, _Args):
                self.arguments[ctx.parentCtx] += value.args
            else:
                self.arguments[ctx.parentCtx].append(value)
        else:
            # Check that there aren't any orphaned parents.
            if not self.debug and (len(self.operators) or len(self.arguments)):
                raise SyntaxError("There was an error parsing the expression")
            if isinstance(value, _Args):
                # There's no way _Args can ever be parsed as a top-level
                # context, so if this happens it's probably due to a bug in
                # the implementation of this class. (E.g., the enter method for
                # the parent context is not properly registering itself on the
                # stack, or the exit method is popping it before it's finished
                # processing its children.)
                raise RuntimeError("Unexpected top-level function args")
            elif not isinstance(value, func._Expression):
                # If the result was a literal value, wrap it.
                value = func.Literal(value)
            self.root = value


def _compile(s: str, debug: bool = False) -> ExprCompiler:
    """Parse the symbolic expression and return the full parse tree.

    Args:
        s - A string expression
        debug - Whether to track objects for debugging later. By default the
        compiler will discard nodes in the tree after visiting them, but if
        this is True it will keep things which can be useful for debugging.

    Returns:
        ExprCompiler with the parse tree.
    """
    lexer = GramLexer(InputStream(s))
    stream = CommonTokenStream(lexer)
    parser = GramParser(stream)
    compiler = ExprCompiler(debug=debug)
    walker = ParseTreeWalker()
    # The `program` rule is the top-level rule that requires the entire
    # input to be valid (i.e., and expression + EOF). This will cause
    # an error if there is any trailing garbage / typos.
    walker.walk(compiler, parser.program())
    return compiler


def parse(s: str, debug: bool = False) -> func._Expression:
    """Parse a given symbolic expression into an _Expression.

    Examples:
        The syntax allows simple boolean algebra expressions. The types and
        operators are the same as the ones defined in `func`.

        The dollar sign `$` is used to signify fields of the input entity. So
        to reference `User.id`, write `$id`.

        ```
            $id Eq "my_id"
            $id In ["first_id", "second_id", "third_id"]
            ($id Eq "my_id") Or ($id In ["first_id", "second_id", "third_id"])
            Hash($id) Lt 0.5
            Hash($id) Le 0.5 And $lang Eq ['en']
            Not($lang In ['ru', 'mk', 'pl'])
        ```

    Args:
        s - A string containing the symbolic expression.

    Returns:
        _Expression object representing the parsed string.
    """
    return _compile(s, debug=debug).root
