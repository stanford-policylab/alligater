# Generated from Gram.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,27,80,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,1,0,4,
        0,14,8,0,11,0,12,0,15,1,0,1,0,1,1,1,1,1,1,3,1,23,8,1,1,1,1,1,1,1,
        1,1,3,1,29,8,1,1,1,1,1,1,1,1,1,1,1,1,1,5,1,37,8,1,10,1,12,1,40,9,
        1,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,3,
        2,57,8,2,1,3,1,3,1,3,5,3,62,8,3,10,3,12,3,65,9,3,3,3,67,8,3,1,4,
        1,4,1,4,5,4,72,8,4,10,4,12,4,75,9,4,1,5,1,5,1,5,1,5,0,1,2,6,0,2,
        4,6,8,10,0,2,1,0,11,19,1,0,9,10,88,0,13,1,0,0,0,2,28,1,0,0,0,4,56,
        1,0,0,0,6,66,1,0,0,0,8,68,1,0,0,0,10,76,1,0,0,0,12,14,3,2,1,0,13,
        12,1,0,0,0,14,15,1,0,0,0,15,13,1,0,0,0,15,16,1,0,0,0,16,17,1,0,0,
        0,17,18,5,0,0,1,18,1,1,0,0,0,19,20,6,1,-1,0,20,29,3,4,2,0,21,23,
        5,8,0,0,22,21,1,0,0,0,22,23,1,0,0,0,23,24,1,0,0,0,24,25,5,1,0,0,
        25,26,3,2,1,0,26,27,5,2,0,0,27,29,1,0,0,0,28,19,1,0,0,0,28,22,1,
        0,0,0,29,38,1,0,0,0,30,31,10,2,0,0,31,32,7,0,0,0,32,37,3,2,1,3,33,
        34,10,1,0,0,34,35,7,1,0,0,35,37,3,2,1,2,36,30,1,0,0,0,36,33,1,0,
        0,0,37,40,1,0,0,0,38,36,1,0,0,0,38,39,1,0,0,0,39,3,1,0,0,0,40,38,
        1,0,0,0,41,42,5,3,0,0,42,43,3,6,3,0,43,44,5,4,0,0,44,57,1,0,0,0,
        45,46,5,22,0,0,46,47,5,1,0,0,47,48,3,6,3,0,48,49,5,2,0,0,49,57,1,
        0,0,0,50,57,3,8,4,0,51,57,5,20,0,0,52,57,5,23,0,0,53,57,5,24,0,0,
        54,57,5,27,0,0,55,57,5,21,0,0,56,41,1,0,0,0,56,45,1,0,0,0,56,50,
        1,0,0,0,56,51,1,0,0,0,56,52,1,0,0,0,56,53,1,0,0,0,56,54,1,0,0,0,
        56,55,1,0,0,0,57,5,1,0,0,0,58,63,3,2,1,0,59,60,5,5,0,0,60,62,3,2,
        1,0,61,59,1,0,0,0,62,65,1,0,0,0,63,61,1,0,0,0,63,64,1,0,0,0,64,67,
        1,0,0,0,65,63,1,0,0,0,66,58,1,0,0,0,66,67,1,0,0,0,67,7,1,0,0,0,68,
        73,3,10,5,0,69,70,5,6,0,0,70,72,3,10,5,0,71,69,1,0,0,0,72,75,1,0,
        0,0,73,71,1,0,0,0,73,74,1,0,0,0,74,9,1,0,0,0,75,73,1,0,0,0,76,77,
        5,7,0,0,77,78,5,22,0,0,78,11,1,0,0,0,9,15,22,28,36,38,56,63,66,73
    ]

class GramParser ( Parser ):

    grammarFileName = "Gram.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'('", "')'", "'['", "']'", "','", "'.'",
                     "'$'", "'Not'", "'And'", "'Or'", "'Eq'", "'Ne'", "'Lt'",
                     "'Le'", "'Gt'", "'Ge'", "'In'", "'Has'", "'Matches'",
                     "<INVALID>", "'None'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>",
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>",
                      "NOT", "AND", "OR", "EQ", "NE", "LT", "LE", "GT",
                      "GE", "IN", "HAS", "MATCHES", "BOOL", "NULL", "NAME",
                      "STRING", "INT", "POS_INT", "SP", "FLOAT" ]

    RULE_program = 0
    RULE_expr = 1
    RULE_value = 2
    RULE_args = 3
    RULE_nested_attr = 4
    RULE_attr = 5

    ruleNames =  [ "program", "expr", "value", "args", "nested_attr", "attr" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    NOT=8
    AND=9
    OR=10
    EQ=11
    NE=12
    LT=13
    LE=14
    GT=15
    GE=16
    IN=17
    HAS=18
    MATCHES=19
    BOOL=20
    NULL=21
    NAME=22
    STRING=23
    INT=24
    POS_INT=25
    SP=26
    FLOAT=27

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ProgramContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return GramParser.RULE_program


        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class FullexprContext(ProgramContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a GramParser.ProgramContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def EOF(self):
            return self.getToken(GramParser.EOF, 0)
        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(GramParser.ExprContext)
            else:
                return self.getTypedRuleContext(GramParser.ExprContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFullexpr" ):
                listener.enterFullexpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFullexpr" ):
                listener.exitFullexpr(self)



    def program(self):

        localctx = GramParser.ProgramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_program)
        self._la = 0 # Token type
        try:
            localctx = GramParser.FullexprContext(self, localctx)
            self.enterOuterAlt(localctx, 1)
            self.state = 13
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 12
                self.expr(0)
                self.state = 15
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 166723978) != 0)):
                    break

            self.state = 17
            self.match(GramParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return GramParser.RULE_expr


        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)


    class ParensContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a GramParser.ExprContext
            super().__init__(parser)
            self.inner = None # ExprContext
            self.copyFrom(ctx)

        def expr(self):
            return self.getTypedRuleContext(GramParser.ExprContext,0)

        def NOT(self):
            return self.getToken(GramParser.NOT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParens" ):
                listener.enterParens(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParens" ):
                listener.exitParens(self)


    class CompareContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a GramParser.ExprContext
            super().__init__(parser)
            self.left = None # ExprContext
            self.op = None # Token
            self.right = None # ExprContext
            self.copyFrom(ctx)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(GramParser.ExprContext)
            else:
                return self.getTypedRuleContext(GramParser.ExprContext,i)

        def EQ(self):
            return self.getToken(GramParser.EQ, 0)
        def NE(self):
            return self.getToken(GramParser.NE, 0)
        def LT(self):
            return self.getToken(GramParser.LT, 0)
        def LE(self):
            return self.getToken(GramParser.LE, 0)
        def GT(self):
            return self.getToken(GramParser.GT, 0)
        def GE(self):
            return self.getToken(GramParser.GE, 0)
        def IN(self):
            return self.getToken(GramParser.IN, 0)
        def HAS(self):
            return self.getToken(GramParser.HAS, 0)
        def MATCHES(self):
            return self.getToken(GramParser.MATCHES, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCompare" ):
                listener.enterCompare(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCompare" ):
                listener.exitCompare(self)


    class LogicalContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a GramParser.ExprContext
            super().__init__(parser)
            self.left = None # ExprContext
            self.op = None # Token
            self.copyFrom(ctx)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(GramParser.ExprContext)
            else:
                return self.getTypedRuleContext(GramParser.ExprContext,i)

        def AND(self):
            return self.getToken(GramParser.AND, 0)
        def OR(self):
            return self.getToken(GramParser.OR, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLogical" ):
                listener.enterLogical(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLogical" ):
                listener.exitLogical(self)


    class LiteralContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a GramParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def value(self):
            return self.getTypedRuleContext(GramParser.ValueContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLiteral" ):
                listener.enterLiteral(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLiteral" ):
                listener.exitLiteral(self)



    def expr(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = GramParser.ExprContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 2
        self.enterRecursionRule(localctx, 2, self.RULE_expr, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 28
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [3, 7, 20, 21, 22, 23, 24, 27]:
                localctx = GramParser.LiteralContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx

                self.state = 20
                self.value()
                pass
            elif token in [1, 8]:
                localctx = GramParser.ParensContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 22
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==8:
                    self.state = 21
                    self.match(GramParser.NOT)


                self.state = 24
                self.match(GramParser.T__0)
                self.state = 25
                localctx.inner = self.expr(0)
                self.state = 26
                self.match(GramParser.T__1)
                pass
            else:
                raise NoViableAltException(self)

            self._ctx.stop = self._input.LT(-1)
            self.state = 38
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,4,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 36
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,3,self._ctx)
                    if la_ == 1:
                        localctx = GramParser.CompareContext(self, GramParser.ExprContext(self, _parentctx, _parentState))
                        localctx.left = _prevctx
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 30
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                        self.state = 31
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 1046528) != 0)):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 32
                        localctx.right = self.expr(3)
                        pass

                    elif la_ == 2:
                        localctx = GramParser.LogicalContext(self, GramParser.ExprContext(self, _parentctx, _parentState))
                        localctx.left = _prevctx
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 33
                        if not self.precpred(self._ctx, 1):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 1)")
                        self.state = 34
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not(_la==9 or _la==10):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 35
                        localctx.left = self.expr(2)
                        pass


                self.state = 40
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,4,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class ValueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return GramParser.RULE_value


        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class BooleanContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a GramParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def BOOL(self):
            return self.getToken(GramParser.BOOL, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBoolean" ):
                listener.enterBoolean(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBoolean" ):
                listener.exitBoolean(self)


    class StringContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a GramParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def STRING(self):
            return self.getToken(GramParser.STRING, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterString" ):
                listener.enterString(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitString" ):
                listener.exitString(self)


    class NullContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a GramParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NULL(self):
            return self.getToken(GramParser.NULL, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNull" ):
                listener.enterNull(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNull" ):
                listener.exitNull(self)


    class ArrayContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a GramParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def args(self):
            return self.getTypedRuleContext(GramParser.ArgsContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterArray" ):
                listener.enterArray(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitArray" ):
                listener.exitArray(self)


    class FunctionContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a GramParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NAME(self):
            return self.getToken(GramParser.NAME, 0)
        def args(self):
            return self.getTypedRuleContext(GramParser.ArgsContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFunction" ):
                listener.enterFunction(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFunction" ):
                listener.exitFunction(self)


    class AttributeContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a GramParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def nested_attr(self):
            return self.getTypedRuleContext(GramParser.Nested_attrContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAttribute" ):
                listener.enterAttribute(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAttribute" ):
                listener.exitAttribute(self)


    class FloatContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a GramParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def FLOAT(self):
            return self.getToken(GramParser.FLOAT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFloat" ):
                listener.enterFloat(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFloat" ):
                listener.exitFloat(self)


    class IntContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a GramParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def INT(self):
            return self.getToken(GramParser.INT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterInt" ):
                listener.enterInt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitInt" ):
                listener.exitInt(self)



    def value(self):

        localctx = GramParser.ValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_value)
        try:
            self.state = 56
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [3]:
                localctx = GramParser.ArrayContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 41
                self.match(GramParser.T__2)
                self.state = 42
                self.args()
                self.state = 43
                self.match(GramParser.T__3)
                pass
            elif token in [22]:
                localctx = GramParser.FunctionContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 45
                self.match(GramParser.NAME)
                self.state = 46
                self.match(GramParser.T__0)
                self.state = 47
                self.args()
                self.state = 48
                self.match(GramParser.T__1)
                pass
            elif token in [7]:
                localctx = GramParser.AttributeContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 50
                self.nested_attr()
                pass
            elif token in [20]:
                localctx = GramParser.BooleanContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 51
                self.match(GramParser.BOOL)
                pass
            elif token in [23]:
                localctx = GramParser.StringContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 52
                self.match(GramParser.STRING)
                pass
            elif token in [24]:
                localctx = GramParser.IntContext(self, localctx)
                self.enterOuterAlt(localctx, 6)
                self.state = 53
                self.match(GramParser.INT)
                pass
            elif token in [27]:
                localctx = GramParser.FloatContext(self, localctx)
                self.enterOuterAlt(localctx, 7)
                self.state = 54
                self.match(GramParser.FLOAT)
                pass
            elif token in [21]:
                localctx = GramParser.NullContext(self, localctx)
                self.enterOuterAlt(localctx, 8)
                self.state = 55
                self.match(GramParser.NULL)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArgsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(GramParser.ExprContext)
            else:
                return self.getTypedRuleContext(GramParser.ExprContext,i)


        def getRuleIndex(self):
            return GramParser.RULE_args

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterArgs" ):
                listener.enterArgs(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitArgs" ):
                listener.exitArgs(self)




    def args(self):

        localctx = GramParser.ArgsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_args)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 66
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 166723978) != 0):
                self.state = 58
                self.expr(0)
                self.state = 63
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==5:
                    self.state = 59
                    self.match(GramParser.T__4)
                    self.state = 60
                    self.expr(0)
                    self.state = 65
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)



        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Nested_attrContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def attr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(GramParser.AttrContext)
            else:
                return self.getTypedRuleContext(GramParser.AttrContext,i)


        def getRuleIndex(self):
            return GramParser.RULE_nested_attr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNested_attr" ):
                listener.enterNested_attr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNested_attr" ):
                listener.exitNested_attr(self)




    def nested_attr(self):

        localctx = GramParser.Nested_attrContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_nested_attr)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 68
            self.attr()
            self.state = 73
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,8,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 69
                    self.match(GramParser.T__5)
                    self.state = 70
                    self.attr()
                self.state = 75
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,8,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AttrContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME(self):
            return self.getToken(GramParser.NAME, 0)

        def getRuleIndex(self):
            return GramParser.RULE_attr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAttr" ):
                listener.enterAttr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAttr" ):
                listener.exitAttr(self)




    def attr(self):

        localctx = GramParser.AttrContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_attr)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 76
            self.match(GramParser.T__6)
            self.state = 77
            self.match(GramParser.NAME)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[1] = self.expr_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def expr_sempred(self, localctx:ExprContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 2)


            if predIndex == 1:
                return self.precpred(self._ctx, 1)
