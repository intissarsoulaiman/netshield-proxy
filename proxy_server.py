# NetShield Proxy
# Contributor: Intissar
# Role: Socket server, client handling, request receiving

import socket
from core.request_parser import parse_http_request

HOST = "127.0.0.1"
PORT = 8080
BUFFER_SIZE = 4096


def start_proxy_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print(f"Server running on {HOST}:{PORT}")
    print("Waiting for connections...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Client connected: {client_address}")

        try:
            request_bytes = client_socket.recv(BUFFER_SIZE)

            if not request_bytes:
                client_socket.close()
                continue

            print("\nRaw request:")
            print(request_bytes)

            parsed = parse_http_request(request_bytes)

            print("\nParsed request:")
            for key, value in parsed.items():
                print(f"{key}: {value}")

            response_body = b"Proxy received your request"
            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/plain\r\n"
                b"Content-Length: " + str(len(response_body)).encode() + b"\r\n"
                b"\r\n" +
                response_body
            )

            client_socket.sendall(response)

        except Exception as e:
            print("Error:", e)

        finally:
            client_socket.close()
            print("Connection closed\n")


if __name__ == "__main__":
    start_proxy_server()