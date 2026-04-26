# ============================================================
# Passo 07 — Loopback UART (simulação Wokwi)
#
# Simula a comunicação entre duas UARTs em um único ESP32.
# UART1 (transmissora) conectada à UART2 (receptora)
# por um fio virtual no diagrama.
#
# Equivalente ao loopback físico com duas placas, mas
# executado em um único ESP32 no simulador Wokwi.
#
# Conexão interna (fio no diagram.json):
#   GPIO 4  (TX1) → GPIO 16 (RX2)
#
# Periféricos:
#   GPIO 13 → botão (pull-up interno)
#   GPIO 2  → LED
#
# Protocolo:
#   b'\x01' → acende LED
#   b'\x00' → apaga LED
#
# Baud rate: 9600 bps
# ============================================================

from machine import UART, Pin  # type: ignore[import]
import time

# --- Configuração das UARTs ---
uart_tx = UART(1, baudrate=9600, tx=4,  rx=5)   # transmissora
uart_rx = UART(2, baudrate=9600, tx=17, rx=16)  # receptora

# --- Periféricos ---
botao = Pin(13, Pin.IN, Pin.PULL_UP)
led   = Pin(2,  Pin.OUT)
led.value(0)

# --- Estado anterior do botão (debounce por software) ---
estado_anterior = 1

print("Passo 07 — Loopback UART iniciado.")
print("Pressione o botão para acionar o LED.")

# --- Loop principal não bloqueante ---
while True:

    # TRANSMISSORA: detecta mudança no botão e envia byte
    estado_atual = botao.value()

    if estado_atual != estado_anterior:
        estado_anterior = estado_atual

        if estado_atual == 0:
            uart_tx.write(b'\x01')
            print("[TX] Enviou 0x01 (LIGAR)")
        else:
            uart_tx.write(b'\x00')
            print("[TX] Enviou 0x00 (DESLIGAR)")

    # RECEPTORA: lê byte recebido e controla o LED
    if uart_rx.any():
        dado = uart_rx.read(1)

        if dado == b'\x01':
            led.value(1)
            print("[RX] LED LIGADO")
        elif dado == b'\x00':
            led.value(0)
            print("[RX] LED DESLIGADO")

    time.sleep(0.02)
