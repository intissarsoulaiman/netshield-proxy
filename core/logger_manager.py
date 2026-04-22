import datetime
import json

# Laura - Logger Manager

def log_event(
    client_ip,
    client_port,
    target_host,
    target_port,
    method,
    url,
    request_time=None,
    response_time=None,
    error=""
):
    if request_time is None:
        request_time = datetime.datetime.now()

    if response_time is None:
        response_time = datetime.datetime.now()

    log_entry = {
        "client_ip": client_ip,
        "client_port": client_port,
        "target_host": target_host,
        "target_port": target_port,
        "method": method,
        "url": url,
        "request_timestamp": str(request_time),
        "response_timestamp": str(response_time),
        "error": error
    }

    # TEXT LOG
    with open("data/logs.txt", "a") as f:
        f.write(
            f"{request_time} | {client_ip}:{client_port} | "
            f"{method} {url} | {target_host}:{target_port} | "
            f"{response_time} | ERROR: {error}\n"
        )

    # JSON LOG (valid JSON per line)
    with open("data/logs.json", "a") as f:
        f.write(json.dumps(log_entry) + "\n")