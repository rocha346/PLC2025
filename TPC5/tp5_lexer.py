import ply.lex as lex

tokens = ('SUM', 'SUB', 'MUL', 'DIV', 'PA', 'PF', 'INT')

t_SUM = r'\+'
t_SUB = r'-'
t_MUL = r'\*'
t_DIV = r'/'
t_PA = r'\('
t_PF = r'\)'
t_INT = r'\d+'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = '\t '

def t_error(t):
    print('Carácter desconhecido: ', t.value[0], 'Linha: ', t.lexer.lineno)
    t.lexer.skip(1)

lexer = lex.lex()
