import socket


HOST_PADRAO_SERVIDOR = "localhost"
PORTA_PADRAO_SERVIDOR = 5000
LIMITE_MINIMO_MENSAGEM = 30
TAMANHO_PACOTE = 4
MODOS = {
    "1": "Go-Back-N",
    "2": "Repeticao Seletiva",
}


def enviar_linha(escritor, mensagem):
    # O protocolo usa uma mensagem por linha para evitar ambiguidades na leitura via TCP.
    escritor.write(mensagem + "\n")
    escritor.flush()


def receber_linha(leitor):
    linha = leitor.readline()
    if linha == "":
        raise ConnectionError("A conexao foi encerrada pelo servidor.")
    return linha.strip()


def escolher_host_servidor():
    return input("Digite o host/IP do servidor [localhost]: ").strip() or HOST_PADRAO_SERVIDOR


def escolher_tamanho_maximo():
    while True:
        valor = input("Digite o tamanho maximo da mensagem em caracteres (minimo 30): ").strip()
        if not valor.isdigit():
            print("Erro .............. digite apenas numeros.")
            continue

        tamanho_maximo = int(valor)
        if tamanho_maximo < LIMITE_MINIMO_MENSAGEM:
            print(f"Erro .............. tamanho minimo: {LIMITE_MINIMO_MENSAGEM} caracteres.")
            continue

        return tamanho_maximo


def escolher_modo_operacao():
    while True:
        print("\nEscolha o modo de operacao:")
        print("  1 - Go-Back-N")
        print("  2 - Repeticao Seletiva")
        codigo_modo = input("Opcao: ").strip()

        if codigo_modo in MODOS:
            return codigo_modo

        print("Erro .............. escolha 1 ou 2.")


def montar_handshake(tamanho_maximo, codigo_modo):
    return f"HANDSHAKE|MAX={tamanho_maximo}|MODE={codigo_modo}"


def interpretar_confirmacao_handshake(mensagem):
    partes = mensagem.split("|")
    if len(partes) != 3 or partes[0] != "HANDSHAKE_OK":
        return None

    campos = {}
    for parte in partes[1:]:
        chave, separador, valor = parte.partition("=")
        if separador != "=":
            return None
        campos[chave] = valor

    if "MAX" not in campos or "MODE" not in campos:
        return None

    return campos["MAX"], campos["MODE"]


def dividir_em_pacotes(texto):
    return [texto[indice:indice + TAMANHO_PACOTE] for indice in range(0, len(texto), TAMANHO_PACOTE)]


def montar_pacote(sequencia, carga_util, ultimo_pacote):
    marcador_final = "1" if ultimo_pacote else "0"
    return f"PACOTE|SEQ={sequencia}|LAST={marcador_final}|TEXT={carga_util}"


def interpretar_confirmacao_pacote(mensagem):
    partes = mensagem.split("|", 2)
    if len(partes) != 3 or partes[0] not in {"ACK", "NACK"}:
        return None

    chave_sequencia, separador, valor_sequencia = partes[1].partition("=")
    chave_detalhe, separador2, valor_detalhe = partes[2].partition("=")
    if chave_sequencia != "SEQ" or separador != "=" or separador2 != "=":
        return None

    if not valor_sequencia.isdigit():
        return None

    return partes[0], int(valor_sequencia), chave_detalhe, valor_detalhe


def realizar_handshake(leitor, escritor, tamanho_maximo, codigo_modo):
    # Na Entrega 1, o handshake negocia apenas o tamanho maximo e o modo de operacao.
    mensagem_handshake = montar_handshake(tamanho_maximo, codigo_modo)
    enviar_linha(escritor, mensagem_handshake)

    resposta = receber_linha(leitor)
    if resposta.startswith("HANDSHAKE_ERROR|"):
        raise ValueError(resposta)

    confirmacao = interpretar_confirmacao_handshake(resposta)
    if confirmacao is None:
        raise ValueError(f"Resposta invalida do servidor: {resposta}")

    tamanho_confirmado, modo_confirmado = confirmacao
    print("\n[HANDSHAKE]")
    print("Status ............ confirmado")
    print(f"Limite ............ {tamanho_confirmado} caracteres")
    print(f"Modo .............. {MODOS.get(modo_confirmado, modo_confirmado)}")
    return int(tamanho_confirmado), modo_confirmado


def enviar_mensagens(leitor, escritor, tamanho_maximo):
    print("\n[MENSAGEM]")
    print("Digite o texto da comunicacao.")
    print("Use 'sair' para encerrar.")

    sequencia = 1

    while True:
        texto = input("Texto > ").strip()
        if not texto:
            print("Erro .............. digite uma mensagem nao vazia.")
            continue

        if texto.lower() == "sair":
            enviar_linha(escritor, "ENCERRAR|ORIGIN=CLIENTE")
            resposta = receber_linha(leitor)
            if resposta == "ENCERRADO|STATUS=OK":
                print("\n[CONEXAO]")
                print("Status ............ encerrada")
                return
            raise ValueError(f"Resposta invalida ao encerrar a conexao: {resposta}")

        if len(texto) > tamanho_maximo:
            print(f"Erro .............. mensagem acima do limite de {tamanho_maximo} caracteres.")
            continue

        pacotes = dividir_em_pacotes(texto)
        print("\n[ENVIO]")
        print(f"Mensagem original . {texto}")
        print(f"Total de pacotes .. {len(pacotes)}")
        print(f"Carga por pacote .. ate {TAMANHO_PACOTE} caracteres")
        print("\n[PACOTES ENVIADOS]")

        for indice, carga_util in enumerate(pacotes):
            ultimo_pacote = indice == len(pacotes) - 1
            mensagem_aplicacao = montar_pacote(sequencia, carga_util, ultimo_pacote)
            print(f"\nSeq ............... {sequencia}")
            print(f"Carga util ........ {carga_util}")
            print(f"Tamanho ........... {len(carga_util)}")
            print(f"Ultimo pacote ..... {'sim' if ultimo_pacote else 'nao'}")
            enviar_linha(escritor, mensagem_aplicacao)

            resposta = receber_linha(leitor)
            resposta_interpretada = interpretar_confirmacao_pacote(resposta)
            if resposta_interpretada is None:
                raise ValueError(f"Resposta invalida do servidor: {resposta}")

            tipo_resposta, sequencia_confirmada, _chave_detalhe, valor_detalhe = resposta_interpretada
            if tipo_resposta == "ACK":
                print(f"Confirmacao ....... ACK ({valor_detalhe})")
                sequencia += 1
            else:
                print(f"Confirmacao ....... NACK ({valor_detalhe})")
                break


def iniciar_cliente():
    host_servidor = escolher_host_servidor()
    tamanho_maximo = escolher_tamanho_maximo()
    codigo_modo = escolher_modo_operacao()

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_cliente:
            socket_cliente.connect((host_servidor, PORTA_PADRAO_SERVIDOR))
            print("\n[CLIENTE]")
            print(f"Servidor .......... {host_servidor}:{PORTA_PADRAO_SERVIDOR}")
            print("Conexao ........... OK")

            with socket_cliente.makefile("r", encoding="utf-8", newline="\n") as leitor:
                with socket_cliente.makefile("w", encoding="utf-8", newline="\n") as escritor:
                    tamanho_confirmado, _modo_confirmado = realizar_handshake(
                        leitor,
                        escritor,
                        tamanho_maximo,
                        codigo_modo,
                    )
                    enviar_mensagens(leitor, escritor, tamanho_confirmado)
    except socket.gaierror:
        print("Erro .............. host ou IP invalido.")
    except ConnectionRefusedError:
        print("Erro .............. servidor indisponivel.")
    except TimeoutError:
        print("Erro .............. tempo de conexao esgotado.")
    except (ConnectionError, ValueError) as erro:
        print(f"Erro .............. {erro}")


if __name__ == "__main__":
    iniciar_cliente()
