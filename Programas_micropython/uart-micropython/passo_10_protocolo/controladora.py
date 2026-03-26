# ============================================================
# Passo 10 — Mini-Protocolo Completo: CONTROLADORA
# ============================================================
# Compatível com: Raspberry Pi Pico e ESP32
# IDE: Thonny
#
# Este arquivo roda na placa CONTROLADORA.
# Arquivos necessários em AMBAS as placas: protocolo.py
#
# O que este programa faz:
#   Envia requisições à periférica usando o mini-protocolo
#   completo. Se receber NAK ou não receber resposta dentro
#   do timeout, retransmite automaticamente até o limite
#   de tentativas. Mantém estatísticas de sessão.
#
# Conexão física (mesma dos passos 7, 8 e 9):
#   TX (GP4) ──► RX (GP5)   |   RX (GP5) ◄── TX (GP4)   |   GND ── GND
# ============================================================

from machine import UART, Pin
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
# Parâmetros de operação
# ------------------------------------------------------------

INTERVALO_MS  = 4000              # Intervalo entre ciclos (ms)
TIMEOUT_MS    = 2000              # Timeout por tentativa (ms)
MAX_TENTATIVAS = proto.MAX_TENTATIVAS  # Importado do módulo

SENSORES = ['TEMP', 'LUM']

# ------------------------------------------------------------
# Inicialização
# ------------------------------------------------------------

uart = UART(UART_ID, baudrate=BAUD_RATE,
            tx=Pin(TX_PIN), rx=Pin(RX_PIN))

# Estatísticas de sessão
stats = {
    'enviados'      : 0,
    'confirmados'   : 0,
    'nak_recebidos' : 0,
    'timeouts'      : 0,
    'retransmissoes': 0,
}

# ------------------------------------------------------------
# Funções de comunicação
# ------------------------------------------------------------

def aguardar_frame():
    """
    Lê bytes da UART até encontrar um frame completo
    (de '$' até '#') ou até o timeout.
    Retorna a string do frame ou None se timeout.
    """
    buffer   = ''
    capturando = False
    t_inicio = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), t_inicio) < TIMEOUT_MS:
        if uart.any():
            char = uart.read(1).decode()

            if char == proto.SOF:
                buffer     = char      # Inicia captura no SOF
                capturando = True

            elif capturando:
                buffer += char
                if char == proto.EOF:  # Frame completo
                    return buffer
                if len(buffer) > proto.BUFFER_MAX:
                    buffer, capturando = '', False  # Frame muito longo

    return None                        # Timeout


def enviar_com_retransmissao(frame_req, sensor):
    """
    Envia um frame e aguarda ACK ou DAD da periférica.
    Retransmite automaticamente em caso de NAK ou timeout.

    Retorna (valor, tentativas) se sucesso, (None, tentativas) se falhou.
    """
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        if tentativa > 1:
            stats['retransmissoes'] += 1
            print(f"  ↺ Retransmissão {tentativa}/{MAX_TENTATIVAS}")

        uart.write(frame_req)
        stats['enviados'] += 1
        print(f"  → [{tentativa}] '{frame_req.strip()}'")

        frame_rec = aguardar_frame()

        if frame_rec is None:
            stats['timeouts'] += 1
            print(f"  ✗ Timeout na tentativa {tentativa}")
            continue                   # Tenta novamente

        resultado = proto.validar_frame(frame_rec)
        print(f"  ← '{frame_rec.strip()}'")

        if not resultado['ok']:
            print(f"  ✗ Frame inválido: {resultado['erro']}")
            continue

        tipo    = resultado['tipo']
        payload = resultado['payload']

        if tipo == proto.T_NAK:
            stats['nak_recebidos'] += 1
            print(f"  ✗ NAK recebido: '{payload}'")
            continue                   # Retransmite

        if tipo == proto.T_DAD:
            # Extrai valor do payload "SENSOR:VALOR"
            partes = payload.split(proto.SEP, 1)
            if len(partes) == 2:
                stats['confirmados'] += 1
                return partes[1], tentativa

        if tipo == proto.T_ERR:
            print(f"  ✗ Erro da periférica: '{payload}'")
            return None, tentativa

    return None, MAX_TENTATIVAS        # Esgotou as tentativas


# ------------------------------------------------------------
# Mensagem inicial
# ------------------------------------------------------------

print("=" * 44)
print("  Passo 10 — Mini-Protocolo (Controladora)")
print("=" * 44)
print(f"  UART{UART_ID} | TX:GP{TX_PIN} | RX:GP{RX_PIN} | {BAUD_RATE} bps")
print(f"  Timeout      : {TIMEOUT_MS} ms")
print(f"  Max tentativas: {MAX_TENTATIVAS}")
print(f"  Sensores     : {', '.join(SENSORES)}")
print(f"  Frame SOF='{proto.SOF}' EOF='{proto.EOF}' CSP='{proto.CSP}'")
print("=" * 44)
print()

# ------------------------------------------------------------
# Loop principal
# ------------------------------------------------------------

ciclo = 0

while True:
    ciclo += 1
    print(f"══ Ciclo {ciclo} {'═' * 32}")

    for sensor in SENSORES:
        print(f"  Sensor: {sensor}")
        frame = proto.frame_req(sensor)
        valor, tentativas = enviar_com_retransmissao(frame, sensor)

        if valor is not None:
            print(f"  ✓ [{sensor}] = {valor}  (em {tentativas} tentativa(s))")
        else:
            print(f"  ✗ [{sensor}] = FALHA após {MAX_TENTATIVAS} tentativas")

    # Estatísticas a cada 5 ciclos
    if ciclo % 5 == 0:
        total = stats['enviados'] if stats['enviados'] > 0 else 1
        taxa  = stats['confirmados'] / total * 100
        print(f"\n  ── Estatísticas ──────────────────────")
        for chave, valor in stats.items():
            print(f"    {chave:<16}: {valor}")
        print(f"    {'taxa OK':<16}: {taxa:.1f}%")

    print()
    time.sleep_ms(INTERVALO_MS)
