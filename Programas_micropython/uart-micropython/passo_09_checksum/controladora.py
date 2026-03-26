# ============================================================
# Passo 9 — Frame com Checksum XOR: CONTROLADORA
# ============================================================
# Compatível com: Raspberry Pi Pico e ESP32
# IDE: Thonny
#
# Este arquivo roda na placa CONTROLADORA.
# O par é: controladora.py  ←→  periferica.py
#
# O que este programa faz:
#   Evolui o protocolo do passo 8 adicionando um checksum
#   XOR ao final de cada frame. O receptor calcula o checksum
#   dos dados recebidos e compara com o que chegou — se
#   divergirem, o frame é descartado.
#
# Formato do frame (texto, terminado em '\n'):
#   PAYLOAD*XX\n
#
#   Onde:
#     PAYLOAD → conteúdo da mensagem (ex: "REQ:TEMP")
#     *       → separador fixo entre payload e checksum
#     XX      → checksum XOR em hexadecimal (2 dígitos)
#     \n      → terminador de frame
#
#   Exemplos:
#     "REQ:TEMP*4A\n"
#     "DADO:TEMP:24.3*7F\n"
#
# Por que XOR?
#   O XOR byte a byte é simples, rápido e detecta qualquer
#   erro em bit único — suficiente para demonstrar o conceito.
#   Protocolos industriais usam CRC (mais robusto), mas o
#   princípio é o mesmo: ambos os lados calculam independente-
#   mente e comparam o resultado.
# ============================================================

from machine import UART, Pin
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
# Parâmetros de operação
# ------------------------------------------------------------

INTERVALO_MS = 3000  # Intervalo entre requisições (ms)
TIMEOUT_MS   = 2000  # Tempo máximo aguardando resposta (ms)
BUFFER_MAX   = 64    # Tamanho máximo do buffer

SENSORES = ['TEMP', 'LUM']

# ------------------------------------------------------------
# Inicialização
# ------------------------------------------------------------

uart = UART(UART_ID, baudrate=BAUD_RATE,
            tx=Pin(TX_PIN), rx=Pin(RX_PIN))

# Contadores de diagnóstico
enviados  = 0
recebidos = 0
invalidos = 0

# ------------------------------------------------------------
# Funções de checksum
# ------------------------------------------------------------

def calcular_checksum(payload):
    """
    Calcula o checksum XOR de todos os bytes do payload.

    O XOR acumula cada byte sobre um resultado inicial zero:
      checksum = b0 ^ b1 ^ b2 ^ ... ^ bN

    Propriedade útil: se qualquer byte for alterado,
    o checksum resultante será diferente.

    Retorna o valor inteiro (0–255).
    """
    resultado = 0
    for byte in payload.encode():   # Converte string para bytes
        resultado ^= byte           # XOR acumulado
    return resultado


def montar_frame(payload):
    """
    Monta o frame completo: PAYLOAD*XX
    O checksum é representado em hexadecimal com 2 dígitos.
    """
    cs = calcular_checksum(payload)
    return f"{payload}*{cs:02X}"    # Ex: "REQ:TEMP*4A"


def validar_frame(frame):
    """
    Valida um frame recebido no formato PAYLOAD*XX.
    Retorna (payload, True) se válido, (None, False) se inválido.
    """
    if '*' not in frame:
        return None, False          # Sem separador — frame malformado

    partes   = frame.rsplit('*', 1) # Divide no ÚLTIMO '*'
    payload  = partes[0]
    cs_rec   = partes[1]

    # Verifica se o campo checksum tem exatamente 2 hex digits
    if len(cs_rec) != 2:
        return None, False

    try:
        cs_calculado = calcular_checksum(payload)
        cs_recebido  = int(cs_rec, 16)   # Converte hex para inteiro
    except ValueError:
        return None, False               # Caracteres inválidos no checksum

    if cs_calculado == cs_recebido:
        return payload, True             # Frame íntegro
    else:
        return payload, False            # Checksum diverge — dados corrompidos


# ------------------------------------------------------------
# Funções de comunicação
# ------------------------------------------------------------

def aguardar_resposta():
    """
    Aguarda uma linha completa dentro do timeout.
    Retorna a string recebida (sem '\n') ou None se timeout.
    """
    buffer   = ''
    t_inicio = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), t_inicio) < TIMEOUT_MS:
        if uart.any():
            char = uart.read(1).decode()
            if char == '\n':
                return buffer
            elif char != '\r':
                if len(buffer) < BUFFER_MAX:
                    buffer += char

    return None


def requisitar(sensor):
    """
    Monta e envia uma requisição com checksum.
    Aguarda resposta, valida o checksum e retorna o valor.
    """
    global enviados, recebidos, invalidos

    payload = f"REQ:{sensor}"
    frame   = montar_frame(payload)

    uart.write(frame + '\n')
    enviados += 1
    print(f"  → Enviado  : '{frame}'")

    resposta = aguardar_resposta()

    if resposta is None:
        print(f"  ← Resposta : (timeout)")
        return sensor, None

    print(f"  ← Recebido : '{resposta}'")

    payload_rec, valido = validar_frame(resposta)

    if not valido:
        invalidos += 1
        print(f"  ✗ Checksum inválido — frame descartado")
        return sensor, None

    recebidos += 1

    # Interpreta o payload validado: DADO:SENSOR:VALOR
    partes = payload_rec.split(':')
    if len(partes) == 3 and partes[0] == 'DADO':
        return partes[1], partes[2]

    return sensor, None

# ------------------------------------------------------------
# Mensagem inicial
# ------------------------------------------------------------

print("=" * 40)
print("  Passo 9 — Checksum XOR (Controladora)")
print("=" * 40)
print(f"  UART{UART_ID} | TX:GP{TX_PIN} | RX:GP{RX_PIN}")
print(f"  Baud rate  : {BAUD_RATE} bps")
print(f"  Formato    : PAYLOAD*XX\\n")
print(f"  Sensores   : {', '.join(SENSORES)}")
print("=" * 40)
print()

# ------------------------------------------------------------
# Loop principal
# ------------------------------------------------------------

ciclo = 0

while True:
    ciclo += 1
    print(f"── Ciclo {ciclo} ──────────────────────────")

    for sensor in SENSORES:
        nome, valor = requisitar(sensor)

        if valor is not None:
            print(f"  [{nome}] = {valor}")
        else:
            print(f"  [{nome}] = FALHA")

    # Estatísticas a cada 5 ciclos
    if ciclo % 5 == 0:
        total = enviados if enviados > 0 else 1
        print(f"\n  Estatísticas:")
        print(f"    Enviados  : {enviados}")
        print(f"    Válidos   : {recebidos}")
        print(f"    Inválidos : {invalidos}")
        print(f"    Taxa OK   : {recebidos/total*100:.1f}%")

    print()
    time.sleep_ms(INTERVALO_MS)
