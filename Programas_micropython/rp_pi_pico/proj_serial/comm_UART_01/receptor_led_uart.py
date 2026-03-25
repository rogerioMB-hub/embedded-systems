# Programa para Raspberry Pi Pico
# Recebe um byte via UART física e controla o LED interno:
#   0xAA (170) → acende o LED
#   0x55 ( 85) → apaga o LED
#
# Ligação com adaptador USB-serial:
#   GP0 (TX) → RX do adaptador
#   GP1 (RX) → TX do adaptador
#   GND      → GND do adaptador

from machine import UART, Pin

# Configura a UART0 nos pinos GP0 (TX) e GP1 (RX)
uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

# LED interno do Pico está no pino 25
led = Pin(25, Pin.OUT)

print("Aguardando bytes pela UART...")

while True:
    # Verifica se chegou algum byte
    if uart.any():
        byte = uart.read(1)
        valor = byte[0]
        print("Recebi o byte:", valor)

        if valor == 0xAA:
            led.on()
            print("LED aceso")

        elif valor == 0x55:
            led.off()
            print("LED apagado")

        else:
            print("Código desconhecido")
