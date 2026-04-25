# NetShield Proxy
# Contributor: Laura
# File: core/cache_manager.py
# Purpose: Manage caching with expiration, headers, and stats tracking.

import time
import threading
from email.utils import parsedate_to_datetime

cache = {}
lock = threading.Lock()

DEFAULT_TTL = 60  # fallback


# ── Cache Key Generation ──────────────────────────────────────────────────────

def generate_cache_key(method, url):
    return f"{method}:{url}"


# ── TTL Extraction ────────────────────────────────────────────────────────────

def extract_ttl(headers):
    cache_control = headers.get("Cache-Control", "")

    if "no-store" in cache_control or "no-cache" in cache_control:
        return 0

    if "max-age" in cache_control:
        try:
            return int(cache_control.split("max-age=")[1].split(",")[0].strip())
        except Exception:
            pass

    expires = headers.get("Expires")
    if expires:
        try:
            expire_time = parsedate_to_datetime(expires).timestamp()
            return max(0, int(expire_time - time.time()))
        except Exception:
            pass

    return DEFAULT_TTL


# ── Parse Response Headers ────────────────────────────────────────────────────

def parse_response_headers(response_bytes):
    """Extract headers dict from raw HTTP response bytes."""
    headers = {}
    try:
        if b"\r\n\r\n" in response_bytes:
            header_section = response_bytes.split(b"\r\n\r\n", 1)[0]
        else:
            header_section = response_bytes

        lines = header_section.decode("iso-8859-1", errors="replace").split("\r\n")
        for line in lines[1:]:  # skip status line
            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.strip()] = v.strip()
    except Exception:
        pass
    return headers


# ── Get from Cache ────────────────────────────────────────────────────────────

def get_cache(key):
    with lock:
        entry = cache.get(key)
        if entry is None:
            return None
        if time.time() < entry["expiry"]:
            return entry["response"]
        # Stale — evict
        del cache[key]
    return None


# ── Store in Cache ────────────────────────────────────────────────────────────

def set_cache(key, response, headers):
    ttl = extract_ttl(headers)
    if ttl == 0:
        return

    with lock:
        cache[key] = {
            "response": response,
            "expiry": time.time() + ttl,
            "stored_at": time.time(),
            "ttl": ttl,
            "size": len(response) if response else 0,
        }


# ── Delete a Single Cache Entry ───────────────────────────────────────────────

def delete_cache_entry(key):
    """Remove a specific key from the cache. Returns True if it existed."""
    with lock:
        if key in cache:
            del cache[key]
            return True
    return False


# ── List Cache (dashboard) ────────────────────────────────────────────────────

def list_cache():
    with lock:
        now = time.time()
        result = []
        for key, entry in cache.items():
            expires_in = int(entry["expiry"] - now)
            result.append({
                "key": key,
                "expires_in": expires_in,
                "ttl": entry.get("ttl", DEFAULT_TTL),
                "stored_at": entry.get("stored_at", 0),
                "size": entry.get("size", 0),
            })
        return result


# ── Clear All Cache ───────────────────────────────────────────────────────────

def clear_cache():
    with lock:
        cache.clear()


# ── Cache Size ────────────────────────────────────────────────────────────────

def cache_size():
    with lock:
        return len(cache)