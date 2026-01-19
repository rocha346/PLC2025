import sys

class Codigo:
    def __init__(self):
        self.codigo = []    #lista onde vai estar guardado as instrucoes 
        self.tabela = []
        self.labels = 0     #L1, L2, L3...
        self.gp_offset = 0  #global pointer
        self.fp_offset = 0  # Frame pointer (local), reinicia para 0 quando entra numa funcao nova

    def emit(self, instr):
        self.codigo.append(instr)

    def new_label(self):        #para gerar uma etiqueta nova para os IF's e loops
        self.labels += 1
        return f"L{self.labels}"
    
    def append_tabela(self):
        self.tabela.append({})

    def pop_tabela(self):
        self.tabela.pop()

    def add_var(self, nome, tipo, categoria):
        # CATEGORIA -> GLOBAL OU LOCAL
        if categoria == 'GLOBAL':
            offset = self.gp_offset
            self.gp_offset += 1
        else:
            offset = self.fp_offset
            self.fp_offset += 1
        # Guarda (Endereço, tipo de dado, GLOBAL/LOCAL)
        self.tabela[-1][nome] = (offset, tipo, categoria)   # guarda na tabela atual (que esta no topo da pilha)
        return offset
    
    def get_var(self, nome):
        for tabela in reversed(self.tabela):        # procura primeiro no local, ate ao global
            if nome in tabela:
                return tabela[nome]
        
        raise Exception(f"Variável {nome} não encontrada")
    
    def visita(self, node): # Encaminha o node para a funcao correta
        if node is None: return

        if isinstance(node, tuple):
            tipo = node[0]
            visitar = getattr(self, f"visita_{tipo}", self.default)
            return visitar(node)
        
        elif isinstance(node, list):
            for n in node:
                self.visita(n) 

    def default(self, node):
        raise Exception(f"Função não encontrada visita_{node[0]}")
    
    def visita_PROGRAM(self, node):
        # (PROGRAM, ID, VARS, SUBPROGRAMAS, BLOCO)
        self.append_tabela()

        self.visita(node[2])     # Visita as vars globais, guarda na tabela

        self.emit("START")

        if self.gp_offset > 0:
            self.emit(f"PUSHN {self.gp_offset}")

        self.emit("JUMP main")

        self.visita(node[3])

        self.emit("main:")
        self.visita(node[4])

        self.emit("STOP")
        self.pop_tabela()


    def visita_DECL_VAR(self, node):
        nomes = node[1]
        tipo = node[2]
        tipo_pointer = 'GLOBAL' if len(self.tabela) == 1 else 'LOCAL'

        for nome in nomes:
            offset = self.add_var(nome, tipo, tipo_pointer)

            # Se for array, começa na heap
            if isinstance(tipo, tuple) and tipo[0] == 'ARRAY':
                range_vals = tipo[1]
                tamanho = range_vals[1] - range_vals[0] + 1

                self.emit(f"PUSHI {tamanho}")   
                self.emit("ALLOCN")     

                if tipo_pointer == 'GLOBAL':
                    self.emit(f"STOREG {offset}")
                else:
                    self.emit(f"STOREL {offset}")

    def add_arg(self, nome, tipo, offset):
        self.tabela[-1][nome] = (offset, tipo, 'LOCAL')
    
    def visita_FUNCTION(self, node):
        nome = node[1]
        args = node[2]

        self.emit(f"F{nome}:")
        self.append_tabela()
        self.fp_offset = 0

        lista_args = []
        for grupo in args:
            ids = grupo[0]
            tipo = grupo[1]
            for nome_arg in ids:
                lista_args.append((nome_arg, tipo))

        num_args = len(lista_args)
        
        for i, (nome_arg, tipo_arg) in enumerate(lista_args):
            offset = -(num_args - i)
            self.add_arg(nome_arg, tipo_arg, offset)
        
        self.add_var(nome, node[3], 'LOCAL')
        offset_retorno = self.get_var(nome)[0]

        self.visita(node[4])        #visita as vars locais, incrementa o FP
        if self.fp_offset > 0:
            self.emit(f"PUSHN {self.fp_offset}")
        
        self.visita(node[5])

        self.emit(f"PUSHL {offset_retorno}") # return value
        offset_retorno_slot = -(num_args + 1)
        self.emit(f"STOREL {offset_retorno_slot}")

        self.emit("RETURN")
        self.pop_tabela()

    
    def visita_PROCEDURE(self, node):
        nome = node[1]
        args = node[2]
        vars_locais = node[3]
        conteudo = node[4]

        self.emit(f"P{nome}:") 
        self.append_tabela()
        self.fp_offset = 0

        lista_args = []
        for grupo in args:
            ids = grupo[0]
            tipo = grupo[1]
            for nome_arg in ids:
                lista_args.append((nome_arg, tipo))
        
        num_args = len(lista_args)
        for i, (nome_arg, tipo_arg) in enumerate(lista_args):
            offset = -(num_args - i)
            self.add_arg(nome_arg, tipo_arg, offset)

        if self.fp_offset > 0:
            self.emit(f"PUSHN {self.fp_offset}")

        self.visita(vars_locais)
        self.visita(conteudo)

        self.emit("RETURN")
        self.pop_tabela()


    def visita_FUNC_CALL(self, node):
        nome = node[1]
        args = node[2]

        self.emit("PUSHI 0") # Espaço para return
        for arg in args:
            self.visita(arg)

        self.emit(f"PUSHA F{nome}")
        self.emit("CALL")

        if len(args) > 0:
            self.emit(f"POP {len(args)}") 

        return 'INTEGER' 
    
    def visita_PROC_CALL(self, node):
        nome = node[1]
        args = node[2]

        for arg in args:
            self.visita(arg)
        
        self.emit(f"PUSHA P{nome}")
        self.emit("CALL")

        if len(args) > 0:
            self.emit(f"POP {len(args)}") 

    
    def visita_BLOCO(self, node):
        for comando in node[1]:
            if comando is not None:
                self.visita(comando)

    
    def visita_ASSIGN(self, node):
        var = node[1]
        
        if isinstance(var, tuple) and var[0] == 'ARRAY_ACESSO':
            nome_array = var[1]
            i_exp = var[2]
            info = self.get_var(nome_array)
            if info[2] == 'GLOBAL': 
                self.emit(f"PUSHG {info[0]}")
            else: 
                self.emit(f"PUSHL {info[0]}")
            
            self.visita(i_exp)
            range_min = info[1][1][0] if isinstance(info[1], tuple) else 1
            if range_min != 0:
                self.emit(f"PUSHI {range_min}") 
                self.emit("SUB")

            self.visita(node[2]) # Valor
            self.emit("STOREN")
        
        else:
            # ATRIBUIÇÃO SIMPLES (ID)
            self.visita(node[2]) # Calcula valor
            
            # Verifica se é ID
            if isinstance(var, tuple) and var[0] == 'ID':
                nome = var[1]
                info = self.get_var(nome)
                offset, tipo, gl = info
                
                if gl == 'GLOBAL': 
                    self.emit(f"STOREG {offset}")
                else: 
                    self.emit(f"STOREL {offset}")
    
    def visita_IF(self, node):
        l_else = self.new_label()
        l_fim = self.new_label()
        self.visita(node[1])
        self.emit(f"JZ {l_else}")
        self.visita(node[2])
        self.emit(f"JUMP {l_fim}")
        self.emit(f"{l_else}:")
        if node[3]:
            self.visita(node[3])
        self.emit(f"{l_fim}:")

    def visita_WHILE(self, node):
        l_inicio = self.new_label()
        l_fim = self.new_label()
        self.emit(f"{l_inicio}:")
        self.visita(node[1])
        self.emit(f"JZ {l_fim}")
        self.visita(node[2])
        self.emit(f"JUMP {l_inicio}")
        self.emit(f"{l_fim}:")
    
    def visita_FOR(self, node):
        var = node[1]
        direcao = node[5]
        l_loop = self.new_label()
        l_fim = self.new_label()
        
        self.visita(node[2]) 
        
        info = self.get_var(var)
        if info[2] == 'GLOBAL':
            store = f"STOREG {info[0]}"
            push = f"PUSHG {info[0]}"
        else:
            store = f"STOREL {info[0]}" 
            push = f"PUSHL {info[0]}"

        self.emit(store)
        self.emit(f"{l_loop}:")
        self.emit(push) 
        
        self.visita(node[3]) 
        
        if direcao == 'to':
            self.emit('INFEQ')
        else:
            self.emit('SUPEQ')

        self.emit(f"JZ {l_fim}")

        self.visita(node[4]) 
        
        self.emit(push)
        self.emit("PUSHI 1")
        if direcao == 'to':
            self.emit('ADD')
        else:
            self.emit('SUB')

        self.emit(store)
        self.emit(f"JUMP {l_loop}")
        self.emit(f"{l_fim}:")

    
    def visita_REPEAT(self, node):
        l_inicio = self.new_label()
        self.emit(f"{l_inicio}:")
        self.visita(('BLOCO', node[1]))
        self.visita(node[2])
        self.emit(f"JZ {l_inicio}")

    def visita_WRITELN(self, node):
        for exp in node[1]:
            tipo = self.visita(exp)
            if tipo == 'INTEGER':
                self.emit('WRITEI')
            elif tipo == 'REAL':
                self.emit('WRITEF')
            elif tipo == 'STRING':
                self.emit('WRITES')
            elif tipo == 'BOOLEAN':
                self.emit('WRITEI')
                
        self.emit("WRITELN")

    def visita_READLN(self, node):
        vars_read = node[1]
        if not isinstance(vars_read, list): 
            vars_read = [vars_read]
            
        for var in vars_read:
            # Caso 1: Array (tuplo) -> Ex: readln(numeros[i])
            if isinstance(var, tuple) and var[0] == 'ARRAY_ACESSO':
                nome_array = var[1]
                i_exp = var[2]
                info = self.get_var(nome_array)
                # 1. Mete o endereço da array no topo
                if info[2] == 'GLOBAL': 
                    self.emit(f"PUSHG {info[0]}")
                else: 
                    self.emit(f"PUSHL {info[0]}")
                # 2.  Índice no topo
                self.visita(i_exp)

                # 3. Ajustar Range
                range_min = info[1][1][0]
                if range_min != 0:
                    self.emit(f"PUSHI {range_min}")
                    self.emit("SUB")
                self.emit("READ")
                # Se o tipo do array for INTEGER ou REAL, converte.
                tipo_elemento = info[1][2] # info[1] = ('ARRAY', range, tipo_elemento)
                if tipo_elemento == 'INTEGER': 
                    self.emit("ATOI")
                elif tipo_elemento == 'REAL': 
                    self.emit("ATOF")
                self.emit("STOREN")

            # CASO VARIÁVEL SIMPLES (ID)
            elif isinstance(var, tuple) and var[0] == 'ID':
                nome = var[1]
                info = self.get_var(nome)
                tipo_var = info[1]

                self.emit("READ")
                if tipo_var == 'INTEGER': 
                    self.emit("ATOI")
                elif tipo_var == 'REAL':
                    self.emit("ATOF")
                
                if info[2] == 'GLOBAL': 
                    self.emit(f"STOREG {info[0]}")
                else: 
                    self.emit(f"STOREL {info[0]}")
    
    def visita_LENGTH(self, node):
        # ('LENGTH', exp)
        self.visita(node[1]) # Coloca a string na pilha
        self.emit("STRLEN")  # Devolve o tamanho
        return 'INTEGER'

    def visita_BINOP(self, node):
        op = node[1]
        t1 = self.visita(node[2])
        t2 = self.visita(node[3])

        is_float = (t1 == 'REAL' or t2 == 'REAL')

        # bin[i] (INTEGER/ASCII) = '1' (STRING)
        if op == '=' and ((t1 == 'INTEGER' and t2 == 'STRING') or (t1 == 'STRING' and t2 == 'INTEGER')):
            # Se um é int e outro string, assume que é comparação de ASCII com Char String
            # Aplica CHRCODE à string para obter o ASCII dela
            self.emit("CHRCODE") 
            self.emit("EQUAL")
            return 'BOOLEAN'

        if op == '+':
            self.emit("FADD" if is_float else "ADD")
        elif op == '-':
            self.emit("FSUB" if is_float else "SUB")
        elif op == '*':
            self.emit("FMUL" if is_float else "MUL")
        elif op == '/':
            self.emit("FDIV" if is_float else "DIV")
        elif op == 'DIV':
            self.emit("DIV")
        elif op == 'MOD':
            self.emit("MOD")
        elif op == '=':
            self.emit("EQUAL")
        elif op == '<>':
            self.emit("EQUAL")
            self.emit("NOT")
        elif op == '<':
            self.emit("FINF" if is_float else "INF")
        elif op == '<=':
            self.emit("FINFEQ" if is_float else "INFEQ")
        elif op == '>':
            self.emit("FSUP" if is_float else "SUP")
        elif op == '>=':
            self.emit("FSUPEQ" if is_float else "SUPEQ")
        elif op == 'AND':
            self.emit("AND")
        elif op == 'OR':
            self.emit("OR")
            
        if op in ['=','<>','<','<=','>','>=', 'AND', 'OR']:
            return 'BOOLEAN'
        return 'REAL' if is_float else 'INTEGER'


    def visita_UNOP(self, node):
        op = node[1]
        tipo = self.visita(node[2])
        if op == 'NOT':
            self.emit("NOT")
        elif op == '-':
            self.emit("PUSHI -1")
            self.emit("MUL") 
        return tipo
    
    def visita_ID(self, node):
        nome = node[1]
        info = self.get_var(nome)
        offset, tipo, categoria = info
        if categoria == 'GLOBAL':
            self.emit(f"PUSHG {offset}")
        else:
            self.emit(f"PUSHL {offset}")
        
        return info[1] 
    
    def visita_INTEGER(self, node):
        # node = ('INTEGER', valor)
        self.emit(f"PUSHI {node[1]}")
        return 'INTEGER'

    def visita_REAL(self, node):
        # node = ('REAL', valor)
        self.emit(f"PUSHF {node[1]}")
        return 'REAL'
    
    def visita_STRING(self, node):
        valor = node[1]
        self.emit(f'PUSHS "{valor}"') 
        return 'STRING'

    def visita_BOOLEAN(self, node):
        valor = node[1]
        if valor:
            self.emit("PUSHI 1")
        else:
            self.emit("PUSHI 0")
        return 'BOOLEAN'
    
    def visita_ARRAY_ACESSO(self, node):
        nome = node[1]
        indice = node[2]
        info = self.get_var(nome)
        
        # 1. Carregar endereço do array ou string
        if info[2] == 'GLOBAL':
            self.emit(f"PUSHG {info[0]}")
        else:
            self.emit(f"PUSHL {info[0]}")
        
        # 2. Se for STRING, usa lógica diferente (CHARAT)
        if info[1] == 'STRING':
            self.visita(indice)
            self.emit("PUSHI 1") # Pascal index 1-based
            self.emit("SUB")     # VM index 0-based
            self.emit("CHARAT")  # Devolve ASCII code
            return 'INTEGER'     
            
        # 3. Se for Array normal
        self.visita(indice)
        range_min = info[1][1][0]
        if range_min != 0:
            self.emit(f"PUSHI {range_min}")
            self.emit("SUB")
        self.emit("LOADN")
        return info[1][2]