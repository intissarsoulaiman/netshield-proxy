# NetShield Proxy
# Contributor: Laura
# File: core/stats_manager.py
# Purpose: Track proxy statistics safely across threads.

import threading
import time

lock = threading.Lock()

stats = {
    "total_requests": 0,
    "blocked_requests": 0,
    "errors": 0,
    "cache_hits": 0,
    "cache_misses": 0,
}

_start_time = time.time()


def increment(key):
    with lock:
        if key in stats:
            stats[key] += 1


def get_stats():
    with lock:
        result = stats.copy()
        result["uptime_seconds"] = int(time.time() - _start_time)
        return result


def reset_stats():
    global _start_time
    with lock:
        for key in stats:
            stats[key] = 0
        _start_time = time.time()