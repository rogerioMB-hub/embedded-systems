# ============================================================
# protocolo.py — Módulo compartilhado do mini-protocolo UART
# ============================================================
# Compatível com: Raspberry Pi Pico e ESP32
# IDE: Thonny
#
# Este módulo deve ser gravado em AMBAS as placas.
# Ele centraliza toda a lógica do protocolo, garantindo
# que controladora e periférica falem exatamente a mesma
# linguagem.
#
# Estrutura do frame:
#
#   $ TIPO : PAYLOAD * XX #
#   │  │      │        │  │
#   │  │      │        │  └── EOF  — fim de frame (fixo: '#')
#   │  │      │        └───── Checksum XOR em hex (2 dígitos)
#   │  │      └────────────── Payload — conteúdo da mensagem
#   │  └───────────────────── Tipo — identifica a mensagem
#   └──────────────────────── SOF  — início de frame (fixo: '$')
#
# Tipos de frame definidos:
#   REQ  → Requisição de dado (controladora → periférica)
#   DAD  → Dado de resposta   (periférica → controladora)
#   ACK  → Confirmação        (qualquer direção)
#   NAK  → Rejeição           (qualquer direção)
#   ERR  → Erro descritivo    (qualquer direção)
#
# Exemplos de frames completos:
#   "$REQ:TEMP*XX#"
#   "$DAD:TEMP:24.3*XX#"
#   "$ACK:REQ:TEMP*XX#"
#   "$NAK:CHECKSUM*XX#"
#   "$ERR:SENSOR_DESCONHECIDO*XX#"
#
# Onde XX é o checksum XOR em hexadecimal.
# ============================================================

# ------------------------------------------------------------
# Constantes do protocolo
# ------------------------------------------------------------

SOF = '$'    # Start of Frame
EOF = '#'    # End of Frame
SEP = ':'    # Separador de campos
CSP = '*'    # Separador de checksum

# Tipos de frame
T_REQ = 'REQ'    # Requisição
T_DAD = 'DAD'    # Dado
T_ACK = 'ACK'    # Confirmação (acknowledge)
T_NAK = 'NAK'    # Rejeição    (negative acknowledge)
T_ERR = 'ERR'    # Erro

TIPOS_VALIDOS = (T_REQ, T_DAD, T_ACK, T_NAK, T_ERR)

# Limites
BUFFER_MAX   = 80    # Tamanho máximo do frame completo
MAX_TENTATIVAS = 3   # Tentativas de retransmissão

# ------------------------------------------------------------
# Funções de checksum
# ------------------------------------------------------------

def calcular_checksum(dados):
    """
    Calcula o checksum XOR de todos os bytes da string 'dados'.
    Retorna inteiro 0–255.
    """
    resultado = 0
    for byte in dados.encode():
        resultado ^= byte
    return resultado


# ------------------------------------------------------------
# Funções de montagem e validação de frame
# ------------------------------------------------------------

def montar_frame(tipo, payload):
    """
    Monta um frame completo no formato: $TIPO:PAYLOAD*XX#
    O checksum cobre o conteúdo entre SOF e CSP: "TIPO:PAYLOAD"
    """
    conteudo = f"{tipo}{SEP}{payload}"
    cs       = calcular_checksum(conteudo)
    return f"{SOF}{conteudo}{CSP}{cs:02X}{EOF}"


def validar_frame(frame):
    """
    Valida e desempacota um frame recebido.

    Retorna um dicionário com:
      {'ok': True,  'tipo': ..., 'payload': ...}  — frame íntegro
      {'ok': False, 'erro': ...}                  — frame inválido

    Verificações realizadas (em ordem):
      1. Presença de SOF e EOF
      2. Presença do separador de checksum
      3. Tamanho do campo checksum (exatamente 2 hex digits)
      4. Validade dos hex digits
      5. Correspondência do checksum calculado vs recebido
      6. Tipo de frame reconhecido
    """
    # 1. SOF e EOF
    if not (frame.startswith(SOF) and frame.endswith(EOF)):
        return {'ok': False, 'erro': 'SOF/EOF ausente'}

    interior = frame[1:-1]          # Remove '$' e '#'

    # 2. Separador de checksum
    if CSP not in interior:
        return {'ok': False, 'erro': 'Separador de checksum ausente'}

    partes   = interior.rsplit(CSP, 1)
    conteudo = partes[0]            # "TIPO:PAYLOAD"
    cs_rec   = partes[1]            # "XX"

    # 3. Tamanho do checksum
    if len(cs_rec) != 2:
        return {'ok': False, 'erro': 'Checksum malformado'}

    # 4. Validade dos hex digits
    try:
        cs_recebido  = int(cs_rec, 16)
        cs_calculado = calcular_checksum(conteudo)
    except ValueError:
        return {'ok': False, 'erro': 'Checksum contém caracteres inválidos'}

    # 5. Comparação de checksum
    if cs_calculado != cs_recebido:
        return {'ok': False, 'erro': f'Checksum diverge: calc={cs_calculado:02X} rec={cs_rec}'}

    # 6. Tipo de frame
    if SEP not in conteudo:
        return {'ok': False, 'erro': 'Separador de tipo ausente'}

    partes2 = conteudo.split(SEP, 1)
    tipo    = partes2[0]
    payload = partes2[1]

    if tipo not in TIPOS_VALIDOS:
        return {'ok': False, 'erro': f'Tipo desconhecido: {tipo}'}

    return {'ok': True, 'tipo': tipo, 'payload': payload}


# ------------------------------------------------------------
# Frames prontos (atalhos para os mais usados)
# ------------------------------------------------------------

def frame_ack(referencia):
    """Monta um ACK referenciando o payload recebido."""
    return montar_frame(T_ACK, referencia)


def frame_nak(motivo):
    """Monta um NAK com o motivo da rejeição."""
    return montar_frame(T_NAK, motivo)


def frame_err(descricao):
    """Monta um ERR com descrição do problema."""
    return montar_frame(T_ERR, descricao)


def frame_req(sensor):
    """Monta uma requisição de sensor."""
    return montar_frame(T_REQ, sensor)


def frame_dad(sensor, valor):
    """Monta uma resposta de dado."""
    return montar_frame(T_DAD, f"{sensor}{SEP}{valor}")
