#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
#include <SoftwareSerial.h>

LiquidCrystal_I2C lcd(0x27,20,4);   // set the LCD address to 0x27 for a 16 chars and 2 line display
SoftwareSerial MasterBoard(10, 11); // RX, TX

String message = "";
unsigned int size_string = message.length();

unsigned int got_char = 0;

void setup()
{
  lcd.init();                      
  lcd.backlight();
  Serial.begin(9600);
  MasterBoard.begin(9600);
}

void loop()
{
  if(Serial.available() == 2) { //se 2 bytes chegarem ....
    uint8_t MSB = MasterBoard.read();
    uint8_t LSB = MasterBoard.read();
    size_message = (MSB << 8) | LSB;
  }

  got_char=0;
  if (MasterBoard.available()) 
  {
    while (MasterBoard.available() > 0) 
    {
      message+=MasterBoard.read();
      got_char++;
    }
  }

  if (got_char==size_message)
    {
      Serial.println(message);
      lcd.clear();
      lcd.print(size_message);
      lcd.setCursor(0, 1);
      lcd.print(message);
    }
}
