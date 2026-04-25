# NetShield Proxy
# Contributor: Intissar
# Role: HTTPS CONNECT tunneling and bidirectional relay

import socket
import select

BUFFER_SIZE = 4096
SOCKET_TIMEOUT = 10


def tunnel_https(client_socket, host, port):
    """
    Establish HTTPS tunnel to target server and relay encrypted traffic.
    """
    remote_socket = None

    try:
        remote_socket = socket.create_connection((host, port), timeout=SOCKET_TIMEOUT)
        remote_socket.settimeout(SOCKET_TIMEOUT)

        client_socket.sendall(
            b"HTTP/1.1 200 Connection Established\r\n"
            b"Proxy-Agent: NetShieldProxy/1.0\r\n"
            b"\r\n"
        )

        relay_bidirectional(client_socket, remote_socket)

    finally:
        if remote_socket:
            try:
                remote_socket.close()
            except Exception:
                pass


def relay_bidirectional(client_socket, remote_socket):
    """
    Relay bytes in both directions until one side closes.
    """
    sockets = [client_socket, remote_socket]

    while True:
        readable, _, exceptional = select.select(sockets, [], sockets, SOCKET_TIMEOUT)

        if exceptional:
            break

        if not readable:
            continue

        for sock in readable:
            try:
                data = sock.recv(BUFFER_SIZE)
                if not data:
                    return

                if sock is client_socket:
                    remote_socket.sendall(data)
                else:
                    client_socket.sendall(data)

            except Exception:
                return