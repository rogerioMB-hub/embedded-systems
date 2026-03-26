# Passo 8 — Modelo Controladora–Periférica

## Objetivo

Dar papéis distintos às duas placas: a **controladora** inicia toda a comunicação fazendo requisições, e a **periférica** responde com leituras de sensor. É o primeiro modelo de comunicação com propósito real — e a base sobre a qual protocolos industriais como Modbus são construídos.

---

## O que muda em relação ao passo 7?

| | Passo 7 | Passo 8 |
|---|---|---|
| Papel das placas | Simétricas (transmissora / receptora) | Assimétricas (controladora / periférica) |
| Quem inicia | Transmissora | Sempre a controladora |
| Conteúdo da mensagem | Texto genérico numerado | Requisição estruturada de sensor |
| Resposta | Eco idêntico | Dado real lido do hardware |
| Protocolo | Nenhum (loopback puro) | `REQ:SENSOR` → `DADO:SENSOR:VALOR` |

---

## O protocolo deste passo

```
Controladora                        Periférica
────────────                        ──────────
  "REQ:TEMP\n"   ──────────────►
                 ◄──────────────  "DADO:TEMP:23.4\n"

  "REQ:LUM\n"    ──────────────►
                 ◄──────────────  "DADO:LUM:67.2\n"
```

### Formato das mensagens

| Direção | Formato | Exemplo |
|---------|---------|---------|
| Controladora → Periférica | `REQ:SENSOR\n` | `REQ:TEMP\n` |
| Periférica → Controladora | `DADO:SENSOR:VALOR\n` | `DADO:TEMP:23.4\n` |
| Periférica (erro) | `ERRO:MOTIVO\n` | `ERRO:SENSOR_DESCONHECIDO:XYZ\n` |

O separador `:` e o terminador `\n` são os mesmos do passo 4 — o protocolo cresce sobre a base já construída.

---

## Sensores implementados

| Nome | Origem | Hardware necessário |
|------|--------|---------------------|
| `TEMP` | Sensor interno do chip | Nenhum — disponível no Pico e ESP32 |
| `LUM` | Leitura ADC no pino GP26 | Nenhum (pino flutuando retorna valor próximo de 0) |

### Leitura de temperatura no Pico

```python
leitura = ADC(4).read_u16()          # Canal interno do Pico
tensao  = leitura * 3.3 / 65535
temp_c  = 27 - (tensao - 0.706) / 0.001721   # Fórmula do datasheet RP2040
```

### Adaptação para ESP32

```python
import esp32
return f"{esp32.raw_temperature():.1f}"
```

---

## Arquivos

```
passo_08_controlador_periferico/
├── controladora.py   → grava na Placa A
└── periferica.py     → grava na Placa B
```

---

## Conexão física

```
  Placa A — controladora          Placa B — periférica
  ──────────────────────          ────────────────────
       TX (GP4) ──────────────────► RX (GP5)
       RX (GP5) ◄────────────────── TX (GP4)
           GND ─────────────────── GND
```

---

## Como executar

1. Grave `periferica.py` na Placa B e execute (▶)
2. Grave `controladora.py` na Placa A e execute (▶)

### Shell da Placa B (periférica)

```
========================================
  Passo 8 — Controladora–Periférica
  Papel: PERIFÉRICA
========================================
  Sensores   : TEMP, LUM
  Aguardando requisições...
========================================
[001] 'REQ:TEMP' → 'DADO:TEMP:24.3'
[002] 'REQ:LUM'  → 'DADO:LUM:0.1'
[003] 'REQ:TEMP' → 'DADO:TEMP:24.4'
...
```

### Shell da Placa A (controladora)

```
── Ciclo 1 ──────────────────────────
  → Requisição : 'REQ:TEMP'
  ← Resposta   : 'DADO:TEMP:24.3'
  [TEMP] = 24.3
  → Requisição : 'REQ:LUM'
  ← Resposta   : 'DADO:LUM:0.1'
  [LUM] = 0.1

── Ciclo 2 ──────────────────────────
...
```

---

## Conceitos abordados

- Modelo controladora–periférica: comunicação iniciada sempre por um lado
- Protocolo com campo de tipo (`REQ` / `DADO` / `ERRO`)
- Leitura de ADC: conversão de valor bruto para grandeza física
- Sensor de temperatura interno do RP2040 (Pico) e ESP32
- Dicionário de sensores: separação entre registro e lógica de leitura
- Tratamento de sensor desconhecido com resposta de erro estruturada

---

## Experimente

- Adicione um sensor `VBAT` que retorna a tensão de alimentação via ADC interno
- Envie `REQ:XYZ` manualmente pelo Shell da controladora — observe a resposta `ERRO:SENSOR_DESCONHECIDO:XYZ`
- Modifique a controladora para exibir um alerta quando a temperatura ultrapassar 35 °C
- Adicione um LED na periférica que pisca a cada requisição atendida — feedback visual do tráfego

---

## Próximo passo

No [Passo 9](../passo_09_checksum/README.md) os frames ganham um **checksum**: um byte calculado a partir do conteúdo da mensagem que permite ao receptor detectar se os dados chegaram corrompidos — e descartar o frame silenciosamente em vez de processar um dado errado.
