from flask import Flask, render_template, request, jsonify
import json
import re
import requests
import os
import random
from functools import lru_cache
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)

# Load product data
with open("Projects.json") as f:
    products = json.load(f)

cart = []

# API Configuration with connection pooling
FAKE_STORE_API_URL = 'https://fakestoreapi.com/products'

# Create session with connection pooling and retry strategy
session = requests.Session()
retry_strategy = Retry(
    total=2,
    backoff_factor=0.1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Cache for API responses
api_cache = {}
CACHE_DURATION = 300  # 5 minutes

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

@lru_cache(maxsize=1)
def fetch_fake_store_products():
    """Fetch from Fake Store API with caching and optimized requests"""
    cache_key = 'fake_store_products'
    current_time = time.time()
    
    # Check cache first
    if cache_key in api_cache:
        cached_data, timestamp = api_cache[cache_key]
        if current_time - timestamp < CACHE_DURATION:
            return cached_data
    
    try:
        response = session.get(FAKE_STORE_API_URL, timeout=3)
        if response.status_code == 200:
            data = response.json()
            formatted_data = format_fake_store_products(data)
            # Cache the result
            api_cache[cache_key] = (formatted_data, current_time)
            return formatted_data
        return []
    except Exception as e:
        print(f"Error fetching products: {e}")
        # Return cached data if available, even if expired
        if cache_key in api_cache:
            return api_cache[cache_key][0]
        return []

def format_fake_store_products(fake_store_data):
    """Convert Fake Store API to our format"""
    formatted_products = []
    
    for item in fake_store_data:
        product = {
            "id": item['id'] + 1000,
            "name": item['title'],
            "price": int(item['price'] * 80),
            "image": item.get('image', ''),
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
    
    # Show cart
    elif "cart" in user_input and ("show" in user_input or "view" in user_input or "my" in user_input):
        if cart:
            total_price = sum(item["price"] for item in cart)
            return jsonify({
                "reply": f"Your cart has {len(cart)} item(s). Total: ₹{total_price}",
                "products": cart
            })
        else:
            return jsonify({"reply": "Your cart is empty. Start shopping to add items!"})

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

        # Combine local and external products for faster search
        all_products = products.copy()
        
        # Only fetch external products if local results are insufficient
        local_results = [p for p in products if p["category"] == category]
        
        if len(local_results) < 3:  # Only fetch external if we need more products
            external_products = fetch_fake_store_products()
            if external_products:
                external_results = [p for p in external_products if p["category"] == category]
                all_products.extend(external_results)
        
        # Filter by category and price in one pass
        price_match = re.findall(r'\d+', user_input)
        max_price = int(price_match[0]) if price_match else float('inf')
        
        results = [p for p in all_products if p["category"] == category and p["price"] <= max_price][:5]
        
        if results:
            reply_text = f"Here are some {category} items" + (f" under ₹{max_price}" if price_match else "") + ":"
            return jsonify({
                "reply": reply_text,
                "products": results
            })
        else:
            return jsonify({"reply": "Sorry, no products found matching your criteria."})

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
    
    # Search local products first (faster)
    item = next((p for p in products if p["id"] == item_id), None)
    
    # Only fetch external products if not found locally
    if not item:
        external_products = fetch_fake_store_products()
        item = next((p for p in external_products if p["id"] == item_id), None)
    
    if item:
        cart.append(item)
        return jsonify({
            "success": True, 
            "message": f"'{item['name']}' added to cart!",
            "cart_count": len(cart)
        })
    return jsonify({"success": False, "message": "Item not found"})

if __name__ == "__main__":
    app.run(debug=True)
