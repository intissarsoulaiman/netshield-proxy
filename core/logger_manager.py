# NetShield Proxy
# Contributor: Laura
# File: core/logger_manager.py
# Purpose: Log proxy events to text and JSON files.

import datetime
import json
import threading

_lock = threading.Lock()

LOG_TXT  = "data/logs.txt"
LOG_JSON = "data/logs.json"


def log_event(
    client_ip,
    client_port,
    target_host,
    target_port,
    method,
    url,
    request_time=None,
    response_time=None,
    error="",
):
    if request_time is None:
        request_time = datetime.datetime.now()
    if response_time is None:
        response_time = datetime.datetime.now()

    log_entry = {
        "client_ip":          client_ip,
        "client_port":        client_port,
        "target_host":        target_host,
        "target_port":        target_port,
        "method":             method,
        "url":                url,
        "request_timestamp":  str(request_time),
        "response_timestamp": str(response_time),
        "error":              error,
    }

    with _lock:
        # Plain-text log
        with open(LOG_TXT, "a") as f:
            f.write(
                f"{request_time} | {client_ip}:{client_port} | "
                f"{method} {url} | {target_host}:{target_port} | "
                f"{response_time} | ERROR: {error}\n"
            )

        # JSON log (one JSON object per line — easy to stream/parse)
        with open(LOG_JSON, "a") as f:
            f.write(json.dumps(log_entry) + "\n")


def read_logs(limit=200):
    """Return the last `limit` log entries as a list of dicts."""
    entries = []
    try:
        with _lock:
            with open(LOG_JSON, "r") as f:
                lines = f.readlines()
        for line in lines[-limit:]:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    except FileNotFoundError:
        pass
    return list(reversed(entries))  # newest first