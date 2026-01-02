### i2cSlave.py
from machine import mem32, ADC, Pin, Timer
from RP2040_I2C_Registers import*
#   para uso na estrutura da temperatura
import struct
#   para uso da thread
import _thread
# uso do tempo
import utime

id_board = 1
addr_board = 0x40 + id_board

byte_length = 1  # Each integer will be represented by 1 byte
byte_order = 'big' # Or 'little' for little-endian

interr_triggered = False

running = False
hab_time_count = True
hab_led = True

inicio_s = 0
final_s = 0

intervalo = 1000 # em ms
tempo = 0

status_ = 0

operations = list()
op = 0

try:
    led = Pin(25, Pin.OUT)
except ValueError:
    led = Pin("LED", Pin.OUT)

# Cria objeto timer
timer_ = Timer(-1) 


tasks_list=[[0,3],[0,4],[0,3]] # tempo em [min,seg] de cada tarefa

def second_core_thread(lock):
    global interr_triggered
    global running
    global hab_led
    global hab_time_count
    global status_
    global inicio_s
    global final_s
    global intervalo
    global tempo
    global operations
    global op
    
    while True:
        with lock:
            if running:
                if (interr_triggered==True):
                    interr_triggered=False
                    
                    if hab_led:
                        led.toggle()
                    else:
                        led.off()
                    #print("Thread 1 hab_count_time: ",hab_time_count)
                    if hab_time_count:
                        tempo += intervalo/1000
                        if ((final_s-inicio_s)==0):
                            status_=0
                        elif (tempo<=inicio_s):
                            status_ = 0
                        else:
                            status_ = calcula_status(inicio_s,final_s)
                            if status_>=100:
                                status_=100
                    
                    if (status_==100):
                    #if (((tempo>final_s) or (status_==100))and(inicio_s!=final_s)):
                        hab_time_count=False
                        hab_led=False
                        led.on()
                        dado = [op, inicio_s, final_s, status_]
                        if dado not in operations:
                            operations.append(dado)
                    
            
def timer_ISR(timer):
    global interr_triggered
    
    interr_triggered = True

def calcula_status(start, stop):
    stt = round(100*((tempo-start)/(stop-start)))
    return stt

def calcula_t_seg(tmin, tseg):
    t_s = tmin*60 + tseg
    return t_s

class i2c_slave:
    """
    RP2040 I2C Slave implementation using direct register access.
    
    This class implements an I2C slave interface for the RP2040 microcontroller,
    allowing it to receive and transmit data as an I2C peripheral device.
    """

    I2C0_BASE = 0x40044000
    I2C1_BASE = 0x40048000
    IO_BANK0_BASE = 0x40014000

    # Atomic Register Access 
    mem_rw = 0x0000     # Normal read/write access
    mem_xor = 0x1000    # XOR on write
    mem_set = 0x2000    # Bitmask set on write
    mem_clr = 0x3000    # Bitmask clear on write

    def get_Bits_Mask(self, bits, register):
        """ This function return the bit mask based on bit name """
        bits_to_clear = bits
        bit_mask = sum([key for key, value in register.items() if value in bits_to_clear])
        return bit_mask

    def RP2040_Write_32b_i2c_Reg(self, register, data, atr=0):
        """ Write RP2040 I2C 32bits register """
        # < Base Addr > | < Atomic Register Access > | < Register > 
        mem32[self.i2c_base | atr | register] = data

    def RP2040_Set_32b_i2c_Reg(self, register, data):
        """ Set bits in RP2040 I2C 32bits register """
        # < Base Addr > | 0x2000 | < Register > 
        self.RP2040_Write_32b_i2c_Reg(register, data, atr=self.mem_set)

    def RP2040_Clear_32b_i2c_Reg(self, register, data):
        """ Clear bits in RP2040 I2C 32bits register """
        # < Base Addr > | 0x3000 | < Register > 
        self.RP2040_Write_32b_i2c_Reg(register, data, atr=self.mem_clr)
    
    def RP2040_Read_32b_i2c_Reg(self, offset):
        """ Read RP2040 I2C 32bits register """
        return mem32[self.i2c_base | offset]
    
    def RP2040_Get_32b_i2c_Bits(self, offset, bit_mask):
        return mem32[self.i2c_base | offset] & bit_mask

    def __init__(self, i2cID=0, sda=0, scl=1, slaveAddress=addr_board, enable_clock_stretch=True):
        self.scl = scl
        self.sda = sda
        self.slaveAddress = slaveAddress
        self.i2c_ID = i2cID
        if self.i2c_ID == 0:
            self.i2c_base = self.I2C0_BASE
        else:
            self.i2c_base = self.I2C1_BASE

        self.Register = list()
        
        """
          I2C Slave Mode Intructions
          https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf
        
        """

        # 1. Disable the DW_apb_i2c by writing a ‘0’ to IC_ENABLE.ENABLE
        self.RP2040_Clear_32b_i2c_Reg(I2C_OFFSET["I2C_IC_ENABLE"], 
                                  self.get_Bits_Mask("ENABLE", I2C_IC_ENABLE))

        # 2. Write to the IC_SAR register (bits 9:0) to set the slave address. 
        # This is the address to which the DW_apb_i2c responds.
        self.RP2040_Clear_32b_i2c_Reg(I2C_OFFSET["I2C_IC_SAR"], 
                                  self.get_Bits_Mask("IC_SAR", I2C_IC_SAR))

        self.RP2040_Set_32b_i2c_Reg(I2C_OFFSET["I2C_IC_SAR"], 
                                self.slaveAddress & self.get_Bits_Mask("IC_SAR", I2C_IC_SAR))

        # 3. Write to the IC_CON register to specify which type of addressing is supported (7-bit or 10-bit by setting bit 3).
        # Enable the DW_apb_i2c in slave-only mode by writing a ‘0’ into bit six (IC_SLAVE_DISABLE) and a ‘0’ to bit zero 
        # (MASTER_MODE).
        
        # Disable Master mode
        self.RP2040_Clear_32b_i2c_Reg(I2C_OFFSET["I2C_IC_CON"], 
                                      self.get_Bits_Mask("MASTER_MODE", I2C_IC_CON))
        
        # Enable slave mode 
        self.RP2040_Clear_32b_i2c_Reg(I2C_OFFSET["I2C_IC_CON"], 
                                      self.get_Bits_Mask("IC_SLAVE_DISABLE", I2C_IC_CON))
        
        # Enable clock strech 
        if enable_clock_stretch:
            self.RP2040_Set_32b_i2c_Reg(I2C_OFFSET["I2C_IC_CON"], 
                                      self.get_Bits_Mask("RX_FIFO_FULL_HLD_CTRL", I2C_IC_CON))

        
        # 4. Enable the DW_apb_i2c by writing a ‘1’ to IC_ENABLE.ENABLE.
        self.RP2040_Set_32b_i2c_Reg(I2C_OFFSET["I2C_IC_ENABLE"], 
                                self.get_Bits_Mask("IC_ENABLE", I2C_IC_ENABLE))
        
        # Reset GPIO0 function 
        mem32[ self.IO_BANK0_BASE | self.mem_clr | ( 4 + 8 * self.sda) ] = 0x1f
        # Set GPIO0 as IC0_SDA function 
        mem32[ self.IO_BANK0_BASE | self.mem_set | ( 4 + 8 * self.sda) ] = 0x03

        # Reset GPIO1 function
        mem32[ self.IO_BANK0_BASE | self.mem_clr | ( 4 + 8 * self.scl) ] = 0x1f
        # Set GPIO1 as IC0_SCL function 
        mem32[ self.IO_BANK0_BASE | self.mem_set | ( 4 + 8 * self.scl) ] = 3
        
    def create_Register(self, num):
        self.Register.clear()
        for x in range(num):
            self.Register.append(0)


    class I2CStateMachine:
        I2C_RECEIVE = 0
        I2C_REQUEST = 1
        I2C_FINISH  = 2
        I2C_START   = 3
        I2C_IDLE    = 4

   
    class I2CTransaction:

        def __init__(self, address: int, data_byte: list):
            self.address = address  
            self.data_byte = data_byte

    
    
    def handle_event(self):
        """Optimized event detection by reading interrupt status register once"""
        # Read entire interrupt status register in one operation
        intr_stat = self.RP2040_Read_32b_i2c_Reg(I2C_OFFSET["I2C_IC_INTR_STAT"])
        
        # Check for restart condition
        if intr_stat & self.get_Bits_Mask("R_RESTART_DET", I2C_IC_INTR_STAT):
            self.RP2040_Read_32b_i2c_Reg(I2C_OFFSET["I2C_IC_CLR_RESTART_DET"])
            # Handle restart logic here
            
        # Check other conditions using the same intr_stat value
        # I2C Master has abort the transactions
        if (intr_stat & self.get_Bits_Mask("R_TX_ABRT", I2C_IC_INTR_STAT)):
            # Clear int
            self.RP2040_Read_32b_i2c_Reg(I2C_OFFSET["I2C_IC_CLR_TX_ABRT"])
            return i2c_slave.I2CStateMachine.I2C_FINISH
        
        # Last byte transmitted by I2C Slave but NACK from I2C Master 
        if (intr_stat & self.get_Bits_Mask("R_RX_DONE", I2C_IC_INTR_STAT)):
            # Clear int
            self.RP2040_Read_32b_i2c_Reg(I2C_OFFSET["I2C_IC_CLR_RX_DONE"])
            return i2c_slave.I2CStateMachine.I2C_FINISH

        # Start condition detected by I2C Slave
        if (intr_stat & self.get_Bits_Mask("R_START_DET", I2C_IC_INTR_STAT)):
            # Clear start detection 
            self.RP2040_Read_32b_i2c_Reg(I2C_OFFSET["I2C_IC_CLR_START_DET"])
            return i2c_slave.I2CStateMachine.I2C_START

        # Stop condition detected by I2C Slave
        if (intr_stat & self.get_Bits_Mask("R_STOP_DET", I2C_IC_INTR_STAT)):
            
            # Clear stop detection
            self.RP2040_Read_32b_i2c_Reg(I2C_OFFSET["I2C_IC_CLR_STOP_DET"])
            return i2c_slave.I2CStateMachine.I2C_FINISH
        
        # Check if RX FIFO is not empty
        if (self.RP2040_Get_32b_i2c_Bits(I2C_OFFSET["I2C_IC_STATUS"],
                                 self.get_Bits_Mask("RFNE", I2C_IC_STATUS))):
            
            return i2c_slave.I2CStateMachine.I2C_RECEIVE
        
        # Check if Master is requesting data 
        if (intr_stat & self.get_Bits_Mask("R_RD_REQ", I2C_IC_INTR_STAT)):
            
            # Shall Wait until transfer is done, timing recommended 10 * fastest SCL clock period
            # for 100 Khz = (1/100E3) * 10 = 100 uS
            # for 400 Khz = (1/400E3) * 10 = 25 uS
                
            return i2c_slave.I2CStateMachine.I2C_REQUEST

        # Add at the end
        return i2c_slave.I2CStateMachine.I2C_IDLE

    def is_Master_Req_Read(self):
        """ Return status if I2C Master is requesting a read sequence """
        
        # Check RD_REQ Interrupt bit (master wants to read data from the slave)
        status = self.RP2040_Get_32b_i2c_Bits(I2C_OFFSET["I2C_IC_RAW_INTR_STAT"],
                                 self.get_Bits_Mask("RD_REQ", I2C_IC_RAW_INTR_STAT))

        if status :
            return True
        return False
    
    def Slave_Write_Data(self, data):
        """ Write 8bits of data at destination of I2C Master """
    
        # Send data
        self.RP2040_Write_32b_i2c_Reg(I2C_OFFSET["I2C_IC_DATA_CMD"], data & 
                                  self.get_Bits_Mask("DAT", I2C_IC_DATA_CMD))
        
        self.RP2040_Read_32b_i2c_Reg(I2C_OFFSET["I2C_IC_CLR_RD_REQ"]) 
        
        
    def Available(self):
        """ Return true if data has been received from I2C Master """

        # Get RFNE Bit (Receive FIFO Not Empty)
        return self.RP2040_Get_32b_i2c_Bits(I2C_OFFSET["I2C_IC_STATUS"],
                                self.get_Bits_Mask("RFNE", I2C_IC_STATUS))
        

    def Read_Data_Received(self):
        """ Return data from I2C Master """
              
        return self.RP2040_Read_32b_i2c_Reg(I2C_OFFSET["I2C_IC_DATA_CMD"]) &  self.get_Bits_Mask("DAT", I2C_IC_DATA_CMD)

    def deinit(self):
        """Disable the I2C slave and release pins"""
        # Disable I2C interface
        self.RP2040_Clear_32b_i2c_Reg(I2C_OFFSET["I2C_IC_ENABLE"], 
                              self.get_Bits_Mask("ENABLE", I2C_IC_ENABLE))
        
        # Reset GPIO pins back to default state
        mem32[self.IO_BANK0_BASE | self.mem_clr | (4 + 8 * self.sda)] = 0x1f
        mem32[self.IO_BANK0_BASE | self.mem_clr | (4 + 8 * self.scl)] = 0x1f


if __name__ == "__main__":
    import machine
    from machine import mem32, Pin
    
    def main():
        global tempo
        global status_
        global intervalo
        global final_s
        global inicio_s
        global running
        global inicio
        global duracao
        global hab_led
        global hab_time_count
        global operations
        global op
        

        data_buf = []
        addr = 0x00
        t_ini = utime.ticks_ms()
        
        inicio = [0,0]
        duracao = [0,0]
        final=[0,0]

        
        # Create I2C slave instance
        s_i2c = i2c_slave(0, sda=0, scl=1, slaveAddress=addr_board, enable_clock_stretch=True)
        state = i2c_slave.I2CStateMachine.I2C_IDLE
        currentTransaction = i2c_slave.I2CTransaction(addr, data_buf)
        
        # Lock para garantir segurança nas manipulações de variáveis globais
        lock = _thread.allocate_lock()
        _thread.start_new_thread(second_core_thread, (lock,))
        # definindo timer
        intervalo = 1000
        timer_.init(period=intervalo, mode=Timer.PERIODIC, callback=timer_ISR)
        
        num_data = 2 # 2 bytes: tempo,status 
        s_i2c.create_Register(num_data)
        
        print("Placa perif. n. ",id_board ,": ", hex(addr_board))
        dados_maquina = list()
        operations = [] # global, com as operações concluídas
        op = 0
        atraso = 0
        running = True
        first_turn = True
        try:
            while True:
                
                state = s_i2c.handle_event()
                
                if state == s_i2c.I2CStateMachine.I2C_START:
                    pass
    
                # Se estiver recebendo dados da Controladora
                if state == s_i2c.I2CStateMachine.I2C_RECEIVE:
                    running = False
                    hab_time_count = False
                    
                    if currentTransaction.address == 0x00:
                        # First byte received is the register address
                        currentTransaction.address = s_i2c.Read_Data_Received()

                    dados_maquina.clear()
                    
                    while (s_i2c.Available()):
                        currentTransaction.data_byte.append(s_i2c.Read_Data_Received())
                    
                    dados_maquina = currentTransaction.data_byte[:]
                    status_maquina = 0 # status de trabalho da operação
                    print("Dados_maquina: ",dados_maquina)
                    
                    num_data=2
                    s_i2c.create_Register(num_data)
                    status_ = 0
                    
                    if (dados_maquina == [0xAA, 0x55]):
                        first_turn=True
                        
                        currentTransaction.address = 0x00
                        currentTransaction.data_byte = []
                        state= s_i2c.I2CStateMachine.I2C_IDLE
                        print(operations)
                        
                        print("AGUARDANDO DEMANDA. t=0")
                    
                    else:
                        # chegando nova demanda
                        if first_turn:
                            tempo = 0
                            operations=[]
                            op=0 # verificar se dou continuidade ou zero as operações
                            first_turn = False
                        
                        inicio = dados_maquina[:2]
                        tarefa = dados_maquina[2]
                        duracao = tasks_list[tarefa]
                        
                        inicio_s = calcula_t_seg(inicio[0],inicio[1])+atraso
                        final_s = calcula_t_seg(inicio[0]+duracao[0],inicio[1]+duracao[1])+atraso
                        
                        print("Recebendo:       Inicio:",inicio_s,"/ Final:",final_s)
                        print("Tempo =", tempo)
                        if (tempo > inicio_s):
                            atraso += (tempo - inicio_s)
                            inicio_s += atraso
                            final_s += atraso
                            
                            print("Corr. delay: Inicio:",inicio_s,"/ Final:",final_s)
                            
                        hab_time_count = True
                        hab_led = True
                        
                        running = True
                        op+=1

                # Se Controladora estiver requisitando dados
                if state == s_i2c.I2CStateMachine.I2C_REQUEST:
                    running = False
                    status_maquina = status_
                    s_i2c.Register[0] = status_maquina
                    s_i2c.Register[1] = int(tempo)
                                     
                    #print("Quantidade de registros a enviar: ",len(s_i2c.Register))
                    while (s_i2c.is_Master_Req_Read()):
                        for oper in s_i2c.Register:
                            s_i2c.Slave_Write_Data(oper)
                    print ("Enviado: ", s_i2c.Register)
                    running = True
                        
             
                if state == s_i2c.I2CStateMachine.I2C_FINISH:
                    #print ("Dado #01: ", currentTransaction.address ,"Outros: ", currentTransaction.data_byte)
                    currentTransaction.address = 0x00
                    currentTransaction.data_byte = []
                    state= s_i2c.I2CStateMachine.I2C_IDLE
                    
                    running = False
                    
        except KeyboardInterrupt:
            running = False
            s_i2c.deinit()  # Clean up when done
            print("I2C perif. ",id_board," finalizada!")
            
        
    main()
