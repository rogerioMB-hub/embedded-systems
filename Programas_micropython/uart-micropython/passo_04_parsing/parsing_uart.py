# ============================================================
# Passo 4 — Parsing de Comandos com Terminador '\n'
# ============================================================
# Compatível com: Raspberry Pi Pico e ESP32
# IDE: Thonny
#
# O que este programa faz:
#   Lê bytes da UART e acumula em um buffer até receber '\n'
#   (o Enter do teclado). Ao detectar o terminador, separa a
#   mensagem em COMANDO e ARGUMENTO e executa a ação.
#
# Formato esperado:
#   COMANDO:ARGUMENTO\n
#
# Exemplos de comandos válidos:
#   LED:L\n    → liga o LED
#   LED:D\n    → desliga o LED
#   MSG:ola\n  → exibe "ola" no Shell
#
# Como usar:
#   1. Grave este arquivo na placa pelo Thonny
#   2. Ajuste LED_PIN conforme sua placa
#   3. Abra o Shell do Thonny
#   4. Digite o comando completo e pressione Enter
#
# Por que o terminador é importante?
#   A UART entrega bytes na ordem em que chegam, sem saber
#   onde começa ou termina uma mensagem. O terminador é a
#   convenção que define o fim de um comando — sem ele,
#   o receptor não sabe quando parar de ler.
# ============================================================

from machine import UART, Pin
import sys

# ------------------------------------------------------------
# Configuração da UART
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
# Raspberry Pi Pico  → LED onboard: pino 25
# ESP32 DevKit v1   → LED onboard: pino 2
# ESP32-C3          → LED onboard: pino 8

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

# Buffer acumula os bytes recebidos até chegar o '\n'
buffer = ''

# ------------------------------------------------------------
# Funções de comando
# ------------------------------------------------------------

def cmd_led(argumento):
    """Controla o LED com base no argumento recebido."""
    if argumento == 'L':
        led.value(1)
        return "LED ligado"
    elif argumento == 'D':
        led.value(0)
        return "LED desligado"
    else:
        return f"Argumento inválido para LED: '{argumento}'"


def cmd_msg(argumento):
    """Exibe uma mensagem no Shell."""
    print(f"[MSG] {argumento}")
    return f"Mensagem recebida: {argumento}"


# Dicionário de comandos: cada chave mapeia para uma função
# Adicionar um novo comando = adicionar uma entrada aqui
comandos = {
    'LED': cmd_led,
    'MSG': cmd_msg,
}

# ------------------------------------------------------------
# Função de parsing
# ------------------------------------------------------------

def processar(linha):
    """
    Recebe uma linha completa (sem o '\n') e a interpreta.
    Formato esperado: COMANDO:ARGUMENTO
    Retorna a string de resposta.
    """
    linha = linha.strip()              # Remove espaços e '\r' residuais

    if ':' not in linha:               # Formato inválido?
        return f"Formato inválido. Use COMANDO:ARGUMENTO"

    # Divide apenas no primeiro ':' — o argumento pode conter ':'
    partes   = linha.split(':', 1)
    comando  = partes[0].upper()       # Comando em maiúsculas
    argumento = partes[1]              # Argumento preserva o caso original

    if comando in comandos:            # Comando reconhecido?
        return comandos[comando](argumento)
    else:
        return f"Comando desconhecido: '{comando}'"

# ------------------------------------------------------------
# Mensagem inicial
# ------------------------------------------------------------

print("=" * 40)
print("  Passo 4 — Parsing de Comandos UART")
print("=" * 40)
print(f"  UART{UART_ID} | {BAUD_RATE} bps | LED: GP{LED_PIN}")
print("  Formato: COMANDO:ARGUMENTO + Enter")
print("  Exemplos:")
print("    LED:L   → liga o LED")
print("    LED:D   → desliga o LED")
print("    MSG:ola → exibe mensagem")
print("=" * 40)

# ------------------------------------------------------------
# Loop principal — acumula bytes até receber '\n'
# ------------------------------------------------------------

while True:
    if uart.any():                         # Há byte(s) disponível(is)?
        byte = uart.read(1)                # Lê exatamente 1 byte
        char = byte.decode()              # Converte para string

        if char == '\n':                   # Terminador detectado?
            resposta = processar(buffer)   # Processa o buffer acumulado
            uart.write(resposta + '\n')    # Envia resposta pela UART
            print(f">> {resposta}")        # Exibe no Shell
            buffer = ''                    # Limpa o buffer para o próximo comando
        else:
            buffer += char                 # Acumula o caractere no buffer
