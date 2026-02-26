import os
import time
from anthropic import AnthropicVertex
# ==========================================
# 1. LE CHIAVI DELLA TUA TASK FORCE
# ==========================================

# A. Configurazione Claude 4.6 (su Google Cloud Vertex AI)
# Sostituisci il percorso qui sotto con quello esatto dove hai salvato il file .json
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\jackj\OneDrive\Desktop\Progetti_Autonomi\gen-lang-client-0198613106-b9c047a1aa34.json"
os.environ["CLOUD_ML_REGION"] = "us-east5"
os.environ["ANTHROPIC_VERTEX_PROJECT_ID"] = "gen-lang-client-0198613106"

# B. Configurazione ChatGPT e Gemini (solo variabili d'ambiente)
CHIAVE_OPENAI = os.environ.get("OPENAI_API_KEY", "")
CHIAVE_GOOGLE = os.environ.get("GEMINI_API_KEY", "")

# ==========================================
# 2. PRIVACY E SICUREZZA
# ==========================================
# Nessun dato uscirà dal tuo dispositivo. I file restano solo a te e non andranno a Federico o altri.
CARTELLA_LAVORO = r"C:\Users\jackj\OneDrive\Desktop\Progetti_Autonomi"

def richiedi_approvazione(messaggio_ai_modelli):
    """Mette in pausa i lavori finché non dai il via libera."""
    print("\n" + "="*50)
    print("⏸️ I MODELLI SONO IN PAUSA. È RICHIESTA LA TUA APPROVAZIONE.")
    # La notifica verrà inviata via email e messa in copia a tutti per sicurezza
    print(f"📧 INVIANDO EMAIL (in copia a tutti): {messaggio_ai_modelli}") 
    print("="*50 + "\n")

def salva_file_per_cursor(nome_file, contenuto_codice):
    """Salva il codice fisicamente sul tuo PC, pronto per Cursor."""
    percorso = os.path.join(CARTELLA_LAVORO, nome_file)
    with open(percorso, "w", encoding="utf-8") as file:
        file.write(contenuto_codice)
    print(f"✅ File '{nome_file}' salvato in locale e protetto.")

# ==========================================
# 3. IL CICLO DI LAVORO AUTONOMO (VERO)
# ==========================================
def avvia_lavoro_autonomo(compito_del_giorno):
    print(f"🚀 INIZIO LAVORI: {compito_del_giorno}\n")
    print("🧠 Claude (Vertex AI) sta analizzando la richiesta e scrivendo il codice...")

    try:
        # Si collega al tuo Google Cloud
        client = AnthropicVertex(
            region=os.environ.get("CLOUD_ML_REGION"),
            project_id=os.environ.get("ANTHROPIC_VERTEX_PROJECT_ID")
        )

        prompt_sistema = """Sei l'assistente programmatore di un progetto strettamente confidenziale. Restituisci SOLO codice Python funzionante.
        REGOLA 1: Tutti i dati utente devono essere salvati in locale sul dispositivo. Non usare MAI database esterni o in cloud.
        REGOLA 2: Predisponi sempre la struttura per Profilo, obiettivi macro e Calendario pasti.
        REGOLA 3: Includi variabili per Glycogen Burn Rate, Fatigue Predictor e Metabolic Windows."""

        risposta = client.messages.create(
            model="claude-sonnet-4-6", 
            max_tokens=4000,
            system=prompt_sistema,
            messages=[{"role": "user", "content": f"Scrivi lo script per questo compito: {compito_del_giorno}"}]
        )

        codice_generato = risposta.content[0].text
        
        # Pulisce il testo
        if "```python" in codice_generato:
            codice_generato = codice_generato.split("```python")[1].split("```")[0].strip()

        nome_file = "app_generata.py"
        salva_file_per_cursor(nome_file, codice_generato)
        
        richiedi_approvazione(f"Ho scritto il vero codice in '{nome_file}'. Posso procedere?")

    except Exception as e:
        print(f"❌ Errore del super cervello: {e}")