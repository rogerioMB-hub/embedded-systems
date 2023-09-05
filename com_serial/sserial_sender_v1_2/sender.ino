#include "SoftwareSerial.h" // Inclui a biblioteca SoftwareSerial

#define intervalo 2000
#define Led_pin 13

// Cria uma serial em software 
SoftwareSerial SenderBoard(10,11); // (RX, TX)

unsigned long anteriorMillis = 0;  
unsigned long atualMillis = 0;  
bool status_led = 0;
unsigned dado_raw=0x3FF;

void setup() {
  // inicia a serial em software com uma taxa de 9600 bit/s
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
    
    //uint8_t LSB = dado_raw;
    //uint8_t MSB = dado_raw >> 8;
    //SenderBoard.write(LSB); // envia byte baixo
    //SenderBoard.write(MSB); // envia byte alto
    
    uint8_t MSB = highByte(dado_raw); //0x3F em MSB
    uint8_t LSB = lowByte(dado_raw);  //0xFF em LSB
    
    SenderBoard.write(LSB); // envia byte baixo
    SenderBoard.write(MSB); // envia byte alto
    
    Serial.print(dado_raw);
    Serial.print(", MSB=");
    Serial.print(MSB, HEX);
    Serial.print(", LSB=");
    Serial.println(LSB, HEX);
    
    digitalWrite(Led_pin, status_led);
    
  }
}

