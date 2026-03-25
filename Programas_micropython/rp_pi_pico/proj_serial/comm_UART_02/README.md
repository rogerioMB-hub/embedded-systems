# Receptor UART com Dicionário – Raspberry Pi Pico

Versão do receptor serial que emprega a **UART física** do Pico (pinos GP0/GP1), permitindo comunicação direta
com outros dispositivos.

## Requisitos
- Raspberry Pi Pico
- MicroPython (RP2 port)
- Thonny IDE
- Adaptador USB-serial (ex: CP2102, CH340, FTDI - já incluso nas placas RBP Pico e ESP32, p. ex.)

## Pinout para ligações futuras ou caso se utilize de placa adaptadora USB-serial

```
Pico GP0 (TX)  →  RX do adaptador
Pico GP1 (RX)  →  TX do adaptador
Pico GND       →  GND do adaptador
```

> ⚠️ Não conecte o 3.3V ou 5V do adaptador ao Pico enquanto ele estiver
> alimentado pelo USB — use apenas o GND em comum.

## Configuração da UART

| Parâmetro | Valor |
|-----------|-------|
| UART      | 0     |
| TX        | GP0   |
| RX        | GP1   |
| Baudrate  | 115200 |
| Bits      | 8     |
| Paridade  | nenhuma |
| Stop bits | 1     |

## Códigos suportados

| Byte | Resposta |
|------|----------|
| 1    | um       |
| 2    | dois     |
| 3    | três     |
| 4    | quatro   |
| 5    | cinco    |
| 6    | seis     |
| 7    | sete     |
| 8    | oito     |
| 9    | nove     |

Qualquer outro valor recebido exibe `fora do dicionário`.

## Como testar

1. Conecte o cabo USB na placa protótipo e no computador
2. Grave e execute `receptor_uart.py` no Pico pelo Thonny
3. Envie bytes pelo terminal — o Pico exibirá a resposta no Shell do Thonny

## Próxima etapa

Com a UART funcionando entre o Pico e o computador, o próximo passo é
substituir o computador por outro Raspberry Pi Pico — conectando os pinos
diretamente entre as duas placas.
