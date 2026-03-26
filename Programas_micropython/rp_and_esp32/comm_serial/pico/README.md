# Exemplos UART – Raspberry Pi Pico

Versões dos exemplos de comunicação serial para o **Raspberry Pi Pico**,
usando a UART0 física nos pinos GP0 (TX) e GP1 (RX).

Nos exemplos 01 e 02, o transmissor é o próprio **Shell do Thonny**,
rodando no computador. A partir do exemplo 03, a comunicação passa a
ser feita diretamente entre duas placas.

## Requisitos
- Raspberry Pi Pico (RP2040)
- MicroPython (RP2 port, versão atual)
- Thonny IDE

## Arquivos

| Arquivo                | Descrição                              |
|------------------------|----------------------------------------|
| `receptor_led_uart.py` | Recebe byte e controla LED (`if/elif`) |
| `receptor_uart.py`     | Recebe byte e consulta dicionário      |

## Ligação com o computador (exemplos 01 e 02)

O Pico se conecta ao computador pelo cabo USB. O Thonny acessa a placa
pela porta serial e permite enviar bytes diretamente pelo Shell.

```
Pico  ←→  cabo USB  ←→  computador (Thonny)
```

## Configuração da UART

| Parâmetro | Valor   |
|-----------|---------|
| UART      | 0       |
| TX        | GP0     |
| RX        | GP1     |
| Baudrate  | 115200  |
| Bits      | 8       |
| Paridade  | nenhuma |
| Stop bits | 1       |

## Como testar pelo Shell do Thonny

Com o programa em execução no Pico, abra o Shell do Thonny e envie bytes:

```python
from machine import UART, Pin
uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

# Para receptor_led_uart.py:
uart.write(bytes([0xAA]))  # acende o LED
uart.write(bytes([0x55]))  # apaga o LED

# Para receptor_uart.py:
uart.write(bytes([3]))     # exibe: Recebi: 3 → três
uart.write(bytes([99]))    # exibe: Recebi: 99 → fora do dicionário
```

## Próxima etapa

A partir do exemplo 03, o transmissor passa a ser outra placa,
conectada diretamente pelos pinos GP0/GP1:

```
Pico A GP0 (TX)  →  GP1 (RX) Pico B
Pico A GP1 (RX)  →  GP0 (TX) Pico B
Pico A GND       →  GND      Pico B
```
