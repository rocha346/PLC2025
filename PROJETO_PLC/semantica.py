import sys

class Semantica:
    # [{}] -> [{VARS_GLOBAIS}, {VARS_FUNC_A}, {VARS_FUNC_B...}]

   
    def __init__(self):
        self.tabela = [{}]
        # { nome : ( ,tipo, extra)}
        # function Soma(a,b: integer) : integer
        # Soma : ('FUNCTION', 'INTEGER', ['INTEGER','INTEGER'])
        # var x : integer
        # x : (VAR,INTEGER,None)
        # var lista: array[1..10] of integer
        # lista : (VAR,(ARRAY,(1,10),INTEGER), None)
        self.ret = None

    def tabela_atual(self):
        return self.tabela[-1]
    
    def append_tabela(self):
        self.tabela.append({})

    def pop_tabela(self):
        self.tabela.pop()
    
    def declarar(self, nome, categoria, tipo, extra=None):
        if nome in self.tabela_atual():
            raise Exception(f"{nome} já foi declarado na tabela.")
        
        self.tabela_atual()[nome] = (categoria,tipo,extra)

    def procura(self,nome):
        for entrada in reversed(self.tabela):
            if nome in entrada:
                return entrada[nome]


        raise Exception(f"{nome} não está declarado!")
    
    
    # Visitar os nodos
    def visita(self,node):
        if node is None: return None

        # p[0] = ('WHILE',p[2],p[4])
        if isinstance(node, tuple):
            tipo = node[0]
            funcao = f'visita_{tipo}'
            visitar = getattr(self, funcao, self.default)
            return visitar(node)

        #  p[0] = p[1] + [p[3]]  
        elif isinstance(node,list):
            for i in node:
                self.visita(i)

    def default(self,node):
        raise Exception(f"Função não encontrada visita_{node[0]}")


    def visita_PROGRAM(self,node):
        # ('PROGRAM', ID, vars, subprogramas, bloco_main)

        # Analisa subprogramas
        self.visita(node[2])

        #Analisa as vars
        self.visita(node[3])

        #Analisa o bloco
        self.visita(node[4])


    def visita_DECL_VAR(self,node):
        # ('DECL_VAR', lista_ids, tipo)

        tipo = node[2]
        if isinstance(tipo, tuple) and tipo[0] == 'ARRAY':
            # tipo -> (ARRAY, range, tipo)
            range = tipo[1] # (range0,range 1)
            if not isinstance(range[0],int) or not isinstance(range[1],int):
                raise Exception(f"Intervalo do array deve ser inteiro")

            if range[0] > range[1]:
                raise Exception(f"Intervalo do array inválido [{range[0]}..{range[1]}]")
        
        for nome in node[1]:
            # ('DECL_VAR', (['x', 'y'], 'INTEGER')
            self.declarar(nome,'VAR',tipo)

    
    #SUBPROGRAMAS
    def visita_FUNCTION(self,node):
        # ('FUNCTION', nome, args, tipo, vars, conteudo)

        nome = node[1]
        args = node[2]
        tipo_retorno = node[3]

        args_input_tipos = [] # [STRING,INTEGER,INTEGER]
        # args = [(['bin'], 'STRING'), (['x', 'y'], 'INTEGER')]
        for grupo_arg in args: 
            #grupo_arg : ([ids],tipo)
            c = len(grupo_arg[0])
            t = grupo_arg[1]
            args_input_tipos.extend([t] * c)
        
        self.declarar(nome,'FUNCTION',tipo_retorno,args_input_tipos)


        #Entrar na tabela local
        self.append_tabela()
        self.ret = tipo_retorno

        for grupo_arg in args:
            ids = grupo_arg[0]
            tipo = grupo_arg[1]
            for nome_arg in ids:
                self.declarar(nome_arg,'VAR',tipo)

        self.declarar(nome,'VAR',tipo_retorno)


        #Vars
        self.visita(node[4])

        #Conteudo
        self.visita(node[5])

        self.pop_tabela()
        self.ret = None
    
    
    def visita_PROCEDURE(self,node):
        # ('PROCEDURE', nome, args, vars, conteudo)
        nome = node[1]
        args = node[2]

        args_input_tipos = []
        for grupo_arg in args:  
            #grupo_arg : ([ids],tipo)
            c = len(grupo_arg[0])
            t = grupo_arg[1]
            args_input_tipos.extend([t] * c)
        
        self.declarar(nome,'PROCEDURE',None, args_input_tipos)

        self.append_tabela()

        for grupo_arg in args:
            ids = grupo_arg[0]
            tipo = grupo_arg[1]
            for nome_arg in ids:
                self.declarar(nome_arg,'VAR',tipo)

        self.visita(node[3])
        self.visita(node[4])

        self.pop_tabela()

    

    # COMANDOS

    def visita_BLOCO(self,node):
        # ('BLOCO', [lista_comandos])
        for comando in node[1]:
            if comando is not None:     #Caso de ter none na lista
                self.visita(comando)

    
    def visita_ASSIGN(self, node):
        # ('ASSIGN', VAR, EXP)
        # OU APARECE (ID, x) ou (ARRAY_ACESSO, ...)
        var = node[1]
        exp = node[2]

        # Verifica se é ID (Variável simples)
        if isinstance(var, tuple) and var[0] == 'ID':
            nome = var[1]
            info = self.procura(nome)
            if info[0] == 'PROCEDURE':  # Functions dao assign, procedures nao.
                raise Exception(f"Não se pode atribuir valores a um procedure {nome}")
            tipo_var = info[1]
        else:
            # Caso Array
            tipo_var = self.visita(var)
        
        tipo_exp = self.visita(exp)

        if tipo_var != tipo_exp:
            if tipo_var == 'REAL' and tipo_exp == 'INTEGER':
                return
            raise Exception(f"Não podes atribuir {tipo_exp} a uma variável {tipo_var}")

    def visita_PROC_CALL(self,node):
        # ('PROC_CALL', nome. [args])
        nome = node[1]
        args = node[2]
    #[x,y]
    #[Integer,Integer]
        info = self.procura(nome)
        # ('PROCEDURE', None, ['INTEGER','INTEGER'])

        categoria = info[0]
        tipo_args_esperados = info[2]

        if categoria != 'PROCEDURE':
            raise Exception(f"Erro: {nome} não é um procedure")

        if len(args) != len(tipo_args_esperados):
            raise Exception(f"{nome} espera {len(tipo_args_esperados)}, recebeu {len(args)}")
        
        #zip(args,tipo_args_esperados)
        #[(x,Integer),(y,Integer)]
        for expr, esperado in zip(args,tipo_args_esperados):
            tipo_dado = self.visita(expr)
            if tipo_dado != esperado:
                if esperado == 'REAL' and tipo_dado == 'INTEGER': continue
                raise Exception(f"Tipo esperado {esperado}, recebeu {tipo_dado}")

    
    def visita_IF(self,node):
        # (IF, condicao, then, else)
        tipo_cond = self.visita(node[1])
        if tipo_cond != 'BOOLEAN':
            raise Exception(f"IF : A condição tem que ser um booleano, recebeu {tipo_cond}")
        
        self.visita(node[2])

        if node[3]: #else é opcional
            self.visita(node[3])
    
    def visita_WHILE(self,node):
        # (WHILE, exp, comando)
        tipo_cond = self.visita(node[1])
        if tipo_cond != 'BOOLEAN':
            raise Exception(f"WHILE : A condição tem que ser um booleano, recebeu {tipo_cond}")
        self.visita(node[2])
    
    def visita_FOR(self,node):
        # (FOR, var, inicio, fim, comando, direcao)
        nome_var = node[1]
        self.procura(nome_var) #verifica se a var existe

        tipo_inicio = self.visita(node[2])
        tipo_fim = self.visita(node[3])

        if tipo_inicio != 'INTEGER' or tipo_fim != 'INTEGER':
            raise Exception(f"FOR: Os limites do FOR devem ser inteiros, recebeu ({tipo_inicio}, {tipo_fim})")
        
        self.visita(node[4])

    def visita_REPEAT(self,node):
        #(REPEAT, [lista_comandos], condicao)
        lista_comandos = node[1]
        if lista_comandos:
            for comando in lista_comandos:
                self.visita(comando)
        
        tipo_cond = self.visita(node[2])
        if tipo_cond != 'BOOLEAN':
            raise Exception(f"REPEAT : A condição tem que ser um booleano, recebeu {tipo_cond}")
        
    
    def visita_WRITELN(self,node):
        #(WRITELN, [lista_exp])
        lista_exp = node[1]
        for exp in lista_exp:       #se a lista for vazia, passa a frente
            self.visita(exp)

    
    def visita_READLN(self, node):
        #(READLN, lista_var) ou (READLN, var)
        conteudo = node[1]
        if isinstance(conteudo, list) and len(conteudo) == 0: 
            return
        #Se conteudo for uma var
        if not isinstance(conteudo, list): 
            lista_vars = [conteudo]
        else: 
            lista_vars = conteudo

        for var in lista_vars:
            # VERIFICAMOS SE É TUPLO 'ID'
            if isinstance(var, tuple) and var[0] == 'ID':
                nome = var[1]
                info = self.procura(nome)
                #(VAR,TIPO,None)
                if info[0] != 'VAR':
                    raise Exception(f"READLN espera vars, recebeu {info[0]}")
            
            #('ARRAY_ACESSO',nome,exp)
            elif isinstance(var, tuple) and var[0] == 'ARRAY_ACESSO':
                self.visita(var)
            else:
                raise Exception(f"READLN espera uma var, recebeu {var}")
            
        
    #EXPRESSOES
    def visita_BINOP(self,node):
        # (BINOP, op, esq , dir)
        op = node[1]
        tipo_esq = self.visita(node[2])
        tipo_dir = self.visita(node[3]) 

        #BOOLEANOS
        if op in ['AND','OR']:
            if tipo_esq != 'BOOLEAN' or tipo_dir != 'BOOLEAN':
                raise Exception(f"{op} exige booleanos, recebeu ({tipo_esq},{tipo_dir})")
            return 'BOOLEAN' 

        if op in ['=','<>','<','>','<=','>=']:
            is_num1 = tipo_esq in ['INTEGER','REAL']
            is_num2 = tipo_dir in ['INTEGER','REAL']

            if is_num1 and is_num2:
                return 'BOOLEAN' # 10 > 5
            
            # se nao forem numeros, tem que ser do mesmo tipo.   
            if tipo_esq == tipo_dir:
                tipos = ['STRING','BOOLEAN']        # Podemos fazer true = true ...

                if tipo_esq not in tipos:
                    raise Exception(f"Não se pode fazer ops com tipos {tipo_esq}")      #para nao dar para fazer array = array, array > array...
                
                return 'BOOLEAN'
                
            raise Exception(f"Tipos incompatíveis na operação ({tipo_esq},{op},{tipo_dir})")
        

        #OP ARITMETICAS
            #Concatenar strings
        if op == '+':
            if tipo_esq == 'STRING' and tipo_dir == 'STRING':
                return 'STRING'
            
        # op com numeros
        if tipo_esq not in ['INTEGER','REAL'] or tipo_dir not in ['INTEGER','REAL']:
            raise Exception(f'{op} exige número, recebeu {tipo_esq},{tipo_dir}')


        if op in ['div','mod']:
            if tipo_esq != 'INTEGER' or tipo_dir != 'INTEGER':
                raise Exception(f"{op} exige INT, recebeu {tipo_esq},{tipo_dir}")
            return 'INTEGER'

        if op == '/':
            return 'REAL'
        
        if tipo_esq == 'REAL' or tipo_dir == 'REAL':
            return 'REAL'

        return 'INTEGER'
    
    def visita_UNOP(self,node):
        # (UNOP, op, exp)
        op = node[1]
        tipo_exp = self.visita(node[2])

        if op == 'NOT':
            if tipo_exp != 'BOOLEAN' :
                raise Exception (f"NOT exige booleano, recebeu {tipo_exp}")
            return 'BOOLEAN'

        if op == '-':
            if tipo_exp not in ['INTEGER','REAL']:
                raise Exception(f'Menos unário (-) exige int ou real, recebeu {tipo_exp}')
            return tipo_exp
        
        return tipo_exp
    
    def visita_LENGTH(self, node):
        exp = node[1]
        # (LENGTH, exp)
        # Se for ID, temos de ver se é Array ou String
        if isinstance(exp, tuple) and exp[0] == 'ID':
            nome = exp[1]
            try:
                info = self.procura(nome)
                tipo_var = info[1]
                
                # Se for Array ou String, aceita
                if isinstance(tipo_var, tuple) and tipo_var[0] == 'ARRAY': 
                    return 'INTEGER'
                if tipo_var == 'STRING': 
                    return 'INTEGER'
                
                raise Exception(f"Length não aceita {tipo_var}")
            except Exception as e:
                # se o erro for "não está declarado!", exp não é uma variável
                # LOgo, se nao for uma variavel, tem que ser uma string
                # ignoramos o erro, e segue para o resto do codigo
                if "não está declarado" not in str(e): 
                    raise e
        
        # Se não for ID (ex: literal string), visita normalmente
        tipo_exp = self.visita(exp)
        if tipo_exp == 'STRING':
            return 'INTEGER'
            
        raise Exception(f"Length espera array ou string, recebeu {tipo_exp}")
    
    def visita_ID(self,node):
        # (ID,nome)
        nome = node[1]
        info = self.procura(nome)
        return info[1]  #devolve o tipo
    
    def visita_INTEGER(self, node):
        # node = ('INTEGER', valor)
        return 'INTEGER'

    def visita_REAL(self, node):
        # node = ('REAL', valor)
        return 'REAL'
    
    def visita_STRING(self, node):
        # node = ('STRING', 'texto')
        return 'STRING'

    def visita_BOOLEAN(self, node):
        # node = ('BOOLEAN', True/False)
        return 'BOOLEAN'

    def visita_ARRAY_ACESSO(self,node):
        # (ARRAY_ACESSO, nome, indice)
        nome = node[1]
        info = self.procura(nome)
        # (VAR, (ARRAY,range,tipo), None) -> arrays
        # (VAR,'STRING',None) -> strings
        tipo_var = info[1] 
        # range : (min,max)
        tipo_indice = self.visita(node[2])
        if tipo_indice != 'INTEGER':
            raise Exception(f"O indice tem que ser um inteiro, recebeu {tipo_indice}")
        
        if isinstance(tipo_var,tuple) or tipo_var[0] == 'ARRAY':
            range_min, range_max = tipo_var[1]
            indice = node[2]
            if isinstance(indice, int):
                range_min, range_max = tipo_var[1]
                if indice < range_min or indice > range_max:
                    raise Exception(f"Indice {indice} fora do intervalo ({range_min},{range_max})")
                    
            return tipo_var[2]
        

        elif tipo_var == 'STRING':
            return 'STRING'

        else:
            raise Exception(f"{nome} não é uma array nem string")
        

    def visita_FUNC_CALL(self,node):
        # (FUNC_CALL, nome, [args])
        nome = node[1]
        args_recebidos = node[2]

        info = self.procura(nome)
        #('FUNCTION', 'INTEGER', ['INTEGER','INTEGER'])


        if info[0] != 'FUNCTION':
                # Na recursividade, ele encontra a VAR de retorno local,
                # Temos de ignorar essa, e procurar pela function origial nas tabelas superiores
                encontrou = False
                for tabela in self.tabela:
                    if nome in tabela and tabela[nome][0] == 'FUNCTION':
                        info = tabela[nome]
                        encontrou = True
                        break
                
                if not encontrou:
                    raise Exception(f"{nome} não é function")
        
        categoria = info[0]
        tipo_args_esperados = info[2]
        
        if len(args_recebidos) != len(tipo_args_esperados):
            raise Exception(f"{nome} espera {len(tipo_args_esperados)} argumentos, recebeu {len(args_recebidos)}")
        
        for expr, esperado in zip(args_recebidos,tipo_args_esperados):
            tipo_dado = self.visita(expr)
            if tipo_dado != esperado:
                if esperado == 'REAL' and tipo_dado == 'INTEGER': continue
                raise Exception(f"Tipo esperado {esperado}, recebeu {tipo_dado}")
            
        return info[1]
    

    
    
