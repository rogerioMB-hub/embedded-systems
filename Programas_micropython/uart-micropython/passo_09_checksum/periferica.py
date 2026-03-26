# ============================================================
# Passo 9 — Frame com Checksum XOR: PERIFÉRICA
# ============================================================
# Compatível com: Raspberry Pi Pico e ESP32
# IDE: Thonny
#
# Este arquivo roda na placa PERIFÉRICA.
# O par é: controladora.py  ←→  periferica.py
#
# O que este programa faz:
#   Recebe frames com checksum, valida a integridade antes
#   de processar, executa a leitura do sensor e responde
#   com um frame igualmente protegido por checksum.
#
# Formato do frame: PAYLOAD*XX\n
#   Veja controladora.py para descrição completa.
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
# Parâmetros de proteção
# ------------------------------------------------------------

TIMEOUT_MS = 2000
BUFFER_MAX = 64

# ------------------------------------------------------------
# Inicialização
# ------------------------------------------------------------

uart = UART(UART_ID, baudrate=BAUD_RATE,
            tx=Pin(TX_PIN), rx=Pin(RX_PIN))

ADC_TEMP = ADC(4)    # Sensor interno — Pico
ADC_LUM  = ADC(26)   # Pino externo  — Pico GP26

estado       = 'IDLE'
buffer       = ''
tempo_inicio = 0

# Contadores de diagnóstico
atendidas = 0
invalidos = 0

# ------------------------------------------------------------
# Funções de checksum (idênticas à controladora)
# ------------------------------------------------------------

def calcular_checksum(payload):
    """Calcula o checksum XOR de todos os bytes do payload."""
    resultado = 0
    for byte in payload.encode():
        resultado ^= byte
    return resultado


def montar_frame(payload):
    """Monta o frame: PAYLOAD*XX"""
    cs = calcular_checksum(payload)
    return f"{payload}*{cs:02X}"


def validar_frame(frame):
    """
    Valida o frame recebido.
    Retorna (payload, True) se íntegro, (None, False) se corrompido.
    """
    if '*' not in frame:
        return None, False

    partes  = frame.rsplit('*', 1)
    payload = partes[0]
    cs_rec  = partes[1]

    if len(cs_rec) != 2:
        return None, False

    try:
        cs_calculado = calcular_checksum(payload)
        cs_recebido  = int(cs_rec, 16)
    except ValueError:
        return None, False

    if cs_calculado == cs_recebido:
        return payload, True
    else:
        return payload, False

# ------------------------------------------------------------
# Funções de leitura de sensores
# ------------------------------------------------------------

def ler_temperatura():
    leitura = ADC_TEMP.read_u16()
    tensao  = leitura * 3.3 / 65535
    temp_c  = 27 - (tensao - 0.706) / 0.001721
    return f"{temp_c:.1f}"


def ler_luminosidade():
    leitura    = ADC_LUM.read_u16()
    percentual = round(leitura / 65535 * 100, 1)
    return f"{percentual}"


sensores = {
    'TEMP': ler_temperatura,
    'LUM' : ler_luminosidade,
}

# ------------------------------------------------------------
# Função de processamento
# ------------------------------------------------------------

def processar(payload):
    """
    Interpreta o payload já validado e retorna o payload
    da resposta (sem checksum — será adicionado pelo chamador).
    """
    if not payload.startswith('REQ:'):
        return "ERRO:FORMATO"

    sensor = payload[4:].upper()

    if sensor in sensores:
        valor = sensores[sensor]()
        return f"DADO:{sensor}:{valor}"
    else:
        return f"ERRO:SENSOR_DESCONHECIDO:{sensor}"

# ------------------------------------------------------------
# Mensagem inicial
# ------------------------------------------------------------

print("=" * 40)
print("  Passo 9 — Checksum XOR (Periférica)")
print("=" * 40)
print(f"  UART{UART_ID} | TX:GP{TX_PIN} | RX:GP{RX_PIN}")
print(f"  Baud rate  : {BAUD_RATE} bps")
print(f"  Formato    : PAYLOAD*XX\\n")
print(f"  Sensores   : {', '.join(sensores.keys())}")
print("  Aguardando frames...")
print("=" * 40)

# ------------------------------------------------------------
# Loop principal — máquina de estados + validação de checksum
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
            payload, valido = validar_frame(buffer)

            if not valido:
                # Frame corrompido — descarta sem processar
                invalidos += 1
                erro_frame = montar_frame("ERRO:CHECKSUM")
                uart.write(erro_frame + '\n')
                print(f"[INVÁLIDO #{invalidos}] '{buffer}' — checksum incorreto")
            else:
                # Frame íntegro — processa e responde
                payload_resp = processar(payload)
                frame_resp   = montar_frame(payload_resp)
                uart.write(frame_resp + '\n')
                atendidas += 1
                print(f"[{atendidas:03d}] '{payload}' → '{frame_resp}'")

            buffer, tempo_inicio = '', 0
            estado = 'IDLE'
