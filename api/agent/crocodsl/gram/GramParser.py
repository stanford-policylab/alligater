# Generated from Gram.g4 by ANTLR 4.10.1
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
        4,1,27,71,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,1,0,1,0,1,0,3,
        0,14,8,0,1,0,1,0,1,0,1,0,3,0,20,8,0,1,0,1,0,1,0,1,0,1,0,1,0,5,0,
        28,8,0,10,0,12,0,31,9,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,3,1,48,8,1,1,2,1,2,1,2,5,2,53,8,2,10,2,12,2,
        56,9,2,3,2,58,8,2,1,3,1,3,1,3,5,3,63,8,3,10,3,12,3,66,9,3,1,4,1,
        4,1,4,1,4,0,1,0,5,0,2,4,6,8,0,2,1,0,11,19,1,0,9,10,79,0,19,1,0,0,
        0,2,47,1,0,0,0,4,57,1,0,0,0,6,59,1,0,0,0,8,67,1,0,0,0,10,11,6,0,
        -1,0,11,20,3,2,1,0,12,14,5,8,0,0,13,12,1,0,0,0,13,14,1,0,0,0,14,
        15,1,0,0,0,15,16,5,1,0,0,16,17,3,0,0,0,17,18,5,2,0,0,18,20,1,0,0,
        0,19,10,1,0,0,0,19,13,1,0,0,0,20,29,1,0,0,0,21,22,10,2,0,0,22,23,
        7,0,0,0,23,28,3,0,0,3,24,25,10,1,0,0,25,26,7,1,0,0,26,28,3,0,0,2,
        27,21,1,0,0,0,27,24,1,0,0,0,28,31,1,0,0,0,29,27,1,0,0,0,29,30,1,
        0,0,0,30,1,1,0,0,0,31,29,1,0,0,0,32,33,5,3,0,0,33,34,3,4,2,0,34,
        35,5,4,0,0,35,48,1,0,0,0,36,37,5,22,0,0,37,38,5,1,0,0,38,39,3,4,
        2,0,39,40,5,2,0,0,40,48,1,0,0,0,41,48,3,6,3,0,42,48,5,20,0,0,43,
        48,5,23,0,0,44,48,5,24,0,0,45,48,5,27,0,0,46,48,5,21,0,0,47,32,1,
        0,0,0,47,36,1,0,0,0,47,41,1,0,0,0,47,42,1,0,0,0,47,43,1,0,0,0,47,
        44,1,0,0,0,47,45,1,0,0,0,47,46,1,0,0,0,48,3,1,0,0,0,49,54,3,0,0,
        0,50,51,5,5,0,0,51,53,3,0,0,0,52,50,1,0,0,0,53,56,1,0,0,0,54,52,
        1,0,0,0,54,55,1,0,0,0,55,58,1,0,0,0,56,54,1,0,0,0,57,49,1,0,0,0,
        57,58,1,0,0,0,58,5,1,0,0,0,59,64,3,8,4,0,60,61,5,6,0,0,61,63,3,8,
        4,0,62,60,1,0,0,0,63,66,1,0,0,0,64,62,1,0,0,0,64,65,1,0,0,0,65,7,
        1,0,0,0,66,64,1,0,0,0,67,68,5,7,0,0,68,69,5,22,0,0,69,9,1,0,0,0,
        8,13,19,27,29,47,54,57,64
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

    RULE_expr = 0
    RULE_value = 1
    RULE_args = 2
    RULE_nested_attr = 3
    RULE_attr = 4

    ruleNames =  [ "expr", "value", "args", "nested_attr", "attr" ]

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
        self.checkVersion("4.10.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




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
        _startState = 0
        self.enterRecursionRule(localctx, 0, self.RULE_expr, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 19
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [GramParser.T__2, GramParser.T__6, GramParser.BOOL, GramParser.NULL, GramParser.NAME, GramParser.STRING, GramParser.INT, GramParser.FLOAT]:
                localctx = GramParser.LiteralContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx

                self.state = 11
                self.value()
                pass
            elif token in [GramParser.T__0, GramParser.NOT]:
                localctx = GramParser.ParensContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 13
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==GramParser.NOT:
                    self.state = 12
                    self.match(GramParser.NOT)


                self.state = 15
                self.match(GramParser.T__0)
                self.state = 16
                localctx.inner = self.expr(0)
                self.state = 17
                self.match(GramParser.T__1)
                pass
            else:
                raise NoViableAltException(self)

            self._ctx.stop = self._input.LT(-1)
            self.state = 29
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,3,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 27
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,2,self._ctx)
                    if la_ == 1:
                        localctx = GramParser.CompareContext(self, GramParser.ExprContext(self, _parentctx, _parentState))
                        localctx.left = _prevctx
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 21
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                        self.state = 22
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << GramParser.EQ) | (1 << GramParser.NE) | (1 << GramParser.LT) | (1 << GramParser.LE) | (1 << GramParser.GT) | (1 << GramParser.GE) | (1 << GramParser.IN) | (1 << GramParser.HAS) | (1 << GramParser.MATCHES))) != 0)):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 23
                        localctx.right = self.expr(3)
                        pass

                    elif la_ == 2:
                        localctx = GramParser.LogicalContext(self, GramParser.ExprContext(self, _parentctx, _parentState))
                        localctx.left = _prevctx
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 24
                        if not self.precpred(self._ctx, 1):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 1)")
                        self.state = 25
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not(_la==GramParser.AND or _la==GramParser.OR):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 26
                        localctx.left = self.expr(2)
                        pass

             
                self.state = 31
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,3,self._ctx)

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
        self.enterRule(localctx, 2, self.RULE_value)
        try:
            self.state = 47
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [GramParser.T__2]:
                localctx = GramParser.ArrayContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 32
                self.match(GramParser.T__2)
                self.state = 33
                self.args()
                self.state = 34
                self.match(GramParser.T__3)
                pass
            elif token in [GramParser.NAME]:
                localctx = GramParser.FunctionContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 36
                self.match(GramParser.NAME)
                self.state = 37
                self.match(GramParser.T__0)
                self.state = 38
                self.args()
                self.state = 39
                self.match(GramParser.T__1)
                pass
            elif token in [GramParser.T__6]:
                localctx = GramParser.AttributeContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 41
                self.nested_attr()
                pass
            elif token in [GramParser.BOOL]:
                localctx = GramParser.BooleanContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 42
                self.match(GramParser.BOOL)
                pass
            elif token in [GramParser.STRING]:
                localctx = GramParser.StringContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 43
                self.match(GramParser.STRING)
                pass
            elif token in [GramParser.INT]:
                localctx = GramParser.IntContext(self, localctx)
                self.enterOuterAlt(localctx, 6)
                self.state = 44
                self.match(GramParser.INT)
                pass
            elif token in [GramParser.FLOAT]:
                localctx = GramParser.FloatContext(self, localctx)
                self.enterOuterAlt(localctx, 7)
                self.state = 45
                self.match(GramParser.FLOAT)
                pass
            elif token in [GramParser.NULL]:
                localctx = GramParser.NullContext(self, localctx)
                self.enterOuterAlt(localctx, 8)
                self.state = 46
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
        self.enterRule(localctx, 4, self.RULE_args)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 57
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << GramParser.T__0) | (1 << GramParser.T__2) | (1 << GramParser.T__6) | (1 << GramParser.NOT) | (1 << GramParser.BOOL) | (1 << GramParser.NULL) | (1 << GramParser.NAME) | (1 << GramParser.STRING) | (1 << GramParser.INT) | (1 << GramParser.FLOAT))) != 0):
                self.state = 49
                self.expr(0)
                self.state = 54
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==GramParser.T__4:
                    self.state = 50
                    self.match(GramParser.T__4)
                    self.state = 51
                    self.expr(0)
                    self.state = 56
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
        self.enterRule(localctx, 6, self.RULE_nested_attr)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 59
            self.attr()
            self.state = 64
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,7,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 60
                    self.match(GramParser.T__5)
                    self.state = 61
                    self.attr() 
                self.state = 66
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,7,self._ctx)

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
        self.enterRule(localctx, 8, self.RULE_attr)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 67
            self.match(GramParser.T__6)
            self.state = 68
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
        self._predicates[0] = self.expr_sempred
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
         




