# Receptor Serial com Dicionário – Raspberry Pi Pico

Segunda versão do receptor serial, introduzindo o conceito de dicionário
em MicroPython. O programa recebe um byte de 1 a 9 e exibe o valor por extenso.

## Requisitos
- Raspberry Pi Pico
- MicroPython (RP2 port)
- Thonny IDE

## Evolução em relação à versão anterior

Na [versão anterior](../receptor_serial.py) usamos `if/elif` para reagir a
cada código recebido. Aqui substituímos essa estrutura por um **dicionário**,
o que torna o código mais organizado e fácil de expandir.

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

## Como usar

1. Grave o arquivo `receptor_dicionario.py` no Pico pelo Thonny
2. Execute o programa
3. No Shell do Thonny, envie bytes com:

```python
from machine import USB_VCP
usb = USB_VCP()
usb.write(bytes([3]))   # exibe: Recebi: 3 → três
usb.write(bytes([7]))   # exibe: Recebi: 7 → sete
usb.write(bytes([99]))  # exibe: Recebi: 99 → fora do dicionário
```

## Conceito-chave: dicionário

O trecho central do programa é este:

```python
if valor in numeros:
    print("Recebi:", valor, "→", numeros[valor])
```

O operador `in` verifica se a chave existe no dicionário antes de acessá-la.
É uma forma mais elegante e escalável do que um `if/elif` para cada caso.

## Objetivo

Programa desenvolvido para introdução ao MicroPython com alunas e alunos
iniciantes. Faz parte de uma série progressiva de exemplos com comunicação
serial no Raspberry Pi Pico.
