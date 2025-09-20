AUTOR: Rodrigo Gonçalves Rocha :A108649

Este TPC consiste em criar uma expressão regular que represente strings binários que não incluem a subsequência "011".

Depois de alguma pesquisa teórica e alguns testes no regex, obtive a expressão pretendida.

^1*0*(0|1)(0|01)*$
