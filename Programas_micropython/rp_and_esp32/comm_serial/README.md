# Comunicação Serial com MicroPython

Série de exemplos progressivos para aprender comunicação serial
em MicroPython, partindo do básico até a construção de um pequeno
protocolo entre placas via UART.

Desenvolvida para alunas e alunos iniciantes, cada exemplo introduz
um conceito novo, construindo sobre o anterior.

Exemplos disponíveis para **Raspberry Pi Pico** e **ESP32 (DevKit)**.

---

## Estrutura do repositório

```
📁 pico/
    receptor_led_uart.py    # Recebe byte e controla LED (if/elif)
    receptor_uart.py        # Recebe byte e consulta dicionário
    README.md

📁 esp32/
    receptor_led_uart.py    # Recebe byte e controla LED (if/elif)
    receptor_uart.py        # Recebe byte e consulta dicionário
    README.md

📁 03_...                   # em breve
```

---

## Roteiro de aprendizado

### ✅ 01 – Receptor com LED (`if/elif`)
Primeiro contato com comunicação serial via UART física. A placa recebe
1 byte enviado pelo Shell do Thonny e reage: acende ou apaga o LED interno.

Conceitos: `UART`, `any()`, `read()`, `if/elif`, controle de hardware com `Pin`.

---

### ✅ 02 – Receptor com dicionário
O `if/elif` cresce rápido quando há muitos códigos. A solução é o dicionário:
uma estrutura que mapeia chaves a valores de forma organizada e escalável.
O transmissor ainda é o Shell do Thonny.

Conceitos: `dict`, operador `in`, consulta por chave.

---

### 🔜 03 – Receptor com resposta *(em construção)*
A placa não só recebe — ela também responde. Para cada byte recebido,
envia de volta uma confirmação ou um dado. Primeira etapa com comunicação
bidirecional entre duas placas.

Conceitos: `uart.write()`, protocolo simples de requisição e resposta.

---

### 🔜 04 – Dois dispositivos conversando via UART *(em construção)*
Duas placas conectadas diretamente pelos pinos UART.
Uma envia, a outra recebe e responde — sem computador no meio.

Conceitos: ligação TX→RX entre placas, GND em comum, troca de papéis.

---

### 🔜 05 – Comunicação bidirecional *(em construção)*
As duas placas trocam mensagens nos dois sentidos: cada uma é ao mesmo
tempo transmissora e receptora.

Conceitos: UART TX e RX simultâneos, controle de fluxo básico.

---

### 🔜 06 – Protocolo simples entre placas *(em construção)*
Definição de um protocolo mínimo: início de mensagem, código de comando,
dado e confirmação de recebimento (ACK).

Conceitos: estrutura de pacote, ACK/NACK, robustez na comunicação.

---

## Diferenças entre as placas

| Característica | Raspberry Pi Pico | ESP32 DevKit |
|----------------|-------------------|--------------|
| UART usada     | UART0             | UART0        |
| Pino TX        | GP0               | GPIO1        |
| Pino RX        | GP1               | GPIO3        |
| LED interno    | Pin(25)           | Pin(2)       |
| Baudrate       | 115200            | 115200       |

---

## Ligação entre duas placas (a partir do exemplo 03)

**Pico ↔ Pico**
```
Pico A GP0 (TX)    →  GP1 (RX)   Pico B
Pico A GP1 (RX)    →  GP0 (TX)   Pico B
Pico A GND         →  GND        Pico B
```

**ESP32 ↔ ESP32**
```
ESP32 A GPIO1 (TX) →  GPIO3 (RX) ESP32 B
ESP32 A GPIO3 (RX) →  GPIO1 (TX) ESP32 B
ESP32 A GND        →  GND        ESP32 B
```

**Pico ↔ ESP32**
```
Pico GP0 (TX)      →  GPIO3 (RX) ESP32
Pico GP1 (RX)      →  GPIO1 (TX) ESP32
Pico GND           →  GND        ESP32
```

---

## Ambiente utilizado

- Raspberry Pi Pico (RP2040) ou ESP32 DevKit
- MicroPython (versão atual para cada placa)
- Thonny IDE
