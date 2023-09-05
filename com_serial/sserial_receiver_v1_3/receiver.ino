#include <SoftwareSerial.h>

#define led_pin 13

SoftwareSerial MasterBoard(10, 11); // RX, TX

String message = "";
unsigned int size_message = message.length();

unsigned int got_char = 0;
int leitura=0;

bool status_led=0;

void setup()
{
  Serial.begin(9600);
  MasterBoard.begin(1200);
  pinMode(led_pin, OUTPUT);
}

void loop()
{
  if((leitura==0)&&(MasterBoard.available()==2)) 
  { //se 2 bytes chegarem ....
    uint8_t LSB = MasterBoard.read();
    uint8_t MSB = MasterBoard.read();
    size_message = (MSB << 8) | LSB;

    Serial.print("Size msg:");
    Serial.print(size_message, DEC);

    got_char=0;
    message="";
    leitura=1;
  }
  
  if((leitura==1) && (MasterBoard.available()==size_message))
  {
    while (MasterBoard.available() > 0) 
    {
      message+=char(MasterBoard.read());
    }

    Serial.println(message);
    
    if (message=="ligar")
      status_led=1;

    if (message=="desligar")
      status_led=0;
    
    digitalWrite(led_pin,status_led);

    leitura=0;
  }

  
}