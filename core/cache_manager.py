# Contributor: Laura
# File: core/cache_manager.py
# Purpose: Manage caching with expiration, headers, and stats tracking.

import time
import threading
from email.utils import parsedate_to_datetime

cache = {}
lock = threading.Lock()

DEFAULT_TTL = 60  # fallback


# Cache Key Generation

def generate_cache_key(method, url):
    return f"{method}:{url}"



# TTL Extraction

def extract_ttl(headers):
    # Cache-Control
    cache_control = headers.get("Cache-Control", "")
    if "no-store" in cache_control:
        return 0

    if "max-age" in cache_control:
        try:
            return int(cache_control.split("max-age=")[1].split(",")[0])
        except:
            pass

    # Expires header
    expires = headers.get("Expires")
    if expires:
        try:
            expire_time = parsedate_to_datetime(expires).timestamp()
            return max(0, int(expire_time - time.time()))
        except:
            pass

    return DEFAULT_TTL



# Get from cache

def get_cache(key):
    with lock:
        if key in cache:
            entry = cache[key]

            # expiration check
            if time.time() < entry["expiry"]:
                return entry["response"]
            else:
                # stale invalidation
                del cache[key]

    return None



# Store in cache

def set_cache(key, response, headers):
    ttl = extract_ttl(headers)

    # do not cache if ttl = 0
    if ttl == 0:
        return

    with lock:
        cache[key] = {
            "response": response,
            "expiry": time.time() + ttl,
            "stored_at": time.time()
        }

# Cache listing (dashboard)

def list_cache():
    with lock:
        result = []
        for key, entry in cache.items():
            result.append({
                "key": key,
                "expires_in": int(entry["expiry"] - time.time())
            })
        return result



# Clear cache

def clear_cache():
    with lock:
        cache.clear()