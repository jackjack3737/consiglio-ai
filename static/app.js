(function () {
  const chatEl = document.getElementById("chat");
  const welcomeEl = document.getElementById("welcome");
  const form = document.getElementById("chatForm");
  const input = document.getElementById("input");
  const sendBtn = document.getElementById("sendBtn");

  let sessionId = localStorage.getItem("consiglio_session_id") || null;
  let isLoading = false;

  // Marked: sanitize e opzioni
  if (typeof marked !== "undefined") {
    marked.setOptions({
      breaks: true,
      gfm: true,
    });
  }

  function renderMarkdown(text) {
    if (typeof marked !== "undefined") {
      return marked.parse(text || "");
    }
    return (text || "").replace(/\n/g, "<br>").replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  }

  function addMessage(role, text) {
    welcomeEl.classList.add("hidden");
    const wrap = document.createElement("div");
    wrap.className = "msg " + role;
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    if (role === "assistant") {
      const content = document.createElement("div");
      content.className = "content";
      content.innerHTML = renderMarkdown(text);
      bubble.appendChild(content);
    } else {
      bubble.textContent = text;
    }
    wrap.appendChild(bubble);
    chatEl.appendChild(wrap);
    chatEl.scrollTop = chatEl.scrollHeight;
  }

  function setLoading(on) {
    isLoading = on;
    sendBtn.disabled = on;
    input.disabled = on;
    let el = document.getElementById("typing-dot");
    if (on && !el) {
      el = document.createElement("div");
      el.id = "typing-dot";
      el.className = "msg assistant";
      el.innerHTML = '<div class="bubble"><div class="typing"><span></span><span></span><span></span></div></div>';
      chatEl.appendChild(el);
      chatEl.scrollTop = chatEl.scrollHeight;
    } else if (!on && el) {
      el.remove();
    }
  }

  function showError(message) {
    const existing = document.querySelector(".error-msg");
    if (existing) existing.remove();
    const err = document.createElement("div");
    err.className = "error-msg";
    err.textContent = message;
    chatEl.appendChild(err);
    chatEl.scrollTop = chatEl.scrollHeight;
  }

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    const text = (input.value || "").trim();
    if (!text || isLoading) return;

    input.value = "";
    addMessage("user", text);
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, session_id: sessionId }),
      });
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Errore di risposta");
      }

      if (data.session_id) {
        sessionId = data.session_id;
        localStorage.setItem("consiglio_session_id", sessionId);
      }
      addMessage("assistant", data.response);
    } catch (err) {
      showError(err.message || "Errore di connessione. Riprova.");
    } finally {
      setLoading(false);
    }
  });

  // Auto-resize textarea
  input.addEventListener("input", function () {
    this.style.height = "24px";
    this.style.height = Math.min(this.scrollHeight, 160) + "px";
  });

  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      form.requestSubmit();
    }
  });
})();
