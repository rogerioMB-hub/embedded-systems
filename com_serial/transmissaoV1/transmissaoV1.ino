#include "SoftwareSerial.h" // Inclui a biblioteca SoftwareSerial

#define PinoBotao 8 
#define intervalo 200
#define Led 13

// Cria uma serial em software 
SoftwareSerial SenderBoard(10,11); // (RX, TX)

unsigned long anteriorMillis = 0;  
unsigned long atualMillis = 0;  


void setup() {
  // inicia a serial em software com uma taxa de 9600 bit/s
  SenderBoard.begin(9600);

  // configura o pino do botao como entrada com resistor de pullup interno
  pinMode(PinoBotao, INPUT_PULLUP);
  pinMode(Led, OUTPUT);
}

void loop() {
  
  atualMillis=millis();
  if (atualMillis - anteriorMillis >= intervalo) 
  {
    // registra novo valor para tempo de referencia
    anteriorMillis = atualMillis;
  // le o estado do botao e salva em uma variavel local
  int lido = digitalRead(PinoBotao);
  
    SenderBoard.print(lido); // envia caractere referente ao estado lógico do botao lido
    digitalWrite(Led,lido);  // acende ou apaga led da placa para facilitar analise do que está sendo enviado
  }
}
