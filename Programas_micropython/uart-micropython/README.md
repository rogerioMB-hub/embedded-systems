# UART com MicroPython — Do Eco ao Protocolo

Repositório didático de comunicação serial UART com MicroPython, desenvolvido para o Raspberry Pi Pico e o ESP32. O conteúdo é organizado em 10 passos progressivos — cada um introduz exatamente um conceito novo, sempre partindo do que já foi aprendido.

Ao final, o aluno terá construído, passo a passo, um mini-protocolo de comunicação bidirecional completo com integridade verificada e retransmissão automática.

---

## Pré-requisitos

| Item | Detalhe |
|------|---------|
| Hardware | Raspberry Pi Pico **ou** ESP32 (um ou dois dispositivos) |
| Firmware | MicroPython instalado na placa |
| IDE | [Thonny](https://thonny.org) — gratuito, multiplataforma |
| Conhecimento | Python básico: variáveis, `if/else`, `while`, funções |

---

## Estrutura do repositório

```
uart-micropython/
│
├── README.md                          ← este arquivo
│
├── passo_01_eco_serial/
│   ├── eco_serial.py
│   └── README.md
│
├── passo_02_led_uart/
│   ├── led_uart.py
│   └── README.md
│
├── passo_03_dicionario/
│   ├── dicionario_uart.py
│   └── README.md
│
├── passo_04_parsing/
│   ├── parsing_uart.py
│   └── README.md
│
├── passo_05_maquina_estados/
│   ├── maquina_estados.py
│   └── README.md
│
├── passo_06_buffer_timeout/
│   ├── buffer_timeout.py
│   └── README.md
│
├── passo_07_loopback/
│   ├── transmissora.py
│   ├── receptora.py
│   └── README.md
│
├── passo_08_controlador_periferico/
│   ├── controladora.py
│   ├── periferica.py
│   └── README.md
│
├── passo_09_checksum/
│   ├── controladora.py
│   ├── periferica.py
│   └── README.md
│
└── passo_10_protocolo/
    ├── protocolo.py                   ← gravar em AMBAS as placas
    ├── controladora.py
    ├── periferica.py
    └── README.md
```

---

## Roteiro de aprendizado

O repositório é dividido em quatro fases. Cada fase constrói sobre a anterior — siga a ordem dos passos.

### Fase 1 — PC ↔ Placa via Shell do Thonny
*Um dispositivo, sem fios extras, feedback imediato.*

| Passo | Arquivo | O que é introduzido |
|-------|---------|---------------------|
| [1](passo_01_eco_serial/README.md) | `eco_serial.py` | UART básica — `uart.any()`, `read()`, `write()` |
| [2](passo_02_led_uart/README.md) | `led_uart.py` | Decisão por char — `if/elif/else`, controle de LED |
| [3](passo_03_dicionario/README.md) | `dicionario_uart.py` | Dicionário — `in`, despacho por chave |

### Fase 2 — Estrutura e robustez
*Ainda um dispositivo, mas com comunicação estruturada e à prova de falhas.*

| Passo | Arquivo | O que é introduzido |
|-------|---------|---------------------|
| [4](passo_04_parsing/README.md) | `parsing_uart.py` | Buffer, terminador `'\n'`, parsing de comandos |
| [5](passo_05_maquina_estados/README.md) | `maquina_estados.py` | Máquina de estados — IDLE / RECEBENDO / PROCESSANDO |
| [6](passo_06_buffer_timeout/README.md) | `buffer_timeout.py` | Timeout, limite de buffer, `ticks_ms()` |

### Fase 3 — Placa ↔ Placa
*Dois dispositivos, fiação TX/RX cruzada, comunicação de hardware real.*

| Passo | Arquivos | O que é introduzido |
|-------|----------|---------------------|
| [7](passo_07_loopback/README.md) | `transmissora.py` + `receptora.py` | Loopback físico, GND comum, estatísticas |
| [8](passo_08_controlador_periferico/README.md) | `controladora.py` + `periferica.py` | Modelo controladora–periférica, leitura de ADC |
| [9](passo_09_checksum/README.md) | `controladora.py` + `periferica.py` | Checksum XOR, detecção de corrupção de dados |

### Fase 4 — Protocolo completo
*Tudo junto: frame estruturado, ACK/NAK e retransmissão automática.*

| Passo | Arquivos | O que é introduzido |
|-------|----------|---------------------|
| [10](passo_10_protocolo/README.md) | `protocolo.py` + `controladora.py` + `periferica.py` | SOF/EOF, tipos de frame, retransmissão, módulo compartilhado |

---

## Hardware necessário por fase

| Fase | Placas | Fios | Outros |
|------|--------|------|--------|
| 1 e 2 | 1 | Nenhum (opcional: 1 fio para loopback) | LED externo no passo 2 (opcional — LED onboard disponível) |
| 3 e 4 | 2 | TX→RX, RX→TX, GND (3 fios) | Nenhum — sensores internos são usados |

---

## Diagrama de conexão (fases 3 e 4)

```
  Placa A                           Placa B
  ───────                           ───────
  TX (GP4) ───────────────────────► RX (GP5)
  RX (GP5) ◄─────────────────────── TX (GP4)
      GND ────────────────────────── GND

  Pinos para UART1:
    Raspberry Pi Pico → TX: GP4  | RX: GP5
    ESP32 DevKit v1   → TX: GP10 | RX: GP9
```

> **Tensão:** Pico e ESP32 operam em 3,3 V — conexão direta entre eles é segura. Nunca conecte diretamente a dispositivos 5 V sem conversor de nível lógico.

> **GND comum é obrigatório.** Sem ele os dados chegam corrompidos ou não chegam.

---

## Convenções adotadas em todos os programas

| Convenção | Escolha |
|-----------|---------|
| Idioma dos comentários | Português |
| Configurações | Constantes no topo do arquivo, nomeadas em maiúsculas |
| UART padrão (fases 1–2) | UART0, pinos padrão da placa |
| UART padrão (fases 3–4) | UART1 (evita conflito com USB/Thonny) |
| Baud rate padrão | 9600 bps |
| Terminador de mensagem | `'\n'` |
| Checksum | XOR byte a byte, 2 dígitos hex maiúsculos |
| Loop principal | Não bloqueante — `if uart.any()` em vez de `while uart.any()` |

---

## Como usar o Thonny com duas placas simultaneamente

A partir do passo 7 são necessárias duas instâncias do Thonny abertas ao mesmo tempo — uma para cada placa.

1. Abra a primeira instância normalmente
2. Abra a segunda instância:
   - **Windows:** abra um segundo Thonny pelo menu Iniciar
   - **Linux/macOS:** execute `thonny &` em um segundo terminal
3. Em cada instância, selecione a porta correta em *Ferramentas → Opções → Interpretador*
4. Execute sempre a **periférica primeiro**, depois a controladora

---

## Referência rápida de MicroPython — UART

```python
from machine import UART, Pin

# Inicialização básica
uart = UART(0, baudrate=9600)

# Inicialização com pinos explícitos
uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

# Verificar se há dados disponíveis
uart.any()           # Retorna número de bytes disponíveis

# Ler bytes
uart.read(1)         # Lê 1 byte — retorna bytes
uart.read(n)         # Lê até n bytes

# Escrever
uart.write(b'texto') # Aceita bytes
uart.write('texto')  # Aceita string (MicroPython converte)

# Medição de tempo (sem overflow)
import time
t = time.ticks_ms()
decorrido = time.ticks_diff(time.ticks_ms(), t)
```

---

## Conceitos abordados ao longo do repositório

- Comunicação serial assíncrona (UART): TX, RX, baud rate
- Leitura não bloqueante com `uart.any()`
- Controle de periféricos: LED, ADC
- Dicionários Python como tabelas de despacho
- Buffer de recepção e terminador de mensagem
- Máquina de estados finitos (FSM)
- Timeout e proteção de memória em embarcados
- Conexão física entre placas: fiação, tensão, GND
- Modelo controladora–periférica
- Checksum XOR para detecção de erros
- Frame estruturado: SOF, tipo, payload, checksum, EOF
- ACK/NAK e retransmissão automática
- Módulo compartilhado como contrato de protocolo

---

## Relação com protocolos do mundo real

Os conceitos deste repositório aparecem diretamente em protocolos industriais e embarcados amplamente usados:

| Conceito aprendido | Onde aparece |
|--------------------|-------------|
| Frame com SOF/EOF | HDLC, PPP, Modbus RTU |
| Checksum / CRC | Modbus, CAN bus, NMEA 0183 |
| ACK / NAK | Modbus, XMODEM, HTTP/1.1 |
| Controladora–periférica | Modbus, I²C, SPI |
| Máquina de estados | Toda implementação de protocolo profissional |

---

## Licença

MIT — livre para uso educacional e comercial com atribuição.
