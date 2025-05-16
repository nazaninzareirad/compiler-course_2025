lexer grammar CMinusle;

// Keywords
IF      : 'if' ;
ELSE    : 'else' ;
VOID    : 'void' ;
INT     : 'int' ;
REPEAT  : 'repeat' ;
BREAK   : 'break' ;
UNTIL   : 'until' ;
RETURN  : 'return' ;

// Identifiers
ID      : [a-zA-Z][a-zA-Z0-9]* ;

// Numbers
NUM     : [0-9]+ ;

// Symbols
SEMI    : ';' ;
COMMA   : ',' ;
LBRACK  : '[' ;
RBRACK  : ']' ;
LPAREN  : '(' ;
RPAREN  : ')' ;
LBRACE  : '{' ;
RBRACE  : '}' ;
PLUS    : '+' ;
MINUS   : '-' ;
TIMES   : '*' ;
LT      : '<' ;
ASSIGN  : '=' ;
EQ      : '==' ;

// Whitespace and comments
WS      : [ \t\r\n]+ -> skip ;
COMMENT : '/*' .*? '*/' -> skip ;
