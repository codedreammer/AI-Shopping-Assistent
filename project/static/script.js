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
        let html = `
          <div class="product-card">
            <img src="${p.image}" alt="${p.name}" class="prod-img"/>
            <div style="flex:1;">
              <div class="prod-title">${p.name}</div>
              <div class="prod-price">₹${p.price}${p.offer ? ' <span style="color:#d53f8c;">('+p.offer+')</span>' : ''}</div>
              ${p.rating ? '<span style="background:#ffeb3b;border-radius:3px;font-size:0.86em;padding:1px 6px 2px 6px;color:#222;margin-top:4px;display:inline-block;">★ '+p.rating+'</span>' : ''}
            </div>
            <button class="add-to-cart-btn" onclick="addToCart(${p.id})">Add to Cart</button>
          </div>
        `;
        appendMessage(html, "bot", true); // add a third param for HTML
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

function appendMessage(text, sender, isHTML = false) {
  const chatBox = document.getElementById("chat-box");
  const msgDiv = document.createElement("div");
  msgDiv.classList.add("message", sender);
  if (isHTML) {
    msgDiv.innerHTML = text;
  } else {
    msgDiv.innerHTML = text;
  }
  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function clearHistory() {
  const chatBox = document.getElementById("chat-box");
  chatBox.innerHTML = '<div class="message bot">Hello! I\'m your AI shopping assistant. How can I help you?</div>';
}

async function addToCart(productId) {
  try {
    const response = await fetch("/add_to_cart", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: productId })
    });
    const data = await response.json();
    if (data.success) {
      appendMessage("✅ Item added to cart!", "bot");
    } else {
      appendMessage("❌ Failed to add item to cart.", "bot");
    }
  } catch (error) {
    appendMessage("⚠️ Error adding to cart.", "bot");
  }
}

document.getElementById("user-input").addEventListener("keypress", function(event) {
  if (event.key === "Enter") {
    sendMessage();
  }
});
