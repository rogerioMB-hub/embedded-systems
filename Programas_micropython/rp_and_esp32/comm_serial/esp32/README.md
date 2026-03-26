# Exemplos UART – ESP32 (DevKit)

Versões dos exemplos de comunicação serial para o **ESP32 DevKit**,
usando a UART0 física nos pinos GPIO1 (TX) e GPIO3 (RX).

Nos exemplos 01 e 02, o transmissor é o próprio **Shell do Thonny**,
rodando no computador. A partir do exemplo 03, a comunicação passa a
ser feita diretamente entre duas placas.

## Requisitos
- ESP32 DevKit
- MicroPython (ESP32 port, versão atual)
- Thonny IDE

## Arquivos

| Arquivo                | Descrição                              |
|------------------------|----------------------------------------|
| `receptor_led_uart.py` | Recebe byte e controla LED (`if/elif`) |
| `receptor_uart.py`     | Recebe byte e consulta dicionário      |

## Ligação com o computador (exemplos 01 e 02)

O ESP32 se conecta ao computador pelo cabo USB. O Thonny acessa a placa
pelo conversor USB-serial embutido e permite enviar bytes pelo Shell.

```
ESP32  ←→  cabo USB  ←→  computador (Thonny)
```

## Configuração da UART

| Parâmetro | Valor   |
|-----------|---------|
| UART      | 0       |
| TX        | GPIO1   |
| RX        | GPIO3   |
| Baudrate  | 115200  |
| Bits      | 8       |
| Paridade  | nenhuma |
| Stop bits | 1       |

## Como testar pelo Shell do Thonny

Com o programa em execução no ESP32, abra o Shell do Thonny e envie bytes:

```python
from machine import UART, Pin
uart = UART(0, baudrate=115200, tx=Pin(1), rx=Pin(3))

# Para receptor_led_uart.py:
uart.write(bytes([0xAA]))  # acende o LED
uart.write(bytes([0x55]))  # apaga o LED

# Para receptor_uart.py:
uart.write(bytes([3]))     # exibe: Recebi: 3 → três
uart.write(bytes([99]))    # exibe: Recebi: 99 → fora do dicionário
```

## Próxima etapa

A partir do exemplo 03, o transmissor passa a ser outra placa,
conectada diretamente pelos pinos UART:

```
ESP32 A GPIO1 (TX)  →  GPIO3 (RX) ESP32 B
ESP32 A GPIO3 (RX)  →  GPIO1 (TX) ESP32 B
ESP32 A GND         →  GND        ESP32 B
```
