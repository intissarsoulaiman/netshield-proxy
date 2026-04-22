# Contributor: Laura
# File: core/filter_manager.py
# Purpose: Manage blacklist/whitelist filtering and blocked HTTP response.

import socket


def load_file(path):
    try:
        with open(path, "r") as f:
            return [line.strip().lower() for line in f if line.strip()]
    except Exception:
        return []


def resolve_ip(domain):
    try:
        return socket.gethostbyname(domain)
    except Exception:
        return None


def reload_lists():
    global blacklist, whitelist
    blacklist = load_file("data/blacklist.txt")
    whitelist = load_file("data/whitelist.txt")


# Initial load
blacklist = load_file("data/blacklist.txt")
whitelist = load_file("data/whitelist.txt")


def is_blocked(host):
    host = host.lower()

    # whitelist mode (if whitelist is not empty)
    if whitelist:
        allowed = any(site in host for site in whitelist)
        if not allowed:
            return True

    # blacklist domain check
    if any(site in host for site in blacklist):
        return True

    # optional IP check
    ip = resolve_ip(host)
    if ip and ip in blacklist:
        return True

    return False


def build_blocked_response(host):
    body = f"""
    <html>
        <head><title>Blocked</title></head>
        <body>
            <h1>403 Forbidden</h1>
            <p>Access to {host} is blocked by the proxy server.</p>
        </body>
    </html>
    """

    response = (
        "HTTP/1.1 403 Forbidden\r\n"
        "Content-Type: text/html\r\n"
        f"Content-Length: {len(body.encode())}\r\n"
        "Connection: close\r\n"
        "\r\n"
        + body
    )

    return response.encode()