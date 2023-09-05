// placa da direita - receptora

#include <SoftwareSerial.h>
#include <Adafruit_LiquidCrystal.h>

#define led_pin 13

SoftwareSerial MasterBoard(10, 11); // RX, TX
Adafruit_LiquidCrystal lcd(0);

String message = "";
unsigned int size_message = message.length();

unsigned int got_char = 0;
int leitura=0;

bool status_led=0;

void setup()
{
  lcd.begin(16, 2);
  lcd.setBacklight(1);

  Serial.begin(9600);
  
  MasterBoard.begin(1200);
  
  pinMode(led_pin, OUTPUT);
}

void loop()
{
  
  if((leitura==0)&&(MasterBoard.available()==2)) 
  { //se 2 bytes chegarem ....
    
    lcd.clear();
  	lcd.print("Mensagem chegou!");
    
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
    
    lcd.setCursor(0, 1);
    lcd.print(message);
    
    digitalWrite(led_pin,status_led);

    leitura=0;
  }

  
}