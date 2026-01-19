import ply.lex as lex

reserved = {
    'program': 'PROGRAM',
    'var': 'VAR',
    'begin': 'BEGIN',
    'end': 'END',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'while': 'WHILE',
    'do': 'DO',
    'for': 'FOR',
    'to': 'TO',
    'downto': 'DOWNTO',
    'procedure': 'PROCEDURE',
    'function': 'FUNCTION',
    'array': 'ARRAY',
    'of': 'OF',
    'integer': 'INTEGER',
    'real' : 'REAL',
    'string' : 'STRING',
    'boolean': 'BOOLEAN',
    'readln': 'READLN',
    'writeln': 'WRITELN',
    'div': 'DIV',
    'mod': 'MOD',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    'repeat' : 'REPEAT',
    'until' : 'UNTIL',
    'true' : 'TRUE',
    'false' : 'FALSE',
    'length' : 'LENGTH'
}

literals = ("+","-","*","/","=",",",";","(",")",":",".","[","]","<",">")

tokens = [
    'ID', 'INT_VAL','REAL_VAL', 'STRING_LITERAL', 'ASSIGN','NEQ','LE','GE','RANGE'
] + list(reserved.values())

t_ASSIGN = r':='
t_NEQ = r'<>'
t_LE = r'<='
t_GE = r'>='
t_RANGE = r'\.\.'

def t_COMMENT(t):
    # { [LE TUDO QUE NAO SEJA "}" -> ^}]*  } 
    # | (* [QQ CHAR OU \n]*? -> repete até se encontrar a sequencia final *)
    r'\{[^}]*\} | \(\*(.|\n)*?\*\)' #Temos que fazer lazy, porque se nao alguns comentarios comia demasiado
    pass

def t_COMMENT_LINE(t):
    r'//.*'
    pass

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value.lower(), 'ID')
    return t

def t_REAL_VAL(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INT_VAL(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING_LITERAL(t):
    r'\'([^\']| \'\')*\''       #Começa com plica, aceita tudo que nao seja plica ou plicas duplas, acaba com plica
    t.value = t.value[1:-1]         # para remover as plicas no return
    return t    

t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Carácter ilegal: {t.value[0]}, linha {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()