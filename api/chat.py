"""
Vercel serverless: POST /api/chat - chat Consiglio AI.
Richiede header: Authorization: Bearer <token> (da /api/auth).
Stato della conversazione va e viene nel body (stateless).
"""
import json
import os
import sys

# Import dalla root del progetto (dove sta chat_logic.py)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from http.server import BaseHTTPRequestHandler

try:
    import jwt
except ImportError:
    jwt = None

from chat_logic import chat_moderata, stato_iniziale


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


def _check_token(handler):
    auth = handler.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[7:].strip()
    secret = os.environ.get("SITE_PASSWORD", "").strip()
    if not secret or not jwt:
        return None
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except Exception:
        return None


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_POST(self):
        if _check_token(self) is None:
            _send_json(self, 401, {"error": "Non autorizzato. Effettua il login."})
            return

        body = _read_body(self)
        message = (body.get("message") or "").strip()
        if not message:
            _send_json(self, 400, {"error": "message richiesto"})
            return

        state = body.get("state")
        if state is None:
            state = stato_iniziale()

        try:
            response_text, new_state = chat_moderata(message, history=[], state=state)
            _send_json(self, 200, {"response": response_text, "state": new_state})
        except Exception as e:
            _send_json(self, 500, {"error": str(e)})
