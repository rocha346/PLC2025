
AUTOR: **Rodrigo Gonçalves Rocha** :A108649

Neste TPC, foi-nos proposto criar uma expressão regular que representasse números binários que não contivessem a subcadeia "011" em nenhuma posição.

Depois de alguma pesquisa teórica e alguns testes no regex, obtive a expressão pretendida.

**^1*0*(0|1)(0|01)*$**

Após a realização de alguns [testes com regex](testes_regex.png/), foi possível concluir que esta expressão engloba todas as cadeias binárias **que não contêm a subcadeia "011"**.
