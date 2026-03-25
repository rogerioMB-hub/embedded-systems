# Programa para Raspberry Pi Pico
# Recebe um byte e controla o LED interno:
#   0xAA (170) → acende o LED
#   0x55 ( 85) → apaga o LED

from machine import Pin, USB_VCP

usb = USB_VCP()
led = Pin(25, Pin.OUT)

print("Aguardando bytes...")

while True:
    # Lê 1 byte (retorna None se não houver dado)
    byte = usb.read(1)

    if byte:
        # Pega o valor numérico do byte recebido
        valor = byte[0]
        print("Recebi o byte:", valor)

        # Decide o que fazer
        if valor == 0xAA:
            led.on()
            print("LED aceso")

        elif valor == 0x55:
            led.off()
            print("LED apagado")

        else:
            print("Código desconhecido")
