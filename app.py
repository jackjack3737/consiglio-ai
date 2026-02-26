"""
Web app: Consiglio di Amministrazione AI
Chat intelligente con Gemini + ChatGPT + Claude.
"""
import gradio as gr
from chat_logic import chat_moderata

# Stile per una web app moderna
CSS = """
/* Header e branding */
.header-box {
    text-align: center;
    padding: 1.5rem 1rem;
    background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 50%, #1e3a5f 100%);
    border-radius: 12px;
    margin-bottom: 1rem;
    color: #fff;
    box-shadow: 0 4px 20px rgba(30, 58, 95, 0.3);
}
.header-box h1 {
    margin: 0;
    font-size: 1.75rem;
    font-weight: 700;
    letter-spacing: -0.02em;
}
.header-box p {
    margin: 0.5rem 0 0 0;
    opacity: 0.9;
    font-size: 0.95rem;
}
/* Badge modelli */
.badges {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 0.75rem;
}
.badge {
    padding: 0.25rem 0.6rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    background: rgba(255,255,255,0.2);
}
/* Footer */
.footer-box {
    text-align: center;
    padding: 0.75rem;
    color: #666;
    font-size: 0.8rem;
    border-top: 1px solid #eee;
    margin-top: 1rem;
}
/* Container principale */
.contain {
    max-width: 900px;
    margin: 0 auto;
}
"""


def build_app():
    with gr.Blocks(title="Consiglio di Amministrazione AI") as app:
        gr.HTML(
            """
            <div class="header-box">
                <h1>🏛️ Consiglio di Amministrazione AI</h1>
                <p>Una risposta, tre menti: Gemini, ChatGPT e Claude lavorano insieme.</p>
                <div class="badges">
                    <span class="badge">🔵 Gemini 2.5 Pro</span>
                    <span class="badge">🟢 ChatGPT 4o</span>
                    <span class="badge">🟠 Claude Opus 4.6</span>
                </div>
            </div>
            """
        )

        with gr.Group(elem_classes=["contain"]):
            gr.ChatInterface(
                fn=chat_moderata,
                multimodal=True,
                textbox=gr.MultimodalTextbox(
                    placeholder="Scrivi un messaggio, usa il microfono o carica un'immagine...",
                    file_types=["image"],
                    scale=7,
                ),
                examples=[{"text": "Ragazzi, ci siete tutti?"}, {"text": "Spiegami il Glycogen Burn Rate."}],
                cache_examples=False,
            )

        gr.HTML(
            """
            <div class="footer-box">
                Chat intelligente · Gemini + GPT + Claude · I dati restano sotto il tuo controllo
            </div>
            """
        )

    return app


app = build_app()

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        share=True,
        theme=gr.themes.Soft(primary_hue="slate", secondary_hue="blue"),
        css=CSS,
    )
