from flask import Flask, render_template, request, jsonify
import json
import re

app = Flask(__name__)

# Load product data
with open("Projects.json") as f:
    products = json.load(f)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").lower()

    # Greetings
    if user_input.strip() in ["hi", "hello"]:
        return jsonify({"reply": "Hello! I am your AI shopping assistant. How can I help you?"})

    # Search products by category
    elif "show" in user_input or "find" in user_input:
        category = None
        if "clothing" in user_input:
            category = "clothing"
        elif "shoes" in user_input or "footwear" in user_input:
            category = "footwear"
        elif "electronics" in user_input:
            category = "electronics"

        if not category:
            return jsonify({"reply": "Please tell me which category (clothing, footwear, electronics) you are looking for."})

        # Detect price
        price_match = re.findall(r'\d+', user_input)
        if price_match:
            max_price = int(price_match[0])
            results = [p for p in products if p["category"] == category and p["price"] <= max_price]
            if results:
                return jsonify({
                    "reply": f"Here are some {category} items under ₹{max_price}:",
                    "products": results
                })
            else:
                return jsonify({"reply": "Sorry, no products found in that category under your budget."})
        else:
            results = [p for p in products if p["category"] == category]
            if results:
                return jsonify({
                    "reply": f"Here are some {category} items:",
                    "products": results
                })
            else:
                return jsonify({"reply": "Sorry, no products found in that category."})

    # FAQs
    elif "delivery" in user_input:
        return jsonify({"reply": "Delivery usually takes 3-5 working days."})
    elif "return" in user_input:
        return jsonify({"reply": "You can return products within 7 days."})

    # Default response
    return jsonify({"reply": "I didn’t understand that. Can you try again?"})

if __name__ == "__main__":
    app.run(debug=True)
