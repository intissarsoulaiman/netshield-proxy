# NetShield Proxy
# Contributor: Intissar
# Role: HTTP/HTTPS request parsing (method, path, headers, host, port, full URL)

from urllib.parse import urlsplit


def parse_http_request(request_bytes):
    try:
        text = request_bytes.decode("iso-8859-1", errors="replace")

        if "\r\n\r\n" in text:
            head_text, body_text = text.split("\r\n\r\n", 1)
            body = body_text.encode("iso-8859-1", errors="replace")
        else:
            head_text = text
            body = b""

        lines = head_text.split("\r\n")
        if not lines or len(lines[0].split()) < 3:
            return {"error": "Malformed request line"}

        first_line = lines[0].split()
        method = first_line[0].upper()
        path = first_line[1]
        version = first_line[2]

        headers = {}
        for line in lines[1:]:
            if not line:
                continue
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()

        # HTTPS CONNECT case
        if method == "CONNECT":
            if ":" in path:
                host, port_text = path.rsplit(":", 1)
                try:
                    port = int(port_text)
                except ValueError:
                    port = 443
            else:
                host = path
                port = 443

            host = host.strip().lower()

            return {
                "method": method,
                "path": path,
                "normalized_path": "",
                "version": version,
                "headers": headers,
                "host": host,
                "port": port,
                "full_url": f"{host}:{port}",
                "body": b"",
                "is_connect": True
            }

        # Regular HTTP case
        host_header = headers.get("Host", "")
        host = ""
        port = 80
        normalized_path = path

        if path.startswith("http://") or path.startswith("https://"):
            parts = urlsplit(path)
            host = parts.hostname or ""
            port = parts.port or (443 if parts.scheme == "https" else 80)
            normalized_path = parts.path or "/"
            if parts.query:
                normalized_path += "?" + parts.query
            full_url = path
        else:
            if ":" in host_header:
                host, port_text = host_header.rsplit(":", 1)
                try:
                    port = int(port_text)
                except ValueError:
                    port = 80
            else:
                host = host_header
                port = 80

            if not normalized_path.startswith("/"):
                normalized_path = "/" + normalized_path

            full_url = f"http://{host}:{port}{normalized_path}"

        host = host.strip().lower()

        if not host:
            return {"error": "Missing Host header or target host"}

        return {
            "method": method,
            "path": path,
            "normalized_path": normalized_path,
            "version": version,
            "headers": headers,
            "host": host,
            "port": port,
            "full_url": full_url,
            "body": body,
            "is_connect": False
        }

    except Exception as e:
        return {"error": str(e)}