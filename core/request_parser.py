# NetShield Proxy
# Contributor: Intissar
# Role: Request parsing for method, path, headers, host, and port

def parse_http_request(request_bytes):
    """Parse raw HTTP request bytes into useful fields."""
    try:
        request_text = request_bytes.decode("utf-8", errors="replace")
        lines = request_text.split("\r\n")

        request_line = lines[0] if lines else ""
        request_parts = request_line.split()

        method = request_parts[0] if len(request_parts) > 0 else ""
        path = request_parts[1] if len(request_parts) > 1 else ""
        version = request_parts[2] if len(request_parts) > 2 else ""

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
            host_parts = host_header.split(":", 1)
            host = host_parts[0].strip()
            try:
                port = int(host_parts[1].strip())
            except ValueError:
                port = 80

        parsed_data = {
            "method": method,
            "path": path,
            "version": version,
            "headers": headers,
            "host": host,
            "port": port,
        }

        return parsed_data

    except Exception as error:
        return {
            "method": "",
            "path": "",
            "version": "",
            "headers": {},
            "host": "",
            "port": 80,
            "error": str(error),
        }