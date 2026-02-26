# Consiglio di Amministrazione AI

Chat con tre modelli in parallelo: **Gemini 2.5 Pro**, **ChatGPT 4o** e **Claude Opus 4.6**. Una risposta, tre voci che si mettono in discussione.

- **Locale:** `py server.py` → http://127.0.0.1:8000  
- **Vercel:** deploy con login a password → vedi [DEPLOY_VERCEL.md](DEPLOY_VERCEL.md)

## Struttura

- `chat_logic.py` – logica Consiglio (Gemini + GPT + Claude)
- `server.py` – backend FastAPI locale
- `api/` – funzioni serverless per Vercel (auth + chat)
- `index.html`, `style.css`, `app.js` – frontend
- `static/` – copia frontend per server locale
