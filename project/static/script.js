async function sendMessage() {
  const inputField = document.getElementById("user-input");
  const message = inputField.value.trim();
  if (!message) return;

  // Display user message
  appendMessage(message, "user");
  inputField.value = "";

  // Send to Flask backend
  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message })
    });

    const data = await response.json();

    // Display bot reply
    appendMessage(data.reply || "⚠️ No reply from server", "bot");

    // If products are returned, display them
    if (data.products) {
      data.products.forEach(p => {
        let productMsg = `${p.name} - ₹${p.price}`;
        if (p.offer) productMsg += ` (${p.offer})`;
        appendMessage(productMsg, "bot");
      });
    }

    // If cart is returned (future feature)
    if (data.cart) {
      let cartMsg = "🛒 Your Cart:<br>";
      data.cart.forEach(item => {
        cartMsg += `${item.name} - ₹${item.price}<br>`;
      });
      cartMsg += `<b>Total: ₹${data.total}</b>`;
      appendMessage(cartMsg, "bot");
    }

  } catch (error) {
    appendMessage("⚠️ Error connecting to server.", "bot");
  }
}

function appendMessage(text, sender) {
  const chatBox = document.getElementById("chat-box");
  const msgDiv = document.createElement("div");
  msgDiv.classList.add("message", sender);
  msgDiv.innerHTML = text;
  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function clearHistory() {
  const chatBox = document.getElementById("chat-box");
  chatBox.innerHTML = '<div class="message bot">Hello! I\'m your AI shopping assistant. How can I help you?</div>';
}

document.getElementById("user-input").addEventListener("keypress", function(event) {
  if (event.key === "Enter") {
    sendMessage();
  }
});
