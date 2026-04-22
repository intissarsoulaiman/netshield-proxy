# NetShield Proxy
# Contributor: Intissar
# Role: HTTP forwarding to target server and returning response to client

import socket

BUFFER_SIZE = 4096
SOCKET_TIMEOUT = 10


def build_forward_request(parsed_request):
    method = parsed_request["method"]
    version = parsed_request["version"]
    normalized_path = parsed_request["normalized_path"]
    headers = parsed_request["headers"].copy()
    body = parsed_request.get("body", b"")

    # Remove proxy-only / hop-by-hop headers
    hop_by_hop = [
        "Proxy-Connection",
        "Connection",
        "Keep-Alive",
        "TE",
        "Trailer",
        "Transfer-Encoding",
        "Upgrade",
    ]
    for header in hop_by_hop:
        headers.pop(header, None)

    # Set standard connection behavior
    headers["Connection"] = "close"

    # Ensure Host header is clean
    host = parsed_request["host"]
    port = parsed_request["port"]
    if port != 80:
        headers["Host"] = f"{host}:{port}"
    else:
        headers["Host"] = host

    request_line = f"{method} {normalized_path} {version}\r\n"
    headers_blob = "".join(f"{k}: {v}\r\n" for k, v in headers.items())
    final_request = (request_line + headers_blob + "\r\n").encode("iso-8859-1") + body

    return final_request


def receive_full_response(server_socket):
    response_parts = []

    while True:
        data = server_socket.recv(BUFFER_SIZE)
        if not data:
            break
        response_parts.append(data)

    return b"".join(response_parts)


def forward_http_request(parsed_request):
    host = parsed_request["host"]
    port = parsed_request["port"]

    request_data = build_forward_request(parsed_request)

    with socket.create_connection((host, port), timeout=SOCKET_TIMEOUT) as server_socket:
        server_socket.settimeout(SOCKET_TIMEOUT)
        server_socket.sendall(request_data)
        response = receive_full_response(server_socket)

    return response