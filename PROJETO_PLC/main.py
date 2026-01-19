import sys
import os
from parser import parser
from lexer import lexer  # Importamos o lexer para resetar o numero de linhas
from semantica import Semantica
from codigo import Codigo

def processar_ficheiro(filename):
    print(f"\n{'='*40}")
    print(f"Ficheiro: {filename}")
    print(f"{'='*40}")

    try:
        with open(filename, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Erro: Ficheiro '{filename}' não encontrado.")
        return

    # RESET DO LEXER 
    lexer.lineno = 1

    # 2. PARSING
    # Passamos o lexer explicitamente para garantir que o tracking de linhas está limpo
    result = parser.parse(content, lexer=lexer)

    if not result:
        print("Erro no Parsing")
        return
    
    # SEMÂNTICA
    try:
        semantica = Semantica()
        semantica.visita(result)
    except Exception as e:
        print(f"Erro Semântico: {e}")
        return

    # GERAÇÃO DE CÓDIGO
    try:
        codegen = Codigo()
        codegen.visita(result)
        
        # Gera o nome do ficheiro de saida com base no de entrada
        nome_base = os.path.splitext(filename)[0]
        nome_saida = f"{nome_base}.vm"

        with open(nome_saida, "w") as f_out:
            for instr in codegen.codigo:
                f_out.write(instr + "\n")
        
        print(f"Sucesso! Gerado: {nome_saida}")

    except Exception as e:
        print(f"Erro na Geração de Código: {e}")

def main():
    # Verifica se foram passados argumentos
    if len(sys.argv) < 2:
        print("Uso: python main.py ficheiro1.pas ficheiro2.pas ...")
        print("Ou:  python main.py *.pas")
        return

    # Itera sobre todos os ficheiros passados no argumento (ignora o main.py)
    arquivos = sys.argv[1:]

    for arq in arquivos:
        processar_ficheiro(arq)

if __name__ == "__main__":
    main()