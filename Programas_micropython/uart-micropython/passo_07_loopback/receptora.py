# ============================================================
# Passo 7 — Loopback entre Duas Placas: RECEPTORA
# ============================================================
# Compatível com: Raspberry Pi Pico e ESP32
# IDE: Thonny
#
# Este arquivo roda na placa RECEPTORA.
# O par é: transmissora.py  ←→  receptora.py
#
# O que este programa faz:
#   Aguarda mensagens da placa transmissora, acumula bytes
#   até receber '\n' e ecoa a mensagem de volta integralmente.
#   Aplica o buffer e timeout do passo 6 para robustez.
#
# Conexão física:
#   Veja o diagrama em transmissora.py ou no README.
# ============================================================

from machine import UART, Pin
import time
import sys

# ------------------------------------------------------------
# Configuração da UART
# ------------------------------------------------------------

UART_ID   = 1        # Deve ser o mesmo da transmissora
BAUD_RATE = 9600     # Deve ser o mesmo da transmissora

# Pinos para UART1:
#   Raspberry Pi Pico → TX: GP4  | RX: GP5
#   ESP32             → TX: GP10 | RX: GP9
#
# Ajuste conforme sua placa:
TX_PIN = 4
RX_PIN = 5

# ------------------------------------------------------------
# Parâmetros de proteção (herdados do passo 6)
# ------------------------------------------------------------

TIMEOUT_MS = 2000    # Descarta buffer se não chegar '\n' a tempo
BUFFER_MAX = 64      # Descarta se buffer ultrapassar este tamanho

# ------------------------------------------------------------
# Inicialização
# ------------------------------------------------------------

uart = UART(UART_ID, baudrate=BAUD_RATE,
            tx=Pin(TX_PIN), rx=Pin(RX_PIN))

estado       = 'IDLE'
buffer       = ''
tempo_inicio = 0
ecoados      = 0
descartados  = 0

# ------------------------------------------------------------
# Mensagem inicial
# ------------------------------------------------------------

print("=" * 40)
print("  Passo 7 — Loopback UART (Receptora)")
print("=" * 40)
print(f"  UART{UART_ID} | TX:GP{TX_PIN} | RX:GP{RX_PIN}")
print(f"  Baud rate : {BAUD_RATE} bps")
print(f"  Timeout   : {TIMEOUT_MS} ms")
print(f"  Buffer máx: {BUFFER_MAX} bytes")
print("  Aguardando mensagens...")
print("=" * 40)

# ------------------------------------------------------------
# Loop principal — recebe e ecoa
# ------------------------------------------------------------

while True:

    # Verificação de timeout (roda mesmo sem bytes disponíveis)
    if estado == 'RECEBENDO':
        decorrido = time.ticks_diff(time.ticks_ms(), tempo_inicio)
        if decorrido >= TIMEOUT_MS:
            descartados += 1
            print(f"[DESCARTADO] timeout — buffer: '{buffer}'")
            estado, buffer, tempo_inicio = 'IDLE', '', 0

    if uart.any():
        byte = uart.read(1)
        char = byte.decode()

        # Estado IDLE — aguarda primeiro byte válido
        if estado == 'IDLE':
            if char not in ('\n', '\r', ' '):
                buffer       = char
                tempo_inicio = time.ticks_ms()
                estado       = 'RECEBENDO'

        # Estado RECEBENDO — acumula até '\n' ou limite
        elif estado == 'RECEBENDO':
            if char == '\n':
                estado = 'PROCESSANDO'
            elif char == '\r':
                pass                         # Ignora '\r'
            elif len(buffer) >= BUFFER_MAX:
                descartados += 1
                print(f"[DESCARTADO] buffer cheio")
                estado, buffer, tempo_inicio = 'IDLE', '', 0
            else:
                buffer += char

        # Estado PROCESSANDO — ecoa e volta ao IDLE
        if estado == 'PROCESSANDO':
            uart.write(buffer + '\n')        # Eco da mensagem recebida
            ecoados += 1
            print(f"[ECO #{ecoados:03d}] '{buffer}'")
            buffer, tempo_inicio = '', 0
            estado = 'IDLE'
