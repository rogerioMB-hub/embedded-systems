# ============================================================
# Passo 2 — Controle de LED via UART
# ============================================================
# Compatível com: Raspberry Pi Pico e ESP32
# IDE: Thonny
#
# O que este programa faz:
#   Aguarda um caractere via UART. Se receber 'L', liga o LED.
#   Se receber 'D', desliga o LED. Qualquer outro caractere
#   gera a mensagem "Caractere desconhecido" no Shell.
#
# Como usar:
#   1. Grave este arquivo na placa pelo Thonny
#   2. Ajuste LED_PIN conforme sua placa (veja comentários)
#   3. Abra o Shell do Thonny
#   4. Digite 'L' para ligar e 'D' para desligar o LED
# ============================================================

from machine import UART, Pin
import sys

# ------------------------------------------------------------
# Configuração da UART — mesma lógica do passo 1
# ------------------------------------------------------------

UART_ID   = 0        # 0 = UART0 | 1 = UART1
BAUD_RATE = 9600     # Taxa de comunicação em bits por segundo

# Deixe como None para usar os pinos padrão da placa.
TX_PIN = None
RX_PIN = None

# ------------------------------------------------------------
# Configuração do LED
# ------------------------------------------------------------
#
# Raspberry Pi Pico:
#   LED onboard → pino 25 (use LED_PIN = 25)
#
# ESP32 (varia conforme o modelo):
#   ESP32 DevKit v1 → LED onboard no pino 2
#   ESP32-C3        → LED onboard no pino 8
#   Sem LED onboard → conecte um LED externo a qualquer GPIO
#
# Para usar um LED externo em qualquer placa:
#   Conecte o LED (com resistor de 330Ω) entre o pino
#   escolhido e o GND, e informe o número do pino abaixo.

LED_PIN = 25         # Ajuste conforme sua placa

# ------------------------------------------------------------
# Inicialização
# ------------------------------------------------------------

if TX_PIN is not None and RX_PIN is not None:
    uart = UART(UART_ID, baudrate=BAUD_RATE,
                tx=Pin(TX_PIN), rx=Pin(RX_PIN))
else:
    uart = UART(UART_ID, baudrate=BAUD_RATE)

led = Pin(LED_PIN, Pin.OUT)

# ------------------------------------------------------------
# Mensagem inicial
# ------------------------------------------------------------

print("=" * 40)
print("  Passo 2 — Controle de LED via UART")
print("=" * 40)
print(f"  UART{UART_ID} | {BAUD_RATE} bps | LED: GP{LED_PIN}")
print("  Comandos disponíveis:")
print("    'L' → Liga o LED")
print("    'D' → Desliga o LED")
print("=" * 40)

# ------------------------------------------------------------
# Loop principal
# ------------------------------------------------------------

while True:
    if uart.any():                       # Há byte(s) disponível(is)?
        byte  = uart.read(1)             # Lê exatamente 1 byte
        char  = byte.decode()            # Converte bytes para string

        if char == 'L':                  # Comando: ligar
            led.value(1)
            uart.write("LED ligado\n")
            print("LED ligado")

        elif char == 'D':                # Comando: desligar
            led.value(0)
            uart.write("LED desligado\n")
            print("LED desligado")

        else:                            # Qualquer outro caractere
            uart.write("Caractere desconhecido\n")
            print(f"Caractere desconhecido: {repr(char)}")
