# Projeto de Infraestrutura de Comunicação

Aplicação cliente-servidor em Python usando `socket`. O projeto simula, na camada de aplicação, a base de um protocolo de transporte confiável.

## Estrutura

```text
.
|-- Cliente.py
|-- README.md
`-- Servidor.py
```

## Versão Atual

O sistema já permite:

- conexão cliente-servidor via socket TCP;
- uso de `localhost` ou IP da máquina do servidor;
- uso da porta padrão `5000`;
- handshake inicial com tamanho máximo e modo de operação;
- validação do tamanho mínimo de `30` caracteres;
- envio de mensagens em pacotes de até `4` caracteres;
- confirmação de cada pacote com `ACK`;
- remontagem da mensagem completa no servidor.

## Como Executar

Abra dois terminais na pasta do projeto.

No primeiro terminal, inicie o servidor:

```bash
py -3 Servidor.py
```

No segundo terminal, inicie o cliente:

```bash
py -3 Cliente.py
```

Durante a execução do cliente:

- pressione `Enter` no host para usar `localhost`;
- informe um tamanho máximo maior ou igual a `30`;
- escolha `1` para Go-Back-N ou `2` para Repetição Seletiva;
- digite uma mensagem para enviar;
- digite `sair` para encerrar a conexão.

## Entrega 1 - Handshake

Nesta etapa, cliente e servidor devem se conectar e trocar os dados iniciais da sessão.

O handshake usado no projeto segue este formato:

```text
HANDSHAKE|MAX=30|MODE=1
```

O servidor responde:

```text
HANDSHAKE_OK|MAX=30|MODE=1
```

Esses campos indicam:

- `MAX`: tamanho máximo da comunicação definido pelo cliente;
- `MODE`: modo de operação escolhido, sendo `1` para Go-Back-N e `2` para Repetição Seletiva.

## Entrega 2 - Troca de Mensagens

Nesta etapa, a comunicacao considera um canal sem erros e sem perdas.

Depois do handshake, o cliente pode digitar mensagens em loop. Cada mensagem e quebrada em pacotes de ate `4` caracteres. O cliente mostra os metadados de cada pacote enviado. O servidor recebe os pacotes, imprime seus metadados, confirma cada um com `ACK` e remonta a mensagem completa no final.

Nesta versao, o modo escolhido no handshake fica registrado na sessao. A diferenca completa entre Go-Back-N e Repeticao Seletiva sera implementada na proxima etapa, junto com erros, perdas e retransmissao.

Exemplo com a mensagem `infraestrutura`:

```text
Pacote 1: infr
Pacote 2: aest
Pacote 3: rutu
Pacote 4: ra
```

## Entrega 3

Em desenvolvimento.
