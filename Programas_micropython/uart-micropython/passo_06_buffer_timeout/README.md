# Passo 6 — Buffer e Timeout na Recepção UART

## Objetivo

Tornar a máquina de estados do passo 5 **resiliente a falhas reais**: mensagens incompletas, silêncio inesperado na linha e buffers que crescem sem controle. Com este passo, a fase 2 está completa — o programa está pronto para enfrentar hardware de verdade.

---

## O problema que este passo resolve

Em condições ideais, toda mensagem enviada chega completa e termina com `'\n'`. Na prática:

| Situação | O que acontece sem proteção |
|----------|-----------------------------|
| Cabo desconectado no meio da transmissão | Programa trava em `RECEBENDO` para sempre |
| Ruído elétrico injeta bytes extras | Buffer cresce indefinidamente |
| Terminal envia mensagem muito longa | `MemoryError` por esgotamento de RAM |

O timeout e o limite de buffer protegem contra todos esses casos.

---

## Os dois mecanismos de proteção

### 1. Timeout

```python
TIMEOUT_MS = 2000   # 2 segundos
```

Se o dispositivo ficar mais de `TIMEOUT_MS` milissegundos no estado `RECEBENDO` sem receber `'\n'`, o buffer é descartado e o sistema volta ao `IDLE`.

A verificação de timeout acontece em **toda iteração do loop** — mesmo quando não há bytes disponíveis. Isso é fundamental: o silêncio na linha precisa ser detectado mesmo sem novos dados chegando.

```python
# Detecta silêncio — roda mesmo sem uart.any()
if estado == RECEBENDO:
    tempo_decorrido = time.ticks_diff(time.ticks_ms(), tempo_inicio)
    if tempo_decorrido >= TIMEOUT_MS:
        estado, buffer, tempo_inicio = descartar("timeout")
```

### Por que `time.ticks_diff()` e não subtração simples?

Em MicroPython, `time.ticks_ms()` é um contador que **reinicia do zero** após atingir seu valor máximo (wrap-around). A subtração direta `agora - inicio` daria resultado errado nesse caso. `ticks_diff()` lida com o wrap-around corretamente.

### 2. Limite de buffer

```python
BUFFER_MAX = 64   # bytes
```

Se o buffer atingir `BUFFER_MAX` bytes sem receber `'\n'`, a mensagem é descartada. Isso protege a RAM limitada do microcontrolador.

```
Pico:  264 KB de RAM total — economize
ESP32: ~320 KB disponíveis — idem
```

---

## Diagrama de estados atualizado

```
                  byte válido / inicia cronômetro
  ┌─────────────────────────────────────────┐
  │                                         ▼
IDLE ◄──────────────────────────────── RECEBENDO
  ▲    descarte (timeout ou buf. cheio)     │
  │                                         │ '\n' recebido
  │                                         ▼
  └──────────────────────────────────── PROCESSANDO
              comando executado
```

---

## A função `descartar()`

```python
def descartar(motivo):
    aviso = f"[DESCARTADO] {motivo}"
    uart.write(aviso + '\n')
    print(aviso)
    return IDLE, '', 0
```

Centralizar o descarte em uma função evita duplicar código nos dois pontos onde ele pode ocorrer (timeout e buffer cheio). Ela também comunica o descarte pela UART — quem enviou a mensagem é avisado de que ela foi perdida.

---

## Estrutura do código

```
passo_06_buffer_timeout/
└── buffer_timeout.py
```

### Constantes configuráveis

```python
UART_ID    = 0     # Qual UART usar (0 ou 1)
BAUD_RATE  = 9600  # Velocidade em bits por segundo
TX_PIN     = None  # None = pino padrão da placa
RX_PIN     = None  # None = pino padrão da placa
LED_PIN    = 25    # Ajuste conforme sua placa
TIMEOUT_MS = 2000  # Tempo máximo em RECEBENDO (ms)
BUFFER_MAX = 64    # Tamanho máximo do buffer (bytes)
```

---

## Como executar e testar os mecanismos

1. Abra o Thonny e conecte sua placa
2. Ajuste `LED_PIN` conforme sua placa
3. Clique em **Run** (▶)

### Testando o timeout

1. Digite `LED` (sem o `:L` e sem pressionar Enter)
2. Aguarde 2 segundos
3. O Shell exibirá: `[DESCARTADO] timeout de 2000 ms — buffer: 'LED'`

### Testando o limite de buffer

1. Ajuste `BUFFER_MAX = 8` temporariamente
2. Digite `LED:LIGADO` (9 caracteres) sem pressionar Enter
3. O Shell exibirá: `[DESCARTADO] buffer cheio (8 bytes)`

### Operação normal

```
[RECEBENDO] >> LED ligado
[IDLE]
```

---

## Conceitos abordados

- Timeout em sistemas embarcados: detectar silêncio na linha
- `time.ticks_ms()` e `time.ticks_diff()`: medição de tempo sem wrap-around
- Limite de buffer: proteger a RAM de microcontroladores
- Função de descarte centralizada: princípio DRY (*Don't Repeat Yourself*)
- Verificação periódica independente de entrada: o loop faz mais do que ler bytes

---

## Experimente

- Reduza `TIMEOUT_MS` para `500` e observe como o sistema fica mais "impaciente"
- Aumente `BUFFER_MAX` para `128` e envie uma mensagem muito longa — qual o limite real antes de um `MemoryError`?
- Implemente um contador de descartes e exiba-o na mensagem inicial do próximo boot: `"Última sessão: N mensagens descartadas"`

---

## Resumo da Fase 2

Ao longo dos passos 4, 5 e 6 construímos, camada por camada, uma recepção UART robusta:

| Passo | O que foi adicionado |
|-------|----------------------|
| 4 | Buffer + terminador + parsing de comandos |
| 5 | Máquina de estados explícita |
| 6 | Timeout + limite de buffer |

O código está pronto para comunicação com hardware real — que é exatamente o que começa no próximo passo.

---

## Próximo passo

No [Passo 7](../passo_07_loopback/README.md) saímos do Shell do Thonny e conectamos **duas placas** diretamente pelos pinos TX e RX. Uma transmite, a outra ecoa — o primeiro teste de UART com hardware de verdade.
