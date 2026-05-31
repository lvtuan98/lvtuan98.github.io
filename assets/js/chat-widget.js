(function () {
  "use strict";

  var BACKEND_URL = window.CHAT_BACKEND_URL || "";
  var messages = [];
  var isOpen = false;
  var isStreaming = false;

  var WELCOME_MSG =
    "Hi! I'm Van-Tuan's AI assistant. Ask me anything about his research, " +
    "experience, or publications. I can also help you send him a message!";

  function $(sel, ctx) {
    return (ctx || document).querySelector(sel);
  }

  function init() {
    if (!BACKEND_URL) return;

    var toggle = $(".chat-toggle");
    var input = $("#chat-input");
    var sendBtn = $("#chat-send");

    appendMessage("bot", WELCOME_MSG);

    toggle.addEventListener("click", function () {
      isOpen = !isOpen;
      var panel = $(".chat-panel");
      if (isOpen) {
        panel.classList.add("open");
        input.focus();
      } else {
        panel.classList.remove("open");
      }
    });

    sendBtn.addEventListener("click", sendMessage);
    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey && !e.isComposing) {
        e.preventDefault();
        setTimeout(sendMessage, 0);
      }
    });
  }

  function appendMessage(role, text) {
    var container = $(".chat-messages");
    var div = document.createElement("div");
    div.className = "chat-msg " + role;
    div.textContent = text;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return div;
  }

  function showTyping() {
    var container = $(".chat-messages");
    var div = document.createElement("div");
    div.className = "chat-msg bot";
    div.id = "typing-indicator";
    div.innerHTML =
      '<div class="typing-dots"><span></span><span></span><span></span></div>';
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return div;
  }

  function removeTyping() {
    var el = document.getElementById("typing-indicator");
    if (el) el.remove();
  }

  async function sendMessage() {
    var inputEl = document.getElementById("chat-input");
    var sendBtn = $("#chat-send");
    var text = inputEl.value.trim();
    if (!text || isStreaming) return;

    inputEl.value = "";
    inputEl.focus();
    appendMessage("user", text);
    messages.push({ role: "user", content: text });

    isStreaming = true;
    sendBtn.disabled = true;
    showTyping();

    try {
      var response = await fetch(BACKEND_URL + "/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: messages }),
      });

      removeTyping();

      if (!response.ok) {
        appendMessage("bot", "Sorry, something went wrong. Please try again.");
        return;
      }

      var reader = response.body.getReader();
      var decoder = new TextDecoder();
      var botDiv = appendMessage("bot", "");
      var fullText = "";

      while (true) {
        var result = await reader.read();
        if (result.done) break;
        var chunk = decoder.decode(result.value, { stream: true });
        fullText += chunk;
        botDiv.textContent = fullText;
        $(".chat-messages").scrollTop = $(".chat-messages").scrollHeight;
      }

      messages.push({ role: "assistant", content: fullText });
    } catch (err) {
      removeTyping();
      appendMessage(
        "bot",
        "Connection error. Please check if the server is running."
      );
    } finally {
      isStreaming = false;
      sendBtn.disabled = false;
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
