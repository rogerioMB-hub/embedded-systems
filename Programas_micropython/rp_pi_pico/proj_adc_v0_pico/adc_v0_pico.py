import machine
import utime

#instancia canal serial 0 - pino GPIO26 
analog_value = machine.ADC(26)
 
while True:
# realiza leitura do ADC (0 a 65535)
leitura = analog_value.read_u16()         

# realiza conversão de valor de amostra para tensão
#  regra de 3: 65535   - 3,3v
#              leitura - volts
volts = leitura * 3.3 / 65535    

#mostra valor pelo canal serial
print("ADC: ",leitura, ", VOLTS: ", volts)

#aguarda 200ms
utime.sleep(0.2)