# Programa para Raspberry Pi Pico
# Recebe um byte via UART física e exibe o valor por extenso
#
# Ligação com adaptador USB-serial:
#   GP0 (TX) → RX do adaptador
#   GP1 (RX) → TX do adaptador
#   GND      → GND do adaptador

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
    # Verifica se chegou algum byte
    if uart.any():
        byte = uart.read(1)
        valor = byte[0]

        if valor in numeros:
            print("Recebi:", valor, "→", numeros[valor])
        else:
            print("Recebi:", valor, "→ fora do dicionário")
