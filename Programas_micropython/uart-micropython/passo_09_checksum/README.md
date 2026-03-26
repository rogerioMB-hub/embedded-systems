# Passo 9 — Frame com Checksum XOR

## Objetivo

Adicionar **integridade** ao protocolo: ambas as placas calculam um checksum XOR do payload e o incluem no frame. O receptor recalcula o checksum de forma independente e descarta o frame se o resultado divergir — detectando corrupção de dados sem precisar de hardware extra.

---

## O problema que este passo resolve

Nos passos anteriores, qualquer byte corrompido em trânsito era processado silenciosamente como se fosse válido. Uma temperatura de `24.3` corrompida para `94.3` seria aceita sem questionamento.

Com checksum, a corrupção é **detectada antes do processamento** — e o frame é descartado.

---

## O checksum XOR

O XOR (ou exclusivo) é uma operação bit a bit com uma propriedade útil: se qualquer bit for alterado, o resultado muda.

```python
def calcular_checksum(payload):
    resultado = 0
    for byte in payload.encode():
        resultado ^= byte       # Acumula XOR de cada byte
    return resultado
```

### Exemplo passo a passo

Para o payload `"REQ:TEMP"`:

```
'R' = 0x52   →  resultado = 0x00 ^ 0x52 = 0x52
'E' = 0x45   →  resultado = 0x52 ^ 0x45 = 0x17
'Q' = 0x51   →  resultado = 0x17 ^ 0x51 = 0x46
':' = 0x3A   →  resultado = 0x46 ^ 0x3A = 0x7C
'T' = 0x54   →  resultado = 0x7C ^ 0x54 = 0x28
'E' = 0x45   →  resultado = 0x28 ^ 0x45 = 0x6D
'M' = 0x4D   →  resultado = 0x6D ^ 0x4D = 0x20
'P' = 0x50   →  resultado = 0x20 ^ 0x50 = 0x70

Checksum = 0x70  →  frame: "REQ:TEMP*70\n"
```

Se o receptor recalcular `"REQ:TEMP"` e obtiver `0x70`, o frame é aceito. Se qualquer byte tiver sido alterado, o resultado será diferente.

---

## Formato do frame

```
PAYLOAD * XX \n
   │      │  │  └─ terminador de frame
   │      │  └──── checksum em hexadecimal (2 dígitos, maiúsculo)
   │      └─────── separador fixo
   └────────────── conteúdo da mensagem
```

### Exemplos de frames completos

| Payload | Checksum | Frame completo |
|---------|----------|----------------|
| `REQ:TEMP` | `70` | `REQ:TEMP*70\n` |
| `REQ:LUM` | `6B` | `REQ:LUM*6B\n` |
| `DADO:TEMP:24.3` | varia | `DADO:TEMP:24.3*XX\n` |
| `ERRO:CHECKSUM` | varia | `ERRO:CHECKSUM*XX\n` |

---

## Fluxo de validação

```
Frame recebido: "REQ:TEMP*70\n"
        │
        ▼
Separa em payload="REQ:TEMP" e cs_rec="70"
        │
        ▼
Calcula checksum de "REQ:TEMP" → 0x70
        │
        ▼
Compara: 0x70 == 0x70?
        │
   Sim  │  Não
        │   └──► Descarta — envia "ERRO:CHECKSUM*XX"
        ▼
  Processa payload
        │
        ▼
  Monta resposta com checksum
        │
        ▼
  Envia frame de volta
```

---

## Por que `rsplit('*', 1)` e não `split`?

```python
partes = frame.rsplit('*', 1)
```

O `rsplit` divide a partir da **direita**, limitado a 1 divisão. Isso garante que, se o payload contiver um `*` (improvável mas possível), o separador correto seja sempre o último — onde o checksum está.

---

## Limitações do XOR e quando evoluir

O checksum XOR é excelente para aprendizado, mas tem limitações:

| Característica | XOR | CRC-16 | CRC-32 |
|----------------|-----|--------|--------|
| Detecta erro em 1 bit | ✓ | ✓ | ✓ |
| Detecta erros em 2 bits | Às vezes | ✓ | ✓ |
| Detecta erros em burst | Não | ✓ | ✓ |
| Complexidade | Mínima | Baixa | Baixa |

Para aplicações reais com ruído elétrico significativo (longas distâncias, ambientes industriais), use CRC-16 ou CRC-32.

---

## Arquivos

```
passo_09_checksum/
├── controladora.py   → grava na Placa A
└── periferica.py     → grava na Placa B
```

---

## Conexão física

Idêntica ao passo 8:

```
  Placa A — controladora          Placa B — periférica
       TX (GP4) ──────────────────► RX (GP5)
       RX (GP5) ◄────────────────── TX (GP4)
           GND ─────────────────── GND
```

---

## Como executar

1. Grave `periferica.py` na Placa B e execute (▶)
2. Grave `controladora.py` na Placa A e execute (▶)

### Shell da Placa A (controladora) — operação normal

```
── Ciclo 1 ──────────────────────────
  → Enviado  : 'REQ:TEMP*70'
  ← Recebido : 'DADO:TEMP:24.3*2E'
  [TEMP] = 24.3
  → Enviado  : 'REQ:LUM*6B'
  ← Recebido : 'DADO:LUM:0.1*1F'
  [LUM] = 0.1
```

### Shell da Placa B (periférica) — operação normal

```
[001] 'REQ:TEMP' → 'DADO:TEMP:24.3*2E'
[002] 'REQ:LUM'  → 'DADO:LUM:0.1*1F'
```

---

## Conceitos abordados

- Checksum XOR: cálculo, inserção no frame e validação
- Representação hexadecimal com `f"{valor:02X}"`
- Conversão de hex para inteiro com `int(cs, 16)`
- `rsplit('*', 1)`: divisão segura mesmo com `*` no payload
- Resposta de erro estruturada para frame corrompido
- Limitações do XOR frente a CRC

---

## Experimente

- Calcule manualmente o checksum de `"REQ:LUM"` byte a byte e compare com o que o programa gera
- Modifique a periférica para introduzir um erro proposital: altere 1 caractere do frame antes de enviar e observe a controladora rejeitar
- Implemente um contador de retransmissões: se a controladora receber `ERRO:CHECKSUM`, reenvie o mesmo frame até 3 vezes antes de desistir

---

## Próximo passo

No [Passo 10](../passo_10_protocolo/README.md) todos os elementos construídos até aqui se unem em um **mini-protocolo completo**: SOF + tipo + payload + checksum + EOF, com ACK/NAK e retransmissão automática — comunicação bidirecional robusta entre qualquer combinação de Pico e ESP32.
