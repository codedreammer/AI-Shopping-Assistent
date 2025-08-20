async function sendMessage() {
            const inputField = document.getElementById("user-input");
            const message = inputField.value;
            if (!message) return;

            // Show user message
            const messagesDiv = document.getElementById("messages");
            messagesDiv.innerHTML += `<p class="user"><b>You:</b> ${message}</p>`;
            inputField.value = "";

            // Send to Flask backend
            const response = await fetch("/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();

            // Show bot reply
            messagesDiv.innerHTML += `<p class="bot"><b>Bot:</b> ${data.reply}</p>`;

        }
