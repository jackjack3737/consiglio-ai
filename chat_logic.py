"""
Logica del Consiglio di Amministrazione AI (Gemini + GPT + Claude).
Stato per sessione: nessun globale, adatto a API/sito.
"""
import os
from openai import OpenAI
from google import genai
import anthropic

# ==========================================
# CONFIGURAZIONE: solo variabili d'ambiente (nessuna chiave in codice)
# ==========================================
CHIAVE_OPENAI = os.environ.get("OPENAI_API_KEY", "")
CHIAVE_GEMINI = os.environ.get("GEMINI_API_KEY", "")
CHIAVE_CLAUDE = os.environ.get("ANTHROPIC_API_KEY", "")

client_openai = OpenAI(api_key=CHIAVE_OPENAI)
client_gemini = genai.Client(api_key=CHIAVE_GEMINI)
client_claude = anthropic.Anthropic(api_key=CHIAVE_CLAUDE)


def stato_iniziale():
    """Stato fresco per una nuova sessione."""
    return {
        "richiesta_pendente": False,
        "correzione_gpt": "",
        "correzione_claude": "",
    }


def chat_moderata(message, history=None, state=None):
    """
    Risposta del Consiglio (Gemini + GPT + Claude).
    - message: str o dict con chiave "text"
    - history: ignorato (mantenuto per compatibilità)
    - state: dict con richiesta_pendente, correzione_gpt, correzione_claude. Se None, usa stato_iniziale().
    Restituisce (risposta_str, nuovo_state).
    """
    state = state if state is not None else stato_iniziale()
    state = dict(state)

    testo_utente = message["text"] if isinstance(message, dict) else message
    messaggio_pulito = (testo_utente or "").lower().strip()

    # Autorizzazione intervento tecnico
    if state["richiesta_pendente"]:
        if messaggio_pulito in ["si", "sì", "vai", "certo", "ok", "procedi"]:
            risposta = ""
            if state["correzione_gpt"]:
                risposta += f"🟢 **ChatGPT:**\n{state['correzione_gpt']}\n\n"
            if state["correzione_claude"]:
                risposta += f"🟠 **Claude Opus 4.6:**\n{state['correzione_claude']}"
            new_state = stato_iniziale()
            return risposta, new_state
        elif messaggio_pulito in ["no", "basta", "stop"]:
            new_state = stato_iniziale()
            return "🛠️ **Sistema:** Interventi annullati. Proseguiamo con Gemini.", new_state

    state.update({"richiesta_pendente": False, "correzione_gpt": "", "correzione_claude": ""})

    # 1. Gemini 2.5 Pro
    try:
        res_gem = client_gemini.models.generate_content(
            model="gemini-2.5-pro",
            contents=testo_utente,
        )
        risposta_gemini = res_gem.text
        output_chat = f"🔵 **Gemini 2.5 Pro:**\n{risposta_gemini}\n\n---\n\n"
    except Exception as e:
        output_chat = f"🔵 **Gemini (Errore):** {e}\n\n"
        risposta_gemini = ""

    # Prompt per Critico e Saggio: devono sempre dare la loro opinione e mettersi in discussione
    prompt_consiglio = f'''L'utente ha condiviso o chiesto:
"{testo_utente}"

Gemini ha risposto così:
"{risposta_gemini}"

Tu fai parte del Consiglio. Il tuo compito è metterti in discussione: critica l'idea o la risposta di Gemini se qualcosa non ti convince, aggiungi obiezioni, punti ciechi, rischi o alternative. Non limitarti a fare da eco: dissentire è benvenuto.

Rispondi SEMPRE con "RISPOSTA:" seguito dal tuo parere (breve o articolato). Esempio: "RISPOSTA: Sono d'accordo su X, ma su Y vedo un rischio: ..."

Se l'utente ha solo salutato ("ciao", "ci siete?"), rispondi in modo cordiale e brevissimo con "RISPOSTA:".

Opzionale: se rilevi errori tecnici su Glycogen Burn Rate, Fatigue Predictor o Macro, aggiungi in fondo alla risposta una riga "PERMESSO: [la correzione]".'''

    def _estrai_risposta_e_permesso(testo):
        """Estrae la parte RISPOSTA: e eventuale PERMESSO: dal testo del modello."""
        testo = (testo or "").strip()
        risposta = ""
        permesso = ""
        if "RISPOSTA:" in testo:
            parti = testo.split("RISPOSTA:", 1)[1]
            if "PERMESSO:" in parti:
                risposta, _, permesso = parti.partition("PERMESSO:")
                risposta = risposta.strip()
                permesso = permesso.strip()
            else:
                risposta = parti.strip()
        return risposta, permesso

    # 2. ChatGPT 4o (Il Critico)
    try:
        res_gpt = (
            client_openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt_consiglio}],
            )
            .choices[0]
            .message.content.strip()
        )
        testo_gpt, permesso_gpt = _estrai_risposta_e_permesso(res_gpt)
        if testo_gpt:
            output_chat += f"🟢 **ChatGPT (il critico):**\n{testo_gpt}\n\n---\n\n"
        if permesso_gpt:
            state["correzione_gpt"] = permesso_gpt
    except Exception:
        pass

    # 3. Claude Opus 4.6 (Il Saggio)
    try:
        res_claude = (
            client_claude.messages.create(
                model="claude-opus-4-6",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt_consiglio}],
            )
            .content[0]
            .text.strip()
        )
        testo_claude, permesso_claude = _estrai_risposta_e_permesso(res_claude)
        if testo_claude:
            output_chat += f"🟠 **Claude Opus 4.6 (il saggio):**\n{testo_claude}\n\n---\n\n"
        if permesso_claude:
            state["correzione_claude"] = permesso_claude
    except Exception as e:
        if "404" not in str(e):
            output_chat += f"🔴 **Debug Claude:** {e}\n\n"

    interventi = []
    if state["correzione_gpt"]:
        interventi.append("ChatGPT")
    if state["correzione_claude"]:
        interventi.append("Claude")

    if interventi:
        state["richiesta_pendente"] = True
        output_chat += f"✋ **{' e '.join(interventi)}** hanno aggiunto una correzione tecnica (Glycogen/Fatigue/Macro). Autorizzi l'integrazione?"

    return output_chat, state
