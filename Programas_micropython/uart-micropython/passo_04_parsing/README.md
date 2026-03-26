# Passo 4 — Parsing de Comandos com Terminador

## Objetivo

Deixar o mundo do caractere único e passar a trabalhar com **mensagens completas**. O dispositivo acumula bytes em um buffer até receber `'\n'` (Enter), então interpreta a mensagem inteira separando **comando** e **argumento**.

Este é o passo em que a comunicação começa a parecer um protocolo de verdade.

---

## O que muda em relação ao passo 3?

| | Passo 3 | Passo 4 |
|---|---|---|
| Unidade de dados | 1 caractere | String completa até `'\n'` |
| Estrutura da mensagem | Char isolado | `COMANDO:ARGUMENTO` |
| Buffer | Não há | Acumula bytes entre recepções |
| Extensibilidade | Dicionário de chars | Dicionário de funções |

---

## Por que precisamos de um terminador?

A UART é um fluxo contínuo de bytes — ela não tem noção de "início" ou "fim" de mensagem. Se o aluno digita `LED:L`, chegam 5 bytes separados: `L`, `E`, `D`, `:`, `L`. O receptor precisa de uma convenção para saber quando a mensagem está completa.

O `'\n'` (caractere de nova linha, gerado pelo Enter) é o terminador mais comum em protocolos textuais — é o mesmo usado por HTTP, SMTP, e muitos outros.

```
Bytes chegando pela UART, um a um:
  'L' → acumula
  'E' → acumula
  'D' → acumula
  ':' → acumula
  'L' → acumula
  '\n'→ PROCESSA o buffer "LED:L"
```

---

## Formato do comando

```
COMANDO:ARGUMENTO\n
```

| Parte | Exemplo | Descrição |
|-------|---------|-----------|
| `COMANDO` | `LED` | Identificador da ação (maiúsculas) |
| `:` | `:` | Separador fixo |
| `ARGUMENTO` | `L` | Parâmetro da ação |
| `\n` | Enter | Terminador de mensagem |

### Comandos disponíveis

| Comando | Argumento | Ação |
|---------|-----------|------|
| `LED` | `L` | Liga o LED |
| `LED` | `D` | Desliga o LED |
| `MSG` | qualquer texto | Exibe o texto no Shell |

---

## Estrutura do código

```
passo_04_parsing/
└── parsing_uart.py
```

### Fluxo de execução

```
Byte chega pela UART
        │
        ├── char != '\n' ──► Acumula no buffer
        │
        └── char == '\n' ──► Processa o buffer
                                    │
                                    ▼
                            linha.split(':', 1)
                                    │
                              ┌─────┴──────┐
                           comando      argumento
                              │
                        comando in comandos?
                              │
                    Sim ──────┴────── Não
                     │                 │
              Chama função       "Comando desconhecido"
                     │
                Retorna resposta
                     │
              uart.write(resposta)
              Limpa buffer
```

### Por que `split(':', 1)`?

O `1` limita a divisão a **uma única ocorrência** do separador. Assim, um argumento como `MSG:http://exemplo.com` é dividido corretamente em `'MSG'` e `'http://exemplo.com'` — e não em três partes.

### Por que as funções de comando em um dicionário?

```python
comandos = {
    'LED': cmd_led,
    'MSG': cmd_msg,
}
```

Em vez de um `if/elif` para cada comando, o dicionário mapeia diretamente o nome da função. Adicionar um novo comando é só escrever a função e registrá-la — sem tocar na lógica de parsing. Esse padrão é chamado de **despacho por tabela** (*dispatch table*) e é muito usado em implementações de protocolos.

---

## Constantes configuráveis

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
4. No Shell do Thonny, digite os comandos e pressione Enter:

| Você digita + Enter | Placa responde |
|---------------------|----------------|
| `LED:L` | `LED ligado` |
| `LED:D` | `LED desligado` |
| `MSG:olá mundo` | `Mensagem recebida: olá mundo` |
| `LED:X` | `Argumento inválido para LED: 'X'` |
| `FOO:bar` | `Comando desconhecido: 'FOO'` |
| `semduopontos` | `Formato inválido. Use COMANDO:ARGUMENTO` |

---

## Conceitos abordados

- Buffer de recepção: acumular bytes até uma condição ser satisfeita
- Terminador de mensagem: a convenção que define o fim de um quadro
- `str.split(':', 1)`: divisão controlada com limite
- `str.strip()`: remoção de `'\r'` residual (comum em terminais Windows)
- Despacho por tabela: dicionário de funções como alternativa ao `if/elif`
- Separação de responsabilidades: parsing separado da execução

---

## Experimente

- Adicione um comando `PWM:valor` que ajusta o brilho do LED com `Pin` em modo PWM
- Envie `LED:L\rLED:D` sem pressionar Enter entre eles — o que acontece?
- Remova o `.strip()` da função `processar` e envie um comando pelo terminal serial do sistema operacional (que costuma adicionar `'\r\n'`) — observe o comportamento

---

## Próximo passo

No [Passo 5](../passo_05_maquina_estados/README.md) o programa ganha uma **máquina de estados** formal — separando os momentos em que está ocioso, recebendo dados e processando uma mensagem. Isso elimina comportamentos inesperados quando bytes chegam em rajadas ou fora de ordem.
