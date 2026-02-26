import gradio as gr
import os
from openai import OpenAI
from google import genai 
import anthropic 

# ==========================================
# 1. CONFIGURAZIONE CHIAVI E CLIENTI (solo variabili d'ambiente)
# ==========================================
CHIAVE_OPENAI = os.environ.get("OPENAI_API_KEY", "")
CHIAVE_GEMINI = os.environ.get("GEMINI_API_KEY", "")
CHIAVE_CLAUDE_DIRETTA = os.environ.get("ANTHROPIC_API_KEY", "")

client_openai = OpenAI(api_key=CHIAVE_OPENAI)
client_gemini = genai.Client(api_key=CHIAVE_GEMINI)
client_claude = anthropic.Anthropic(api_key=CHIAVE_CLAUDE_DIRETTA)

stato_riunione = {
    "richiesta_pendente": False,
    "correzione_gpt": "",
    "correzione_claude": ""
}

# ==========================================
# 2. LOGICA DEL MASTERMIND (GEMINI + GPT + CLAUDE)
# ==========================================
def chat_moderata(message, history):
    global stato_riunione
    
    # Estraiamo il testo (gestisce sia stringa semplice che formato multimodale dict)
    testo_utente = message["text"] if isinstance(message, dict) else message
    messaggio_pulito = testo_utente.lower().strip()
    
    # CASO A: Autorizzazione intervento tecnico per Glycogen, Fatigue o Macro
    if stato_riunione["richiesta_pendente"]:
        if messaggio_pulito in ["si", "sì", "vai", "certo", "ok", "procedi"]:
            risposta = ""
            if stato_riunione['correzione_gpt']:
                risposta += f"🟢 **ChatGPT:**\n{stato_riunione['correzione_gpt']}\n\n"
            if stato_riunione['correzione_claude']:
                risposta += f"🟠 **Claude Opus 4.6:**\n{stato_riunione['correzione_claude']}"
            
            stato_riunione.update({"richiesta_pendente": False, "correzione_gpt": "", "correzione_claude": ""})
            return risposta
            
        elif messaggio_pulito in ["no", "basta", "stop"]:
            stato_riunione.update({"richiesta_pendente": False, "correzione_gpt": "", "correzione_claude": ""})
            return "🛠️ **Sistema:** Interventi annullati. Proseguiamo con Gemini."

    # CASO B: Nuova domanda (Analisi corale)
    stato_riunione.update({"richiesta_pendente": False, "correzione_gpt": "", "correzione_claude": ""})
    
    # 1. Gemini 2.5 Pro (Analisi iniziale)
    try:
        res_gem = client_gemini.models.generate_content(
            model='gemini-2.5-pro',
            contents=testo_utente
        )
        risposta_gemini = res_gem.text
        output_chat = f"🔵 **Gemini 2.5 Pro:**\n{risposta_gemini}\n\n---\n\n"
    except Exception as e:
        output_chat = f"🔵 **Gemini (Errore):** {e}\n\n"
        risposta_gemini = ""

    prompt_bg = f"""
    Il Capo ha chiesto: "{testo_utente}". 
    Gemini ha risposto: "{risposta_gemini}".
    
    Regole:
    1. Se l'utente saluta o chiede "ci siete?", rispondi subito confermando. Inizia con "DIRETTO:".
    2. Se rilevi errori tecnici su Glycogen Burn Rate, Fatigue Predictor o Macro, inizia con "PERMESSO:".
    3. Altrimenti scrivi solo "SILENZIO".
    """

    # 2. ChatGPT 4o (Il Critico)
    try:
        res_gpt = client_openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt_bg}]
        ).choices[0].message.content.strip()
        
        if res_gpt.startswith("DIRETTO:"):
            output_chat += f"🟢 **ChatGPT:**\n{res_gpt.replace('DIRETTO:', '').strip()}\n\n---\n\n"
        elif res_gpt.startswith("PERMESSO:"):
            stato_riunione['correzione_gpt'] = res_gpt.replace("PERMESSO:", "").strip()
    except: pass 

    # 3. Claude Opus 4.6 (Il Saggio)
    try:
        res_claude = client_claude.messages.create(
            model="claude-opus-4-6", 
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt_bg}]
        ).content[0].text.strip()
        
        if res_claude.startswith("DIRETTO:"):
            output_chat += f"🟠 **Claude Opus 4.6:**\n{res_claude.replace('DIRETTO:', '').strip()}\n\n---\n\n"
        elif res_claude.startswith("PERMESSO:"):
            stato_riunione['correzione_claude'] = res_claude.replace("PERMESSO:", "").strip()
    except Exception as e:
        if "404" not in str(e):
             output_chat += f"🔴 **Debug Claude:** {e}\n\n"
              
    # 4. Verifica se servono approfondimenti tecnici
    interventi = []
    if stato_riunione['correzione_gpt']: interventi.append("ChatGPT")
    if stato_riunione['correzione_claude']: interventi.append("Claude")

    if interventi:
        stato_riunione["richiesta_pendente"] = True
        output_chat += f"✋ **{' e '.join(interventi)}** hanno notato dettagli su Glycogen/Metabolic Windows. Autorizzi l'integrazione?"
        
    return output_chat

# ==========================================
# 3. INTERFACCIA WEB-APP (CORRETTA PER GRADIO 6.0)
# ==========================================
app = gr.ChatInterface(
    fn=chat_moderata,
    title="🏛️ Consiglio di Amministrazione AI",
    multimodal=True,
    textbox=gr.MultimodalTextbox(
        placeholder="Scrivi un problema, usa il microfono o carica una foto...",
        file_types=["image"],
        scale=7
    ),
    # Il tema non va più qui, rimosso per stabilità
    examples=[{"text": "Ragazzi, ci siete tutti?"}],
    cache_examples=False
)

if __name__ == "__main__":
    # Il tema si definisce esclusivamente qui in launch()
    app.launch(server_name="0.0.0.0", share=True, theme=gr.themes.Soft())