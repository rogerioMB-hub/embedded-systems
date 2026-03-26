# ============================================================
# Passo 8 — Modelo Controladora–Periférica: PERIFÉRICA
# ============================================================
# Compatível com: Raspberry Pi Pico e ESP32
# IDE: Thonny
#
# Este arquivo roda na placa PERIFÉRICA.
# O par é: controladora.py  ←→  periferica.py
#
# O que este programa faz:
#   Aguarda requisições da controladora, lê o sensor pedido
#   e responde com o valor no formato acordado.
#
# Protocolo:
#   Controladora envia : "REQ:SENSOR\n"
#   Periférica responde: "DADO:SENSOR:VALOR\n"
#
#   Exemplo real:
#     Entrada : "REQ:TEMP\n"
#     Saída   : "DADO:TEMP:23.4\n"
#
# Sensores implementados:
#   TEMP → temperatura interna do chip (sensor real disponível
#          no Pico e em muitos ESP32 — sem hardware externo)
#   LUM  → leitura analógica do ADC (simula luminosidade)
#          No Pico: usa o pino GP26 (ADC0)
#          No ESP32: usa o pino GP34 (ADC0)
#
# Conexão física: veja controladora.py ou o README.
# ============================================================

from machine import UART, Pin, ADC
import time
import sys

# ------------------------------------------------------------
# Configuração da UART
# ------------------------------------------------------------

UART_ID   = 1
BAUD_RATE = 9600
TX_PIN    = 4        # Ajuste conforme sua placa
RX_PIN    = 5        # Ajuste conforme sua placa

# ------------------------------------------------------------
# Configuração dos sensores
# ------------------------------------------------------------
#
# Pico  → sensor de temperatura interno: ADC(4)
#         pino analógico externo       : ADC(26) = GP26
#
# ESP32 → sensor de temperatura interno: disponível via esp32.raw_temperature()
#         pino analógico externo       : ADC(Pin(34))
#
# Este exemplo usa o sensor interno do Pico (ADC(4)).
# Se usar ESP32, ajuste a função ler_temperatura() abaixo.

ADC_TEMP = ADC(4)    # Sensor interno — Pico
ADC_LUM  = ADC(26)   # Pino externo  — Pico (GP26)
                     # Para ESP32: ADC(Pin(34))

BUFFER_MAX = 64
TIMEOUT_MS = 2000

# ------------------------------------------------------------
# Inicialização
# ------------------------------------------------------------

uart = UART(UART_ID, baudrate=BAUD_RATE,
            tx=Pin(TX_PIN), rx=Pin(RX_PIN))

estado       = 'IDLE'
buffer       = ''
tempo_inicio = 0
atendidas    = 0

# ------------------------------------------------------------
# Funções de leitura de sensores
# ------------------------------------------------------------

def ler_temperatura():
    """
    Lê o sensor de temperatura interno do Pico (ADC canal 4).
    Converte a leitura bruta para graus Celsius.

    Para ESP32, substitua por:
        import esp32
        return f"{esp32.raw_temperature():.1f}"
    """
    leitura  = ADC_TEMP.read_u16()           # Valor bruto: 0–65535
    tensao   = leitura * 3.3 / 65535         # Converte para volts
    temp_c   = 27 - (tensao - 0.706) / 0.001721  # Fórmula do datasheet
    return f"{temp_c:.1f}"


def ler_luminosidade():
    """
    Lê um valor analógico no pino GP26 e converte para
    uma escala percentual de 0 a 100.
    Sem sensor externo, retornará um valor próximo de 0
    (pino flutuando) — suficiente para demonstrar o protocolo.
    """
    leitura   = ADC_LUM.read_u16()           # Valor bruto: 0–65535
    percentual = round(leitura / 65535 * 100, 1)
    return f"{percentual}"


# Dicionário de sensores: nome → função de leitura
# Para adicionar um sensor novo, basta criar a função
# e registrá-la aqui — o restante do código não muda.
sensores = {
    'TEMP': ler_temperatura,
    'LUM' : ler_luminosidade,
}

# ------------------------------------------------------------
# Função de processamento de requisição
# ------------------------------------------------------------

def processar_requisicao(buffer):
    """
    Interpreta uma requisição no formato "REQ:SENSOR" e
    retorna a string de resposta completa.
    """
    linha = buffer.strip()

    if not linha.startswith('REQ:'):
        return "ERRO:FORMATO"

    sensor = linha[4:].upper()          # Extrai o nome do sensor

    if sensor in sensores:
        valor    = sensores[sensor]()   # Chama a função de leitura
        return f"DADO:{sensor}:{valor}"
    else:
        return f"ERRO:SENSOR_DESCONHECIDO:{sensor}"

# ------------------------------------------------------------
# Mensagem inicial
# ------------------------------------------------------------

print("=" * 40)
print("  Passo 8 — Controladora–Periférica")
print("  Papel: PERIFÉRICA")
print("=" * 40)
print(f"  UART{UART_ID} | TX:GP{TX_PIN} | RX:GP{RX_PIN}")
print(f"  Baud rate  : {BAUD_RATE} bps")
print(f"  Sensores   : {', '.join(sensores.keys())}")
print("  Aguardando requisições...")
print("=" * 40)

# ------------------------------------------------------------
# Loop principal — máquina de estados com timeout
# ------------------------------------------------------------

while True:

    # Verificação de timeout
    if estado == 'RECEBENDO':
        decorrido = time.ticks_diff(time.ticks_ms(), tempo_inicio)
        if decorrido >= TIMEOUT_MS:
            print(f"[DESCARTADO] timeout — buffer: '{buffer}'")
            estado, buffer, tempo_inicio = 'IDLE', '', 0

    if uart.any():
        char = uart.read(1).decode()

        if estado == 'IDLE':
            if char not in ('\n', '\r', ' '):
                buffer       = char
                tempo_inicio = time.ticks_ms()
                estado       = 'RECEBENDO'

        elif estado == 'RECEBENDO':
            if char == '\n':
                estado = 'PROCESSANDO'
            elif char == '\r':
                pass
            elif len(buffer) >= BUFFER_MAX:
                print(f"[DESCARTADO] buffer cheio")
                estado, buffer, tempo_inicio = 'IDLE', '', 0
            else:
                buffer += char

        if estado == 'PROCESSANDO':
            resposta = processar_requisicao(buffer)
            uart.write(resposta + '\n')
            atendidas += 1
            print(f"[{atendidas:03d}] '{buffer}' → '{resposta}'")
            buffer, tempo_inicio = '', 0
            estado = 'IDLE'
