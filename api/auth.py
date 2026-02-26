"""
Vercel serverless: POST /api/auth - login con password, restituisce JWT.
Imposta in Vercel la variabile d'ambiente SITE_PASSWORD (solo tu la conosci).
"""
import json
import os
import time
from http.server import BaseHTTPRequestHandler

try:
    import jwt
except ImportError:
    jwt = None


def _read_body(handler):
    length = int(handler.headers.get("Content-Length", 0))
    if length == 0:
        return {}
    raw = handler.rfile.read(length)
    try:
        return json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return {}


def _send_json(handler, status, data):
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_POST(self):
        if jwt is None:
            _send_json(self, 500, {"error": "JWT non configurato"})
            return

        password = os.environ.get("SITE_PASSWORD", "").strip()
        if not password:
            _send_json(self, 500, {"error": "SITE_PASSWORD non impostata su Vercel"})
            return

        body = _read_body(self)
        if body.get("password") != password:
            _send_json(self, 401, {"error": "Password errata"})
            return

        # Token valido 7 giorni
        payload = {"sub": "user", "exp": int(time.time()) + 7 * 24 * 3600}
        token = jwt.encode(payload, password, algorithm="HS256")
        if hasattr(token, "decode"):
            token = token.decode("utf-8")
        _send_json(self, 200, {"ok": True, "token": token})
