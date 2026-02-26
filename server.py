"""
Backend del sito: API chat + servizio file statici.
Avvio: py server.py
"""
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from chat_logic import chat_moderata, stato_iniziale

app = FastAPI(title="Consiglio di Amministrazione AI")

# Sessioni: session_id -> stato
sessions: dict[str, dict] = {}

STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


@app.get("/")
def index():
    """Pagina principale: chat."""
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/chat", response_model=ChatResponse)
def api_chat(body: ChatRequest):
    session_id = body.session_id or str(uuid.uuid4())
    if session_id not in sessions:
        sessions[session_id] = stato_iniziale()
    state = sessions[session_id]
    try:
        response_text, new_state = chat_moderata(body.message, history=[], state=state)
        sessions[session_id] = new_state
        return ChatResponse(response=response_text, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# File statici (dopo le route esatte)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


if __name__ == "__main__":
    import uvicorn
    print("\n  Apri il browser su:  http://127.0.0.1:8000\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)
