#include <SoftwareSerial.h>

#define led_pin 13

SoftwareSerial MasterBoard(10, 11); // RX, TX

unsigned int dado_raw=0;
bool status_led=0;

void setup()
{
  Serial.begin(9600);
  MasterBoard.begin(1200);
  pinMode(led_pin, OUTPUT);
}

void loop()
{
  if(MasterBoard.available()==2) 
  { //se 2 bytes chegarem ....
    uint8_t LSB = MasterBoard.read();
    uint8_t MSB = MasterBoard.read();
    dado_raw = (MSB * 256) + LSB;  
    //dado_raw = (MSB << 8) | LSB;

    Serial.print(dado_raw);
    Serial.print(", MSB=");
    Serial.print(MSB);
    Serial.print(", LSB=");
    Serial.println(LSB);
    
    status_led=!status_led;
    digitalWrite(led_pin,status_led);
    
   }  
}