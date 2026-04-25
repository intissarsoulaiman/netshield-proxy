# NetShield Proxy — Admin Dashboard
# Contributor: Laura
# File: admin_dashboard.py
# Run: python admin_dashboard.py  (separate process from the proxy)

import sys
import os

# Allow imports from project root
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template, request, redirect, url_for, jsonify

from core import (
    cache_manager,
    filter_manager,
    logger_manager,
)
try:
    import proxy_server as _proxy_server
    def _active_connections():
        return _proxy_server.active_connections
except Exception:
    # Dashboard launched standalone (without proxy in same process) — show 0
    def _active_connections():
        return 0

app = Flask(__name__, template_folder="templates/admin")


# ── Stats from log file (shared source of truth between proxy + dashboard) ────

def compute_stats_from_logs():
    import json, time
    stats = {
        "total_requests":   0,
        "blocked_requests": 0,
        "errors":           0,
        "cache_hits":       0,
        "cache_misses":     0,
        "uptime_seconds":   0,
    }

    # uptime — read start time written by proxy_server.py on startup
    try:
        with open("data/proxy_start.json", "r") as f:
            data = json.load(f)
        stats["uptime_seconds"] = int(time.time() - data["start_time"])
    except Exception:
        pass

    try:
        with open("data/logs.json", "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except Exception:
                    continue
                error = entry.get("error", "")
                stats["total_requests"] += 1
                if error == "BLOCKED":
                    stats["blocked_requests"] += 1
                elif error == "CACHE_HIT":
                    stats["cache_hits"] += 1
                elif error == "":
                    if entry.get("method") == "GET":
                        stats["cache_misses"] += 1
                else:
                    stats["errors"] += 1
    except FileNotFoundError:
        pass

    return stats

# ── Dashboard Home ─────────────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    st = compute_stats_from_logs()
    total = st["total_requests"] or 1
    cache_total = (st["cache_hits"] + st["cache_misses"]) or 1
    return render_template(
        "dashboard.html",
        stats=st,
        active_connections=_active_connections(),
        hit_rate=round(st["cache_hits"] / cache_total * 100, 1),
        block_rate=round(st["blocked_requests"] / total * 100, 1),
        error_rate=round(st["errors"] / total * 100, 1),
    )


# ── Logs ──────────────────────────────────────────────────────────────────────

@app.route("/logs")
def logs():
    entries = logger_manager.read_logs(limit=300)
    method_filter = request.args.get("method", "").upper()
    error_filter  = request.args.get("error", "")
    if method_filter:
        entries = [e for e in entries if e.get("method") == method_filter]
    if error_filter == "accepted_only":
        entries = [e for e in entries if e.get("error") == ""]
    elif error_filter == "cache_hits_only":
        entries = [e for e in entries if e.get("error") == "CACHE_HIT"]
    elif error_filter == "errors_only":
        entries = [e for e in entries if e.get("error") and e["error"] != "BLOCKED"]
    elif error_filter == "blocked_only":
        entries = [e for e in entries if e.get("error") == "BLOCKED"]
    return render_template("logs.html", logs=entries,
                           method_filter=method_filter, error_filter=error_filter)


# ── Cache ─────────────────────────────────────────────────────────────────────

@app.route("/cache")
def cache_view():
    entries = cache_manager.list_cache()
    st = compute_stats_from_logs()
    cache_total = (st["cache_hits"] + st["cache_misses"]) or 1
    return render_template(
        "cache.html",
        entries=entries,
        hits=st["cache_hits"],
        misses=st["cache_misses"],
        hit_rate=round(st["cache_hits"] / cache_total * 100, 1),
    )


@app.route("/cache/delete", methods=["POST"])
def cache_delete():
    key = request.form.get("key", "")
    cache_manager.delete_cache_entry(key)
    return redirect(url_for("cache_view"))


@app.route("/cache/clear", methods=["POST"])
def cache_clear():
    cache_manager.clear_cache()
    return redirect(url_for("cache_view"))


# ── Filters ───────────────────────────────────────────────────────────────────

@app.route("/filters")
def filters():
    return render_template(
        "filters.html",
        blacklist=filter_manager.get_blacklist(),
        whitelist=filter_manager.get_whitelist(),
    )


@app.route("/filters/blacklist/add", methods=["POST"])
def blacklist_add():
    domain = request.form.get("domain", "").strip()
    if domain:
        filter_manager.add_to_blacklist(domain)
    return redirect(url_for("filters"))


@app.route("/filters/blacklist/remove", methods=["POST"])
def blacklist_remove():
    domain = request.form.get("domain", "").strip()
    if domain:
        filter_manager.remove_from_blacklist(domain)
    return redirect(url_for("filters"))


@app.route("/filters/whitelist/add", methods=["POST"])
def whitelist_add():
    domain = request.form.get("domain", "").strip()
    if domain:
        filter_manager.add_to_whitelist(domain)
    return redirect(url_for("filters"))


@app.route("/filters/whitelist/remove", methods=["POST"])
def whitelist_remove():
    domain = request.form.get("domain", "").strip()
    if domain:
        filter_manager.remove_from_whitelist(domain)
    return redirect(url_for("filters"))


# ── Stats JSON (for live refresh) ────────────────────────────────────────────

@app.route("/api/stats")
def api_stats():
    st = compute_stats_from_logs()
    st["active_connections"] = _active_connections()
    return jsonify(st)


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True, use_reloader=False)