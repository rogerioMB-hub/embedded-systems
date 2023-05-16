#include "SoftwareSerial.h" // Inclui a biblioteca SoftwareSerial

#define intervalo 200
#define Led 13

// Cria uma serial em software 
SoftwareSerial SenderBoard(10,11); // (RX, TX)

unsigned long anteriorMillis = 0;  
unsigned long atualMillis = 0;  
int tick = 0;

void setup() {
  // inicia a serial em software com uma taxa de 9600 bit/s
  SenderBoard.begin(9600);

  // configura o pino do botao como entrada com resistor de pullup interno
  pinMode(Led, OUTPUT);
}

void loop() {
  
  atualMillis=millis();
  if (atualMillis - anteriorMillis >= intervalo) 
  {
    // registra novo valor para tempo de referencia
    anteriorMillis = atualMillis;
    tick++;
    SenderBoard.print(tick); // envia caractere referente ao estado lógico do botao lido
  }
}
