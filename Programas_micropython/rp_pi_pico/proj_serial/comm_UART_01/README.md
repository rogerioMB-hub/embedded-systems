# Receptor UART com LED – Raspberry Pi Pico

Versão alternativa do primeiro programa, agora usando a **UART física**
(pinos GP0/GP1) no lugar do USB_VCP. O Pico recebe 1 byte e controla
o LED interno.

## Requisitos
- Raspberry Pi Pico
- MicroPython (RP2 port)
- Thonny IDE
- Adaptador USB-serial (ex: CP2102, CH340, FTDI)

## Evolução em relação à versão anterior

Na [versão original](../receptor_serial.py) usamos `USB_VCP`, que funciona
pelo cabo USB do Thonny. Aqui migramos para a **UART0**, acessível pelos
pinos físicos do Pico. A lógica do programa é a mesma — só o canal de
comunicação mudou.

## Ligação com o adaptador USB-serial

```
Pico GP0 (TX)  →  RX do adaptador
Pico GP1 (RX)  →  TX do adaptador
Pico GND       →  GND do adaptador
```

> ⚠️ Não conecte o 3.3V ou 5V do adaptador ao Pico enquanto ele estiver
> alimentado pelo USB — use apenas o GND em comum.

## Configuração da UART

| Parâmetro | Valor   |
|-----------|---------|
| UART      | 0       |
| TX        | GP0     |
| RX        | GP1     |
| Baudrate  | 115200  |
| Bits      | 8       |
| Paridade  | nenhuma |
| Stop bits | 1       |

## Códigos suportados

| Byte | Valor | Ação         |
|------|-------|--------------|
| 0xAA | 170   | Acende o LED |
| 0x55 | 85    | Apaga o LED  |

Qualquer outro valor recebido exibe `Código desconhecido`.

## Como testar

1. Conecte o adaptador USB-serial conforme a ligação acima
2. Grave e execute `receptor_led_uart.py` no Pico pelo Thonny
3. No computador, abra um terminal serial (ex: PuTTY, minicom, screen)
   na porta do adaptador, com 115200 baud
4. Envie os bytes pelo terminal:
   - `0xAA` → LED acende
   - `0x55` → LED apaga

## Próxima etapa

Com a UART funcionando entre o Pico e o computador, o próximo passo é
substituir o computador por outro Raspberry Pi Pico — conectando os pinos
diretamente entre as duas placas.
