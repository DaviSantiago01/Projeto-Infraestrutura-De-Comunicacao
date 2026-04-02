# Projeto de Infraestrutura de Comunicação

## Visão geral
Este projeto implementa uma aplicação cliente-servidor em Python usando `socket`. O foco é evoluir uma comunicação simples para um protocolo de aplicação que simule transporte confiável.

## Como a comunicação foi pensada
Nesta entrega, o foco está na base da comunicação entre os dois processos:
- a aplicação segue o modelo cliente-servidor;
- a comunicação ocorre sobre TCP, usando sockets como interface entre processo e rede;
- o cliente inicia a conexão e o servidor permanece em escuta na porta `12345`;
- antes da troca de mensagens, cliente e servidor negociam os parâmetros da sessão por meio de um handshake;
- o protocolo da aplicação define tipos de mensagem, formato e regras de troca entre os processos.

## Grupo
Grupo 5

### Integrantes
- Lucas Samuel Pereira Alves
- Pedro Guerra
- Gabriel Assef
- Caio Costa
- Luís Eduardo Berard
- João Victor Guimarães
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
- trocar o modo de operação;
- trocar o tamanho máximo da comunicação.

### Foco desta primeira etapa
Nesta etapa, a ideia principal não é mostrar o transporte confiável completo, mas sim provar que a infraestrutura básica da comunicação já está funcionando:
- estabelecimento da conexão entre processos;
- uso correto de host, porta e socket;
- definição de um protocolo de aplicação simples;
- negociação inicial dos parâmetros da sessão.

### O que já está funcionando
- sobe um servidor TCP;
- conecta um cliente TCP;
- permite informar `localhost` ou IP no cliente;
- envia o tamanho máximo informado pelo usuário;
- envia o modo de operação escolhido pelo usuário;
- valida que o tamanho mínimo é `30`;
- confirma o handshake no servidor e no cliente.

### Manual de uso da Entrega 1

#### Requisitos
- Python 3 instalado;
- dois terminais abertos na pasta do projeto.

#### Observações importantes
- inicie o servidor antes do cliente;
- no Windows, use `py -3` se `python3` não estiver configurado;
- se cliente e servidor estiverem na mesma máquina, pressione `Enter` para usar `localhost`.

#### 1. Inicie o servidor
```bash
py -3 Servidor.py
```

#### 2. Inicie o cliente
```bash
py -3 Cliente.py
```

#### 3. Informe o host ou IP do servidor
Se cliente e servidor estiverem no mesmo computador, use `localhost`.
Se quiser usar o IP da rede local, confira primeiro o IPv4 atual da máquina do servidor.

Exemplos:

```text
Digite o host/IP do servidor [localhost]:
Digite o host/IP do servidor [localhost]: 192.168.0.10
```

#### 4. Informe o tamanho máximo
Exemplo:

```text
Digite o tamanho máximo da mensagem em caracteres (mínimo 30): 30
```

#### 5. Escolha o modo de operação
- `1` para `Go-Back-N`
- `2` para `Repetição Seletiva`

#### 6. Teste a sessão
- após o handshake, o cliente entra em loop de mensagens;
- cada mensagem respeita o limite negociado;
- digite `sair` para encerrar a sessão.

#### O que você deve ver
- o servidor deve indicar que está aguardando conexões;
- o cliente deve exibir a conexão com o servidor;
- o cliente e o servidor devem confirmar o handshake com `MAX` e `MODE`.

#### Demonstração rápida
- inicie o servidor;
- conecte o cliente usando `localhost`;
- informe um tamanho maior ou igual a `30`;
- escolha o modo `1` ou `2`;
- confirme que o handshake foi aceito nos dois lados.

### Como a comunicação acontece
1. o servidor abre o socket e entra em estado de espera;
2. o cliente abre a conexão TCP com o servidor;
3. o cliente envia a mensagem de handshake com `MAX` e `MODE`;
4. o servidor valida os dados recebidos;
5. o servidor responde com a confirmação do handshake;
6. a sessão fica pronta para a troca de mensagens.

### Handshake da Entrega 1
Handshake é a troca inicial de mensagens entre cliente e servidor para definir como a sessão vai funcionar.

Mensagem enviada pelo cliente:

```text
HANDSHAKE|MAX=30|MODE=1
```

Mensagem de confirmação enviada pelo servidor:

```text
HANDSHAKE_OK|MAX=30|MODE=1
```

### Observação sobre IA
Este projeto contou com apoio de IA para esclarecimento de requisitos, revisão textual e ajustes pontuais no código e na documentação.

## Entrega 2
Em desenvolvimento.

## Entrega 3
Em desenvolvimento.
