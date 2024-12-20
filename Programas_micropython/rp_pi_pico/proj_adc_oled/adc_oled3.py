# Complete project details at https://RandomNerdTutorials.com/raspberry-pi-pico-analog-inputs-micropython/
from machine import ADC, Pin, I2C #usa I2C hardwarev - pinos 9 e 8
from time import sleep
import ssd1306

ADC0 = ADC(Pin(26))
ADC1 = ADC(Pin(27))
conv_factor = 3.3 / 65535

# usando I2C hardware com pinos originais 9 e 8
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)

oled_width = 128
oled_height = 32
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

oled.text('Conv_ADC', 0, 0)

while True:
    data0 = ADC0.read_u16() * conv_factor
    data1 = ADC1.read_u16() * conv_factor
    
    # Clear the oled display in case it has junk on it.
    oled.fill(0)
    
    # Add some text
    oled.text("ADC0: ",5,8)
    oled.text(str(round(data0,2)),45,8)
    
    # Add some text
    oled.text("ADC1: ",5,18)
    oled.text(str(round(data0,2)),45,18)


    # Finally update the oled display so the image & text is displayed
    oled.show()
    sleep(0.1)
    
    
