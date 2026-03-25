# Programa para Raspberry Pi Pico
# Recebe um byte de 1 a 9 e exibe o valor por extenso

from machine import USB_VCP

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

usb = USB_VCP()

print("Aguardando bytes...")

while True:
    byte = usb.read(1)

    if byte:
        valor = byte[0]

        if valor in numeros:
            print("Recebi:", valor, "→", numeros[valor])
        else:
            print("Recebi:", valor, "→ fora do dicionário")
