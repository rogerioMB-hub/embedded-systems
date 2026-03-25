# Receptor Serial – Raspberry Pi Pico

Programa introdutório em MicroPython para receber bytes via USB
e controlar o LED interno do Pico.

## Requisitos
- Raspberry Pi Pico
- MicroPython (RP2 port)
- Thonny IDE

## Códigos suportados

| Byte | Valor | Ação         |
|------|-------|--------------|
| 0xAA | 170   | Acende o LED |
| 0x55 | 85    | Apaga o LED  |

Qualquer outro valor recebido exibe `Código desconhecido`.

## Como usar

1. Grave o arquivo `receptor_serial.py` no Pico pelo Thonny
2. Execute o programa
3. No Shell do Thonny, envie bytes com:

```python
from machine import USB_VCP
usb = USB_VCP()
usb.write(bytes([0xAA]))  # acende o LED
usb.write(bytes([0x55]))  # apaga o LED
```

## Objetivo

Programa desenvolvido para introdução ao MicroPython com alunas e alunos
iniciantes. O foco é mostrar, de forma simples, como o Pico pode receber
dados e reagir a eles controlando um hardware real.
