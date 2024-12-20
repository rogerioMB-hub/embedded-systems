# I2C Scanner MicroPython
from machine import Pin, I2C

# You can choose any other combination of I2C pins
i2c = I2C(0)

print('I2C SCANNER')
devices = i2c.scan()

if len(devices) == 0:
  print("No i2c device !")
else:
  print('i2c devices found:', len(devices))

  for device in devices:
    print("I2C hexadecimal address: ", hex(device))