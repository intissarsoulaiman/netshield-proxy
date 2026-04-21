# NetShield Proxy
# Contributor: Intissar
# Role: Core proxy server, request parsing integration, HTTP forwarding foundation

# NetShield Proxy
# Contributor: Intissar (Tesh role)
# Role: Core proxy server, request parsing integration, HTTP forwarding foundation

import socket
from core.request_parser import parse_http_request

HOST = "127.0.0.1"
PORT = 8080
BUFFER_SIZE = 4096


def start_proxy_server():
    """Start a basic proxy socket server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print(f"[STARTED] Proxy server running on {HOST}:{PORT}")
    print("[WAITING] Listening for client connections...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"[CONNECTED] Client connected from {client_address}")

        try:
            request_bytes = client_socket.recv(BUFFER_SIZE)

            if not request_bytes:
                print("[WARNING] Empty request received.")
                client_socket.close()
                continue

            print("\n[RAW REQUEST BYTES]")
            print(request_bytes)

            parsed_request = parse_http_request(request_bytes)

            print("\n[PARSED REQUEST]")
            for key, value in parsed_request.items():
                print(f"{key}: {value}")

            response_body = b"NetShield Proxy received your request successfully."
            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/plain\r\n"
                b"Content-Length: " + str(len(response_body)).encode() + b"\r\n"
                b"Connection: close\r\n\r\n" +
                response_body
            )

            client_socket.sendall(response)

        except Exception as error:
            print(f"[ERROR] {error}")

        finally:
            client_socket.close()
            print("[CLOSED] Client connection closed.\n")


if __name__ == "__main__":
    start_proxy_server()