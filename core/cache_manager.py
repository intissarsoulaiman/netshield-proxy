import time
import threading

# Laura - Cache Manager

cache = {}
lock = threading.Lock()

CACHE_TTL = 60  # seconds

def get_cache(key):
    with lock:
        if key in cache:
            value, timestamp = cache[key]

            if time.time() - timestamp < CACHE_TTL:
                return value
            else:
                del cache[key]

    return None

def set_cache(key, value):
    with lock:
        cache[key] = (value, time.time())

def clear_cache():
    with lock:
        cache.clear()