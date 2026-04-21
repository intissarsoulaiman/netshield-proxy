import time

# simple in-memory cache
cache = {}

# optional TTL (simple version)
CACHE_TTL = 60  # seconds

def get_cache(key):
    if key in cache:
        value, timestamp = cache[key]

        # check expiry
        if time.time() - timestamp < CACHE_TTL:
            return value
        else:
            del cache[key]  # expired

    return None


def set_cache(key, value):
    cache[key] = (value, time.time())


def clear_cache():
    cache.clear()