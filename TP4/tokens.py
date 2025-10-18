import ply.lex as lex


states = (
    ('moeda', 'exclusive'),      # Só regras t_moeda_... funcionam
    ('selecionar', 'exclusive'), # Só regras t_selecionar_... funcionam
)

# --- 2. Lista de Tokens ---
tokens = (
    "LISTAR",
    "MOEDA",
    "SELECIONAR",
    "SAIR",
    "EUROS",
    "CENTIMOS",
    "PONTO",
    "CODIGO"
    
)


t_ignore = " \t\n"


def t_MOEDA(t):
    r"MOEDA"
    t.lexer.begin('moeda')  
    return t

def t_SELECIONAR(t):
    r"SELECIONAR"
    t.lexer.begin('selecionar') 
    return t


t_LISTAR = r"LISTAR"
t_SAIR = r"SAIR"


t_moeda_ignore = " \t"


t_selecionar_ignore = " \t"

def t_moeda_EUROS(t):
    r"\d+e"
    t.value = int(t.value[:-1]) 
    return t

def t_moeda_CENTIMOS(t):
    r"\d+c"
    t.value = int(t.value[:-1])
    return t

def t_moeda_VIRGULA(t):
    r","
    pass 

def t_moeda_PONTO(t):
    r"\."
    t.lexer.begin('INITIAL') # Volta ao estado inicial
    return t                 

def t_selecionar_CODIGO(t):
    r"[A-Z]\d+"  
    t.lexer.begin('INITIAL') 
    return t


def t_error(t):
    print(f"Comando ou caractere ilegal: {t.value[0]}")
    t.lexer.skip(1)


def t_moeda_error(t):
    print(f"Input inválido ao inserir moeda: {t.value[0]}. Esperava Xc, Ye ou '.'")
    
    t.lexer.begin('INITIAL') 
    t.lexer.skip(1)

def t_selecionar_error(t):
    print(f"Input inválido ao selecionar: {t.value[0]}. Esperava um código (ex: A23)")
    
    t.lexer.begin('INITIAL') 
    t.lexer.skip(1)


lexer = lex.lex()