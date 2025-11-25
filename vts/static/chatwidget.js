// Chatbot Widget Script (based mostly on chat.js)
document.addEventListener('DOMContentLoaded', function() {
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

  // Initialize mouse tracking CSS vars
  widget.style.setProperty('--mouse-x', '50%');
  widget.style.setProperty('--mouse-y', '50%');

  // Show gradient overlay while hovering the widget
  widget.addEventListener('mousemove', function(e) {
    const rect = widget.getBoundingClientRect();
    const x = (e.clientX - rect.left) + 'px';
    const y = (e.clientY - rect.top) + 'px';
    widget.style.setProperty('--mouse-x', x);
    widget.style.setProperty('--mouse-y', y);
    widget.classList.add('hover-gradient');
  });

  widget.addEventListener('mouseleave', function() {
    // Reset gradient to center when leaving
    widget.style.setProperty('--mouse-x', '50%');
    widget.style.setProperty('--mouse-y', '50%');
    widget.classList.remove('hover-gradient');
  });

  // Toggle widget visibility
  floatBtn.addEventListener('click', function() {
    widget.classList.toggle('show');
    if (widget.classList.contains('show')) {
      floatBtn.style.display = 'none';
      widgetInput.focus();
      // Default open size is quarter width, half height
      scaleState = 0;
      widget.classList.remove('scale-1', 'scale-2');
      widget.classList.add('scale-default');
      if (expandBtn) expandBtn.title = 'Expanded: quarter width, half height';
    }
  });

  // Close widget
  closeBtn.addEventListener('click', function() {
    widget.classList.remove('show');
    // Reset any scale classes when closing
    widget.classList.remove('scale-default', 'scale-1', 'scale-2');
    floatBtn.style.display = 'flex';
  });

  // Cycle widget scale: cycles 0 -> 1 -> 2 -> 0
  if (expandBtn) {
    expandBtn.addEventListener('click', function() {
      // Ensure widget is visible when expanding
      if (!widget.classList.contains('show')) {
        widget.classList.add('show');
        floatBtn.style.display = 'none';
      }
      // Cycle state through 0..2
      scaleState = (scaleState + 1) % 3; // 0..2
      // Remove existing scale classes
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

  // Handle message submission
  widgetForm.addEventListener('submit', function(e) {
    e.preventDefault();

    const message = widgetInput.value.trim();
    if (!message) return;

    // Add user's message
    const userDiv = document.createElement('div');
    userDiv.className = 'message user';
    userDiv.innerHTML = `
      <div class="bubble user-bubble">${message}</div>
      <span class="emoji">😊</span>
    `;
    widgetMessages.appendChild(userDiv);
    widgetMessages.scrollTop = widgetMessages.scrollHeight;

    // Simulated bot reply
    setTimeout(() => {
      const botDiv = document.createElement('div');
      botDiv.className = 'message bot';
      botDiv.innerHTML = `
        <img src="/static/UMBC_STYLES/dogumbc.png" class="avatar" alt="UMBC Mascot">
        <div class="bubble bot-bubble">That's a great question!</div>
      `;
      widgetMessages.appendChild(botDiv);
      widgetMessages.scrollTop = widgetMessages.scrollHeight;
    }, 700);

    // Clear input field
    widgetInput.value = '';
    
  });
});
