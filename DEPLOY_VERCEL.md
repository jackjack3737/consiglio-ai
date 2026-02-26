# Deploy su Vercel (solo tu accedi)

## 1. Prepara il repo

- Metti il progetto su GitHub (o GitLab/Bitbucket).
- **Non** committare file con chiavi: le API key vanno solo nelle variabili d'ambiente di Vercel.

## 2. Crea il progetto su Vercel

1. Vai su [vercel.com](https://vercel.com) e fai login.
2. **Add New** → **Project** e importa il repo.
3. **Root Directory**: lascia `.` (root).
4. **Build**: nessun comando di build (è solo static + API).
5. Clicca **Deploy** (la prima volta può fallire senza env).

## 3. Variabili d'ambiente (obbligatorie)

In **Project → Settings → Environment Variables** aggiungi:

| Nome | Valore | Note |
|------|--------|------|
| `SITE_PASSWORD` | *la tua password segreta* | Solo tu la conosci: serve per il login. |
| `OPENAI_API_KEY` | *chiave OpenAI* | Come in chat_logic. |
| `GEMINI_API_KEY` | *chiave Google Gemini* | Come in chat_logic. |
| `ANTHROPIC_API_KEY` | *chiave Anthropic* | Come in chat_logic. |

Poi **Redeploy** il progetto (Deployments → ⋮ → Redeploy).

## 4. Usare il sito

- Apri l’URL che Vercel ti dà (es. `https://tuo-progetto.vercel.app`).
- Vedrai la schermata **Accesso riservato**: inserisci la password che hai messo in `SITE_PASSWORD`.
- Dopo il login usi la chat come in locale. **Esci** per tornare al login.

## Note

- La password non è nel codice: è solo in `SITE_PASSWORD` su Vercel.
- Il token di sessione dura 7 giorni; dopo scade e devi rientrare con la password.
- In locale continua a funzionare `py server.py` (senza login, su http://127.0.0.1:8000).
