# ============================================================
# Passo 10 — Mini-Protocolo Completo: PERIFÉRICA
# ============================================================
# Compatível com: Raspberry Pi Pico e ESP32
# IDE: Thonny
#
# Este arquivo roda na placa PERIFÉRICA.
# Arquivos necessários em AMBAS as placas: protocolo.py
#
# O que este programa faz:
#   Aguarda frames da controladora, valida checksum e tipo,
#   executa a leitura do sensor requisitado e responde com
#   um frame DAD protegido. Se o frame recebido for inválido,
#   responde com NAK para acionar a retransmissão.
# ============================================================

from machine import UART, Pin, ADC
import time
import protocolo as proto

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

# ------------------------------------------------------------
# Inicialização
# ------------------------------------------------------------

uart = UART(UART_ID, baudrate=BAUD_RATE,
            tx=Pin(TX_PIN), rx=Pin(RX_PIN))

ADC_TEMP = ADC(4)    # Sensor interno — Pico
ADC_LUM  = ADC(26)   # Pino externo  — Pico GP26

# Variáveis da máquina de estados
estado       = 'IDLE'
buffer       = ''
tempo_inicio = 0

# Estatísticas
atendidas = 0
naks      = 0

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
# Função de processamento de requisição
# ------------------------------------------------------------

def processar_req(payload):
    """
    Processa um payload do tipo REQ.
    Retorna o frame de resposta completo (DAD, NAK ou ERR).
    """
    sensor = payload.strip().upper()

    if sensor in sensores:
        valor = sensores[sensor]()
        return proto.frame_dad(sensor, valor)
    else:
        return proto.frame_err(f"SENSOR_DESCONHECIDO:{sensor}")

# ------------------------------------------------------------
# Mensagem inicial
# ------------------------------------------------------------

print("=" * 44)
print("  Passo 10 — Mini-Protocolo (Periférica)")
print("=" * 44)
print(f"  UART{UART_ID} | TX:GP{TX_PIN} | RX:GP{RX_PIN} | {BAUD_RATE} bps")
print(f"  Timeout   : {TIMEOUT_MS} ms")
print(f"  Sensores  : {', '.join(sensores.keys())}")
print(f"  Frame SOF='{proto.SOF}' EOF='{proto.EOF}' CSP='{proto.CSP}'")
print("  Aguardando frames...")
print("=" * 44)

# ------------------------------------------------------------
# Loop principal
# ------------------------------------------------------------

while True:

    # Verificação de timeout
    if estado == 'RECEBENDO':
        decorrido = time.ticks_diff(time.ticks_ms(), tempo_inicio)
        if decorrido >= TIMEOUT_MS:
            print(f"[TIMEOUT] buffer descartado: '{buffer}'")
            estado, buffer, tempo_inicio = 'IDLE', '', 0

    if uart.any():
        char = uart.read(1).decode()

        # IDLE — aguarda SOF
        if estado == 'IDLE':
            if char == proto.SOF:          # Só inicia no SOF
                buffer       = char
                tempo_inicio = time.ticks_ms()
                estado       = 'RECEBENDO'

        # RECEBENDO — acumula até EOF
        elif estado == 'RECEBENDO':
            buffer += char

            if char == proto.EOF:          # Frame completo
                estado = 'PROCESSANDO'

            elif len(buffer) > proto.BUFFER_MAX:
                naks += 1
                nak = proto.frame_nak('FRAME_MUITO_LONGO')
                uart.write(nak)
                print(f"[NAK] frame muito longo — descartado")
                estado, buffer, tempo_inicio = 'IDLE', '', 0

        # PROCESSANDO — valida e responde
        if estado == 'PROCESSANDO':
            resultado = proto.validar_frame(buffer)

            if not resultado['ok']:
                # Frame inválido → NAK para acionar retransmissão
                naks += 1
                nak = proto.frame_nak(resultado['erro'][:20])
                uart.write(nak)
                print(f"[NAK #{naks}] '{buffer}' → {resultado['erro']}")

            elif resultado['tipo'] == proto.T_REQ:
                # Requisição válida → processa e responde
                resposta = processar_req(resultado['payload'])
                uart.write(resposta)
                atendidas += 1
                print(f"[DAD #{atendidas:03d}] '{buffer}' → '{resposta}'")

            else:
                # Tipo inesperado (ACK, DAD, ERR recebido pela periférica)
                err = proto.frame_err('TIPO_INESPERADO')
                uart.write(err)
                print(f"[ERR] tipo inesperado: {resultado['tipo']}")

            buffer, tempo_inicio = '', 0
            estado = 'IDLE'
