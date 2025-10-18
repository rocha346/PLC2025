import json
import sys
import tokens as lex 
from datetime import date



def formatar_saldo(saldo_em_centimos):
    """Converte 130 (int) para '1e30c' (str)."""
    euros, centimos = divmod(saldo_em_centimos, 100)
    return f"{euros}e{centimos}c"

def calcular_troco(saldo_em_centimos):
    """Converte 74 (int) para '1x 50c, 1x 20c, 2x 2c' (str). (VERSÃO CORRIGIDA)"""
    if saldo_em_centimos == 0:
        return "Sem troco a devolver."
        
    moedas = [(200, "2e"), (100, "1e"), (50, "50c"), (20, "20c"), 
              (10, "10c"), (5, "5c"), (2, "2c"), (1, "1c")]
    
    partes_troco = []
    for valor_cent, nome_moeda in moedas:
        quantidade = saldo_em_centimos // valor_cent
        if quantidade > 0: 
            partes_troco.append(f"{quantidade}x {nome_moeda}")
            saldo_em_centimos %= valor_cent
            
    if not partes_troco:
        return "Sem troco a devolver."

    return "Pode retirar o troco: " + ", ".join(partes_troco) + "."



STOCK_FILE = "stock.json"
stock = []
try:
    with open(STOCK_FILE, "r", encoding="utf-8") as f:
        dados = json.load(f)
        stock = dados["stock"] # Acede à lista "stock" dentro do JSON
        
       
        for prod in stock:
            # Converte o preço de float (ex: 0.7) para int (ex: 70)
            prod["preco"] = int(prod["preco"] * 100)
            
    print(f"maq: {date.today()}, Stock carregado, Estado atualizado.")
    
except Exception as e:
    print(f"ERRO CRÍTICO ao carregar o stock: {e}")
    sys.exit(1)


# --- 3. Estado Inicial ---
saldo = 0
running = True 
print("maq: Bom dia. Estou disponível para atender o seu pedido.")


for linha in sys.stdin:
    
    lex.lexer.input(linha)
    
    for tok in lex.lexer:
            
        if(tok.type == 'LISTAR'):
          
            saida = "maq:\n"
            saida += "cod  | nome".ljust(20) + " | quantidade |  preço\n"
            saida += "------------------------------------------------------\n"
            for prod in stock: 
              
                preco_euros = prod['preco'] / 100.0
                saida += f"{prod['cod']:<5}| {prod['nome']:<20} | {prod['quant']:>10} | {preco_euros:.2f}e\n"
            
            saida += "\nSaldo = " + formatar_saldo(saldo) + "\n" 
            print(saida)
        
        # ----- MUDANÇA DE TOKENS AQUI -----
        if(tok.type == 'EUROS'): 
            saldo += tok.value * 100 
            
        if(tok.type == 'CENTIMOS'): 
            saldo += tok.value 
        
        if(tok.type == 'PONTO'): 
            print("maq: Saldo = "+ formatar_saldo(saldo)) 

        if(tok.type == 'SELECIONAR'):
            pass 

        if(tok.type == 'CODIGO'):
            found = False
            for prod in stock: 
                if prod['cod'] == tok.value:
                    found = True
                    
                    if prod['quant'] <= 0:
                        print(f"maq: Produto \"{prod['nome']}\" está esgotado.")
                    
                    
                    elif prod['preco'] <= saldo: # Ex: 70 <= 100 (Correto)
                        
                       
                        saldo -= prod['preco'] # Ex: 100 - 70 (Correto)
                        prod['quant'] -= 1
                        print("maq: Pode retirar o produto dispensado \"" +  prod['nome'] + "\"")
                        print('maq: Saldo = ' + formatar_saldo(saldo))
                    else:
                        print("maq: Saldo insufuciente para satisfazer o seu pedido")
                       
                        print("Saldo = " + formatar_saldo(saldo) + "; Pedido = " + formatar_saldo(prod['preco']))
                    break
            
            if not found:
                print("maq: Produto inexistente")
            
        if(tok.type == 'SAIR'):
            print("maq: " + calcular_troco(saldo)) 
            print("maq: OBRIGADO!")
            running = False 
            break 
            
    if not running:
        break 

# --- 5. Desligar (GUARDAR O STOCK - FALTAVA NO CÓDIGO DO TEU COLEGA) ---

print("maq: A desligar. A guardar o stock...")

# Prepara os dados para guardar: Converte 70 (cêntimos) de volta para 0.7 (euros)
stock_para_guardar = {"stock": []}
for prod in stock:
    prod_copia = prod.copy()
    prod_copia["preco"] = prod["preco"] / 100.0 # Converte de 70 para 0.7
    stock_para_guardar["stock"].append(prod_copia)

try:
    with open(STOCK_FILE, "w", encoding="utf-8") as f:
        json.dump(stock_para_guardar, f, indent=4, ensure_ascii=False) 
    print("maq: Stock guardado.")
except Exception as e:
    print(f"ERRO CRÍTICO ao guardar o stock: {e}")

    
