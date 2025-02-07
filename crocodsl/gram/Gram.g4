grammar Gram;


program
    : expr + EOF #fullexpr
    ;

expr
    : value                                                                      #literal
    | NOT? '(' inner=expr ')'                                                    #parens
    | left=expr op=(EQ | NE | LT | LE | GT | GE | IN | HAS | MATCHES) right=expr #compare
    | left=expr op=(AND | OR) left=expr                                          #logical
    ;

value
    : '[' args ']'      #array
    | NAME '(' args ')' #function
    | nested_attr       #attribute
    | BOOL              #boolean
    | STRING            #string
    | INT               #int
    | FLOAT             #float
    | NULL              #null
    ;

args
    : ( expr ( ',' expr )* )?
    ;

nested_attr
    : attr ( '.' attr )*
    ;

attr
    : '$' NAME
    ;

// Operators
NOT: 'Not';

AND: 'And';
OR: 'Or';

EQ: 'Eq';
NE: 'Ne';
LT: 'Lt';
LE: 'Le';
GT: 'Gt';
GE: 'Ge';
IN: 'In';
HAS: 'Has';
MATCHES: 'Matches';

// Types

BOOL
    : 'True'
    | 'False'
    ;

NULL
    : 'None'
    ;

NAME
    : ALPHA NAME_CHARS*
    ;

STRING
    : '\'' (ESC | ~['\\])* '\''
    | '"' (ESC | ~["\\])* '"'
    ;

INT
    : '-'? POS_INT
    ;

POS_INT
    // Int with no leading 0s
    : '0'
    | [1-9] [0-9]*
    ;

SP
    : [ \r\n\t]+ -> skip
    ;

FLOAT
    : '-'? POS_INT '.' [0-9]+
    ;

// Character classes
fragment ESC
    : '\\' (['"\\/bfnrt])
    ;

fragment NAME_CHARS
    : ALPHA
    | DIGIT
    | '_'
    ;

fragment ALPHA
    : ( 'A'..'Z' | 'a'..'z' )
    ;

fragment DIGIT
    : ('0'..'9')
    ;
