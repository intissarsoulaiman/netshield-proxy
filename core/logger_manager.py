import datetime

def log_event(client_ip, target, method, status, error=""):
    timestamp = datetime.datetime.now()

    with open("data/logs.txt", "a") as f:
        f.write(
            f"{timestamp} | {client_ip} | {method} | {target} | {status} | {error}\n"
        )

    # simple json-style logging (required file exists)
    with open("data/logs.json", "a") as f:
        f.write(
            f'{{"time":"{timestamp}","ip":"{client_ip}","method":"{method}","target":"{target}","status":"{status}"}}\n'
        )