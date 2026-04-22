# NetShield Proxy

NetShield Proxy: A Multithreaded Caching Proxy Server with Access Control, HTTPS Tunneling, and Web Admin Interface

## Support System for Proxy Server
Modules:
- logger.py → logs all requests with metadata
- cache.py → in-memory cache with TTL
- filter.py → blacklist/whitelist filtering (file-based)
- stats.py → tracks system usage

## Team
- Intissar: Core proxy server, request parsing, HTTP forwarding, HTTPS tunneling
- Laura: Logging, cache, filtering, stats, admin dashboard