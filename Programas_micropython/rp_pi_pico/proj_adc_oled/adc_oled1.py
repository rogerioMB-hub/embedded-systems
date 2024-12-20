# Complete project details at https://RandomNerdTutorials.com/raspberry-pi-pico-analog-inputs-micropython/
from machine import ADC, Pin, SoftI2C
from time import sleep
import ssd1306

ADC1 = ADC(Pin(26))
conv_factor = 3.3 / 65535

#You can choose any other combination of I2C pins
i2c = SoftI2C(scl=Pin(5), sda=Pin(4), freq=200000) 

oled_width = 128
oled_height = 32
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

oled.text('Conv_ADC', 0, 0)

while True:
    data = ADC1.read_u16() * conv_factor
    
    # Clear the oled display in case it has junk on it.
    oled.fill(0)
    
    # Add some text
    oled.text("ADC1: ",5,8)
    oled.text(str(round(data,2)),45,8)


    # Finally update the oled display so the image & text is displayed
    oled.show()
    sleep(0.1)
    
    
