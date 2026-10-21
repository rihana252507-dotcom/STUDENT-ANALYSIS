/**
 * CampusIQ – Study Assistant Chatbot
 * Lightweight chat UI controller for the Student Dashboard Recommendations section.
 * Rule-based responses via /api/student/chat endpoint.
 */

(function () {
  "use strict";

  const CHATBOT_MAX_LENGTH = 1000;
  const WELCOME_MESSAGE =
    "Hi! I'm your CampusIQ Multilingual Study Assistant. Ask me about your attendance, CGPA, backlogs, study plan, or recommendations in English, Telugu (తెలుగు), Hindi (हिन्दी), or your preferred language!";

  // DOM references (resolved on init)
  let chatMessages, chatInput, chatSendBtn, chatClearBtn;

  // ── Initialise when DOM is ready ──────────────────────────────────────────
  document.addEventListener("DOMContentLoaded", function () {
    chatMessages = document.getElementById("ciqChatMessages");
    chatInput = document.getElementById("ciqChatInput");
    chatSendBtn = document.getElementById("ciqChatSend");
    chatClearBtn = document.getElementById("ciqChatClear");

    if (!chatMessages || !chatInput || !chatSendBtn) return; // not on student page

    // Welcome bubble
    appendBotMessage(WELCOME_MESSAGE);

    // Send on click
    chatSendBtn.addEventListener("click", handleSend);

    // Send on Enter (Shift+Enter for newline is not needed — single-line input)
    chatInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    });

    // Clear chat
    if (chatClearBtn) {
      chatClearBtn.addEventListener("click", function () {
        chatMessages.innerHTML = "";
        appendBotMessage(WELCOME_MESSAGE);
        chatInput.value = "";
        chatInput.focus();
      });
    }

    // Suggested question pills
    document.querySelectorAll(".ciq-chat-suggestion").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var q = btn.getAttribute("data-question");
        if (q) {
          chatInput.value = q;
          handleSend();
        }
      });
    });
  });

  // ── Send handler ──────────────────────────────────────────────────────────
  function handleSend() {
    var text = (chatInput.value || "").trim();
    if (!text) return;
    if (text.length > CHATBOT_MAX_LENGTH) {
      appendBotMessage("Please keep your message under " + CHATBOT_MAX_LENGTH + " characters.");
      return;
    }

    // Show user bubble
    appendUserMessage(text);
    chatInput.value = "";
    chatInput.focus();

    // Show typing indicator
    var typingEl = showTypingIndicator();

    // Call backend
    fetch("/api/student/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        removeTypingIndicator(typingEl);
        appendBotMessage(data.reply || "Sorry, I couldn't generate a response. Please try again.");
      })
      .catch(function () {
        removeTypingIndicator(typingEl);
        appendBotMessage("Oops! Something went wrong. Please check your connection and try again.");
      });
  }

  // ── Chat bubble helpers ───────────────────────────────────────────────────
  function appendUserMessage(text) {
    var wrap = document.createElement("div");
    wrap.className = "ciq-chat-row ciq-chat-user";
    var bubble = document.createElement("div");
    bubble.className = "ciq-chat-bubble ciq-chat-bubble-user";
    bubble.textContent = text;
    wrap.appendChild(bubble);
    chatMessages.appendChild(wrap);
    scrollToBottom();
  }

  function appendBotMessage(text) {
    var wrap = document.createElement("div");
    wrap.className = "ciq-chat-row ciq-chat-bot";

    var avatar = document.createElement("div");
    avatar.className = "ciq-chat-avatar";
    avatar.textContent = "IQ";
    wrap.appendChild(avatar);

    var bubble = document.createElement("div");
    bubble.className = "ciq-chat-bubble ciq-chat-bubble-bot";
    // Preserve line breaks
    bubble.innerHTML = escapeHtmlChat(text).replace(/\n/g, "<br>");
    wrap.appendChild(bubble);

    chatMessages.appendChild(wrap);
    scrollToBottom();
  }

  function showTypingIndicator() {
    var wrap = document.createElement("div");
    wrap.className = "ciq-chat-row ciq-chat-bot ciq-chat-typing-row";
    var avatar = document.createElement("div");
    avatar.className = "ciq-chat-avatar";
    avatar.textContent = "IQ";
    wrap.appendChild(avatar);
    var bubble = document.createElement("div");
    bubble.className = "ciq-chat-bubble ciq-chat-bubble-bot ciq-chat-typing";
    bubble.innerHTML = '<span class="ciq-dot"></span><span class="ciq-dot"></span><span class="ciq-dot"></span>';
    wrap.appendChild(bubble);
    chatMessages.appendChild(wrap);
    scrollToBottom();
    return wrap;
  }

  function removeTypingIndicator(el) {
    if (el && el.parentNode) el.parentNode.removeChild(el);
  }

  function scrollToBottom() {
    if (chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function escapeHtmlChat(str) {
    var div = document.createElement("div");
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }
})();
