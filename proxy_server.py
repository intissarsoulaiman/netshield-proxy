# NetShield Proxy
# Contributor: Intissar
# Role: Socket server, threaded client handling, request receiving, forwarding integration

import socket
import threading
from core.request_parser import parse_http_request
from core.http_handler import forward_http_request
from core.filter_manager import is_blocked, build_blocked_response
from core import logger_manager, filter_manager

HOST = "127.0.0.1"
PORT = 8080
BUFFER_SIZE = 4096


def build_error_response(message):
    body = f"""
    <html>
        <head><title>Proxy Error</title></head>
        <body>
            <h1>502 Bad Gateway</h1>
            <p>{message}</p>
        </body>
    </html>
    """

    response = (
        "HTTP/1.1 502 Bad Gateway\r\n"
        "Content-Type: text/html\r\n"
        f"Content-Length: {len(body.encode())}\r\n"
        "Connection: close\r\n"
        "\r\n"
        + body
    )

    return response.encode()


def handle_client(client_socket, client_address):
    client_ip, client_port = client_address

    print(f"Client connected: {client_address}")

    try:
        request_bytes = client_socket.recv(BUFFER_SIZE)

        if not request_bytes:
            return

        print("\nRaw request:")
        print(request_bytes)

        parsed = parse_http_request(request_bytes)

        if "error" in parsed:
            raise Exception(parsed["error"])

        print("\nParsed request:")
        for key, value in parsed.items():
            print(f"{key}: {value}")

        method = parsed["method"]
        host = parsed["host"]
        port = parsed["port"]
        url = parsed["full_url"]

        filter_manager.reload_lists()

        if is_blocked(host):
            blocked_response = build_blocked_response(host)
            client_socket.sendall(blocked_response)

            logger_manager.log_event(
                client_ip=client_ip,
                client_port=client_port,
                target_host=host,
                target_port=port,
                method=method,
                url=url,
                error="BLOCKED"
            )

            print(f"Blocked request to: {host}")
            return

        response = forward_http_request(parsed)
        client_socket.sendall(response)

        logger_manager.log_event(
            client_ip=client_ip,
            client_port=client_port,
            target_host=host,
            target_port=port,
            method=method,
            url=url,
            error=""
        )

        print(f"Forwarded successfully: {method} {url}")

    except Exception as e:
        error_message = str(e)
        print("Error:", error_message)

        try:
            target_host = parsed.get("host", "unknown") if "parsed" in locals() else "unknown"
            target_port = parsed.get("port", 0) if "parsed" in locals() else 0
            method = parsed.get("method", "") if "parsed" in locals() else ""
            url = parsed.get("full_url", "") if "parsed" in locals() else ""

            logger_manager.log_event(
                client_ip=client_ip,
                client_port=client_port,
                target_host=target_host,
                target_port=target_port,
                method=method,
                url=url,
                error=error_message
            )
        except Exception as log_error:
            print("Logging error:", log_error)

        try:
            client_socket.sendall(build_error_response(error_message))
        except Exception:
            pass

    finally:
        try:
            client_socket.close()
        except Exception:
            pass

        print(f"Connection closed: {client_address}\n")


def start_proxy_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(20)

    print(f"Server running on {HOST}:{PORT}")
    print("Waiting for connections...")

    try:
        while True:
            client_socket, client_address = server_socket.accept()

            # Intissar - Day 3 multithreading
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address),
                daemon=True
            )
            client_thread.start()

    except KeyboardInterrupt:
        print("\nServer stopped by user.")

    finally:
        server_socket.close()


if __name__ == "__main__":
    start_proxy_server()