// o programa mostra os valores de i, partindo de 0 e indo de 1 em 1 até 9.


int i;    // variavel utilizada no laço for

void setup() {
  //define porta serial com taxa de 9600 bits/s.
  Serial.begin(9600);  

}

void loop() {
  // criando loaco FOR que assume valores de 0 a 9 para i.
  // a estrutura do lacó comprende 3 coisas: inicialização, teste e passo.
  //inicialização: atribuição do valor inicial da variável de controle
  // teste: realizado sempre antes de executar o laço. Se verdadeiro, o laço é executado, se nao, salta para fora do mesmo.
  // passo: consiste no incremento (ou decremento) a o valor a ser somado (ou removido) da variável de contrle.
  // pode ser i++, no caso da variável i usada aqui, ou i=i+1 ( ao novo i, atribui-se o valor de i+1).
  // se desejar-mos um passo 3 positivo, podemos escrever i=i+3, por exemplo.
  // no caso de passo negativo, com i iniciando em 200 e sendo decrementado até 0, com passo 2, pode-se escrever:
  // for(i=200; i<=0; i=i-2) { 
  // }
  }
  for (i=0; i<10; i++)
  {
    //mostra o valor de i
    Serial.println(i);
  }
  // e mostra na serial 
  
}

