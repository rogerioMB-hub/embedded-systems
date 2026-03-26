# Passo 5 — Máquina de Estados para Recepção UART

## Objetivo

Dar ao programa uma **consciência do próprio estado**: em vez de um loop que acumula bytes sem critério, o dispositivo sabe exatamente em que fase do ciclo de comunicação se encontra — e age de forma diferente em cada uma.

---

## O problema do passo 4

No passo anterior, o buffer acumulava bytes incondicionalmente. Isso funciona bem em condições ideais, mas apresenta fragilidades:

- Se chegar um `'\n'` solto (ruído de linha), o programa processa um buffer vazio
- Se bytes chegarem antes do programa estar pronto, podem se misturar com a mensagem anterior
- Não há como distinguir "aguardando o primeiro byte" de "no meio de uma mensagem"

A máquina de estados resolve todos esses casos tornando o comportamento **explícito**.

---

## Os três estados

```
        byte válido            '\n' recebido
  ┌──────────────────┐    ┌──────────────────┐
  │                  ▼    │                  ▼
IDLE ──────────► RECEBENDO ──────────► PROCESSANDO
  ▲                                         │
  └─────────────────────────────────────────┘
              comando executado
```

| Estado | O programa está... | Ao receber `'\n'` | Ao receber outro byte |
|--------|--------------------|-------------------|-----------------------|
| `IDLE` | Aguardando | Ignora (ruído) | Inicia recepção |
| `RECEBENDO` | Acumulando bytes | Vai para PROCESSANDO | Acumula no buffer |
| `PROCESSANDO` | Executando comando | — | — |

### Por que estados nomeados em vez de números?

```python
# Ruim — o que significa estado == 2?
estado = 2

# Bom — legível e autodocumentado
estado = PROCESSANDO
```

Constantes nomeadas tornam o código legível e facilitam a depuração: a mensagem `[RECEBENDO]` no Shell é imediatamente compreensível.

---

## Diagrama detalhado de transições

```
Inicializa
    │
    ▼
 [IDLE] ◄────────────────────────────────┐
    │                                     │
    │ byte != '\n', '\r', ' '             │
    ▼                                     │
[RECEBENDO] ── byte != '\n' ──► acumula  │
    │                                     │
    │ byte == '\n'                        │
    ▼                                     │
[PROCESSANDO]                            │
    │                                     │
    ├── parseia buffer                    │
    ├── executa comando                   │
    ├── envia resposta                    │
    ├── limpa buffer                      │
    └── volta para ─────────────────────►┘
```

---

## O que mudou no código em relação ao passo 4?

| Aspecto | Passo 4 | Passo 5 |
|---------|---------|---------|
| Controle de fluxo | `if char == '\n'` | Variável `estado` + funções por estado |
| Tratamento de ruído | Nenhum | `IDLE` ignora `'\n'`, `'\r'`, espaços soltos |
| Visibilidade | Silencioso | Imprime `[ESTADO]` a cada transição |
| Extensibilidade | Difícil | Novo estado = nova função |

---

## Estrutura do código

```
passo_05_maquina_estados/
└── maquina_estados.py
```

### Constantes configuráveis

```python
UART_ID   = 0     # Qual UART usar (0 ou 1)
BAUD_RATE = 9600  # Velocidade em bits por segundo
TX_PIN    = None  # None = pino padrão da placa
RX_PIN    = None  # None = pino padrão da placa
LED_PIN   = 25    # Ajuste conforme sua placa
```

---

## Como executar

1. Abra o Thonny e conecte sua placa
2. Ajuste `LED_PIN` conforme sua placa
3. Clique em **Run** (▶)
4. Observe no Shell as transições de estado enquanto digita

Exemplo de sessão no Shell ao enviar `LED:L`:

```
[RECEBENDO] [RECEBENDO] [RECEBENDO] [RECEBENDO] [RECEBENDO] [PROCESSANDO]
>> LED ligado
[IDLE]
```

---

## Conceitos abordados

- Máquina de estados finitos (FSM): estados, transições e ações
- Constantes nomeadas como alternativa a números mágicos
- Separação de responsabilidades: uma função por estado
- Tratamento de ruído de linha (`'\r'` e `'\n'` soltos)
- Visibilidade do estado interno para fins de depuração

---

## Experimente

- Envie bytes com um intervalo de alguns segundos entre eles — observe como o estado `RECEBENDO` persiste entre os bytes
- Pressione Enter várias vezes seguidas sem digitar nada — observe que o estado `IDLE` os absorve sem erro
- Adicione um quarto estado `ERRO` que é ativado quando o buffer ultrapassa 32 caracteres sem receber `'\n'` (mensagem muito longa)

---

## Próximo passo

No [Passo 6](../passo_06_buffer_timeout/README.md) a máquina de estados ganha um **timeout**: se o dispositivo ficar muito tempo no estado `RECEBENDO` sem receber o terminador, descarta o buffer e volta ao `IDLE` — protegendo o sistema contra mensagens incompletas.
