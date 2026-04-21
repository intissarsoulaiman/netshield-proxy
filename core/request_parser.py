# NetShield Proxy
# Contributor: Intissar
# Role: HTTP request parsing (method, path, headers, host, port)

def parse_http_request(request_bytes):
    try:
        text = request_bytes.decode("utf-8", errors="replace")
        lines = text.split("\r\n")

        first_line = lines[0].split()
        method = first_line[0] if len(first_line) > 0 else ""
        path = first_line[1] if len(first_line) > 1 else ""
        version = first_line[2] if len(first_line) > 2 else ""

        headers = {}
        for line in lines[1:]:
            if line == "":
                break
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()

        host_header = headers.get("Host", "")
        host = host_header
        port = 80

        if ":" in host_header:
            parts = host_header.split(":")
            host = parts[0]
            port = int(parts[1])

        return {
            "method": method,
            "path": path,
            "version": version,
            "headers": headers,
            "host": host,
            "port": port
        }

    except Exception as e:
        return {"error": str(e)}