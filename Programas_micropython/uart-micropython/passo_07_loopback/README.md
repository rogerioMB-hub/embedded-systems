# Passo 7 — Loopback entre Duas Placas

## Objetivo

Sair do Shell do Thonny e conectar **duas placas físicas** pelos pinos TX e RX. A placa transmissora envia mensagens numeradas, a receptora as ecoa de volta, e a transmissora verifica se o eco confere — produzindo um relatório de integridade da comunicação.

É o primeiro teste de UART com hardware de verdade.

---

## Conexão física

```
  Placa A — transmissora          Placa B — receptora
  ──────────────────────          ───────────────────
       TX (GP4) ──────────────────► RX (GP5)
       RX (GP5) ◄────────────────── TX (GP4)
           GND ─────────────────── GND
```

> **GND comum é obrigatório.** Sem ele, os níveis de tensão ficam sem referência e os dados chegam corrompidos — ou não chegam.

> **Tensão:** Pico e ESP32 operam em 3,3 V e podem ser conectados diretamente entre si. Nunca conecte diretamente a um dispositivo 5 V sem um conversor de nível lógico.

### Pinos padrão utilizados (UART1)

| Placa | TX | RX |
|-------|----|----|
| Raspberry Pi Pico | GP4 | GP5 |
| ESP32 DevKit v1 | GP10 | GP9 |

> Por que UART1 e não UART0? A UART0 do Pico compartilha pinos com o USB em algumas configurações, o que pode causar conflito com o Thonny. UART1 é mais segura para comunicação entre placas.

---

## Arquivos

```
passo_07_loopback/
├── transmissora.py   → grava na Placa A
└── receptora.py      → grava na Placa B
```

---

## Como executar

### Preparação

1. Conecte as duas placas conforme o diagrama acima
2. Abra **duas instâncias do Thonny** — uma para cada placa
3. Em cada instância, selecione a porta COM correta em *Ferramentas → Opções → Interpretador*

### Ordem de inicialização

```
1. Grave receptora.py na Placa B e execute (▶)
2. Grave transmissora.py na Placa A e execute (▶)
```

A receptora deve estar pronta antes da transmissora começar a enviar.

### O que você verá

**Shell da Placa B (receptora):**
```
========================================
  Passo 7 — Loopback UART (Receptora)
========================================
  Aguardando mensagens...
========================================
[ECO #001] 'MSG:001'
[ECO #002] 'MSG:002'
[ECO #003] 'MSG:003'
...
```

**Shell da Placa A (transmissora):**
```
[1]
  Enviado : 'MSG:001'
  Eco     : 'MSG:001' ✓
[2]
  Enviado : 'MSG:002'
  Eco     : 'MSG:002' ✓
...
  → Estatísticas: 5/5 OK (100%)
...
========================================
  Relatório final
========================================
  Enviados  : 10
  Recebidos : 10
  Erros     : 0
  Taxa OK   : 100.0%
========================================
```

---

## O que este passo valida

| O que é testado | Como é testado |
|-----------------|----------------|
| Conexão física TX/RX | Sem conexão = timeout imediato na transmissora |
| GND comum | Sem GND = erros aleatórios ou sem eco |
| Baud rate igual em ambas | Divergência = caracteres corrompidos no eco |
| Integridade dos dados | Comparação byte a byte do enviado com o eco |
| Robustez da receptora | Timeout e limite de buffer do passo 6 |

---

## Parâmetros configuráveis

### transmissora.py

```python
UART_ID      = 1     # Qual UART usar
BAUD_RATE    = 9600  # Deve ser igual na receptora
TX_PIN       = 4     # Ajuste conforme sua placa
RX_PIN       = 5     # Ajuste conforme sua placa
INTERVALO_MS = 2000  # Intervalo entre envios (ms)
TIMEOUT_ECO  = 1000  # Tempo máximo aguardando eco (ms)
TOTAL_ENVIOS = 10    # 0 = roda indefinidamente
```

### receptora.py

```python
UART_ID    = 1     # Deve ser igual na transmissora
BAUD_RATE  = 9600  # Deve ser igual na transmissora
TX_PIN     = 4     # Ajuste conforme sua placa
RX_PIN     = 5     # Ajuste conforme sua placa
TIMEOUT_MS = 2000  # Timeout de recepção
BUFFER_MAX = 64    # Limite do buffer
```

---

## Conceitos abordados

- Conexão física UART entre dois dispositivos: TX→RX, RX→TX, GND comum
- Importância do GND comum e da compatibilidade de tensão
- Uso de UART1 para evitar conflito com o canal USB/Thonny
- Verificação de integridade por comparação de eco
- Estatísticas de comunicação: taxa de sucesso, erros, timeouts
- Operação simultânea de duas instâncias do Thonny

---

## Diagnóstico de problemas

| Sintoma | Causa provável | Solução |
|---------|---------------|---------|
| Timeout imediato na transmissora | TX/RX não conectados | Verifique a fiação |
| Eco com caracteres errados | Baud rate diferente entre as placas | Iguale `BAUD_RATE` nos dois arquivos |
| Eco corrompido aleatoriamente | GND não conectado | Adicione o fio de GND |
| Receptora não exibe nada | Pinos TX/RX invertidos | Troque TX↔RX na receptora |
| Conflito com Thonny | UART0 conflitando com USB | Use UART1 (GP4/GP5 no Pico) |

---

## Experimente

- Aumente `BAUD_RATE` para `115200` nas duas placas e observe se a taxa de sucesso se mantém
- Desconecte o fio TX no meio do teste e reconecte — a transmissora detecta o problema e a receptora se recupera sozinha?
- Mude `TOTAL_ENVIOS = 0` na transmissora para rodar indefinidamente e deixe por alguns minutos — a taxa de sucesso permanece em 100%?

---

## Próximo passo

No [Passo 8](../passo_08_controlador_periferico/README.md) as placas ganham papéis definidos: a **controladora** faz perguntas e a **periférica** responde com leituras de um sensor — o primeiro modelo de comunicação com propósito real.
