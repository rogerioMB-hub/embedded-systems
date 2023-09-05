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
  if(MasterBoard.available()>0) 
  { 
    while (MasterBoard.available()>0) 
    {
    	dado_raw=MasterBoard.read();
    	Serial.print(dado_raw);
    }
    Serial.println("; ");
    status_led=!status_led;
    digitalWrite(led_pin,status_led);
    
   }  
}