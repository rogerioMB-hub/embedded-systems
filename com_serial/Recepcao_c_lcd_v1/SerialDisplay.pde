#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
#include <SoftwareSerial.h>

LiquidCrystal_I2C lcd(0x27,20,4);  // set the LCD address to 0x27 for a 16 chars and 2 line display

void setup()
{
  lcd.init();                      
  lcd.backlight();
  Serial.begin(9600);
}

void loop()
{
  if (Serial.available()) 
  {
    delay(100);
    lcd.clear();
    while (Serial.available() > 0) 
    {
      lcd.write(Serial.read());
    }
  }
}
