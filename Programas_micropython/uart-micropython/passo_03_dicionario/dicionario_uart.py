# ============================================================
# Passo 3 — Dicionário de Dígitos por Extenso via UART
# ============================================================
# Compatível com: Raspberry Pi Pico e ESP32
# IDE: Thonny
#
# O que este programa faz:
#   Aguarda um caractere via UART. Se receber um dígito entre
#   '1' e '9', responde com o nome do número por extenso.
#   Qualquer outro caractere gera "Caractere desconhecido".
#
# Como usar:
#   1. Grave este arquivo na placa pelo Thonny
#   2. Abra o Shell do Thonny
#   3. Digite um dígito de 1 a 9 e observe a resposta
#
# Conceito central:
#   Um dicionário Python mapeia cada chave (char) a um valor
#   (string). O operador 'in' verifica se a chave existe antes
#   de acessar — evitando erros e dispensando longas cadeias
#   de if/elif.
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
# Dicionário de dígitos por extenso
# ------------------------------------------------------------
#
# Cada chave é um caractere ('1', '2', ..., '9').
# Cada valor é a string correspondente por extenso.
#
# Note que as chaves são STRINGS, não inteiros —
# pois o que chega pela UART é sempre um caractere de texto.

digitos = {
    '1': 'um',
    '2': 'dois',
    '3': 'três',
    '4': 'quatro',
    '5': 'cinco',
    '6': 'seis',
    '7': 'sete',
    '8': 'oito',
    '9': 'nove',
}

# ------------------------------------------------------------
# Inicialização
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
print("  Passo 3 — Dicionário via UART")
print("=" * 40)
print(f"  UART{UART_ID} | {BAUD_RATE} bps")
print("  Envie um dígito de 1 a 9")
print("=" * 40)

# ------------------------------------------------------------
# Loop principal
# ------------------------------------------------------------

while True:
    if uart.any():                        # Há byte(s) disponível(is)?
        byte = uart.read(1)               # Lê exatamente 1 byte
        char = byte.decode()              # Converte bytes para string

        if char in digitos:               # A chave existe no dicionário?
            resposta = digitos[char]      # Recupera o valor
            uart.write(resposta + '\n')
            print(f"'{char}' → {resposta}")

        else:                             # Chave não encontrada
            uart.write("Caractere desconhecido\n")
            print(f"Caractere desconhecido: {repr(char)}")
