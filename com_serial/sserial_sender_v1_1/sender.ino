#include "SoftwareSerial.h" // Inclui a biblioteca SoftwareSerial

#define intervalo 2000
#define Led_pin 13

// Cria uma serial em software 
SoftwareSerial SenderBoard(10,11); // (RX, TX)

unsigned long anteriorMillis = 0;  
unsigned long atualMillis = 0;  
bool status_led = 0;
unsigned dado_raw=0x03FF; // 0000 0011 1111 1111

void setup() {
  // inicia a serial em software com uma taxa de 1200 bits/s
  SenderBoard.begin(1200);

  // configura o pino do botao como entrada com resistor de pullup interno
  pinMode(Led_pin, OUTPUT);
  
  Serial.begin(9600);
}

void loop() {
  
  atualMillis=millis();
  if (atualMillis - anteriorMillis >= intervalo) 
  {
    // registra novo valor para tempo de referencia
    anteriorMillis = atualMillis;

    status_led=!status_led;
    
    SenderBoard.write(dado_raw); // envia byte, mas qual ?
    
    Serial.println(dado_raw);
        
    digitalWrite(Led_pin, status_led);
    
  }
}

