# ============================================================
# Passo 1 — Eco Serial via UART
# ============================================================
# Compatível com: Raspberry Pi Pico e ESP32
# IDE: Thonny
#
# O que este programa faz:
#   Tudo que o aluno digitar no Shell do Thonny é enviado
#   pela UART e ecoado de volta, byte a byte, para o Shell.
#
# Como usar:
#   1. Grave este arquivo na placa pelo Thonny
#   2. Abra o Shell do Thonny
#   3. Digite qualquer caractere — ele aparecerá de volta
#
# Conexão para teste com eco real (opcional):
#   Pico  → conecte TX ao RX com um fio (loopback)
#   ESP32 → conecte TX ao RX com um fio (loopback)
#
#   Sem o fio, o Thonny já faz o eco via USB/REPL —
#   use o loopback para ver a UART funcionando de verdade.
# ============================================================

from machine import UART, Pin
import sys

# ------------------------------------------------------------
# Configuração — ajuste aqui se necessário
# ------------------------------------------------------------

UART_ID   = 0        # 0 = UART0 | 1 = UART1
BAUD_RATE = 9600     # Taxa de comunicação em bits por segundo

# Pinos padrão para UART0:
#   Raspberry Pi Pico → TX: GP0  | RX: GP1
#   ESP32             → TX: GP1  | RX: GP3
#
# Pinos padrão para UART1:
#   Raspberry Pi Pico → TX: GP4  | RX: GP5
#   ESP32             → TX: GP10 | RX: GP9
#
# Deixe TX_PIN e RX_PIN como None para usar os pinos padrão
# da placa, ou informe os números desejados.

TX_PIN = None
RX_PIN = None

# ------------------------------------------------------------
# Inicialização da UART
# ------------------------------------------------------------

if TX_PIN is not None and RX_PIN is not None:
    uart = UART(UART_ID, baudrate=BAUD_RATE,
                tx=Pin(TX_PIN), rx=Pin(RX_PIN))
else:
    uart = UART(UART_ID, baudrate=BAUD_RATE)

# ------------------------------------------------------------
# Mensagem inicial
# ------------------------------------------------------------

print("=" * 40)
print("  Passo 1 — Eco Serial UART")
print("=" * 40)
print(f"  UART{UART_ID} | {BAUD_RATE} bps")
print("  Aguardando dados...")
print("=" * 40)

# ------------------------------------------------------------
# Loop principal — eco byte a byte
# ------------------------------------------------------------

while True:
    if uart.any():                  # Há byte(s) disponível(is)?
        byte = uart.read(1)         # Lê exatamente 1 byte
        uart.write(byte)            # Ecoa o mesmo byte de volta
        print(byte.decode(), end="")  # Mostra no Shell do Thonny
