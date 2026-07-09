#!/usr/bin/env python3
"""Local dev server with CORS proxy for Flathub API."""
import http.server
import json
import os
import urllib.request
import urllib.error
from urllib.parse import urlparse, parse_qs, unquote

PORT = 8080
FLATHUB_STATS_URL = "https://flathub.org/api/v2/stats/{}"
FLATHUB_APPSTREAM_URL = "https://flathub.org/api/v2/appstream/{}"

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/flathub/stats":
            qs = parse_qs(parsed.query)
            app_id = qs.get("id", [None])[0]
            if not app_id:
                self.send_error(400, "Missing ?id= parameter")
                return
            try:
                url = FLATHUB_STATS_URL.format(app_id)
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = resp.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                super().end_headers()
                self.wfile.write(data)
            except Exception as e:
                self.send_error(502, f"Flathub API error: {e}")
            return

        if parsed.path == "/api/flathub/appstream":
            qs = parse_qs(parsed.query)
            app_id = qs.get("id", [None])[0]
            if not app_id:
                self.send_error(400, "Missing ?id= parameter")
                return
            try:
                url = FLATHUB_APPSTREAM_URL.format(app_id)
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = resp.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                super().end_headers()
                self.wfile.write(data)
            except Exception as e:
                self.send_error(502, f"Flathub API error: {e}")
            return

        super().do_GET()

    def log_message(self, format, *args):
        try:
            msg = str(args[0]) if args else ""
            if "/api/flathub" in msg or ".well-known" in msg:
                return
        except Exception:
            pass
        super().log_message(format, *args)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with http.server.HTTPServer(("", PORT), Handler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        print(f"  Static files: .")
        print(f"  Flathub proxy: /api/flathub/stats?id=<app_id>")
        httpd.serve_forever()
