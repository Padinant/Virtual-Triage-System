document.addEventListener("DOMContentLoaded", () => {
  // Chat page script

  // Initialize elements
  const form = document.getElementById("chat-form");
  const input = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");
  const chatContainer = document.getElementById("chat-container");
  const fsBtn = document.getElementById("chat-fullscreen-btn");

  if (!form || !input || !chatBox) {
    console.error("Chat elements not found Check your HTML IDs");
    return;
  }

  // Mouse tracking for gradient overlay
  chatBox.style.setProperty('--mouse-x', '50%');
  chatBox.style.setProperty('--mouse-y', '50%');

  chatBox.addEventListener('mousemove', (e) => {
    const rect = chatBox.getBoundingClientRect();
    const x = (e.clientX - rect.left) + 'px';
    const y = (e.clientY - rect.top) + 'px';
    chatBox.style.setProperty('--mouse-x', x);
    chatBox.style.setProperty('--mouse-y', y);
    chatBox.classList.add('hover-gradient');
  });

  chatBox.addEventListener('mouseleave', () => {
    chatBox.style.setProperty('--mouse-x', '50%');
    chatBox.style.setProperty('--mouse-y', '50%');
    chatBox.classList.remove('hover-gradient');
  });

  // Fullscreen toggle handler
  function setFullscreen(on) {
    if (!chatContainer) return;
    if (on) {
      chatContainer.classList.add('fullscreen');
      document.body.classList.add('chat-fullscreen');
      if (fsBtn) {
        fsBtn.setAttribute('title', 'Exit Fullscreen');
      }
    } else {
      chatContainer.classList.remove('fullscreen');
      document.body.classList.remove('chat-fullscreen');
      if (fsBtn) {
        fsBtn.setAttribute('title', 'Toggle Expand');
      }
    }
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  if (fsBtn) {
    fsBtn.addEventListener('click', () => {
      const on = !chatContainer.classList.contains('fullscreen');
      setFullscreen(on);
    });
  }

  // Exit fullscreen on Esc key press
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && chatContainer && chatContainer.classList.contains('fullscreen')) {
      setFullscreen(false);
    }
  });

  // Form submit handler adds user message and simulates bot reply
  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const message = input.value.trim();
    if (!message) return;

    // Create and append user's message
    const userDiv = document.createElement("div");
    userDiv.className = "message user";
    userDiv.innerHTML = `
      <div class="bubble user-bubble">
        ${message}
        <button class="copy-btn copy-left">
          <svg class="icon" viewBox="0 0 24 24" focusable="false" width="16" height="16">
            <use href="/static/ICONS/sprite.svg#copy"></use>
          </svg>
        </button>
      </div>
      <img src="/static/UMBC_STYLES/userprofile.png" class="avatar" alt="User Avatar">
    `;
    chatBox.appendChild(userDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    // Fetch the bot response
    const response = fetch("/message",
                           { method: "POST",
                             headers: { "Content-Type": "application/json" },
                             body: JSON.stringify({ message: message })
                           });

    // Handle the bot response
    response.then((success) => {
      const botDiv = document.createElement("div");
      const reply = success.json();
      reply.then((success) => {
        const reply_msg = success['reply'].trim();
        botDiv.className = "message bot";
        botDiv.innerHTML = `
          <img src="/static/UMBC_STYLES/dogumbc.png" class="avatar" alt="UMBC Mascot">
          <div class="bubble bot-bubble">
            ${reply_msg}
            <button class="copy-btn copy-right">
              <svg class="icon" viewBox="0 0 24 24" focusable="false" width="16" height="16">
                <use href="/static/ICONS/sprite.svg#copy"></use>
              </svg>
            </button>
          </div>
        `;
        chatBox.appendChild(botDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
      });
    });

    // Clear input field
    input.value = "";
  });

  // Copy-to-clipboard handler
  chatBox.addEventListener('click', async (e) => {
    const btn = e.target.closest('.copy-btn');
    if (!btn) return;
    const bubble = btn.closest('.bubble');
    if (!bubble) return;
    const text = bubble.textContent.trim();
    await navigator.clipboard.writeText(text); // Copy text to clipboard
    btn.classList.add('copied');
    setTimeout(() => {
      btn.classList.remove('copied');
    }, 1000); // 1000 = 1 second timeout
  });
});
