# Passo 3 — Dicionário de Dígitos por Extenso via UART

## Objetivo

Substituir a cadeia de `if/elif` do passo anterior por uma estrutura de dados mais poderosa: o **dicionário**. O dispositivo recebe um dígito de `'1'` a `'9'` e responde com o nome por extenso. Qualquer outro caractere gera `"Caractere desconhecido"`.

---

## O que muda em relação ao passo 2?

| | Passo 2 | Passo 3 |
|---|---|---|
| Estrutura de decisão | `if / elif / else` | `if char in dict` |
| Número de comandos | 2 (`'L'` e `'D'`) | 9 (`'1'` a `'9'`) |
| Como adicionar comandos | Escrever novo `elif` | Adicionar entrada ao dicionário |
| Ação ao receber comando | Liga/desliga LED | Retorna string por extenso |

Com apenas 2 comandos, o `if/elif` é legível. Com 9 — ou futuramente 50 — o dicionário é muito mais limpo e fácil de manter.

---

## O dicionário em detalhe

```python
digitos = {
    '1': 'um',
    '2': 'dois',
    '3': 'três',
    ...
    '9': 'nove',
}
```

Cada **chave** é um caractere string — porque o que chega pela UART é sempre texto, nunca um inteiro. Cada **valor** é a representação por extenso.

### Por que usar `in` antes de acessar?

```python
if char in digitos:          # Verifica se a chave existe
    resposta = digitos[char] # Só então acessa o valor
else:
    uart.write("Caractere desconhecido\n")
```

Acessar uma chave inexistente com `digitos[char]` causaria um `KeyError` e travaria o programa. O operador `in` é a forma mais idiomática de evitar isso em Python — mais legível do que usar `try/except` ou `.get()` neste contexto didático.

---

## Diagrama de funcionamento

```
Aluno digita no Shell
         │
         ▼
   Chega 1 byte pela UART
         │
         ▼
   char in digitos?
         │
    Sim  │  Não
         │   └──► "Caractere desconhecido"
         ▼
   Recupera digitos[char]
         │
         ▼
   Envia por extenso pela UART
   Exibe no Shell
```

---

## Estrutura do código

```
passo_03_dicionario/
└── dicionario_uart.py
```

### Constantes configuráveis

```python
UART_ID   = 0     # Qual UART usar (0 ou 1)
BAUD_RATE = 9600  # Velocidade em bits por segundo
TX_PIN    = None  # None = pino padrão da placa
RX_PIN    = None  # None = pino padrão da placa
```

---

## Como executar

1. Abra o Thonny e conecte sua placa
2. Clique em **Run** (▶)
3. No Shell do Thonny, envie:

| Você digita | Placa responde |
|:-----------:|----------------|
| `1` | `um` |
| `5` | `cinco` |
| `9` | `nove` |
| `0` | `Caractere desconhecido` |
| `a` | `Caractere desconhecido` |

---

## Conceitos abordados

- Dicionário (`dict`): criação, acesso por chave e operador `in`
- Por que chaves são strings quando os dados vêm da UART
- Separação entre **dados** (o dicionário) e **lógica** (o loop) — princípio que reaparecerá nos protocolos dos passos seguintes
- Extensibilidade: adicionar um novo comando exige apenas uma nova linha no dicionário, sem tocar na lógica

---

## Experimente

- Adicione o `'0'` ao dicionário com o valor `'zero'` e teste
- Adicione letras como chaves: `'a': 'alfa'`, `'b': 'bravo'` — o código não precisa de nenhuma outra mudança
- Tente acessar `digitos['x']` diretamente no Shell do Thonny (sem o `if in`) e observe o `KeyError`
- Reescreva o mesmo comportamento usando `if/elif` para todos os 9 dígitos — compare o tamanho dos dois códigos

---

## Próximo passo

No [Passo 4](../passo_04_parsing/README.md) o programa deixa de reagir a um único caractere e passa a ler **strings completas** terminadas por `'\n'`, separando comando e argumento — o primeiro passo rumo a um protocolo de comunicação real.
