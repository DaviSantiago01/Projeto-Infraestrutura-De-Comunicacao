# Projeto de Infraestrutura de Comunicacao

## Visao geral
Este projeto implementa uma aplicacao cliente-servidor em Python usando `socket`. O foco e evoluir uma comunicacao simples para um protocolo de aplicacao que simule transporte confiavel.

## Grupo
Grupo 5

### Integrantes
- Lucas Samuel Pereira Alves
- Pedro Guerra
- Gabriel Assef
- Caio Costa
- Luis Eduardo Berard
- Joao Victor Guimaraes
- Eduardo Malheiros
- Davi Santiago Costa

## Estrutura do projeto

```text
.
|-- Cliente.py
|-- README.md
`-- Servidor.py
```


## Entrega 1 - Handshake inicial

### Escopo da entrega
Na primeira entrega, cliente e servidor devem:
- se conectar via socket;
- trocar o modo de operacao;
- trocar o tamanho maximo da comunicacao.

### O que o projeto atual ja faz
- sobe um servidor TCP;
- conecta um cliente TCP;
- permite informar `localhost` ou IP no cliente;
- envia o tamanho maximo informado pelo usuario;
- envia o modo de operacao escolhido pelo usuario;
- valida que o tamanho minimo e `30`;
- confirma o handshake no servidor e no cliente.

### Como executar a Entrega 1

#### 1. Inicie o servidor
```bash
py -3 Servidor.py
```

#### 2. Inicie o cliente
```bash
py -3 Cliente.py
```

#### 3. Informe o host ou IP do servidor
Exemplos:

```text
Digite o host/IP do servidor [localhost]:
Digite o host/IP do servidor [localhost]: 192.168.0.10
```

#### 4. Informe o tamanho maximo
Exemplo:

```text
Digite o tamanho maximo da mensagem em caracteres (minimo 30): 30
```

#### 5. Escolha o modo de operacao
- `1` para `Go-Back-N`
- `2` para `Repeticao Seletiva`

#### 6. Envie mensagens
- apos o handshake, o cliente entra em loop de mensagens;
- cada mensagem respeita o limite negociado;
- digite `sair` para encerrar a sessao.

### Protocolo de handshake da Entrega 1
Mensagem enviada pelo cliente:

```text
HANDSHAKE|MAX=30|MODE=1
```

Mensagem de confirmacao enviada pelo servidor:

```text
HANDSHAKE_OK|MAX=30|MODE=1
```


## Entrega 2
Em desenvolvimento.

## Entrega 3
Em desenvolvimento.
