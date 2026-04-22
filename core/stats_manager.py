# Contributor: Laura
# File: core/stats_manager.py
# Purpose: Track proxy statistics safely across requests.

import threading

lock = threading.Lock()

stats = {
    "total_requests": 0,
    "blocked_requests": 0,
    "errors": 0,
    "cache_hits": 0,
    "cache_misses": 0
}


def increment(key):
    with lock:
        if key in stats:
            stats[key] += 1


def get_stats():
    with lock:
        return stats.copy()