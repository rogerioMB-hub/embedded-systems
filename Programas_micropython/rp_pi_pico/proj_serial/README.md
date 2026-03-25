# Comunicação Serial com Raspberry Pi Pico – MicroPython

Série de exemplos progressivos para aprender comunicação serial
em MicroPython, partindo do básico até a construção de um pequeno
protocolo entre placas via UART.

Desenvolvida para alunas e alunos iniciantes, cada exemplo introduz
um conceito novo, construindo sobre o anterior.

---

## Estrutura do repositório

```
📁 01_receptor_led/
    receptor_serial.py       # Recebe byte e controla LED via USB_VCP
    receptor_led_uart.py     # Mesma lógica, agora via UART física
    README.md

📁 02_receptor_dicionario/
    receptor_dicionario.py   # Recebe byte e consulta dicionário via USB_VCP
    receptor_uart.py         # Mesma lógica, agora via UART física
    README.md

📁 03_...                    # em breve
```

---

## Roteiro de aprendizado

### ✅ 01 – Receptor com LED (`if/elif`)
Primeiro contato com comunicação serial. O Pico recebe 1 byte e reage
a ele: acende ou apaga o LED interno.

Disponível em duas versões:
- **USB_VCP** – usa o cabo USB do Thonny, sem hardware extra
- **UART física** – usa os pinos GP0/GP1 com adaptador USB-serial

Conceitos: `USB_VCP`, `UART`, `read()`, `if/elif`, controle de hardware com `Pin`.

---

### ✅ 02 – Receptor com dicionário
O `if/elif` cresce rápido quando há muitos códigos. A solução é o dicionário:
uma estrutura que mapeia chaves a valores de forma organizada e escalável.

Disponível em duas versões:
- **USB_VCP** – usa o cabo USB do Thonny, sem hardware extra
- **UART física** – usa os pinos GP0/GP1 com adaptador USB-serial

Conceitos: `dict`, operador `in`, consulta por chave.

---

### 🔜 03 – Receptor com resposta *(em construção)*
O Pico não só recebe — ele também responde. Para cada byte recebido,
envia de volta uma confirmação ou um dado.

Conceitos: `write()`, protocolo simples de requisição e resposta.

---

### 🔜 04 – Duas placas conversando (USB_VCP) *(em construção)*
Dois Picos conectados ao mesmo computador, cada um em sua porta USB.
Um envia, o outro responde. O computador faz a ponte.

Conceitos: múltiplas portas seriais, endereçamento básico.

---

### 🔜 05 – Comunicação direta entre placas (UART) *(em construção)*
Os dois Picos conversam diretamente pelos pinos GP0/GP1,
sem passar pelo computador.

Conceitos: `UART`, fiação TX→RX, níveis de tensão.

---

### 🔜 06 – Protocolo simples entre placas *(em construção)*
Definição de um protocolo mínimo: início de mensagem, código de comando,
dado e confirmação de recebimento (ACK).

Conceitos: estrutura de pacote, ACK/NACK, robustez na comunicação.

---

## Por que USB_VCP primeiro?

O `USB_VCP` permite testar tudo com o cabo USB que já conecta o Pico ao
computador, sem fios extras. É a forma mais simples de começar.

Quando o conceito estiver claro, a migração para a UART física é natural:
a lógica do programa é idêntica — só o canal de comunicação muda.
Comparar as duas versões lado a lado é um ótimo exercício.

---

## Sobre a UART física

A UART física usa os pinos GP0 (TX) e GP1 (RX) do Pico e requer um
adaptador USB-serial (ex: CP2102, CH340, FTDI) para se conectar ao
computador. É o mesmo canal que será usado futuramente para a comunicação
direta entre dois Picos.

```
Pico GP0 (TX)  →  RX do adaptador
Pico GP1 (RX)  →  TX do adaptador
Pico GND       →  GND do adaptador
```

---

## Ambiente utilizado

- Raspberry Pi Pico (RP2040)
- MicroPython (RP2 port, versão atual)
- Thonny IDE
- Adaptador USB-serial (para exemplos com UART física)
