# ============================================================
# Passo 8 — Modelo Controladora–Periférica: CONTROLADORA
# ============================================================
# Compatível com: Raspberry Pi Pico e ESP32
# IDE: Thonny
#
# Este arquivo roda na placa CONTROLADORA.
# O par é: controladora.py  ←→  periferica.py
#
# O que este programa faz:
#   Envia requisições periódicas à placa periférica pedindo
#   leituras de sensor. Aguarda a resposta, interpreta os
#   dados recebidos e os exibe no Shell com formatação.
#
# Protocolo usado (texto simples, terminado em '\n'):
#   Controladora envia : "REQ:SENSOR\n"
#   Periférica responde: "DADO:TEMP:23.4\n"  (exemplo)
#
# Conexão física (mesma do passo 7):
#
#   Controladora                  Periférica
#   ────────────                  ──────────
#   TX (GP4) ──────────────────► RX (GP5)
#   RX (GP5) ◄────────────────── TX (GP4)
#       GND ─────────────────── GND
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

INTERVALO_MS  = 3000  # Intervalo entre requisições (ms)
TIMEOUT_MS    = 2000  # Tempo máximo aguardando resposta (ms)
BUFFER_MAX    = 64    # Tamanho máximo do buffer de resposta

# Sensores que a controladora pode requisitar.
# A periférica deve reconhecer os mesmos nomes.
SENSORES = ['TEMP', 'LUM']

# ------------------------------------------------------------
# Inicialização
# ------------------------------------------------------------

uart = UART(UART_ID, baudrate=BAUD_RATE,
            tx=Pin(TX_PIN), rx=Pin(RX_PIN))

# ------------------------------------------------------------
# Funções auxiliares
# ------------------------------------------------------------

def aguardar_resposta():
    """
    Aguarda uma linha completa da periférica dentro do timeout.
    Retorna a string recebida (sem '\n') ou None se timeout.
    """
    buffer   = ''
    t_inicio = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), t_inicio) < TIMEOUT_MS:
        if uart.any():
            char = uart.read(1).decode()
            if char == '\n':
                return buffer          # Resposta completa
            elif char != '\r':
                if len(buffer) < BUFFER_MAX:
                    buffer += char

    return None                        # Timeout — sem resposta


def interpretar_resposta(resposta):
    """
    Interpreta a resposta da periférica no formato:
      DADO:SENSOR:VALOR
    Retorna (sensor, valor) ou (None, None) se inválido.
    """
    if not resposta or ':' not in resposta:
        return None, None

    partes = resposta.split(':')

    # Formato esperado: 3 partes — DADO, SENSOR, VALOR
    if len(partes) != 3 or partes[0] != 'DADO':
        return None, None

    return partes[1], partes[2]       # (sensor, valor)


def requisitar(sensor):
    """
    Envia uma requisição para o sensor indicado e retorna
    (sensor, valor) com o resultado, ou (sensor, None) se falhou.
    """
    mensagem = f"REQ:{sensor}"
    uart.write(mensagem + '\n')
    print(f"  → Requisição : '{mensagem}'")

    resposta = aguardar_resposta()

    if resposta is None:
        print(f"  ← Resposta   : (timeout)")
        return sensor, None

    print(f"  ← Resposta   : '{resposta}'")
    sensor_rec, valor = interpretar_resposta(resposta)

    if sensor_rec is None:
        print(f"  ← Formato inválido")
        return sensor, None

    return sensor_rec, valor

# ------------------------------------------------------------
# Mensagem inicial
# ------------------------------------------------------------

print("=" * 40)
print("  Passo 8 — Controladora–Periférica")
print("  Papel: CONTROLADORA")
print("=" * 40)
print(f"  UART{UART_ID} | TX:GP{TX_PIN} | RX:GP{RX_PIN}")
print(f"  Baud rate  : {BAUD_RATE} bps")
print(f"  Intervalo  : {INTERVALO_MS} ms")
print(f"  Timeout    : {TIMEOUT_MS} ms")
print(f"  Sensores   : {', '.join(SENSORES)}")
print("=" * 40)
print()

# ------------------------------------------------------------
# Loop principal — ciclo de requisições
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

    print()
    time.sleep_ms(INTERVALO_MS)
