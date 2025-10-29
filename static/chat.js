document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");

  if (!form || !input || !chatBox) {
    console.error("Chat elements not found. Check your HTML IDs.");
    return;
  }

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

    // clear input field
    input.value = "";
  });
});