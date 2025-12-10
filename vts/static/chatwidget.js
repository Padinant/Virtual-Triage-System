document.addEventListener('DOMContentLoaded', function() {
  // Chat widget script

  // Initialize elements
  const floatBtn = document.getElementById('chatbot-float-btn');
  const widget = document.getElementById('chatbot-widget');
  const closeBtn = document.getElementById('chatbot-widget-close');
  const expandBtn = document.getElementById('chatbot-widget-expand');
  const widgetForm = document.getElementById('chatbot-widget-form');
  const widgetInput = document.getElementById('chatbot-widget-input');
  const widgetMessages = document.getElementById('chatbot-widget-messages');

  // Track current scale state
  let scaleState = 0;

  if (!floatBtn || !widget) return;

  // Mouse tracking for gradient overlay
  widget.style.setProperty('--mouse-x', '50%');
  widget.style.setProperty('--mouse-y', '50%');

  widget.addEventListener('mousemove', function(e) {
    const rect = widget.getBoundingClientRect();
    const x = (e.clientX - rect.left) + 'px';
    const y = (e.clientY - rect.top) + 'px';
    widget.style.setProperty('--mouse-x', x);
    widget.style.setProperty('--mouse-y', y);
    widget.classList.add('hover-gradient');
  });

  widget.addEventListener('mouseleave', function() {
    widget.style.setProperty('--mouse-x', '50%');
    widget.style.setProperty('--mouse-y', '50%');
    widget.classList.remove('hover-gradient');
  });

  // Toggle widget visibility and initialize default scale
  floatBtn.addEventListener('click', function() {
    widget.classList.toggle('show');
    if (widget.classList.contains('show')) {
      floatBtn.style.display = 'none';
      if (widgetInput) widgetInput.focus();
      scaleState = 0;
      widget.classList.remove('scale-1', 'scale-2');
      widget.classList.add('scale-default');
      if (expandBtn) expandBtn.title = 'Expanded: quarter width, half height';
    }
  });

  // Close widget and reset scale classes
  closeBtn.addEventListener('click', function() {
    widget.classList.remove('show');
    widget.classList.remove('scale-default', 'scale-1', 'scale-2');
    floatBtn.style.display = 'flex';
  });

  // Cycle widget scale through predefined states
  if (expandBtn) {
    expandBtn.addEventListener('click', function() {
      if (!widget.classList.contains('show')) {
        widget.classList.add('show');
        floatBtn.style.display = 'none';
      }
      scaleState = (scaleState + 1) % 3;
      widget.classList.remove('scale-default', 'scale-1', 'scale-2');
      if (scaleState === 0) {
        widget.classList.add('scale-default');
        expandBtn.title = 'Expanded: quarter width, half height';
      } else if (scaleState === 1) {
        widget.classList.add('scale-1');
        expandBtn.title = 'Expanded: quarter width, full height';
      } else if (scaleState === 2) {
        widget.classList.add('scale-2');
        expandBtn.title = 'Expanded: half width, full height';
      }
    });
  }

  // Form submit handler adds user message and simulates bot reply
  if (widgetForm) widgetForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const message = widgetInput ? widgetInput.value.trim() : "";
    if (!message) return;

    // Create and append user's message
    const userDiv = document.createElement("div");
    userDiv.className = "message user";
    userDiv.innerHTML = `
      <img src="/static/UMBC_STYLES/userprofile.png" class="avatar" alt="User Avatar">
      <div class="bubble user-bubble">
        ${message}
        <button class="copy-btn copy-left">
          <svg class="icon" viewBox="0 0 24 24" focusable="false" width="16" height="16">
            <use href="/static/ICONS/sprite.svg#copy"></use>
          </svg>
        </button>
      </div>
    `;
    widgetMessages.appendChild(userDiv);
    widgetMessages.scrollTop = widgetMessages.scrollHeight;

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
        widgetMessages.appendChild(botDiv);
        widgetMessages.scrollTop = widgetMessages.scrollHeight;
      });
    });

    // Clear input field
    if (widgetInput) widgetInput.value = "";
  });

  // Copy-to-clipboard handler for widget
  if (widgetMessages) {
    widgetMessages.addEventListener('click', async (e) => {
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
  }
});
