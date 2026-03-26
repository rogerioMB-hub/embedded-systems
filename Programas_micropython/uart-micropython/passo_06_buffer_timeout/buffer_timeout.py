# ============================================================
# Passo 6 — Buffer e Timeout na Recepção UART
# ============================================================
# Compatível com: Raspberry Pi Pico e ESP32
# IDE: Thonny
#
# O que este programa faz:
#   Evolui a máquina de estados do passo 5 com dois mecanismos
#   de proteção essenciais em comunicação serial real:
#
#   1. TIMEOUT: se o dispositivo ficar muito tempo no estado
#      RECEBENDO sem receber o terminador '\n', descarta o
#      buffer e volta ao IDLE. Evita travamento por mensagens
#      incompletas.
#
#   2. LIMITE DE BUFFER: se o buffer atingir o tamanho máximo
#      sem o terminador, a mensagem é descartada. Evita
#      consumo excessivo de memória RAM (crítico em embarcados).
#
# Por que isso importa?
#   Em comunicação serial real, bytes se perdem, cabos são
#   desconectados no meio de uma transmissão e ruído elétrico
#   corrompe dados. Um sistema robusto precisa se recuperar
#   dessas situações sozinho, sem travar e sem precisar de
#   reset manual.
#
# Formato do comando (mesmo dos passos 4 e 5):
#   COMANDO:ARGUMENTO\n
# ============================================================

from machine import UART, Pin
import time
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
# Parâmetros de proteção do buffer
# ------------------------------------------------------------

TIMEOUT_MS  = 2000   # Tempo máximo em RECEBENDO (milissegundos)
BUFFER_MAX  = 64     # Tamanho máximo do buffer (bytes)
                     # Mantenha baixo: microcontroladores têm
                     # RAM limitada (Pico: 264 KB, ESP32: ~320 KB)

# ------------------------------------------------------------
# Estados da máquina
# ------------------------------------------------------------

IDLE        = 'IDLE'
RECEBENDO   = 'RECEBENDO'
PROCESSANDO = 'PROCESSANDO'

# ------------------------------------------------------------
# Inicialização
# ------------------------------------------------------------

if TX_PIN is not None and RX_PIN is not None:
    uart = UART(UART_ID, baudrate=BAUD_RATE,
                tx=Pin(TX_PIN), rx=Pin(RX_PIN))
else:
    uart = UART(UART_ID, baudrate=BAUD_RATE)

led = Pin(LED_PIN, Pin.OUT)

estado         = IDLE
buffer         = ''
tempo_inicio   = 0   # Marca o instante em que RECEBENDO começou

# ------------------------------------------------------------
# Funções de comando
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
# Função de parsing (mesma do passo 4 e 5)
# ------------------------------------------------------------

def processar_comando(buffer):
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
# Função de descarte — centraliza a lógica de reset
# ------------------------------------------------------------

def descartar(motivo):
    """
    Descarta o buffer atual, envia aviso pela UART e
    retorna o sistema ao estado IDLE.
    Centralizar aqui evita repetir código em dois lugares.
    """
    aviso = f"[DESCARTADO] {motivo}"
    uart.write(aviso + '\n')
    print(aviso)
    return IDLE, '', 0   # Retorna: estado, buffer, tempo_inicio

# ------------------------------------------------------------
# Mensagem inicial
# ------------------------------------------------------------

print("=" * 40)
print("  Passo 6 — Buffer e Timeout UART")
print("=" * 40)
print(f"  UART{UART_ID} | {BAUD_RATE} bps | LED: GP{LED_PIN}")
print(f"  Timeout: {TIMEOUT_MS} ms | Buffer máx: {BUFFER_MAX} bytes")
print("  Formato: COMANDO:ARGUMENTO + Enter")
print("=" * 40)

# ------------------------------------------------------------
# Loop principal
# ------------------------------------------------------------

while True:

    # --- Verificação de timeout (independente de novos bytes) ---
    #
    # Esta verificação ocorre a CADA iteração do loop, mesmo
    # quando não há bytes disponíveis. É o que permite detectar
    # silêncio na linha — o clock continua correndo mesmo sem dados.

    if estado == RECEBENDO:
        tempo_decorrido = time.ticks_diff(time.ticks_ms(), tempo_inicio)
        if tempo_decorrido >= TIMEOUT_MS:
            estado, buffer, tempo_inicio = descartar(
                f"timeout de {TIMEOUT_MS} ms — buffer: '{buffer}'"
            )

    # --- Leitura de bytes disponíveis ---

    if uart.any():
        byte = uart.read(1)
        char = byte.decode()

        # Estado IDLE
        if estado == IDLE:
            if char not in ('\n', '\r', ' '):
                buffer       = char
                tempo_inicio = time.ticks_ms()   # Inicia o cronômetro
                estado       = RECEBENDO
                print(f"[{estado}]", end=' ')

        # Estado RECEBENDO
        elif estado == RECEBENDO:
            if char == '\n':
                estado = PROCESSANDO

            elif char == '\r':
                pass                             # Ignora '\r' (Windows)

            elif len(buffer) >= BUFFER_MAX:
                estado, buffer, tempo_inicio = descartar(
                    f"buffer cheio ({BUFFER_MAX} bytes)"
                )

            else:
                buffer += char

        # Estado PROCESSANDO
        if estado == PROCESSANDO:
            resposta = processar_comando(buffer)
            uart.write(resposta + '\n')
            print(f"\n>> {resposta}")
            buffer       = ''
            tempo_inicio = 0
            estado       = IDLE
            print(f"[{estado}]", end=' ')
