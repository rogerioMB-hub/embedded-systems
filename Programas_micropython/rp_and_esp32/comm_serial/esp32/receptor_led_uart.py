# Programa para ESP32 (DevKit)
# Recebe um byte via UART física e controla o LED interno:
#   0xAA (170) → acende o LED
#   0x55 ( 85) → apaga o LED
#
# Ligação com outro ESP32 ou Raspberry Pi Pico:
#   GPIO1 (TX) → RX do outro dispositivo
#   GPIO3 (RX) → TX do outro dispositivo
#   GND        → GND do outro dispositivo

from machine import UART, Pin

# Configura a UART0 nos pinos GPIO1 (TX) e GPIO3 (RX)
uart = UART(0, baudrate=115200, tx=Pin(1), rx=Pin(3))

# LED interno do ESP32 DevKit está no pino 2
led = Pin(2, Pin.OUT)

print("Aguardando bytes pela UART...")

while True:
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
