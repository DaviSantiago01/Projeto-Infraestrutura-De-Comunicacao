import socket


DEFAULT_SERVER_HOST = "localhost"
SERVER_PORT = 12345
MIN_MESSAGE_LIMIT = 30
MODES = {
    "1": "Go-Back-N",
    "2": "Repeticao Seletiva",
}


def enviar_linha(writer, message):
    writer.write(message + "\n")
    writer.flush()


def receber_linha(reader):
    line = reader.readline()
    if line == "":
        raise ConnectionError("A conexao foi encerrada pelo servidor.")
    return line.strip()


def escolher_host_servidor():
    return input("Digite o host/IP do servidor [localhost]: ").strip() or DEFAULT_SERVER_HOST


def escolher_tamanho_maximo():
    while True:
        raw_value = input("Digite o tamanho maximo da mensagem em caracteres (minimo 30): ").strip()
        if not raw_value.isdigit():
            print("[!] Digite apenas numeros.")
            continue

        message_limit = int(raw_value)
        if message_limit < MIN_MESSAGE_LIMIT:
            print(f"[!] O tamanho minimo permitido e {MIN_MESSAGE_LIMIT} caracteres.")
            continue

        return message_limit


def escolher_modo_operacao():
    while True:
        print("\nEscolha o modo de operacao:")
        print("  1 - Go-Back-N")
        print("  2 - Repeticao Seletiva")
        mode_code = input("Opcao: ").strip()

        if mode_code in MODES:
            return mode_code

        print("[!] Opcao invalida. Escolha 1 ou 2.")


def montar_mensagem_handshake(message_limit, mode_code):
    return f"HANDSHAKE|MAX={message_limit}|MODE={mode_code}"


def interpretar_resposta_handshake(message):
    parts = message.split("|")
    if len(parts) != 3 or parts[0] != "HANDSHAKE_OK":
        return None

    fields = {}
    for part in parts[1:]:
        key, separator, value = part.partition("=")
        if separator != "=":
            return None
        fields[key] = value

    if "MAX" not in fields or "MODE" not in fields:
        return None

    return fields["MAX"], fields["MODE"]


def montar_mensagem_aplicacao(sequence_number, text):
    return f"MESSAGE|SEQ={sequence_number}|TEXT={text}"


def interpretar_resposta_aplicacao(message):
    parts = message.split("|", 2)
    if len(parts) != 3 or parts[0] not in {"ACK", "NACK"}:
        return None

    sequence_key, separator, sequence_value = parts[1].partition("=")
    detail_key, separator2, detail_value = parts[2].partition("=")
    if sequence_key != "SEQ" or separator != "=" or separator2 != "=":
        return None

    if not sequence_value.isdigit():
        return None

    return parts[0], int(sequence_value), detail_key, detail_value


def realizar_handshake(reader, writer, message_limit, mode_code):
    handshake_message = montar_mensagem_handshake(message_limit, mode_code)
    enviar_linha(writer, handshake_message)

    response = receber_linha(reader)
    if response.startswith("HANDSHAKE_ERROR|"):
        raise ValueError(response)

    parsed_response = interpretar_resposta_handshake(response)
    if parsed_response is None:
        raise ValueError(f"Resposta invalida do servidor: {response}")

    confirmed_limit, confirmed_mode = parsed_response
    print("[*] Handshake concluido com sucesso.")
    print(f"[*] Tamanho maximo confirmado pelo servidor: {confirmed_limit}")
    print(f"[*] Modo de operacao confirmado pelo servidor: {MODES.get(confirmed_mode, confirmed_mode)}")
    return int(confirmed_limit), confirmed_mode


def enviar_mensagens(reader, writer, message_limit):
    print("\n[*] Sessao de mensagens iniciada.")
    print("[*] Digite suas mensagens e pressione Enter para enviar.")
    print("[*] Digite 'sair' para encerrar a conexao.")

    sequence_number = 1

    while True:
        text = input("Mensagem: ").strip()
        if not text:
            print("[!] Digite uma mensagem nao vazia.")
            continue

        if text.lower() == "sair":
            enviar_linha(writer, "ENCERRAR|ORIGIN=CLIENTE")
            response = receber_linha(reader)
            if response == "ENCERRADO|STATUS=OK":
                print("[*] Conexao encerrada com sucesso.")
                return
            raise ValueError(f"Resposta invalida ao encerrar a conexao: {response}")

        if len(text) > message_limit:
            print(f"[!] A mensagem excede o limite negociado de {message_limit} caracteres.")
            continue

        application_message = montar_mensagem_aplicacao(sequence_number, text)
        enviar_linha(writer, application_message)

        response = receber_linha(reader)
        parsed_response = interpretar_resposta_aplicacao(response)
        if parsed_response is None:
            raise ValueError(f"Resposta invalida do servidor: {response}")

        response_type, confirmed_sequence, detail_key, detail_value = parsed_response
        if response_type == "ACK":
            print(f"[Servidor] ACK do pacote {confirmed_sequence}: {detail_value}")
            sequence_number += 1
        else:
            print(f"[Servidor] NACK do pacote {confirmed_sequence}: {detail_value}")


def iniciar_cliente():
    server_host = escolher_host_servidor()
    message_limit = escolher_tamanho_maximo()
    mode_code = escolher_modo_operacao()

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((server_host, SERVER_PORT))
            print(f"[*] Conectado ao servidor em {server_host}:{SERVER_PORT}.")

            with client_socket.makefile("r", encoding="utf-8", newline="\n") as reader:
                with client_socket.makefile("w", encoding="utf-8", newline="\n") as writer:
                    confirmed_limit, _confirmed_mode = realizar_handshake(reader, writer, message_limit, mode_code)
                    enviar_mensagens(reader, writer, confirmed_limit)
    except socket.gaierror:
        print("[!] Host ou IP invalido. Use localhost, 127.0.0.1 ou o IP do servidor.")
    except ConnectionRefusedError:
        print("[!] Nao foi possivel conectar. Verifique se o servidor esta em execucao.")
    except TimeoutError:
        print("[!] Tempo esgotado. Verifique o IP e se o servidor esta ativo.")
    except (ConnectionError, ValueError) as error:
        print(f"[!] Erro na comunicacao: {error}")


if __name__ == "__main__":
    iniciar_cliente()
