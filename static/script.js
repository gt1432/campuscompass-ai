document.addEventListener("DOMContentLoaded", () => {
  let sessionId = localStorage.getItem("pu_session_id") || ("pu_" + Date.now());
  localStorage.setItem("pu_session_id", sessionId);

  const chatFeed = document.getElementById("chatFeed");
  const chatForm = document.getElementById("chatForm");
  const chatInput = document.getElementById("chatInput");
  const typingInd = document.getElementById("typingInd");
  const clearBtn = document.getElementById("clearBtn");
  const promptPills = document.querySelectorAll(".prompt-pill");

  function appendMsg(role, text, category, provider) {
    const isUser = role === "user";
    const row = document.createElement("div");
    row.className = `msg-row ${isUser ? "msg-user" : "msg-assistant"}`;
    
    const prov = provider || "Gemini 3.8 Flash";
    const cat = category || "General";
    
    let footer = "";
    if (!isUser) {
      footer = `
        <div class="d-flex justify-content-between align-items-center mt-2 pt-2 border-top">
          <span class="meta-tag">${escapeHtml(cat)}</span>
          <button class="copy-btn" onclick="navigator.clipboard.writeText(${JSON.stringify(text)})">
            <i class="bi bi-clipboard me-1"></i> Copy
          </button>
        </div>
      `;
    }

    row.innerHTML = `
      <div class="bubble ${isUser ? "bubble-user" : "bubble-assistant"}">
        <div class="d-flex justify-content-between align-items-center mb-1">
          <strong class="small ${isUser ? "text-light" : "text-dark"}">${isUser ? "You" : "Presidency AI Assistant"}</strong>
          <span class="small ${isUser ? "text-secondary" : "text-muted"}">Just now</span>
        </div>
        <p class="m-0">${escapeHtml(text)}</p>
        ${footer}
      </div>
    `;

    chatFeed.appendChild(row);
    chatFeed.scrollTop = chatFeed.scrollHeight;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }

  async function sendMessage(text) {
    if (!text || !text.trim()) return;
    const query = text.trim();
    
    appendMsg("user", query);
    if (chatInput) chatInput.value = "";
    if (typingInd) typingInd.classList.remove("d-none");
    chatFeed.scrollTop = chatFeed.scrollHeight;

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: query, session_id: sessionId })
      });
      const data = await res.json();
      if (typingInd) typingInd.classList.add("d-none");
      if (data && data.answer) {
        appendMsg("assistant", data.answer, data.category, data.provider);
      } else {
        appendMsg("assistant", "I could not retrieve an answer. Please try again.", "General", "System");
      }
    } catch (err) {
      if (typingInd) typingInd.classList.add("d-none");
      appendMsg("assistant", "Guidance is available through official university channels.", "General", "Offline");
    }
  }

  if (chatForm) {
    chatForm.addEventListener("submit", (e) => {
      e.preventDefault();
      sendMessage(chatInput.value);
    });
  }

  promptPills.forEach(pill => {
    pill.addEventListener("click", () => {
      const q = pill.getAttribute("data-query");
      const target = document.getElementById("chat-workspace");
      if (target) target.scrollIntoView({ behavior: "smooth" });
      setTimeout(() => sendMessage(q), 300);
    });
  });

  if (clearBtn) {
    clearBtn.addEventListener("click", async () => {
      sessionId = "pu_" + Date.now();
      localStorage.setItem("pu_session_id", sessionId);
      chatFeed.innerHTML = `
        <div class="msg-row msg-assistant">
          <div class="bubble bubble-assistant">
            <div class="d-flex justify-content-between align-items-center mb-1">
              <strong class="small text-dark">Presidency AI Assistant</strong>
              <span class="small text-muted">Just now</span>
            </div>
            <p class="m-0 text-dark">Conversation cleared. What would you like to ask about Presidency University?</p>
          </div>
        </div>
      `;
    });
  }
});
