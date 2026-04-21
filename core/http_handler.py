# NetShield Proxy
# Contributor: Intissar
# Role: HTTP response handling foundation

def build_response():
    body = b"Basic response from proxy"
    response = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: text/plain\r\n"
        b"Content-Length: " + str(len(body)).encode() + b"\r\n"
        b"\r\n" +
        body
    )
    return response