document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");
  const chatContainer = document.getElementById("chat-container");
  const fsBtn = document.getElementById("chat-fullscreen-btn");

  if (!form || !input || !chatBox) {
    console.error("Chat elements not found. Check your HTML IDs.");
    return;
  }

  // Initialize mouse-tracking CSS vars for chat page gradient
  chatBox.style.setProperty('--mouse-x', '50%');
  chatBox.style.setProperty('--mouse-y', '50%');

  chatBox.addEventListener('mousemove', function(e) {
    const rect = chatBox.getBoundingClientRect();
    const x = (e.clientX - rect.left) + 'px';
    const y = (e.clientY - rect.top) + 'px';
    chatBox.style.setProperty('--mouse-x', x);
    chatBox.style.setProperty('--mouse-y', y);
    chatBox.classList.add('hover-gradient');
  });

  chatBox.addEventListener('mouseleave', function() {
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
        fsBtn.setAttribute('aria-pressed', 'true');
        fsBtn.setAttribute('title', 'Exit Fullscreen');
      }
    } else {
      chatContainer.classList.remove('fullscreen');
      document.body.classList.remove('chat-fullscreen');
      if (fsBtn) {
        fsBtn.setAttribute('aria-pressed', 'false');
        fsBtn.setAttribute('title', 'Toggle Expand');
      }
    }
    // Ensure chat scroll stays at bottom
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  if (fsBtn) {
    fsBtn.addEventListener('click', function() {
      const on = !chatContainer.classList.contains('fullscreen');
      setFullscreen(on);
    });
  }

  // Exit fullscreen on Escape
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && chatContainer && chatContainer.classList.contains('fullscreen')) {
      setFullscreen(false);
    }
  });

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const message = input.value.trim();
    if (!message) return;

    // --- Add user's message (right side)
    const userDiv = document.createElement("div");
    userDiv.className = "message user";
    userDiv.innerHTML = `
      <div class="bubble user-bubble">${message}</div>
      <span class="emoji">😊</span>
    `;
    chatBox.appendChild(userDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    // --- Simulated bot reply
    setTimeout(() => {
      const botDiv = document.createElement("div");
      botDiv.className = "message bot";
      botDiv.innerHTML = `
        <img src="/static/UMBC_STYLES/dogumbc.png" class="avatar" alt="UMBC Mascot">
        <div class="bubble bot-bubble">That's a great question!</div>
      `;
      chatBox.appendChild(botDiv);
      chatBox.scrollTop = chatBox.scrollHeight;
    }, 700);

    // Clear input field
    input.value = "";
  });
});
