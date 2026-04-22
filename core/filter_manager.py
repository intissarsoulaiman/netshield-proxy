import socket

# Laura - Filter Manager

def load_file(path):
    try:
        with open(path, "r") as f:
            return [line.strip().lower() for line in f if line.strip()]
    except:
        return []

def resolve_ip(domain):
    try:
        return socket.gethostbyname(domain)
    except:
        return None

def reload_lists():
    global blacklist, whitelist
    blacklist = load_file("data/blacklist.txt")
    whitelist = load_file("data/whitelist.txt")

# initial load
blacklist = load_file("data/blacklist.txt")
whitelist = load_file("data/whitelist.txt")

def is_blocked(host):
    host = host.lower()

    # whitelist mode (if not empty)
    if whitelist:
        allowed = any(site in host for site in whitelist)
        if not allowed:
            return True

    # blacklist check
    if any(site in host for site in blacklist):
        return True

    # optional IP check
    ip = resolve_ip(host)
    if ip and ip in blacklist:
        return True

    return False
    
    # Laura - Custom Blocked Response

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