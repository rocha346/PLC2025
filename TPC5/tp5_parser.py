from tp5_lexer import lexer

# Gramática
#
# Expr -> Termo Expr'
# Expr' -> "+" Termo Expr' | "-" Termo Expr' | ε
# 
# Termo -> Fator Termo'
# Termo' -> "*" Fator Termo' | "/" Fator Termo' | ε
#
# Fator -> Int | "(" Expr ")"

prox_simb = None

def processa_terminal(tipo):
    global prox_simb
    if tipo == prox_simb.type:
        token_atual = prox_simb
        prox_simb = lexer.token()
        print(f"Reconheci: {token_atual.value}")
    else:
        raise ValueError("Invalid token")
    
def rec_Fator():
    global prox_simb
    if prox_simb and prox_simb.type == "INT":
        processa_terminal("INT")
    elif prox_simb and prox_simb.type == "PA":
        processa_terminal("PA")
        rec_Expr()
        if prox_simb and prox_simb.type == "PF":
            processa_terminal("PF")
        else:
            raise ValueError("Era esperado um ')'")
    else:
        raise ValueError("Era esperado um INT ou um '('")

    
def rec_Termolinha():
    global prox_simb
    if prox_simb and prox_simb.type == "MUL":
        processa_terminal("MUL")
        rec_Fator()
        rec_Termolinha()
    elif prox_simb and prox_simb.type == "DIV":
        processa_terminal("DIV")
        rec_Fator()
        rec_Termolinha()
    else:
        pass

def rec_Termo():
    rec_Fator()
    rec_Termolinha()

def rec_Exprlinha():
    global prox_simb
    if prox_simb and prox_simb.type == "SUM":
        processa_terminal("SUM")
        rec_Termo()
        rec_Exprlinha()
    elif prox_simb and prox_simb.type == "SUB":
        processa_terminal("SUB")
        rec_Termo()
        rec_Exprlinha()
    else:
        pass

def rec_Expr():
    global prox_simb
    rec_Termo()
    rec_Exprlinha()

def rec_Parser(linha):
    global prox_simb
    lexer.input(linha)
    prox_simb = lexer.token()
    rec_Expr()
    print("That's all folks!")

linha = input("Introduza uma expressão: ")
rec_Parser(linha)