from flask import Flask, render_template, request, jsonify
import json
import re
import requests
import os
import random

app = Flask(__name__)

# Load product data
with open("Projects.json") as f:
    products = json.load(f)

cart = []

# API Configuration
FAKE_STORE_API_URL = 'https://fakestoreapi.com/products'

def get_random_fashion_image():
    # Use a curated Unsplash collection or Picsum
    ids = [100, 101, 102, 103, 104]
    return f"https://picsum.photos/id/{random.choice(ids)}/200/200"

# Demo: Fetch products from Apify's Myntra Scraper (JSON)
def fetch_myntra_products():
    url = "https://api.apify.com/v2/acts/easyapi~myntra-product-scraper/runs/last/dataset/items"
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return []

def fetch_fake_store_products():
    """Fetch from Fake Store API - Free alternative for testing"""
    try:
        response = requests.get(FAKE_STORE_API_URL)
        if response.status_code == 200:
            data = response.json()
            return format_fake_store_products(data)
        return []
    except Exception as e:
        print(f"Error fetching products: {e}")
        return []

def format_fake_store_products(fake_store_data):
    """Convert Fake Store API to our format"""
    formatted_products = []
    
    for item in fake_store_data:
        product = {
            "id": item['id'] + 1000,
            "name": item['title'],
            "price": int(item['price'] * 80),
            "image": item['image'] if item.get('image') else get_random_fashion_image(),
            "brand": "Generic",
            "category": map_category(item['category']),
            "rating": round(item.get('rating', {}).get('rate', random.uniform(3.5, 4.9)), 1)
        }
        formatted_products.append(product)
        
    return formatted_products

def map_category(api_category):
    """Map API categories to our categories"""
    category_map = {
        "men's clothing": "clothing",
        "women's clothing": "clothing",
        "electronics": "electronics",
        "jewelery": "accessories",
        "jewelry": "accessories",
        "home & garden": "home appliances",
        "sports & outdoors": "sports",
        "health & beauty": "beauty",
        "books": "books",
        "toys & games": "toys"
    }
    return category_map.get(api_category, "general")

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
        if "clothing" in user_input or "clothes" in user_input:
            category = "clothing"
        elif "shoes" in user_input or "footwear" in user_input:
            category = "footwear"
        elif "electronics" in user_input or "gadgets" in user_input:
            category = "electronics"
        elif "home" in user_input or "appliances" in user_input:
            category = "home appliances"
        elif "beauty" in user_input or "cosmetics" in user_input:
            category = "beauty"
        elif "furniture" in user_input:
            category = "furniture"
        elif "books" in user_input:
            category = "books"
        elif "groceries" in user_input or "food" in user_input:
            category = "groceries"
        elif "accessories" in user_input or "jewelry" in user_input:
            category = "accessories"
        elif "sports" in user_input or "fitness" in user_input:
            category = "sports"
        elif "toys" in user_input or "games" in user_input:
            category = "toys"
        elif "health" in user_input or "medical" in user_input:
            category = "health"

        if not category:
            return jsonify({"reply": "Please tell me which category you are looking for: clothing, footwear, electronics, home appliances, beauty, furniture, books, groceries, accessories, sports, toys, or health."})

        # Try external API first, then fallback to local data
        external_products = fetch_fake_store_products()
        
        if external_products:
            external_results = [p for p in external_products if p["category"] == category]
            if external_results:
                price_match = re.findall(r'\d+', user_input)
                if price_match:
                    max_price = int(price_match[0])
                    external_results = [p for p in external_results if p["price"] <= max_price]
                    if external_results:
                        return jsonify({
                            "reply": f"Here are some {category} items under ₹{max_price}:",
                            "products": external_results[:5]
                        })
                else:
                    return jsonify({
                        "reply": f"Here are some {category} items:",
                        "products": external_results[:5]
                    })
        
        # Fallback to local products
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

    # Filter and sort endpoint
    elif "filter" in user_input or "sort" in user_input:
        # Pseudo-extraction (expand for your real dataset)
        if "brand" in user_input:
            brand = user_input.split("brand")[-1].strip()
            results = [p for p in products if brand.lower() in p["brand"].lower()]
        elif "low to high" in user_input or "sort by price" in user_input:
            results = sorted(products, key=lambda x: x["price"])
        elif "high to low" in user_input:
            results = sorted(products, key=lambda x: -x["price"])
        # Respond
        if results:
            return jsonify({"reply": "Here are your results:", "products": results})
        else:
            return jsonify({"reply": "No products found matching your filter/sort."})

    # FAQs
    elif "delivery" in user_input:
        return jsonify({"reply": "Delivery usually takes 3-5 working days."})
    elif "return" in user_input:
        return jsonify({"reply": "You can return products within 7 days."})

    # Default response
    return jsonify({"reply": "I didn’t understand that. Can you try again?"})

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    item_id = request.json.get("id")
    all_products = products + fetch_fake_store_products()
    item = next((p for p in all_products if p["id"] == item_id), None)
    if item:
        cart.append(item)
        return jsonify({"success": True, "cart": cart})
    return jsonify({"success": False})

if __name__ == "__main__":
    app.run(debug=True)
