# Generated from Gram.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .GramParser import GramParser
else:
    from GramParser import GramParser

# This class defines a complete listener for a parse tree produced by GramParser.
class GramListener(ParseTreeListener):

    # Enter a parse tree produced by GramParser#fullexpr.
    def enterFullexpr(self, ctx:GramParser.FullexprContext):
        pass

    # Exit a parse tree produced by GramParser#fullexpr.
    def exitFullexpr(self, ctx:GramParser.FullexprContext):
        pass


    # Enter a parse tree produced by GramParser#parens.
    def enterParens(self, ctx:GramParser.ParensContext):
        pass

    # Exit a parse tree produced by GramParser#parens.
    def exitParens(self, ctx:GramParser.ParensContext):
        pass


    # Enter a parse tree produced by GramParser#compare.
    def enterCompare(self, ctx:GramParser.CompareContext):
        pass

    # Exit a parse tree produced by GramParser#compare.
    def exitCompare(self, ctx:GramParser.CompareContext):
        pass


    # Enter a parse tree produced by GramParser#logical.
    def enterLogical(self, ctx:GramParser.LogicalContext):
        pass

    # Exit a parse tree produced by GramParser#logical.
    def exitLogical(self, ctx:GramParser.LogicalContext):
        pass


    # Enter a parse tree produced by GramParser#literal.
    def enterLiteral(self, ctx:GramParser.LiteralContext):
        pass

    # Exit a parse tree produced by GramParser#literal.
    def exitLiteral(self, ctx:GramParser.LiteralContext):
        pass


    # Enter a parse tree produced by GramParser#array.
    def enterArray(self, ctx:GramParser.ArrayContext):
        pass

    # Exit a parse tree produced by GramParser#array.
    def exitArray(self, ctx:GramParser.ArrayContext):
        pass


    # Enter a parse tree produced by GramParser#function.
    def enterFunction(self, ctx:GramParser.FunctionContext):
        pass

    # Exit a parse tree produced by GramParser#function.
    def exitFunction(self, ctx:GramParser.FunctionContext):
        pass


    # Enter a parse tree produced by GramParser#attribute.
    def enterAttribute(self, ctx:GramParser.AttributeContext):
        pass

    # Exit a parse tree produced by GramParser#attribute.
    def exitAttribute(self, ctx:GramParser.AttributeContext):
        pass


    # Enter a parse tree produced by GramParser#boolean.
    def enterBoolean(self, ctx:GramParser.BooleanContext):
        pass

    # Exit a parse tree produced by GramParser#boolean.
    def exitBoolean(self, ctx:GramParser.BooleanContext):
        pass


    # Enter a parse tree produced by GramParser#string.
    def enterString(self, ctx:GramParser.StringContext):
        pass

    # Exit a parse tree produced by GramParser#string.
    def exitString(self, ctx:GramParser.StringContext):
        pass


    # Enter a parse tree produced by GramParser#int.
    def enterInt(self, ctx:GramParser.IntContext):
        pass

    # Exit a parse tree produced by GramParser#int.
    def exitInt(self, ctx:GramParser.IntContext):
        pass


    # Enter a parse tree produced by GramParser#float.
    def enterFloat(self, ctx:GramParser.FloatContext):
        pass

    # Exit a parse tree produced by GramParser#float.
    def exitFloat(self, ctx:GramParser.FloatContext):
        pass


    # Enter a parse tree produced by GramParser#null.
    def enterNull(self, ctx:GramParser.NullContext):
        pass

    # Exit a parse tree produced by GramParser#null.
    def exitNull(self, ctx:GramParser.NullContext):
        pass


    # Enter a parse tree produced by GramParser#args.
    def enterArgs(self, ctx:GramParser.ArgsContext):
        pass

    # Exit a parse tree produced by GramParser#args.
    def exitArgs(self, ctx:GramParser.ArgsContext):
        pass


    # Enter a parse tree produced by GramParser#nested_attr.
    def enterNested_attr(self, ctx:GramParser.Nested_attrContext):
        pass

    # Exit a parse tree produced by GramParser#nested_attr.
    def exitNested_attr(self, ctx:GramParser.Nested_attrContext):
        pass


    # Enter a parse tree produced by GramParser#attr.
    def enterAttr(self, ctx:GramParser.AttrContext):
        pass

    # Exit a parse tree produced by GramParser#attr.
    def exitAttr(self, ctx:GramParser.AttrContext):
        pass



del GramParser
