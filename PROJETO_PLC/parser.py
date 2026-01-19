import ply.yacc as yacc
from lexer import reserved, literals, tokens, lexer

def p_program(p):
    r'program : PROGRAM ID ";" vars lista_subprogramas conteudo "."'
    # ('PROGRAM', ID, vars, subprogramas,bloco_main)
    p[0] = ('PROGRAM', p[2], p[4], p[5], p[6])

def p_conteudo(p):
    r'conteudo : BEGIN lista_comandos END'
    p[0] = ('BLOCO', p[2])

#--- SUBPROGRAMAS ---
def p_lista_subprogramas_rec(p):
    r'lista_subprogramas : lista_subprogramas subprograma'
    p[0] = p[1] + [p[2]]

def p_lista_subprogramas_vazio(p):
    r'lista_subprogramas : '
    p[0] = []

def p_subprograma_function(p):
    r'subprograma : decl_function'
    p[0] = p[1]

def p_subprograma_procedure(p):
    r'subprograma : decl_procedure'
    p[0] = p[1]

def p_decl_function(p):
    r'decl_function : FUNCTION ID "(" args_opt ")" ":" tipo ";" vars conteudo ";"'
    p[0] = ('FUNCTION',p[2],p[4],p[7],p[9],p[10])

def p_decl_procedure(p):
    r'decl_procedure : PROCEDURE ID "(" args_opt ")" ";" vars conteudo ";"'
    p[0] = ('PROCEDURE', p[2],p[4],p[7],p[8])

def p_args_opt_lista(p):
    r'args_opt : lista_args'
    p[0] = p[1]

def p_args_opt_vazio(p):
    r'args_opt : '
    p[0] = []

def p_lista_args_rec(p):
    r'lista_args : lista_args ";" arg_grupo'
    p[0] = p[1] + [p[3]]

def p_lista_args_single(p):
    r'lista_args : arg_grupo'
    p[0] = [p[1]]

def p_arg_grupo(p):
    r'arg_grupo : lista_ids ":" tipo'
    p[0] = (p[1],p[3])

#--- VARS ---

def p_vars_lista(p):
    r'vars : VAR lista_vars'
    p[0] = p[2]

def p_vars_vazio(p):
    r'vars : '
    p[0] = []

def p_lista_vars_rec(p):
    r'lista_vars : lista_vars decl_var'
    p[0] = p[1] + [p[2]]    #Juntamos listas

def p_lista_vars_single(p):
    r'lista_vars : decl_var'
    p[0] = [p[1]]
 
def p_decl_var(p):
    r'decl_var : lista_ids ":" tipo ";"'
    # ('DECL_VAR', lista_ids, tipo) -> ('DECL_VAR', (['x', 'y'], 'INTEGER')
    p[0] = ('DECL_VAR', p[1], p[3])

def p_lista_ids_rec(p):
    r'lista_ids : lista_ids "," ID'
    p[0] = p[1] + [p[3]]

def p_lista_ids_single(p):
    r'lista_ids : ID'
    p[0] = [p[1]]

#TIPOS VARS

def p_tipo_integer(p):
    r'tipo : INTEGER'
    p[0] = 'INTEGER'

def p_tipo_boolean(p):
    r'tipo : BOOLEAN'
    p[0] = 'BOOLEAN'

def p_tipo_real(p):
    r'tipo : REAL'
    p[0] = 'REAL'

def p_tipo_string(p):
    r'tipo : STRING'
    p[0] = 'STRING'

def p_tipo_array(p):
    r'tipo : ARRAY "[" tam "]" OF tipo'
    # (ARRAY, range, tipo)
    p[0] = ('ARRAY', p[3], p[6])

def p_tam(p):
    r'tam : INT_VAL RANGE INT_VAL'
    p[0] = (p[1],p[3])


# COMANDOS
def p_lista_comandos_rec(p):
    r'lista_comandos : lista_comandos ";" comando'
    if p[3] is None:
        # Casos onde o ultima comando antes do end final acaba com um ";". Assim nao reconhece o vazio
        p[0] = p[1]
    else :
        p[0] = p[1] + [p[3]]    

def p_lista_comandos_single(p):
    r'lista_comandos : comando'
    p[0] = [p[1]]

def p_comando_assignment(p):
    r'comando : assignment'
    p[0] = p[1]

def p_comando_proc_call(p):
    r'comando : procedure_call'
    p[0] = p[1]

def p_comando_if(p):
    r'comando : if_comando'
    p[0] = p[1]

def p_comando_while(p):
    r'comando : while_comando'
    p[0] = p[1]

def p_comando_for(p):
    r'comando : for_comando'
    p[0] = p[1]

def p_comando_io(p):
    r'comando : io_comando'
    p[0] = p[1]

def p_comando_repeat(p):
    r'comando : repeat_comando'
    p[0] = p[1]

def p_comando_conteudo(p):
    r'comando : conteudo'
    p[0] = p[1]

def p_comando_vazio(p):
    r'comando : '
    p[0] = None

def p_assignment(p):
    r'assignment : variavel ASSIGN exp'
    p[0] = ('ASSIGN', p[1],p[3])

def p_variavel_single(p):
    r'variavel : ID'
    p[0] = ('ID',p[1])

def p_variavel_array(p):
    r'variavel : ID "[" exp "]"'
    p[0] = ('ARRAY_ACESSO',p[1],p[3])

def p_procedure_call(p):
    r'procedure_call : ID "(" args_subp ")"'
    p[0] = ('PROC_CALL', p[1],p[3])

def p_args_subp_lista(p):
    r'args_subp : lista_exp'
    p[0] = p[1]

def p_args_subp_vazio(p):
    r'args_subp : '
    p[0] = []

def p_if_comando_no_else(p):
    r'if_comando : IF exp THEN comando'
    p[0] = ('IF',p[2],p[4],None)

def p_if_comando_else(p):
    r'if_comando : IF exp THEN comando ELSE comando'
    p[0] = ('IF',p[2],p[4],p[6])

def p_while_comando(p):
    r'while_comando : WHILE exp DO comando'
    p[0] = ('WHILE',p[2],p[4])

def p_for_comando_to(p):
    r'for_comando : FOR ID ASSIGN exp TO exp DO comando'
    p[0] = ('FOR',p[2],p[4],p[6],p[8],'to')

def p_for_comando_downto(p):
    r'for_comando : FOR ID ASSIGN exp DOWNTO exp DO comando'
    p[0] = ('FOR',p[2],p[4],p[6],p[8],'downto')

def p_io_comando_writeln_exp(p):
    r'io_comando : WRITELN "(" lista_exp ")"'
    p[0] = ('WRITELN',p[3])

def p_io_comando_writeln_vazio(p):
    r'io_comando : WRITELN'
    p[0] = ('WRITELN',[])

def p_io_comando_writeln_vazio2(p):
    r'io_comando : WRITELN "(" ")"'
    p[0] = ('WRITELN',[])

def p_io_comando_readln_var(p):
    r'io_comando : READLN "(" variavel ")"'
    p[0] = ('READLN',p[3])

def p_io_comando_readln_vazio(p):
    r'io_comando : READLN'
    p[0] = ('READLN',[])

def p_io_comando_readln_vazio2(p):
    r'io_comando : READLN "(" ")"'
    p[0] = ('READLN',[])

def p_repeat_comando(p):
    r'repeat_comando : REPEAT lista_comandos UNTIL exp'
    p[0] = ('REPEAT',p[2],p[4])

#EXP
def p_lista_exp_rec(p):
    r'lista_exp : lista_exp "," exp'
    p[0] = p[1] + [p[3]]

def p_lista_exp_single(p):
    r'lista_exp : exp'
    p[0] = [p[1]]


#nivel 1 

def p_exp_single(p):
    r'exp : exp_simples'
    p[0] = p[1]

def p_exp_eq(p):
    r'exp : exp_simples "=" exp_simples'
    p[0] = ('BINOP', "=", p[1],p[3])

def p_exp_neq(p):
    r'exp : exp_simples NEQ exp_simples'
    p[0] = ('BINOP', "<>", p[1],p[3])

def p_exp_lt(p):
    r'exp : exp_simples "<" exp_simples'
    p[0] = ('BINOP', "<", p[1],p[3])

def p_exp_gt(p):
    r'exp : exp_simples ">" exp_simples'
    p[0] = ('BINOP', ">", p[1],p[3])

def p_exp_le(p):
    r'exp : exp_simples LE exp_simples'
    p[0] = ('BINOP', "<=", p[1],p[3])

def p_exp_ge(p):
    r'exp : exp_simples GE exp_simples'
    p[0] = ('BINOP', ">=", p[1],p[3])


#NIVEL 2
def p_exp_simples_add(p):
    r'exp_simples : exp_simples "+" term'
    p[0] = ('BINOP','+',p[1],p[3])

def p_exp_simples_minus(p):
    r'exp_simples : exp_simples "-" term'
    p[0] = ('BINOP','-',p[1],p[3])

def p_exp_simples_or(p):
    r'exp_simples : exp_simples OR term'
    p[0] = ('BINOP','OR',p[1],p[3])

def p_exp_simples_term(p):
    r'exp_simples : term'
    p[0] = p[1]


#NIVEL3
def p_term_mult(p):
    r'term : term "*" factor'
    p[0] = ('BINOP', '*', p[1],p[3])

def p_term_dividir(p):
    r'term : term "/" factor'
    p[0] = ('BINOP', '/', p[1],p[3])

def p_term_div_int(p):
    r'term : term DIV factor'
    p[0] = ('BINOP', 'DIV', p[1],p[3])

def p_term_mod(p):
    r'term : term MOD factor'
    p[0] = ('BINOP', 'MOD', p[1],p[3])

def p_term_and(p):
    r'term : term AND factor'
    p[0] = ('BINOP', 'AND', p[1],p[3])

def p_term_factor(p):
    r'term : factor'
    p[0] = p[1]


#NIVEL 4
def p_factor_variavel(p):
    r'factor : variavel'
    p[0] = p[1]

def p_factor_int(p):
    r'factor : INT_VAL'
    p[0] = ('INTEGER',p[1])

def p_factor_real(p):
    r'factor : REAL_VAL'
    p[0] = ('REAL',p[1])

def p_factor_string(p):
    r'factor : STRING_LITERAL'
    p[0] = ('STRING',p[1])

def p_factor_true(p):
    r'factor : TRUE'
    p[0] = ('BOOLEAN',True)

def p_factor_false(p):
    r'factor : FALSE'
    p[0] = ('BOOLEAN',False)

def p_factor_exp(p):
    r'factor : "(" exp ")"'
    p[0] = p[2]

def p_factor_not(p):
    r'factor : NOT factor'
    p[0] = ('UNOP', 'NOT', p[2])

def p_factor_uminus(p):
    r'factor : "-" factor'
    p[0] = ('UNOP', '-', p[2])

def p_factor_length(p):
    r'factor : LENGTH "(" exp ")"'
    p[0] = ('LENGTH',p[3])

def p_factor_call(p):
    r'factor : function_call'
    p[0] = p[1]

def p_function_call(p):
    r'function_call : ID "(" args_subp ")"'
    p[0] = ('FUNC_CALL',p[1],p[3])

def p_error(p):
    if p:
        print(f"Erro de sintaxe próximo ao token '{p.value}' na linha {p.lineno}")
    else:
        print("Erro de sintaxe no final do arquivo (EOF)")


parser = yacc.yacc()