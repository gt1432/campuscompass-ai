/**
 * CampusCompass AI - Frontend Application
 * Handles chat communication, health monitoring, animations, and interactions.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Session & Storage Setup
  let sessionId = localStorage.getItem('cc_session_id');
  if (!sessionId) {
    sessionId = 'cc_' + Math.random().toString(36).substring(2, 11) + '_' + Date.now();
    localStorage.setItem('cc_session_id', sessionId);
  }

  // DOM Elements
  const chatForm = document.getElementById('chatForm');
  const chatInput = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');
  const chatFeed = document.getElementById('chatFeed');
  const typingIndicator = document.getElementById('typingIndicator');
  const clearChatBtn = document.getElementById('clearChatBtn');
  const confirmClearBtn = document.getElementById('confirmClearBtn');
  const heroStatusText = document.getElementById('heroStatusText');
  const navStatusText = document.getElementById('navStatusText');
  const chatModelIndicator = document.getElementById('chatModelIndicator');
  const suggestedChips = document.getElementById('suggestedChips');
  const categoryCards = document.querySelectorAll('.category-card');

  // 2. Health Monitoring
  async function checkBackendHealth() {
    try {
      const res = await fetch('/api/health');
      if (res.ok) {
        const data = await res.json();
        if (heroStatusText) heroStatusText.textContent = data.gemini_connected ? 'AI Assistant Online' : 'Campus Knowledge Online';
        if (navStatusText) navStatusText.textContent = 'System Active';
        if (chatModelIndicator) {
          chatModelIndicator.textContent = data.gemini_connected ? (data.gemini_model + ' Active') : 'KnowledgeBase Active';
        }
      }
    } catch (err) {
      console.warn('Backend health check note:', err);
      if (heroStatusText) heroStatusText.textContent = 'KnowledgeBase Offline Mode';
    }
  }
  checkBackendHealth();
  setInterval(checkBackendHealth, 30000);

  // 3. Auto-expanding Textarea
  if (chatInput) {
    chatInput.addEventListener('input', function() {
      this.style.height = 'auto';
      this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });

    chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
      }
    });
  }

  // Toast Helper
  function showToast(message) {
    const toastEl = document.getElementById('appToast');
    const toastMsg = document.getElementById('toastMessage');
    if (toastEl && toastMsg) {
      toastMsg.textContent = message;
      const toast = new bootstrap.Toast(toastEl, { delay: 2500 });
      toast.show();
    }
  }
  // 4. Message Rendering
  function appendMessage(role, text, category = 'General', provider = 'Gemini', messageId = null) {
    const isUser = role === 'user';
    const row = document.createElement('div');
    row.className = `message-row ${isUser ? 'user-row' : 'assistant-row'}`;
    
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const msgId = messageId || ('msg_' + Date.now());

    let actionsHtml = '';
    let footerHtml = '';
    
    if (!isUser) {
      const providerLabel = provider.includes('Gemini') ? 'Gemini 3.8 Flash' : 'KnowledgeBase';
      footerHtml = `
        <div class="message-footer d-flex justify-content-between align-items-center mt-2 pt-2 border-top">
          <div class="d-flex align-items-center gap-2">
            <span class="badge bg-pastel-lavender">${category}</span>
            <span class="badge bg-light text-dark border">${providerLabel}</span>
          </div>
          <div class="message-actions d-flex gap-1">
            <button class="btn btn-tiny copy-btn" title="Copy response" data-content="${encodeURIComponent(text)}">
              <i class="bi bi-clipboard"></i>
            </button>
            <button class="btn btn-tiny feedback-btn" title="Helpful" data-type="helpful" data-id="${msgId}">
              <i class="bi bi-hand-thumbs-up"></i>
            </button>
            <button class="btn btn-tiny feedback-btn" title="Not Helpful" data-type="not_helpful" data-id="${msgId}">
              <i class="bi bi-hand-thumbs-down"></i>
            </button>
          </div>
        </div>
      `;
    }

    row.innerHTML = `
      <div class="message-avatar">
        <i class="bi ${isUser ? 'bi-person-fill' : 'bi-robot'}"></i>
      </div>
      <div class="message-bubble ${isUser ? 'user-bubble' : 'assistant-bubble'}">
        <div class="message-meta d-flex justify-content-between align-items-center mb-1">
          <span class="message-sender">${isUser ? 'You (Student)' : 'CampusCompass AI'}</span>
          <span class="message-time">${timeStr}</span>
        </div>
        <div class="message-text">${escapeHtml(text)}</div>
        ${footerHtml}
      </div>
    `;

    chatFeed.appendChild(row);
    chatFeed.scrollTop = chatFeed.scrollHeight;

    // Attach actions
    if (!isUser) {
      const copyBtn = row.querySelector('.copy-btn');
      if (copyBtn) {
        copyBtn.addEventListener('click', () => {
          navigator.clipboard.writeText(text);
          showToast('Response copied to clipboard!');
        });
      }

      const fbBtns = row.querySelectorAll('.feedback-btn');
      fbBtns.forEach(btn => {
        btn.addEventListener('click', async () => {
          const type = btn.getAttribute('data-type');
          fbBtns.forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          try {
            await fetch('/api/feedback', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                session_id: sessionId,
                message_id: msgId,
                feedback: type,
                response: text
              })
            });
            showToast(type === 'helpful' ? 'Marked as helpful. Thank you!' : 'Feedback noted. Thank you!');
          } catch (e) {
            console.error('Feedback error:', e);
          }
        });
      });
    }
  }

  function escapeHtml(string) {
    const entityMap = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    };
    return String(string).replace(/[&<>"']/g, s => entityMap[s]);
  }

  // 5. Send Message to Backend
  async function sendMessage(text) {
    if (!text || !text.trim()) return;
    const query = text.trim();

    appendMessage('user', query);
    if (chatInput) {
      chatInput.value = '';
      chatInput.style.height = 'auto';
    }

    if (typingIndicator) typingIndicator.classList.remove('d-none');
    chatFeed.scrollTop = chatFeed.scrollHeight;

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: query,
          session_id: sessionId
        })
      });

      const data = await res.json();
      if (typingIndicator) typingIndicator.classList.add('d-none');

      if (data && data.answer) {
        appendMessage('assistant', data.answer, data.category || 'General', data.provider || 'Gemini');
      } else {
        appendMessage('assistant', 'I encountered an issue processing your request. Please try again.', 'General', 'System');
      }
    } catch (err) {
      console.error('Chat error:', err);
      if (typingIndicator) typingIndicator.classList.add('d-none');
      appendMessage('assistant', 'Network connection issue. Falling back to official university knowledge.', 'General', 'Offline');
    }
  }

  if (chatForm) {
    chatForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const val = chatInput ? chatInput.value : '';
      sendMessage(val);
    });
  }

  // 6. Global trigger for Predefined Queries
  window.sendPredefinedQuery = function(query) {
    const chatSection = document.getElementById('chat-demo');
    if (chatSection) {
      chatSection.scrollIntoView({ behavior: 'smooth' });
    }
    setTimeout(() => {
      sendMessage(query);
    }, 400);
  };

  // 7. Suggested Chips Clicks
  if (suggestedChips) {
    suggestedChips.addEventListener('click', (e) => {
      const btn = e.target.closest('.chip-btn');
      if (btn) {
        const q = btn.getAttribute('data-question');
        if (q) sendMessage(q);
      }
    });
  }

  // 8. Category Cards Clicks
  categoryCards.forEach(card => {
    card.addEventListener('click', () => {
      const q = card.getAttribute('data-query');
      if (q) window.sendPredefinedQuery(q);
    });
  });

  // 9. Clear Chat
  if (confirmClearBtn) {
    confirmClearBtn.addEventListener('click', async () => {
      try {
        await fetch('/api/clear', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_id: sessionId })
        });
      } catch (e) {
        console.error(e);
      }
      sessionId = 'cc_' + Math.random().toString(36).substring(2, 11) + '_' + Date.now();
      localStorage.setItem('cc_session_id', sessionId);
      
      // Reset feed to initial welcome message
      chatFeed.innerHTML = `
        <div class="message-row assistant-row">
          <div class="message-avatar"><i class="bi bi-robot"></i></div>
          <div class="message-bubble assistant-bubble">
            <div class="message-meta d-flex justify-content-between align-items-center mb-1">
              <span class="message-sender">CampusCompass AI</span>
              <span class="message-time">Just now</span>
            </div>
            <div class="message-text">
              Hello! Welcome to <strong>CampusCompass AI</strong>! I'm your intelligent campus assistant. I can help you with academics, attendance, examinations, placements, library, hostel, administration and events. What would you like to know today?
            </div>
            <div class="message-footer d-flex justify-content-between align-items-center mt-2 pt-2 border-top">
              <div class="d-flex align-items-center gap-2">
                <span class="badge bg-pastel-lavender">General</span>
                <span class="badge bg-light text-dark border">Verified Assistant</span>
              </div>
              <div class="message-actions d-flex gap-2">
                <button class="btn btn-tiny copy-btn" title="Copy response"><i class="bi bi-clipboard"></i></button>
              </div>
            </div>
          </div>
        </div>
      `;

      const modalEl = document.getElementById('clearChatModal');
      if (modalEl) {
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
      }
      showToast('Conversation cleared.');
    });
  }

  if (clearChatBtn) {
    clearChatBtn.addEventListener('click', () => {
      const modalEl = document.getElementById('clearChatModal');
      if (modalEl) {
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
      }
    });
  }

  // 10. Smooth Navbar Highlighting
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-pills-custom .nav-link');
  window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach(sec => {
      const top = sec.offsetTop - 120;
      if (window.scrollY >= top) {
        current = sec.getAttribute('id');
      }
    });
    navLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === '#' + current) {
        link.classList.add('active');
      }
    });
  });

  console.log('CampusCompass AI Client Initialized.');
});
