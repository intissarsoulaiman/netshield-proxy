from flask import Flask
from core.stats_manager import get_stats

# Laura - Admin Dashboard

app = Flask(__name__)

@app.route("/")
def home():
    stats = get_stats()

    return f"""
    <h1>Proxy Dashboard</h1>
    <p>Total Requests: {stats['total_requests']}</p>
    <p>Blocked Requests: {stats['blocked_requests']}</p>
    <p>Errors: {stats['errors']}</p>
    <p>Cache Hits: {stats['cache_hits']}</p>
    <p>Cache Misses: {stats['cache_misses']}</p>
    """

if __name__ == "__main__":
    app.run(debug=True)