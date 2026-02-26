(function () {
  const TOKEN_KEY = "consiglio_token";
  const STATE_KEY = "consiglio_state";

  const loginScreen = document.getElementById("loginScreen");
  const appScreen = document.getElementById("appScreen");
  const loginForm = document.getElementById("loginForm");
  const loginPassword = document.getElementById("loginPassword");
  const loginError = document.getElementById("loginError");
  const logoutBtn = document.getElementById("logoutBtn");

  const chatEl = document.getElementById("chat");
  const welcomeEl = document.getElementById("welcome");
  const form = document.getElementById("chatForm");
  const input = document.getElementById("input");
  const sendBtn = document.getElementById("sendBtn");

  let chatState = null;
  let isLoading = false;

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }
  function setToken(token) {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  }
  function clearState() {
    chatState = null;
    localStorage.removeItem(STATE_KEY);
  }

  function showLogin() {
    loginScreen.classList.remove("hidden");
    appScreen.classList.add("hidden");
    loginError.classList.add("hidden");
  }
  function showApp() {
    loginScreen.classList.add("hidden");
    appScreen.classList.remove("hidden");
  }

  function init() {
    if (getToken()) {
      showApp();
      try {
        const saved = localStorage.getItem(STATE_KEY);
        if (saved) chatState = JSON.parse(saved);
      } catch (_) { clearState(); }
    } else {
      showLogin();
    }
  }

  loginForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    const password = (loginPassword.value || "").trim();
    if (!password) return;
    loginError.classList.add("hidden");
    try {
      const res = await fetch("/api/auth", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password: password }),
      });
      const data = await res.json();
      if (!res.ok) {
        loginError.textContent = data.error || "Errore di accesso";
        loginError.classList.remove("hidden");
        return;
      }
      setToken(data.token);
      clearState();
      showApp();
      loginPassword.value = "";
    } catch (err) {
      loginError.textContent = "Errore di connessione.";
      loginError.classList.remove("hidden");
    }
  });

  logoutBtn.addEventListener("click", function () {
    setToken(null);
    clearState();
    showLogin();
  });

  if (typeof marked !== "undefined") {
    marked.setOptions({ breaks: true, gfm: true });
  }
  function renderMarkdown(text) {
    if (typeof marked !== "undefined") return marked.parse(text || "");
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
    } else if (!on && el) el.remove();
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

    const token = getToken();
    if (!token) {
      showLogin();
      return;
    }

    input.value = "";
    addMessage("user", text);
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer " + token,
        },
        body: JSON.stringify({
          message: text,
          state: chatState,
        }),
      });
      const data = await res.json();

      if (res.status === 401) {
        setToken(null);
        showLogin();
        return;
      }

      if (!res.ok) {
        throw new Error(data.error || data.detail || "Errore di risposta");
      }

      if (data.state != null) {
        chatState = data.state;
        try {
          localStorage.setItem(STATE_KEY, JSON.stringify(chatState));
        } catch (_) {}
      }
      addMessage("assistant", data.response);
    } catch (err) {
      showError(err.message || "Errore di connessione. Riprova.");
    } finally {
      setLoading(false);
    }
  });

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

  init();
})();
