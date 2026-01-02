from machine import Pin, I2C
from pico_i2c_lcd import I2cLcd
import utime


i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)

PERIF_ADDR=list()
PERIF_ADDR = i2c.scan()

LCD_ADDR = 0X27
LCD_STATUS = 0
LCD_ROWS = 4
LCD_COLS = 20

RP1_ADDR = 0X41
RP1_STATUS = 0

M1=[[[0,0],0],[[0,5],1],[[0,10],2]]

data=list()
data_final=[0xAA, 0x55]
registrador = 0x00

historico = list()

def create_data_pack2(m_maq):
    data2send=list()
    for d1_ in m_maq:
        data2send.append((d1_))
    return data2send

# data é uma lista de tuplas, contendo inicio [min,seg] e duração [min,seg]
# de cada operação
data = create_data_pack2(M1)

print("Dados a enviar")
print(data)

byte_length = 1  # Each integer will be represented by 1 byte
byte_order = 'big' # Or 'little' for little-endian
#data2send = bytes(data)
data_size=len(data)

if LCD_ADDR in PERIF_ADDR:
    print("LCD ok: at ", hex(LCD_ADDR))
    LCD_STATUS = 1
    lcd = I2cLcd(i2c, LCD_ADDR, LCD_ROWS, LCD_COLS)
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("LCD: ON")
    lcd.move_to(2, 1)
    lcd.putstr("- 20x4 at: ")
    lcd.putstr(hex(LCD_ADDR))
else:
    print("LCD não encontrado!")

if RP1_ADDR in PERIF_ADDR:
    print("RP1 [ok] at ", hex(RP1_ADDR))
    RP1_STATUS = 1
    if LCD_STATUS>0:
        lcd.move_to(0, 2)
        lcd.putstr("RP1: ON")
        lcd.move_to(2, 2)
        lcd.putstr("- RP1 at: ")
        lcd.putstr(hex(RP1_ADDR))
else:
    print("RP1 não encontrado!")
    if LCD_STATUS>0:
        lcd.move_to(0, 2)
        lcd.putstr("RP1: OFF")
        lcd.move_to(2, 3)
        lcd.putstr("- verific. ")
        lcd.putstr(hex(RP1_ADDR))

utime.sleep(1)

if ((LCD_STATUS>0) and (RP1_STATUS>0)):
    print("INICIANDO COMUNICAÇÃO I2C ...")
    
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Iniciando")
    lcd.move_to(7, 1)
    lcd.putstr("Comunicação")
    lcd.move_to(17, 2)
    lcd.putstr("I2C")
    
    utime.sleep(0.5)
    
    interval = 1000
    j=0
    flag1=True
    fim = False
    num_bytes_rec = 2 # status % (0 a 100), tempo
    mq=1
    tref = utime.ticks_ms()
    
    try:
        while not fim:
            
            if (flag1==True):
                data2send = registrador.to_bytes(byte_length, byte_order)
                i2c.writeto(RP1_ADDR, data2send,1)
                # envia inicio (min e seg) e duração (min e seg)
                transmit_ = [data[j][0][0],data[j][0][1],data[j][1]]
                for d1 in transmit_:
                    data2send = d1.to_bytes(byte_length, byte_order)
                    i2c.writeto(RP1_ADDR, data2send,1)
                flag1=False #já visitou aqui. Agora só qdo j mudar.
                
    
            now = utime.ticks_ms()
            if (((now - tref)>=interval) and not flag1):
                tref = now
                data_received = i2c.readfrom(RP1_ADDR, num_bytes_rec)
                # retorno: status = 0 a 100 (inteiro ref % processamento)
                data_received2int=[]
                for byte in data_received:
                    data_received2int.append(byte)
            
                # modificar isto: anexar somente os concluídos
                #                 status<100% apenas para analise e display
                #                 talvez, envolver operations (da placa perif)
                if ((data_received2int[0]==100)and(data_received2int not in historico)):
                    historico.append(data_received2int)
            
                ## tenho de pegar o que chega e ir deslocando 
                lcd.clear()
                lcd.move_to(0, 0) # Column 0, Row 1
                lcd.putstr("Status das operações")
                
                for d in data_received2int:
                    lcd.clear()
                    lcd.move_to(0, mq) 
                    lcd.putstr("Mq.: ")
                    lcd.move_to(6, mq) 
                    lcd.putstr(str(mq))
                    lcd.move_to(10, mq) 
                    lcd.putstr("T%:")
                    lcd.move_to(13, mq)
                    lcd.putstr(str(d))
                    
                if (data_received2int[0]==100):
                    j+=1
                    flag1=True
                    if j==len(data):
                        fim=True
        
        data2send = registrador.to_bytes(byte_length, byte_order)
        i2c.writeto(RP1_ADDR, data2send,1)
        # envia inicio (min e seg) e duração (min e seg)
        for d1 in data_final:
            data2send = d1.to_bytes(byte_length, byte_order)
            i2c.writeto(RP1_ADDR, data2send,1)
        
        print(historico)
                
    except OSError as e:
        print("Erro I2C:", e)
        lcd.clear()
        lcd.move_to(0, 1) # Column 0, Row 1
        lcd.putstr("Erro I2C:")
        lcd.move_to(2, 2) # Column 0, Row 1
        lcd.putstr(str(e))
        utime.sleep(1)

        utime.sleep(1)
else:
    print("Falha no funcionamento!")
    

