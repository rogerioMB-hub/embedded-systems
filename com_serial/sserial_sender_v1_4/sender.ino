#include "SoftwareSerial.h" // Inclui a biblioteca SoftwareSerial

#define intervalo 2000
#define Led_pin 13

// Cria uma serial em software 
SoftwareSerial SenderBoard(10,11); // (RX, TX)

unsigned long anteriorMillis = 0;  
unsigned long atualMillis = 0;  
bool status_led = 0;
String message = "desligar";
unsigned int size_string = message.length();

void setup() {
  // inicia a serial em software com uma taxa de 9600 bit/s
  SenderBoard.begin(1200);

  // configura o pino do botao como entrada com resistor de pullup interno
  pinMode(Led_pin, OUTPUT);
}

void loop() {
  
  atualMillis=millis();
  if (atualMillis - anteriorMillis >= intervalo) 
  {
    // registra novo valor para tempo de referencia
    anteriorMillis = atualMillis;

    status_led=!status_led;
    if (status_led)
    {
      message="ligar";
    }
    else
    {
      message="desligar";
    }
    
    size_string = message.length(); 
    uint8_t LSB = size_string;
    uint8_t MSB = size_string >> 8;
    SenderBoard.write(LSB); // envia byte baixo
    SenderBoard.write(MSB); // envia byte alto
    delay(5);
    SenderBoard.print(message); // envia todos os caracteres da mensagem via serial, um por um, usando tabela ASC

    digitalWrite(Led_pin, status_led);
    
  }
}

