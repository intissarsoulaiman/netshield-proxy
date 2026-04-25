# NetShield Proxy

NetShield Proxy is a Python-based multithreaded proxy server that supports HTTP request forwarding, HTTPS tunneling through `CONNECT`, request logging, blacklist/whitelist filtering, and caching for eligible GET requests.

## Features

- HTTP GET and POST forwarding
- HTTPS `CONNECT` tunneling
- Request parsing (method, path, headers, host, port)
- Multithreaded client handling
- Blacklist/whitelist filtering
- Custom blocked response page
- Request/error logging
- GET response caching with expiration support
- Stats and admin-side integration

## Project Structure

```text
NetShield-Proxy/
├── proxy_server.py
├── core/
│   ├── request_parser.py
│   ├── http_handler.py
│   ├── https_tunnel.py
│   ├── cache_manager.py
│   ├── logger_manager.py
│   ├── filter_manager.py
│   └── stats_manager.py
├── data/
│   ├── blacklist.txt
│   ├── whitelist.txt
│   ├── logs.txt
│   └── logs.json
└── README.md

How It Works

The proxy accepts client requests, parses them, checks filtering rules, forwards allowed HTTP requests to target servers, and returns the response back to the client. For HTTPS, it uses the CONNECT method to open a secure tunnel without decrypting the traffic.

For GET requests, the proxy can store responses in cache and serve repeated requests from cache when valid.

Running the Project

Start the proxy server:
python proxy_server.py
Expected output:
Server running on 127.0.0.1:8080
Waiting for connections...

Example Tests:
HTTP GET
curl -x http://127.0.0.1:8080 http://example.com

HTTP POST
curl -x http://127.0.0.1:8080 -X POST http://httpbin.org/post -d "name=test"

HTTPS CONNECT
curl -x http://127.0.0.1:8080 https://example.com -k

Blocked Request
Add a domain to data/blacklist.txt, then run:
curl -x http://127.0.0.1:8080 http://example.com

Filtering
Filtering is controlled by:
data/blacklist.txt
data/whitelist.txt
If the whitelist is not empty, only listed domains are allowed. Any domain in the blacklist is blocked.

Caching
The proxy caches eligible HTTP GET responses. Cache behavior includes:
- cache key generation using method + URL
- TTL extraction from response headers
- fallback expiration time
- cache hit / cache miss tracking

HTTPS Support
HTTPS is supported using CONNECT tunneling. The proxy:
- parses the CONNECT request
- connects to the target server
- sends 200 Connection Established
- relays encrypted traffic in both directions

Team Member Contributions

Member 1: Intissar Soulaiman

Responsible for: Core Proxy Server & HTTPS CONNECT Support

Contributions:
Set up the main proxy server using Python sockets and handled client connections.

Implemented request parsing to extract the method, path, headers, host, and port from incoming client requests.

Developed the HTTP forwarding flow so the proxy could send GET and POST requests to the target server and return the response back to the client.

Added multithreading so the proxy could handle multiple client requests at the same time without crashing.

Integrated the main proxy flow with filtering, logging, stats, and cache support.

Implemented HTTPS CONNECT tunneling by creating a secure tunnel between the client and target server and relaying traffic in both directions.

Tested the core proxy features, including HTTP forwarding, multithreading, error handling, blocked requests, and HTTPS CONNECT support.


Member 2: Laura Malaeb
Responsible for: Support Modules & Admin Dashboard

Contributions:
Developed the cache manager to store eligible GET responses and handle cache expiration.

Implemented the logger manager to record request details, response timestamps, and error messages in both text and JSON log files.

Built the filter manager to support blacklist and whitelist behavior, including blocked response handling.

Created the stats manager to track total requests, blocked requests, errors, cache hits, and cache misses.

Worked on the admin/dashboard side to display logs, cache entries, filters, and usage statistics.

Tested the support modules and dashboard features, including cache behavior, filtering, logging, and stats display.

Testing Completed
HTTP GET forwarding
HTTP POST forwarding
blocked request handling
blocked response page
invalid host / error handling
multithreading
concurrent request handling
HTTPS CONNECT tunneling
blocked HTTPS handling
cache store and cache hit verification


Known Limitations
HTTPS traffic is tunneled but not decrypted
caching focuses on HTTP GET requests
POST requests are forwarded but not cached
some dashboard features depend on final full integration


Notes
This project was built to satisfy the proxy server requirements while also adding bonus-related functionality through HTTPS tunneling and admin-side integration.