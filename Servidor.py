import socket
import threading


HOST_ESCUTA = "0.0.0.0"  # Escuta conexoes por localhost e pelos IPs da maquina.
PORTA_SERVIDOR = 5000
LIMITE_MINIMO_MENSAGEM = 30
TAMANHO_PACOTE = 4
MODOS = {
    "1": "Go-Back-N",
    "2": "Repeticao Seletiva",
}


def enviar_linha(escritor, mensagem):
    escritor.write(mensagem + "\n")
    escritor.flush()


def receber_linha(leitor):
    linha = leitor.readline()
    if linha == "":
        raise ConnectionError("O cliente encerrou a conexao.")
    return linha.strip()


def separar_endereco(endereco_cliente):
    ip_cliente, porta_cliente = endereco_cliente
    return ip_cliente, porta_cliente


def interpretar_modo(codigo_modo):
    return MODOS.get(codigo_modo, f"Desconhecido ({codigo_modo})")


def interpretar_handshake(mensagem):
    partes = mensagem.split("|")
    if len(partes) != 3 or partes[0] != "HANDSHAKE":
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


def interpretar_pacote(mensagem):
    partes = mensagem.split("|", 3)
    if len(partes) != 4 or partes[0] != "PACOTE":
        return None

    chave_sequencia, separador, valor_sequencia = partes[1].partition("=")
    chave_ultimo, separador2, valor_ultimo = partes[2].partition("=")
    chave_texto, separador3, carga_util = partes[3].partition("=")
    if chave_sequencia != "SEQ" or separador != "=":
        return None

    if chave_ultimo != "LAST" or separador2 != "=" or valor_ultimo not in {"0", "1"}:
        return None

    if chave_texto != "TEXT" or separador3 != "=":
        return None

    if not valor_sequencia.isdigit():
        return None

    return int(valor_sequencia), valor_ultimo == "1", carga_util


def validar_handshake(mensagem):
    dados_handshake = interpretar_handshake(mensagem)
    if dados_handshake is None:
        return None, "formato invalido de handshake"

    tamanho_bruto, codigo_modo = dados_handshake
    if not tamanho_bruto.isdigit():
        return None, "tamanho maximo invalido"

    tamanho_maximo = int(tamanho_bruto)
    if tamanho_maximo < LIMITE_MINIMO_MENSAGEM:
        return None, f"tamanho minimo deve ser {LIMITE_MINIMO_MENSAGEM}"

    if codigo_modo not in MODOS:
        return None, "modo de operacao invalido"

    return (tamanho_maximo, codigo_modo), None


def processar_mensagens(leitor, escritor, endereco_cliente, tamanho_maximo):
    partes_recebidas = []
    tamanho_recebido = 0
    ip_cliente, porta_cliente = separar_endereco(endereco_cliente)

    while True:
        mensagem = receber_linha(leitor)

        if mensagem == "ENCERRAR|ORIGIN=CLIENTE":
            enviar_linha(escritor, "ENCERRADO|STATUS=OK")
            print("\n[CONEXAO]")
            print(f"Cliente ........... {ip_cliente}")
            print(f"Porta cliente ..... {porta_cliente}")
            print("Status ............ encerrada pelo cliente")
            return

        dados_pacote = interpretar_pacote(mensagem)
        if dados_pacote is None:
            enviar_linha(escritor, "NACK|SEQ=0|ERROR=FORMATO_INVALIDO")
            print("\n[ERRO]")
            print(f"Cliente ........... {ip_cliente}")
            print("Motivo ............ pacote malformado")
            print(f"Recebido .......... {mensagem}")
            continue

        sequencia, ultimo_pacote, carga_util = dados_pacote
        if len(carga_util) > TAMANHO_PACOTE:
            enviar_linha(escritor, f"NACK|SEQ={sequencia}|ERROR=PACOTE_MUITO_GRANDE")
            print("\n[ERRO]")
            print(f"Pacote ............ {sequencia}")
            print(f"Motivo ............ carga maior que {TAMANHO_PACOTE} caracteres")
            continue

        if tamanho_recebido + len(carga_util) > tamanho_maximo:
            enviar_linha(escritor, f"NACK|SEQ={sequencia}|ERROR=LIMITE_EXCEDIDO")
            print("\n[ERRO]")
            print(f"Pacote ............ {sequencia}")
            print(f"Motivo ............ limite negociado excedido")
            partes_recebidas = []
            tamanho_recebido = 0
            continue

        partes_recebidas.append(carga_util)
        tamanho_recebido += len(carga_util)

        print("\n[PACOTE RECEBIDO]")
        print(f"Cliente ........... {ip_cliente}")
        print(f"Porta cliente ..... {porta_cliente}")
        print(f"Porta servidor .... {PORTA_SERVIDOR}")
        print(f"Sequencia ......... {sequencia}")
        print(f"Carga util ........ {carga_util}")
        print(f"Tamanho ........... {len(carga_util)}")
        print(f"Ultimo pacote ..... {'sim' if ultimo_pacote else 'nao'}")

        enviar_linha(escritor, f"ACK|SEQ={sequencia}|STATUS=RECEBIDA")

        if ultimo_pacote:
            mensagem_completa = "".join(partes_recebidas)
            print("\n[MENSAGEM REMONTADA]")
            print(f"Cliente ........... {ip_cliente}")
            print(f"Texto completo .... {mensagem_completa}")
            print(f"Tamanho total ..... {len(mensagem_completa)} caracteres")
            partes_recebidas = []
            tamanho_recebido = 0


def processar_cliente(socket_cliente, endereco_cliente):
    ip_cliente, porta_cliente = separar_endereco(endereco_cliente)
    print("\n[CONEXAO]")
    print(f"Cliente ........... {ip_cliente}")
    print(f"Porta cliente ..... {porta_cliente}")
    print(f"Porta servidor .... {PORTA_SERVIDOR}")
    print("Status ............ conectada")

    with socket_cliente:
        with socket_cliente.makefile("r", encoding="utf-8", newline="\n") as leitor:
            with socket_cliente.makefile("w", encoding="utf-8", newline="\n") as escritor:
                try:
                    mensagem_handshake = receber_linha(leitor)
                    dados_handshake, mensagem_erro = validar_handshake(mensagem_handshake)

                    if mensagem_erro is not None:
                        enviar_linha(escritor, f"HANDSHAKE_ERROR|MESSAGE={mensagem_erro}")
                        print("\n[HANDSHAKE]")
                        print(f"Cliente ........... {ip_cliente}")
                        print("Status ............ rejeitado")
                        print(f"Motivo ............ {mensagem_erro}")
                        return

                    tamanho_maximo, codigo_modo = dados_handshake
                    nome_modo = interpretar_modo(codigo_modo)

                    print("\n[HANDSHAKE]")
                    print(f"Cliente ........... {ip_cliente}")
                    print("Status ............ confirmado")
                    print(f"Limite ............ {tamanho_maximo} caracteres")
                    print(f"Modo .............. {nome_modo}")

                    confirmacao = f"HANDSHAKE_OK|MAX={tamanho_maximo}|MODE={codigo_modo}"
                    enviar_linha(escritor, confirmacao)

                    processar_mensagens(leitor, escritor, endereco_cliente, tamanho_maximo)
                except (ConnectionError, ValueError) as erro:
                    print("\n[ERRO]")
                    print(f"Cliente ........... {ip_cliente}")
                    print(f"Motivo ............ {erro}")
                finally:
                    print("\n[CONEXAO]")
                    print(f"Cliente ........... {ip_cliente}")
                    print(f"Porta cliente ..... {porta_cliente}")
                    print("Status ............ finalizada")


def iniciar_servidor():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_servidor:
        socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_servidor.bind((HOST_ESCUTA, PORTA_SERVIDOR))
        socket_servidor.listen()

        print("[SERVIDOR]")
        print(f"Host .............. {HOST_ESCUTA}")
        print(f"Porta ............. {PORTA_SERVIDOR}")
        print("Status ............ aguardando conexoes")

        while True:
            socket_cliente, endereco_cliente = socket_servidor.accept()
            # Cada cliente e atendido em uma thread separada para nao bloquear novas conexoes.
            thread_cliente = threading.Thread(
                target=processar_cliente,
                args=(socket_cliente, endereco_cliente),
            )
            thread_cliente.start()


if __name__ == "__main__":
    iniciar_servidor()
