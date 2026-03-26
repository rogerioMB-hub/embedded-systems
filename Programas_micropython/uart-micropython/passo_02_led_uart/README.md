# Passo 2 — Controle de LED via UART

## Objetivo

Evoluir o eco simples do passo anterior para um programa que **interpreta** o dado recebido e toma uma decisão: ligar o LED, desligá-lo, ou informar que o caractere enviado não é reconhecido.

É o primeiro contato com lógica de comando via comunicação serial.

---

## O que muda em relação ao passo 1?

| | Passo 1 | Passo 2 |
|---|---|---|
| O dispositivo faz | Ecoa o byte recebido | Interpreta o byte e age |
| Estrutura de decisão | Nenhuma | `if / elif / else` |
| Saída | Mesmo byte de volta | Mensagem descritiva + ação física |
| Periférico envolvido | Nenhum | LED |

---

## Diagrama de funcionamento

```
Aluno digita no Shell
         │
         ▼
   Chega 1 byte pela UART
         │
         ├── char == 'L' ──► Liga LED  ──► Responde "LED ligado"
         │
         ├── char == 'D' ──► Desliga LED ► Responde "LED desligado"
         │
         └── outro char  ──► Responde "Caractere desconhecido"
```

---

## Estrutura do código

```
passo_02_led_uart/
└── led_uart.py
```

### Constantes configuráveis

```python
UART_ID   = 0     # Qual UART usar (0 ou 1)
BAUD_RATE = 9600  # Velocidade em bits por segundo
TX_PIN    = None  # None = pino padrão da placa
RX_PIN    = None  # None = pino padrão da placa
LED_PIN   = 25    # Ajuste conforme sua placa (veja tabela abaixo)
```

### Referência de pinos do LED

| Placa | LED | Pino |
|-------|-----|------|
| Raspberry Pi Pico | Onboard | 25 |
| ESP32 DevKit v1 | Onboard | 2 |
| ESP32-C3 | Onboard | 8 |
| Qualquer placa | Externo | Livre (com resistor de 330Ω) |

---

## Como executar

1. Abra o Thonny e conecte sua placa
2. Ajuste `LED_PIN` conforme sua placa
3. Clique em **Run** (▶)
4. No Shell do Thonny, digite:
   - `L` → o LED acende e a placa responde `LED ligado`
   - `D` → o LED apaga e a placa responde `LED desligado`
   - Qualquer outro caractere → a placa responde `Caractere desconhecido`

---

## Conceitos abordados

- Conversão de `bytes` para `str` com `.decode()`
- Estrutura de decisão `if / elif / else` aplicada a comandos seriais
- Controle de saída digital com `Pin.OUT` e `.value()`
- Resposta bidirecional: a placa não só recebe, mas também envia mensagens
- Uso de `repr()` para exibir caracteres especiais com segurança no Shell

---

## Por que `repr(char)` na mensagem de erro?

Caracteres como `'\n'` (Enter), `'\r'` (retorno de carro) ou `'\t'` (tab) são invisíveis quando impressos normalmente. O `repr()` os exibe de forma legível — por exemplo, `'\n'` aparece como `"'\\n'"` no Shell. Isso ajuda muito na depuração.

---

## Experimente

- Envie `'l'` (minúsculo) em vez de `'L'`: o LED não liga — por quê? Como você corrigiria isso?
- Adicione o comando `'T'` para **alternar** o estado do LED (toggle) sem precisar saber o estado atual
- Envie um Enter (tecla ↵) e observe o que aparece no Shell com `repr()`

---

## Próximo passo

No [Passo 3](../passo_03_dicionario/README.md) o dispositivo usa um **dicionário** Python para mapear os dígitos `'1'` a `'9'` aos seus nomes por extenso — introduzindo uma estrutura de dados mais poderosa para o tratamento de comandos.
