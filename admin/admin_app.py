from flask import Flask
from core.stats_manager import get_stats
from core.cache_manager import list_cache

# Laura - Admin Dashboard

app = Flask(__name__)

@app.route("/")
def home():
    stats = get_stats()
    cache_entries = list_cache()

    cache_html = ""
    for entry in cache_entries:
        cache_html += f"<li>{entry['key']} (expires in {entry['expires_in']}s)</li>"

    return f"""
    <h1>Proxy Dashboard</h1>

    <h2>Stats</h2>
    <p>Total Requests: {stats['total_requests']}</p>
    <p>Blocked Requests: {stats['blocked_requests']}</p>
    <p>Errors: {stats['errors']}</p>
    <p>Cache Hits: {stats['cache_hits']}</p>
    <p>Cache Misses: {stats['cache_misses']}</p>

    <h2>Cache</h2>
    <ul>
        {cache_html if cache_html else "<li>No cache entries</li>"}
    </ul>
    """
    
if __name__ == "__main__":
    app.run(debug=True)