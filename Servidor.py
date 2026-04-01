import socket
import threading


LISTEN_HOST = "0.0.0.0"
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
        raise ConnectionError("O cliente encerrou a conexao.")
    return line.strip()


def interpretar_modo(mode_code):
    return MODES.get(mode_code, f"Desconhecido ({mode_code})")


def interpretar_mensagem_handshake(message):
    parts = message.split("|")
    if len(parts) != 3 or parts[0] != "HANDSHAKE":
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


def interpretar_mensagem_aplicacao(message):
    parts = message.split("|", 2)
    if len(parts) != 3 or parts[0] != "MESSAGE":
        return None

    sequence_key, separator, sequence_value = parts[1].partition("=")
    text_key, separator2, text_value = parts[2].partition("=")
    if sequence_key != "SEQ" or separator != "=" or text_key != "TEXT" or separator2 != "=":
        return None

    if not sequence_value.isdigit():
        return None

    return int(sequence_value), text_value


def validar_handshake(message):
    parsed_message = interpretar_mensagem_handshake(message)
    if parsed_message is None:
        return None, "formato invalido de handshake"

    raw_limit, mode_code = parsed_message
    if not raw_limit.isdigit():
        return None, "tamanho maximo invalido"

    message_limit = int(raw_limit)
    if message_limit < MIN_MESSAGE_LIMIT:
        return None, f"tamanho minimo deve ser {MIN_MESSAGE_LIMIT}"

    if mode_code not in MODES:
        return None, "modo de operacao invalido"

    return (message_limit, mode_code), None


def processar_mensagens(reader, writer, client_address, message_limit):
    while True:
        message = receber_linha(reader)

        if message == "ENCERRAR|ORIGIN=CLIENTE":
            enviar_linha(writer, "ENCERRADO|STATUS=OK")
            print(f"[*] Cliente {client_address} solicitou o encerramento da sessao.")
            return

        parsed_message = interpretar_mensagem_aplicacao(message)
        if parsed_message is None:
            enviar_linha(writer, "NACK|SEQ=0|ERROR=FORMATO_INVALIDO")
            print(f"[!] Mensagem invalida recebida de {client_address}: {message}")
            continue

        sequence_number, text = parsed_message
        if len(text) > message_limit:
            enviar_linha(writer, f"NACK|SEQ={sequence_number}|ERROR=LIMITE_EXCEDIDO")
            print(f"[!] Pacote {sequence_number} excedeu o limite negociado para {client_address}.")
            continue

        print("[*] Pacote de aplicacao recebido.")
        print(f"[*] Cliente: {client_address}")
        print(f"[*] Sequencia: {sequence_number}")
        print(f"[*] Tamanho da mensagem: {len(text)}")
        print(f"[*] Conteudo: {text}")

        enviar_linha(writer, f"ACK|SEQ={sequence_number}|STATUS=RECEBIDA")


def processar_cliente(client_socket, client_address):
    print(f"[+] Conexao estabelecida com {client_address}")

    with client_socket:
        with client_socket.makefile("r", encoding="utf-8", newline="\n") as reader:
            with client_socket.makefile("w", encoding="utf-8", newline="\n") as writer:
                try:
                    handshake_message = receber_linha(reader)
                    handshake_data, error_message = validar_handshake(handshake_message)

                    if error_message is not None:
                        enviar_linha(writer, f"HANDSHAKE_ERROR|MESSAGE={error_message}")
                        print(f"[!] Handshake rejeitado para {client_address}: {error_message}")
                        return

                    message_limit, mode_code = handshake_data
                    mode_name = interpretar_modo(mode_code)

                    print("[*] Handshake recebido com sucesso.")
                    print(f"[*] Cliente: {client_address}")
                    print(f"[*] Tamanho maximo negociado: {message_limit} caracteres")
                    print(f"[*] Modo de operacao negociado: {mode_name}")

                    confirmation = f"HANDSHAKE_OK|MAX={message_limit}|MODE={mode_code}"
                    enviar_linha(writer, confirmation)
                    print(f"[*] Confirmacao de handshake enviada para {client_address}")

                    processar_mensagens(reader, writer, client_address, message_limit)
                except (ConnectionError, ValueError) as error:
                    print(f"[!] Falha ao processar o cliente {client_address}: {error}")
                finally:
                    print(f"[-] Conexao encerrada com {client_address}")


def iniciar_servidor():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((LISTEN_HOST, SERVER_PORT))
        server_socket.listen()

        print(f"[*] Servidor aguardando conexoes na porta {SERVER_PORT}.")
        print("[*] Aceita conexoes por localhost ou por IP da maquina.")

        while True:
            client_socket, client_address = server_socket.accept()
            # Cada cliente e atendido em uma thread separada para nao bloquear novas conexoes.
            client_thread = threading.Thread(
                target=processar_cliente,
                args=(client_socket, client_address),
            )
            client_thread.start()


if __name__ == "__main__":
    iniciar_servidor()
