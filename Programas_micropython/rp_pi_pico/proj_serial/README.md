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
    receptor_serial.py      # Recebe byte e controla LED (if/elif)
    README.md

📁 02_receptor_dicionario/
    receptor_dicionario.py  # Recebe byte e consulta dicionário
    README.md

📁 03_...                   # em breve
```

---

## Roteiro de aprendizado

### ✅ 01 – Receptor com LED (`if/elif`)
Primeiro contato com a comunicação serial via USB_VCP.
O Pico recebe 1 byte e reage a ele: acende ou apaga o LED interno.

Conceitos: `USB_VCP`, `read()`, `if/elif`, controle de hardware com `Pin`.

---

### ✅ 02 – Receptor com dicionário
O `if/elif` cresce rápido quando há muitos códigos. A solução é o dicionário:
uma estrutura que mapeia chaves a valores de forma organizada e escalável.

Conceitos: `dict`, operador `in`, consulta por chave.

---

### 🔜 03 – Receptor com resposta *(em construção)*
O Pico não só recebe — ele também responde. Para cada byte recebido,
envia de volta uma confirmação ou um dado.

Conceitos: `usb.write()`, protocolo simples de requisição e resposta.

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
a lógica é a mesma, só muda o canal.

---

## Ambiente utilizado

- Raspberry Pi Pico (RP2040)
- MicroPython (RP2 port, versão atual)
- Thonny IDE
