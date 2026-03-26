# ============================================================
# Passo 5 — Máquina de Estados para Recepção UART
# ============================================================
# Compatível com: Raspberry Pi Pico e ESP32
# IDE: Thonny
#
# O que este programa faz:
#   Implementa uma máquina de estados simples para controlar
#   o ciclo de vida de uma mensagem UART:
#
#     IDLE → RECEBENDO → PROCESSANDO → IDLE
#
#   Em vez de um loop que simplesmente acumula bytes, o
#   programa sabe exatamente em que fase se encontra — e age
#   de forma diferente em cada uma.
#
# Por que isso importa?
#   No passo 4, o buffer acumulava bytes sem critério. Se
#   chegassem dados corrompidos ou fora de ordem, o programa
#   tentaria processar uma mensagem mal formada sem perceber.
#   A máquina de estados torna o comportamento explícito e
#   previsível em qualquer situação.
#
# Formato do comando (mesmo do passo 4):
#   COMANDO:ARGUMENTO\n
# ============================================================

from machine import UART, Pin
import sys

# ------------------------------------------------------------
# Configuração da UART
# ------------------------------------------------------------

UART_ID   = 0        # 0 = UART0 | 1 = UART1
BAUD_RATE = 9600     # Taxa de comunicação em bits por segundo

TX_PIN = None        # None = pino padrão da placa
RX_PIN = None        # None = pino padrão da placa

# ------------------------------------------------------------
# Configuração do LED
# ------------------------------------------------------------
#
# Raspberry Pi Pico  → LED onboard: pino 25
# ESP32 DevKit v1   → LED onboard: pino 2
# ESP32-C3          → LED onboard: pino 8

LED_PIN = 25         # Ajuste conforme sua placa

# ------------------------------------------------------------
# Definição dos estados
# ------------------------------------------------------------
#
# Usar constantes nomeadas (em vez de números mágicos como
# 0, 1, 2) torna o código legível e fácil de depurar.

IDLE         = 'IDLE'         # Aguardando início de mensagem
RECEBENDO    = 'RECEBENDO'    # Acumulando bytes no buffer
PROCESSANDO  = 'PROCESSANDO'  # Executando o comando recebido

# ------------------------------------------------------------
# Inicialização
# ------------------------------------------------------------

if TX_PIN is not None and RX_PIN is not None:
    uart = UART(UART_ID, baudrate=BAUD_RATE,
                tx=Pin(TX_PIN), rx=Pin(RX_PIN))
else:
    uart = UART(UART_ID, baudrate=BAUD_RATE)

led  = Pin(LED_PIN, Pin.OUT)

estado = IDLE   # Estado inicial da máquina
buffer = ''     # Acumula os bytes da mensagem atual

# ------------------------------------------------------------
# Funções de comando (mesmas do passo 4)
# ------------------------------------------------------------

def cmd_led(argumento):
    if argumento == 'L':
        led.value(1)
        return "LED ligado"
    elif argumento == 'D':
        led.value(0)
        return "LED desligado"
    else:
        return f"Argumento inválido para LED: '{argumento}'"


def cmd_msg(argumento):
    print(f"[MSG] {argumento}")
    return f"Mensagem recebida: {argumento}"


comandos = {
    'LED': cmd_led,
    'MSG': cmd_msg,
}

# ------------------------------------------------------------
# Funções da máquina de estados
# ------------------------------------------------------------

def processar_idle(char):
    """
    Estado IDLE: aguarda o primeiro byte de uma mensagem.
    Ignora espaços, '\n' e '\r' soltos (ruído de linha).
    Qualquer outro byte inicia uma nova mensagem.
    """
    if char in ('\n', '\r', ' '):
        return IDLE              # Ignora ruído, permanece IDLE
    else:
        return RECEBENDO         # Primeiro byte válido: inicia recepção


def processar_recebendo(char, buffer):
    """
    Estado RECEBENDO: acumula bytes até o terminador '\n'.
    Retorna o próximo estado e o buffer atualizado.
    """
    if char == '\n':
        return PROCESSANDO, buffer    # Mensagem completa
    elif char == '\r':
        return RECEBENDO, buffer      # Ignora '\r' (Windows)
    else:
        return RECEBENDO, buffer + char  # Acumula


def processar_comando(buffer):
    """
    Estado PROCESSANDO: interpreta o buffer e executa o comando.
    Retorna a string de resposta.
    """
    linha = buffer.strip()

    if ':' not in linha:
        return "Formato inválido. Use COMANDO:ARGUMENTO"

    partes    = linha.split(':', 1)
    comando   = partes[0].upper()
    argumento = partes[1]

    if comando in comandos:
        return comandos[comando](argumento)
    else:
        return f"Comando desconhecido: '{comando}'"

# ------------------------------------------------------------
# Mensagem inicial
# ------------------------------------------------------------

print("=" * 40)
print("  Passo 5 — Máquina de Estados UART")
print("=" * 40)
print(f"  UART{UART_ID} | {BAUD_RATE} bps | LED: GP{LED_PIN}")
print(f"  Estado inicial: {estado}")
print("  Formato: COMANDO:ARGUMENTO + Enter")
print("=" * 40)

# ------------------------------------------------------------
# Loop principal — transições de estado explícitas
# ------------------------------------------------------------

while True:
    if uart.any():
        byte = uart.read(1)
        char = byte.decode()

        # --- Estado IDLE ---
        if estado == IDLE:
            proximo = processar_idle(char)
            if proximo == RECEBENDO:
                buffer = char            # Guarda o primeiro byte
            estado = proximo
            print(f"[{estado}]", end=' ')

        # --- Estado RECEBENDO ---
        elif estado == RECEBENDO:
            proximo, buffer = processar_recebendo(char, buffer)
            estado = proximo
            print(f"[{estado}]", end=' ')

        # --- Estado PROCESSANDO ---
        if estado == PROCESSANDO:
            resposta = processar_comando(buffer)
            uart.write(resposta + '\n')
            print(f"\n>> {resposta}")
            buffer = ''                  # Limpa para a próxima mensagem
            estado = IDLE                # Volta ao início do ciclo
            print(f"[{estado}]", end=' ')
