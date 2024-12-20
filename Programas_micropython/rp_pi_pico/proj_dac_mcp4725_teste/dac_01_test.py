"""
Created on Thu Nov  4 17:45:18 2024

@author: rmbra
"""
# Complete project details at https://RandomNerdTutorials.com/raspberry-pi-pico-analog-inputs-micropython/
from machine import ADC, Pin, I2C #usa I2C hardwarev - pinos 9 e 8
import time 
import ssd1306
from mcp4725 import MCP4725, BUS_ADDRESS


ADC0 = ADC(Pin(26))
conv_factor = 3.3 / 65535

# usando I2C hardware com pinos originais 9 e 8
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)

#create the MCP4725 driver
dac=MCP4725(i2c,BUS_ADDRESS[0])

#criando oled
oled_width = 128
oled_height = 32
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

for v in range(4096):
    #gera valor
    dac.write(v)
    #mede valor
    volts = ADC1.read_u16() * conv_factor
    #mostra valor
    oled.fill(0)
    oled.text('Conv_ADC', 0, 0)
    oled.text("ADC1: ",5,8)
    oled.text(str(round(volts,2)),45,8)
    oled.show()
    
