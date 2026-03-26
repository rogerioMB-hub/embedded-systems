# Passo 10 — Mini-Protocolo Bidirecional Completo

## Objetivo

Reunir tudo que foi construído nos nove passos anteriores em um **mini-protocolo de comunicação completo**: frame estruturado com SOF e EOF, tipo de mensagem, payload, checksum XOR, ACK/NAK e retransmissão automática. Compatível com qualquer combinação de Pico e ESP32.

---

## Visão geral do protocolo

```
  Controladora                          Periférica
  ────────────                          ──────────

  $REQ:TEMP*XX#  ──────────────────►
                 ◄──────────────────  $DAD:TEMP:24.3*XX#

  $REQ:LUM*XX#   ──────────────────►
                 ◄──────────────────  $DAD:LUM:67.2*XX#

  (frame corrompido) ──────────────►
                 ◄──────────────────  $NAK:CHECKSUM*XX#

  $REQ:LUM*XX#   ──────────────────►  (retransmissão)
                 ◄──────────────────  $DAD:LUM:67.2*XX#
```

---

## Estrutura do frame

```
$ TIPO : PAYLOAD * XX #
│  │       │      │  │
│  │       │      │  └── EOF — fim de frame (fixo: '#')
│  │       │      └───── Checksum XOR em hex (2 dígitos)
│  │       └──────────── Payload — conteúdo da mensagem
│  └──────────────────── Tipo — identifica a mensagem
└─────────────────────── SOF — início de frame (fixo: '$')
```

O checksum cobre o campo `TIPO:PAYLOAD` — tudo entre `$` e `*`.

### Tipos de frame

| Tipo | Direção | Significado |
|------|---------|-------------|
| `REQ` | Controladora → Periférica | Requisição de leitura de sensor |
| `DAD` | Periférica → Controladora | Dado de resposta |
| `ACK` | Qualquer | Confirmação genérica |
| `NAK` | Qualquer | Rejeição — solicita retransmissão |
| `ERR` | Qualquer | Erro descritivo |

### Exemplos de frames completos

| Situação | Frame |
|----------|-------|
| Requisição de temperatura | `$REQ:TEMP*70#` |
| Resposta com dado | `$DAD:TEMP:24.3*2E#` |
| Frame corrompido detectado | `$NAK:CHECKSUM*XX#` |
| Sensor desconhecido | `$ERR:SENSOR_DESCONHECIDO:XYZ*XX#` |

---

## Fluxo de retransmissão

```
Controladora envia REQ
        │
        ▼
  Aguarda resposta (timeout)
        │
        ├── DAD recebido e válido ──► Sucesso ✓
        │
        ├── NAK recebido ───────────► Retransmite (até MAX_TENTATIVAS)
        │
        ├── Frame inválido ──────────► Retransmite (até MAX_TENTATIVAS)
        │
        └── Timeout ────────────────► Retransmite (até MAX_TENTATIVAS)
                                              │
                                     Esgotou tentativas?
                                              │
                                         Registra falha
```

---

## Detecção de SOF na periférica

Uma diferença importante em relação aos passos anteriores: a máquina de estados da periférica agora **só inicia a captura quando recebe o SOF (`$`)**. Bytes recebidos fora do contexto de um frame (ruído, resíduos de transmissões anteriores) são silenciosamente ignorados.

```python
if estado == 'IDLE':
    if char == proto.SOF:   # Só o '$' inicia a captura
        buffer = char
        estado = 'RECEBENDO'
```

Isso é mais robusto do que iniciar no primeiro byte válido qualquer — o SOF funciona como âncora de sincronização.

---

## Arquivos

```
passo_10_protocolo/
├── protocolo.py    → grava em AMBAS as placas
├── controladora.py → grava na Placa A
└── periferica.py   → grava na Placa B
```

> **Atenção:** `protocolo.py` deve ser gravado nas **duas placas** antes de executar qualquer um dos outros arquivos. No Thonny, use *Arquivo → Salvar cópia em → MicroPython device*.

---

## O módulo `protocolo.py`

Toda a lógica do protocolo vive em um único módulo compartilhado. Isso garante que ambas as placas falem exatamente a mesma linguagem — sem duplicação de código.

```python
import protocolo as proto

# Montar frames
proto.frame_req('TEMP')          # "$REQ:TEMP*XX#"
proto.frame_dad('TEMP', '24.3') # "$DAD:TEMP:24.3*XX#"
proto.frame_nak('CHECKSUM')      # "$NAK:CHECKSUM*XX#"

# Validar frame recebido
resultado = proto.validar_frame(frame)
if resultado['ok']:
    tipo    = resultado['tipo']    # 'REQ', 'DAD', etc.
    payload = resultado['payload'] # conteúdo após o tipo
```

---

## Conexão física

```
  Placa A — controladora          Placa B — periférica
       TX (GP4) ──────────────────► RX (GP5)
       RX (GP5) ◄────────────────── TX (GP4)
           GND ─────────────────── GND
```

Compatível com qualquer combinação: Pico↔Pico, ESP32↔ESP32, Pico↔ESP32.

---

## Como executar

1. Grave `protocolo.py` na **Placa A** e na **Placa B**
2. Grave `periferica.py` na Placa B e execute (▶)
3. Grave `controladora.py` na Placa A e execute (▶)

### Shell da Placa A (controladora) — operação normal

```
══ Ciclo 1 ════════════════════════════
  Sensor: TEMP
  → [1] '$REQ:TEMP*70#'
  ← '$DAD:TEMP:24.3*2E#'
  ✓ [TEMP] = 24.3  (em 1 tentativa(s))
  Sensor: LUM
  → [1] '$REQ:LUM*6B#'
  ← '$DAD:LUM:0.1*1F#'
  ✓ [LUM] = 0.1  (em 1 tentativa(s))
```

### Shell da Placa A — retransmissão em ação

```
  Sensor: TEMP
  → [1] '$REQ:TEMP*70#'
  ✗ Timeout na tentativa 1
  ↺ Retransmissão 2/3
  → [2] '$REQ:TEMP*70#'
  ← '$DAD:TEMP:24.4*2F#'
  ✓ [TEMP] = 24.4  (em 2 tentativa(s))
```

### Shell da Placa B (periférica)

```
[DAD #001] '$REQ:TEMP*70#' → '$DAD:TEMP:24.3*2E#'
[DAD #002] '$REQ:LUM*6B#'  → '$DAD:LUM:0.1*1F#'
```

---

## O que foi construído ao longo dos 10 passos

| Passo | Elemento adicionado | Presente neste passo |
|-------|--------------------|-----------------------|
| 1 | Comunicação UART básica | ✓ |
| 2 | Decisão baseada em dado recebido | ✓ |
| 3 | Dicionário de despacho | ✓ |
| 4 | Buffer + terminador + parsing | ✓ |
| 5 | Máquina de estados | ✓ |
| 6 | Timeout + limite de buffer | ✓ |
| 7 | Comunicação placa↔placa | ✓ |
| 8 | Modelo controladora–periférica | ✓ |
| 9 | Checksum XOR | ✓ |
| 10 | SOF/EOF + tipos + ACK/NAK + retransmissão | ✓ |

---

## Conceitos abordados

- Módulo compartilhado: código único para ambos os lados do protocolo
- SOF/EOF como âncoras de sincronização
- Tipos de frame: semântica formal de mensagens
- Retransmissão automática com limite de tentativas
- NAK como mecanismo de solicitação de reenvio
- Estatísticas de sessão: taxa de sucesso, retransmissões, timeouts

---

## Experimente

- Desconecte e reconecte o fio TX no meio de uma transmissão — o sistema se recupera sozinho?
- Adicione um campo de número de sequência ao payload (`$REQ:001:TEMP*XX#`) para rastrear frames perdidos
- Implemente o lado oposto: a periférica envia dados espontaneamente sem ser requisitada, e a controladora envia ACK
- Substitua o checksum XOR por CRC-16 usando a biblioteca `ustruct` do MicroPython

---

## Parabéns!

Você chegou ao final do repositório tendo construído, passo a passo, um protocolo de comunicação serial completo — do eco mais simples até retransmissão automática com integridade verificada. Os mesmos princípios aplicados aqui estão presentes em protocolos industriais como Modbus, NMEA 0183 e muitos outros usados em sistemas embarcados reais.
