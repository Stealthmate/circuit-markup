grammar CircuitMarkup;

program : statement* EOF;
statement : useStatement | nodePlaceStatement | edgeChain;
useStatement : USE stringL ';';

nodePlaceStatement : ID '{' attributeAssigns '}'  position ';' | ID position ';';
attributeAssigns : attributeAssign*;
attributeAssign : ID '=' expression ';';

edgeChain : position edge position | position edge edgeChain ;

edge : '-{' attributeAssigns '}-' | '--';

position : coordinates | nodeAnchor ;
nodeAnchor : ID '.' ID ;
coordinates : '(' NUMBER ',' NUMBER ')';

expression : stringL;
stringL : QUOTED_STRING;

USE : 'use';
ID : [a-zA-Z][a-zA-Z0-9_]*;
NUMBER: [-]?[0-9]+(.[0-9]+)?;
QUOTED_STRING : '"' SAFE_STRING '"' ;
fragment SAFE_STRING : ~["]* ;

WS : [ \t\n\r]+ -> skip ;
