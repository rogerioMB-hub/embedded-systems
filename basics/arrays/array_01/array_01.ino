// programa exemplo: uso de arrays
// objetivo: manipulando array em laco for


int i, j;
int meu_array[10];                    // criando array de tamanho 10, tipo inteiro

void setup() {
  Serial.begin(9600);                 // configurando porta serial para uso como serial mobitor
  randomSeed(analogRead(A0));         // defininco semente de gerador de números aleatórios (pseudo)
  for (i=0; i<10; i++)                // carregando o array com números aleatorios de 0 a 10
  {
    meu_array[i]=random(10);
  }


}

void loop() {                         // mostrando array pelo monitor serial
  Serial.println("Array gerado: ");
  for (j=0; j<10; j++)
  {
    Serial.print("meu_array[");
    Serial.print(j);
    Serial.print("]=");
    Serial.println(meu_array[j]);
  }
  delay(1000);

}
