program TesteGeral;
var
    x, y, temp: integer;
    contador: integer;

{ 1. Teste de Procedure com argumentos locais }
procedure MostrarSoma(a, b: integer);
var
    soma: integer;
begin
    soma := a + b;
    writeln('Soma dentro do procedure: ', soma);
end;

{ 2. Teste de Procedure que altera variáveis GLOBAIS }
procedure AlterarX();
begin
    writeln('... A executar procedure AlterarX ...');
    x := 100; { Isto altera o x definido lá em cima }
end;

begin
    writeln('--- INICIO DO TESTE ---');

    { Inicialização }
    x := 10;
    y := 20;
    
    { 3. Teste de Atribuição Simples (x := y) }
    writeln('Valor original de x: ', x);
    temp := x; 
    writeln('Valor de temp (copia de x): ', temp);

    { Chamada de Procedure com argumentos }
    MostrarSoma(x, y);

    { 4. Teste de Scope e Alteração Global }
    AlterarX();
    writeln('Valor de x apos AlterarX (esperado 100): ', x);

    { 5. Teste de Repeat Until }
    writeln('--- Teste Repeat Until (5 a 1) ---');
    contador := 5;
    repeat
        writeln(contador);
        contador := contador - 1;
    until contador = 0;

    { 6. Teste Final de Lógica }
    if (x = 100) and (temp = 10) then
        writeln('SUCESSO: Todas as validacoes estao corretas.')
    else
        writeln('ERRO: Alguma validacao falhou.');
        
    writeln('--- FIM ---');
end.