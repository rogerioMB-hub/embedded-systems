#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
#include <SoftwareSerial.h>

LiquidCrystal_I2C lcd(0x27,20,4);  // set the LCD address to 0x27 for a 16 chars and 2 line display
SoftwareSerial MasterBoard(10, 11); // RX, TX

void setup()
{
  lcd.init();                      
  lcd.backlight();
  Serial.begin(9600);
  MasterBoard.begin(9600);
}

void loop()
{
  if (MasterBoard.available()) 
  {
    lcd.clear();
    while (MasterBoard.available() > 0) 
    {
      char dado=MasterBoard.read();
      lcd.write(dado);
      Serial.print(dado);
    }
    Serial.println();
  }
}
