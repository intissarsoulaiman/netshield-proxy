# NetShield Proxy
# Contributor: Laura
# File: core/filter_manager.py
# Purpose: Manage blacklist/whitelist filtering, blocked HTTP response, and runtime edits.

import socket
import threading

BLACKLIST_PATH = "data/blacklist.txt"
WHITELIST_PATH = "data/whitelist.txt"

_lock = threading.Lock()


# ── File I/O ──────────────────────────────────────────────────────────────────

def load_file(path):
    try:
        with open(path, "r") as f:
            return [line.strip().lower() for line in f if line.strip()]
    except Exception:
        return []


def save_file(path, entries):
    try:
        with open(path, "w") as f:
            for entry in sorted(set(entries)):
                f.write(entry + "\n")
    except Exception:
        pass


# ── Initial load ──────────────────────────────────────────────────────────────

blacklist = load_file(BLACKLIST_PATH)
whitelist = load_file(WHITELIST_PATH)


def reload_lists():
    global blacklist, whitelist
    with _lock:
        blacklist = load_file(BLACKLIST_PATH)
        whitelist = load_file(WHITELIST_PATH)


# ── Blacklist CRUD ────────────────────────────────────────────────────────────

def add_to_blacklist(domain):
    global blacklist
    domain = domain.strip().lower()
    with _lock:
        if domain not in blacklist:
            blacklist.append(domain)
            save_file(BLACKLIST_PATH, blacklist)
            return True
    return False  # already present


def remove_from_blacklist(domain):
    global blacklist
    domain = domain.strip().lower()
    with _lock:
        if domain in blacklist:
            blacklist.remove(domain)
            save_file(BLACKLIST_PATH, blacklist)
            return True
    return False  # not found


def get_blacklist():
    with _lock:
        return list(blacklist)


# ── Whitelist CRUD ────────────────────────────────────────────────────────────

def add_to_whitelist(domain):
    global whitelist
    domain = domain.strip().lower()
    with _lock:
        if domain not in whitelist:
            whitelist.append(domain)
            save_file(WHITELIST_PATH, whitelist)
            return True
    return False


def remove_from_whitelist(domain):
    global whitelist
    domain = domain.strip().lower()
    with _lock:
        if domain in whitelist:
            whitelist.remove(domain)
            save_file(WHITELIST_PATH, whitelist)
            return True
    return False


def get_whitelist():
    with _lock:
        return list(whitelist)


# ── Filtering Logic ───────────────────────────────────────────────────────────

def resolve_ip(domain):
    try:
        return socket.gethostbyname(domain)
    except Exception:
        return None


def is_blocked(host):
    host = host.lower()

    with _lock:
        wl = list(whitelist)
        bl = list(blacklist)

    # Whitelist mode: if whitelist is not empty, only allow listed domains
    if wl:
        allowed = any(site in host for site in wl)
        if not allowed:
            return True

    # Blacklist domain check
    if any(site in host for site in bl):
        return True

    # Optional IP check
    ip = resolve_ip(host)
    if ip and ip in bl:
        return True

    return False


# ── Blocked Response ──────────────────────────────────────────────────────────

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