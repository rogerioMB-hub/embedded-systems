# Passo 1 — Eco Serial via UART

## Objetivo

Estabelecer o primeiro contato com a comunicação UART: o aluno envia um caractere pelo Shell do Thonny e o dispositivo o ecoa de volta, byte a byte.

É o "Olá, mundo!" da comunicação serial — simples, imediato e revelador.

---

## O que é UART?

UART (*Universal Asynchronous Receiver-Transmitter*) é um dos protocolos de comunicação serial mais antigos e amplamente utilizados em eletrônica embarcada. Ele transmite dados bit a bit, de forma assíncrona (sem sinal de clock compartilhado), usando apenas dois fios:

| Sinal | Direção | Função |
|-------|---------|--------|
| **TX** | Saída | Transmite dados |
| **RX** | Entrada | Recebe dados |

A velocidade de transmissão é definida pelo **baud rate** (bits por segundo). Ambos os lados devem usar o mesmo valor — neste passo usamos **9600 bps**.

---

## Diagrama de conexão

### Modo loopback (uma placa, teste local)

```
┌─────────────────────┐
│    Raspberry Pi     │
│    Pico / ESP32     │
│                     │
│  TX ───────── RX    │  ← fio curto conectando TX ao RX
│                     │
└─────────────────────┘
         │
        USB
         │
      Thonny
```

No modo loopback, tudo que a UART transmite ela mesma recebe — perfeito para validar o código sem precisar de uma segunda placa.

### Pinos padrão

| Placa | UART | TX | RX |
|-------|------|----|----|
| Raspberry Pi Pico | UART0 | GP0 | GP1 |
| Raspberry Pi Pico | UART1 | GP4 | GP5 |
| ESP32 | UART0 | GP1 | GP3 |
| ESP32 | UART1 | GP10 | GP9 |

---

## Estrutura do código

```
passo_01_eco_serial/
└── eco_serial.py
```

### Constantes configuráveis

```python
UART_ID   = 0       # Qual UART usar (0 ou 1)
BAUD_RATE = 9600    # Velocidade em bits por segundo
TX_PIN    = None    # None = pino padrão da placa
RX_PIN    = None    # None = pino padrão da placa
```

### Fluxo de execução

```
Inicializa UART
      │
      ▼
Exibe mensagem no Shell
      │
      ▼
┌─────────────────────┐
│  Há byte disponível?│ ◄──────────┐
└─────────┬───────────┘            │
          │ Sim                    │
          ▼                        │
    Lê 1 byte da UART              │
          │                        │
          ▼                        │
    Ecoa o byte de volta           │
          │                        │
          ▼                        │
    Exibe no Shell do Thonny       │
          │                        │
          └────────────────────────┘
```

---

## Como executar

1. Abra o Thonny e conecte sua placa
2. Abra o arquivo `eco_serial.py`
3. Se quiser testar com loopback: conecte TX ao RX com um fio
4. Clique em **Run** (▶)
5. No Shell do Thonny, digite qualquer caractere

Você verá cada caractere aparecer de volta no Shell assim que for enviado.

---

## Conceitos abordados

- Inicialização de periférico `UART` com `machine.UART`
- Parâmetros `baudrate`, `tx` e `rx`
- Verificação de dados disponíveis com `uart.any()`
- Leitura byte a byte com `uart.read(1)`
- Escrita com `uart.write()`
- Estrutura de loop não-bloqueante com `if` (em vez de `while uart.any()`)

---

## Experimente

- Mude `BAUD_RATE` para `115200` e veja que o comportamento não muda (ambos os lados se ajustam)
- Remova o fio de loopback: o eco some — a UART transmite, mas ninguém responde
- Altere `uart.read(1)` para `uart.read(2)`: o que acontece quando você digita uma letra só?

---

## Próximo passo

No [Passo 2](../passo_02_led_uart/README.md) o dispositivo interpreta o caractere recebido: `'L'` liga um LED, `'D'` desliga — e qualquer outro char gera uma resposta de "caractere desconhecido".
