# Programa para ESP32 (DevKit)
# Recebe um byte via UART física e exibe o valor por extenso
#
# Ligação com outro ESP32 ou Raspberry Pi Pico:
#   GPIO1 (TX) → RX do outro dispositivo
#   GPIO3 (RX) → TX do outro dispositivo
#   GND        → GND do outro dispositivo

from machine import UART, Pin

# Configura a UART0 nos pinos GPIO1 (TX) e GPIO3 (RX)
uart = UART(0, baudrate=115200, tx=Pin(1), rx=Pin(3))

# Dicionário: byte recebido → texto correspondente
numeros = {
    1: "um",
    2: "dois",
    3: "três",
    4: "quatro",
    5: "cinco",
    6: "seis",
    7: "sete",
    8: "oito",
    9: "nove",
}

print("Aguardando bytes pela UART...")

while True:
    if uart.any():
        byte = uart.read(1)
        valor = byte[0]

        if valor in numeros:
            print("Recebi:", valor, "→", numeros[valor])
        else:
            print("Recebi:", valor, "→ fora do dicionário")
