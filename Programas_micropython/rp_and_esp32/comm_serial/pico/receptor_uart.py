# Programa para Raspberry Pi Pico
# Recebe um byte via UART física e exibe o valor por extenso
#
# Ligação com outro Raspberry Pi Pico:
#   GP0 (TX) → GP1 (RX) do outro Pico
#   GP1 (RX) → GP0 (TX) do outro Pico
#   GND      → GND do outro Pico

from machine import UART, Pin

# Configura a UART0 nos pinos GP0 (TX) e GP1 (RX)
uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

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
