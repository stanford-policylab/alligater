# Generated from Gram.g4 by ANTLR 4.9.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\32")
        buf.write(";\4\2\t\2\4\3\t\3\4\4\t\4\3\2\3\2\3\2\5\2\f\n\2\3\2\3")
        buf.write("\2\3\2\3\2\5\2\22\n\2\3\2\3\2\3\2\3\2\3\2\3\2\7\2\32\n")
        buf.write("\2\f\2\16\2\35\13\2\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3")
        buf.write("\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\5\3/\n\3\3\4\3\4\3\4\7")
        buf.write("\4\64\n\4\f\4\16\4\67\13\4\5\49\n\4\3\4\2\3\2\5\2\4\6")
        buf.write("\2\4\3\2\f\22\3\2\n\13\2D\2\21\3\2\2\2\4.\3\2\2\2\68\3")
        buf.write("\2\2\2\b\t\b\2\1\2\t\22\5\4\3\2\n\f\7\t\2\2\13\n\3\2\2")
        buf.write("\2\13\f\3\2\2\2\f\r\3\2\2\2\r\16\7\3\2\2\16\17\5\2\2\2")
        buf.write("\17\20\7\4\2\2\20\22\3\2\2\2\21\b\3\2\2\2\21\13\3\2\2")
        buf.write("\2\22\33\3\2\2\2\23\24\f\4\2\2\24\25\t\2\2\2\25\32\5\2")
        buf.write("\2\5\26\27\f\3\2\2\27\30\t\3\2\2\30\32\5\2\2\4\31\23\3")
        buf.write("\2\2\2\31\26\3\2\2\2\32\35\3\2\2\2\33\31\3\2\2\2\33\34")
        buf.write("\3\2\2\2\34\3\3\2\2\2\35\33\3\2\2\2\36\37\7\5\2\2\37 ")
        buf.write("\5\6\4\2 !\7\6\2\2!/\3\2\2\2\"#\7\25\2\2#$\7\3\2\2$%\5")
        buf.write("\6\4\2%&\7\4\2\2&/\3\2\2\2\'(\7\7\2\2(/\7\25\2\2)/\7\23")
        buf.write("\2\2*/\7\26\2\2+/\7\27\2\2,/\7\32\2\2-/\7\24\2\2.\36\3")
        buf.write("\2\2\2.\"\3\2\2\2.\'\3\2\2\2.)\3\2\2\2.*\3\2\2\2.+\3\2")
        buf.write("\2\2.,\3\2\2\2.-\3\2\2\2/\5\3\2\2\2\60\65\5\2\2\2\61\62")
        buf.write("\7\b\2\2\62\64\5\2\2\2\63\61\3\2\2\2\64\67\3\2\2\2\65")
        buf.write("\63\3\2\2\2\65\66\3\2\2\2\669\3\2\2\2\67\65\3\2\2\28\60")
        buf.write("\3\2\2\289\3\2\2\29\7\3\2\2\2\t\13\21\31\33.\658")
        return buf.getvalue()


class GramParser ( Parser ):

    grammarFileName = "Gram.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'('", "')'", "'['", "']'", "'$'", "','", 
                     "'Not'", "'And'", "'Or'", "'Eq'", "'Ne'", "'Lt'", "'Le'", 
                     "'Gt'", "'Ge'", "'In'", "<INVALID>", "'None'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "NOT", "AND", 
                      "OR", "EQ", "NE", "LT", "LE", "GT", "GE", "IN", "BOOL", 
                      "NULL", "NAME", "STRING", "INT", "POS_INT", "SP", 
                      "FLOAT" ]

    RULE_expr = 0
    RULE_value = 1
    RULE_args = 2

    ruleNames =  [ "expr", "value", "args" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    NOT=7
    AND=8
    OR=9
    EQ=10
    NE=11
    LT=12
    LE=13
    GT=14
    GE=15
    IN=16
    BOOL=17
    NULL=18
    NAME=19
    STRING=20
    INT=21
    POS_INT=22
    SP=23
    FLOAT=24

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9.2")
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
            self.state = 15
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [GramParser.T__2, GramParser.T__4, GramParser.BOOL, GramParser.NULL, GramParser.NAME, GramParser.STRING, GramParser.INT, GramParser.FLOAT]:
                localctx = GramParser.LiteralContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx

                self.state = 7
                self.value()
                pass
            elif token in [GramParser.T__0, GramParser.NOT]:
                localctx = GramParser.ParensContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 9
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==GramParser.NOT:
                    self.state = 8
                    self.match(GramParser.NOT)


                self.state = 11
                self.match(GramParser.T__0)
                self.state = 12
                localctx.inner = self.expr(0)
                self.state = 13
                self.match(GramParser.T__1)
                pass
            else:
                raise NoViableAltException(self)

            self._ctx.stop = self._input.LT(-1)
            self.state = 25
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,3,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 23
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,2,self._ctx)
                    if la_ == 1:
                        localctx = GramParser.CompareContext(self, GramParser.ExprContext(self, _parentctx, _parentState))
                        localctx.left = _prevctx
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 17
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                        self.state = 18
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << GramParser.EQ) | (1 << GramParser.NE) | (1 << GramParser.LT) | (1 << GramParser.LE) | (1 << GramParser.GT) | (1 << GramParser.GE) | (1 << GramParser.IN))) != 0)):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 19
                        localctx.right = self.expr(3)
                        pass

                    elif la_ == 2:
                        localctx = GramParser.LogicalContext(self, GramParser.ExprContext(self, _parentctx, _parentState))
                        localctx.left = _prevctx
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 20
                        if not self.precpred(self._ctx, 1):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 1)")
                        self.state = 21
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not(_la==GramParser.AND or _la==GramParser.OR):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 22
                        localctx.left = self.expr(2)
                        pass

             
                self.state = 27
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

        def NAME(self):
            return self.getToken(GramParser.NAME, 0)

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
            self.state = 44
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [GramParser.T__2]:
                localctx = GramParser.ArrayContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 28
                self.match(GramParser.T__2)
                self.state = 29
                self.args()
                self.state = 30
                self.match(GramParser.T__3)
                pass
            elif token in [GramParser.NAME]:
                localctx = GramParser.FunctionContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 32
                self.match(GramParser.NAME)
                self.state = 33
                self.match(GramParser.T__0)
                self.state = 34
                self.args()
                self.state = 35
                self.match(GramParser.T__1)
                pass
            elif token in [GramParser.T__4]:
                localctx = GramParser.AttributeContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 37
                self.match(GramParser.T__4)
                self.state = 38
                self.match(GramParser.NAME)
                pass
            elif token in [GramParser.BOOL]:
                localctx = GramParser.BooleanContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 39
                self.match(GramParser.BOOL)
                pass
            elif token in [GramParser.STRING]:
                localctx = GramParser.StringContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 40
                self.match(GramParser.STRING)
                pass
            elif token in [GramParser.INT]:
                localctx = GramParser.IntContext(self, localctx)
                self.enterOuterAlt(localctx, 6)
                self.state = 41
                self.match(GramParser.INT)
                pass
            elif token in [GramParser.FLOAT]:
                localctx = GramParser.FloatContext(self, localctx)
                self.enterOuterAlt(localctx, 7)
                self.state = 42
                self.match(GramParser.FLOAT)
                pass
            elif token in [GramParser.NULL]:
                localctx = GramParser.NullContext(self, localctx)
                self.enterOuterAlt(localctx, 8)
                self.state = 43
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
            self.state = 54
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << GramParser.T__0) | (1 << GramParser.T__2) | (1 << GramParser.T__4) | (1 << GramParser.NOT) | (1 << GramParser.BOOL) | (1 << GramParser.NULL) | (1 << GramParser.NAME) | (1 << GramParser.STRING) | (1 << GramParser.INT) | (1 << GramParser.FLOAT))) != 0):
                self.state = 46
                self.expr(0)
                self.state = 51
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==GramParser.T__5:
                    self.state = 47
                    self.match(GramParser.T__5)
                    self.state = 48
                    self.expr(0)
                    self.state = 53
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)



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
         




