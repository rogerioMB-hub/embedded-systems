# ============================================================
# Passo 7 — Loopback entre Duas Placas: TRANSMISSORA
# ============================================================
# Compatível com: Raspberry Pi Pico e ESP32
# IDE: Thonny
#
# Este arquivo roda na placa TRANSMISSORA.
# O par é: transmissora.py  ←→  receptora.py
#
# O que este programa faz:
#   Envia mensagens numeradas pela UART a cada intervalo
#   definido e aguarda o eco da placa receptora. Compara
#   o que foi enviado com o que voltou e reporta se a
#   comunicação está íntegra.
#
# Conexão física entre as placas:
#
#   Placa A (transmissora)      Placa B (receptora)
#   ──────────────────────      ──────────────────
#        TX  ──────────────────►  RX
#        RX  ◄──────────────────  TX
#       GND  ────────────────── GND   ← OBRIGATÓRIO
#
#   ATENÇÃO: GND comum é obrigatório para a comunicação
#   funcionar. Sem ele, os níveis de tensão ficam flutuando
#   e os dados chegam corrompidos ou não chegam.
#
#   ATENÇÃO: Pico opera em 3,3 V. ESP32 também opera em 3,3 V.
#   Conexão direta Pico ↔ ESP32 é segura.
#   NUNCA conecte diretamente a um dispositivo 5 V sem
#   um conversor de nível lógico.
# ============================================================

from machine import UART, Pin
import time
import sys

# ------------------------------------------------------------
# Configuração da UART
# ------------------------------------------------------------

UART_ID   = 1        # Usar UART1 para não conflitar com o USB
BAUD_RATE = 9600

# Pinos para UART1:
#   Raspberry Pi Pico → TX: GP4  | RX: GP5
#   ESP32             → TX: GP10 | RX: GP9
#
# Ajuste conforme sua placa:
TX_PIN = 4
RX_PIN = 5

# ------------------------------------------------------------
# Parâmetros do teste de loopback
# ------------------------------------------------------------

INTERVALO_MS  = 2000   # Intervalo entre envios (ms)
TIMEOUT_ECO   = 1000   # Tempo máximo aguardando eco (ms)
TOTAL_ENVIOS  = 10     # Quantidade de mensagens a enviar
                       # Use 0 para rodar indefinidamente

# ------------------------------------------------------------
# Inicialização
# ------------------------------------------------------------

uart = UART(UART_ID, baudrate=BAUD_RATE,
            tx=Pin(TX_PIN), rx=Pin(RX_PIN))

# Contadores para estatísticas ao final
enviados  = 0
recebidos = 0
erros     = 0

# ------------------------------------------------------------
# Funções auxiliares
# ------------------------------------------------------------

def enviar_e_aguardar(mensagem):
    """
    Envia uma mensagem e aguarda o eco da placa receptora.
    Retorna True se o eco bater com o enviado, False caso contrário.
    """
    uart.write(mensagem + '\n')
    print(f"  Enviado : '{mensagem}'")

    # Aguarda o eco dentro do timeout
    eco        = ''
    t_inicio   = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), t_inicio) < TIMEOUT_ECO:
        if uart.any():
            byte = uart.read(1)
            char = byte.decode()
            if char == '\n':
                break              # Eco completo recebido
            eco += char

    if eco == mensagem:
        print(f"  Eco     : '{eco}' ✓")
        return True
    elif eco == '':
        print(f"  Eco     : (nenhum — timeout)")
        return False
    else:
        print(f"  Eco     : '{eco}' ✗ (diverge!)")
        return False

# ------------------------------------------------------------
# Mensagem inicial
# ------------------------------------------------------------

print("=" * 40)
print("  Passo 7 — Loopback UART (Transmissora)")
print("=" * 40)
print(f"  UART{UART_ID} | TX:GP{TX_PIN} | RX:GP{RX_PIN}")
print(f"  Baud rate : {BAUD_RATE} bps")
print(f"  Intervalo : {INTERVALO_MS} ms")
print(f"  Timeout   : {TIMEOUT_ECO} ms")
limite = str(TOTAL_ENVIOS) if TOTAL_ENVIOS > 0 else "∞"
print(f"  Envios    : {limite}")
print("=" * 40)
print()

# ------------------------------------------------------------
# Loop de teste
# ------------------------------------------------------------

contador = 0

while True:
    contador += 1
    mensagem  = f"MSG:{contador:03d}"   # Exemplo: "MSG:001"

    print(f"[{contador}]")
    ok = enviar_e_aguardar(mensagem)
    enviados += 1

    if ok:
        recebidos += 1
    else:
        erros += 1

    # Exibe estatísticas parciais a cada 5 envios
    if contador % 5 == 0:
        taxa = (recebidos / enviados) * 100
        print(f"  → Estatísticas: {recebidos}/{enviados} OK ({taxa:.0f}%)")

    # Encerra se atingiu o total definido
    if TOTAL_ENVIOS > 0 and contador >= TOTAL_ENVIOS:
        break

    time.sleep_ms(INTERVALO_MS)

# ------------------------------------------------------------
# Relatório final
# ------------------------------------------------------------

print()
print("=" * 40)
print("  Relatório final")
print("=" * 40)
print(f"  Enviados  : {enviados}")
print(f"  Recebidos : {recebidos}")
print(f"  Erros     : {erros}")
taxa = (recebidos / enviados) * 100 if enviados > 0 else 0
print(f"  Taxa OK   : {taxa:.1f}%")
print("=" * 40)
