from flask import Flask, request, render_template, redirect, url_for, session
import mysql.connector
import os
import ollama
import re
import stripe
import json
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'test.env'))
from urllib.parse import urlparse

def format_suggestions_for_template(text: str) -> str:
    """
    Convert headings like **1. Cherry Tomatoes (🍅)** into
    ### Cherry Tomatoes (🍅) so Jinja template can split easily.
    """
    if not text:
        return ""

    # Replace headings: **1. Plant Name (🍅)** → ### Plant Name (🍅)
    formatted = re.sub(r"\*\*\s*\d+\.\s*(.*?)\s*\*\*", r"### \1", text)

    return formatted.strip()

app = Flask(__name__)

secret_key = "FLWSECK_TEST-75c66817fd1daa44adeca38a34102f55-X"
app.secret_key = "a3f5b17a92e74c45d2e1f2f5c88b3d7a"
DATABASE_URL = os.environ.get("DATABASE_URL")

# Database connection config
url = urlparse(DATABASE_URL)
db_config = {
    "host": url.hostname,
    "port": url.port,
    "user": url.username,
    "password": url.password,
    "database": url.path[1:]  # remove leading /
}

def create_tables():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS plants_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        phone VARCHAR(50),
        name VARCHAR(255),
        email VARCHAR(255),
        balcony_type VARCHAR(100),
        sunlight VARCHAR(50),
        balconySize VARCHAR(50),
        water VARCHAR(50),
        soil VARCHAR(50),
        season VARCHAR(50)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    tx_ref VARCHAR(100) UNIQUE,
    total_amount DECIMAL(10,2),
    payment_status VARCHAR(20) DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_name VARCHAR(100),
    quantity INT,
    price DECIMAL(10,2),
    subtotal DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(id)
)
    """)

    conn.commit()
    cursor.close()
    conn.close() 

    create_tables()              



@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/suggestions")
def suggestions_page():
    return render_template("suggestions.html")

@app.route("/guides")
def guides():
    return render_template("guides.html")
@app.route("/success")
def success():
    return "<h1> ✅ Payment successfull! Thank you for your purchase"
@app.route("/cancel")
def cancel():
    return "<h1 ❌ payment cancelled. Please try again"
@app.route("/buy")
def buy():
    
    # Static product data (later can come from MySQL)
    products = {
    "pots": [
        {"id": 1, "name": "Clay Pot", "price": 150, "unit": "per pot", "img": "clay_pot.webp"},
        {"id": 2, "name": "Plastic Pot", "price": 30, "unit": "per pot", "img": "plastic.jpg"},
    ],
    "seeds": [
        {"id": 3, "name": "Tomato Seeds", "price": 200, "unit": "per pack", "img": "tomatoes.jpg"},
        {"id": 4, "name": "Spinach Seeds", "price": 45, "unit": "per pack", "img": "seeds.jpg"},
    ],
    "seedlings": [
        {"id": 5, "name": "Kale Seedlings", "price": 10, "unit": "per seedling", "img": "kales.jpg"},
        {"id": 6, "name": "Rosemary Seedlings", "price": 40, "unit": "per seedling", "img": "rosemary.jpg"},
    ],
    "manures": [
        {"id": 7, "name": "Organic Manure", "price": 200, "unit": "per 50kg bag", "img": "manure.jpg"},
    ],
    "soil": [
        {"id": 8, "name": "Loamy Soil", "price": 120, "unit": "per 20kg bag", "img": "loamy.jpg"},
        {"id": 9, "name": "Compost Soil", "price": 120, "unit": "per 20kg bag", "img": "compost.jpg"},
    ]
}

    

    return render_template("buy.html", products=products)

import requests

@app.route("/checkout", methods=["POST"])
def checkout():
    selected_products = request.form.getlist('products[]')


    # Product list (should ideally be reused from a shared config)
    products = {
    1: {"name": "Clay Pot", "price": 150, "unit": "per pot"},
    2: {"name": "Plastic Pot", "price": 30, "unit": "per pot"},
    3: {"name": "Tomato Seeds", "price": 200, "unit": "per pack"},
    4: {"name": "Spinach Seeds", "price": 45, "unit": "per pack"},
    5: {"name": "Kale Seedlings", "price": 10, "unit": "per seedling"},
    6: {"name": "Rosemary Seedlings", "price": 40, "unit": "per seedling"},
    7: {"name": "Organic Manure", "price": 200, "unit": "per 50kg bag"},
    8: {"name": "Loamy Soil", "price": 120, "unit": "per 20kg bag"},
    9: {"name": "Compost Soil", "price": 120, "unit": "per 20kg bag"},
}

    selected_items = []
    total_amount = 0
    for pid in selected_products:
        pid_int = int(pid)
        if pid_int in products:
            quantity = int(request.form.get(f'quantity_{pid}', 1))
            item = products[pid_int].copy()
            item['quantity'] = quantity
            selected_items.append(item)
            total_amount += item['price'] * quantity


            # ✅ Store order details in session
    session["name"] = request.form.get("name")
    session["phone"] = request.form.get("phone")
    session["email"] = request.form.get("email")
    session["cart"] = selected_items  # list of dicts with product, price, qty
    session["total_amount"] = total_amount


    # Use Sandbox Secret Key for testing
    secret_key = "FLWSECK_TEST-75c66817fd1daa44adeca38a34102f55-X"

    # Flutterwave payment payload
    payload = {
        "tx_ref": f"tx-{os.urandom(8).hex()}",
        "amount": total_amount,
        "currency": "KES",
        "payment_options": "card,mobilemoney,mpesa",
        "redirect_url": url_for("payment_callback", _external=True),
        "customer": {
            "email": request.form.get("email"),
            "name": request.form.get("name")
        },
        "customizations": {
            "title": "Balcony2Farm Purchase",
            "description": "Purchase of gardening products"
        }
    }

    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json"
    }

    # Send request to Flutterwave Sandbox
    response = requests.post(
        "https://api.flutterwave.com/v3/payments",
        headers=headers,
        data=json.dumps(payload)
    ).json()

    if response.get("status") == "success":
        # Redirect user to Flutterwave payment page
        return redirect(response["data"]["link"])
    else:
        return f"❌ Payment initialization failed: {response.get('message')}"



@app.route("/payment/callback")
def payment_callback():
    tx_ref = request.args.get("tx_ref")
    status = request.args.get("status")

    if status == "successful":
        try:
            # ✅ Get order details from session (stored during checkout)
            name = session.get("name")
            phone = session.get("phone")
            email = session.get("email")
            cart = session.get("cart")  # [{product, price, quantity}, ...]

            if not cart:
                return "❌ No cart data found in session."

            # ✅ Calculate total amount
            total_amount = sum(item["price"] * item["quantity"] for item in cart)

            # ✅ Save order into DB
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            for item in cart:
                cursor.execute("""
                    INSERT INTO orders 
                    (name, phone, email, product_name, quantity, price, total_amount, tx_ref)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    name, phone, email, 
                    item["name"], item["quantity"], item["price"],
                    total_amount, tx_ref
                ))

            conn.commit()
            cursor.close()
            conn.close()

            return render_template("payment.html", name=name, total=total_amount)
        
        except Exception as e:
            return f"❌ Error saving order: {str(e)}"

    else:
        return render_template("payment_failed.html")

        


@app.route("/submit", methods=["POST"])
def submit():
    # Get form data
    phone = request.form.get("phone")
    name = request.form.get("name")
    email = request.form.get("email")
    balcony_type = request.form.get("balcony-type")
    sunlight = request.form.get("sunlight")
    balcony_size = request.form.get("balconySize")
    water = request.form.get("water")
    soil = request.form.get("soil")
    season = request.form.get("season")

    try:
        # Save to database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = """
            INSERT INTO plants_data 
            (phone, name, email, balcony_type, sunlight, balconySize, water, soil, season)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (phone, name, email, balcony_type, sunlight, balcony_size, water, soil, season)

        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()

        # Build user profile
        user_profile = f"""
        Name: {name}
        Balcony type: {balcony_type}
        Sunlight hours: {sunlight}
        Balcony size: {balcony_size} sqm
        Water available: {water}
        Soil type: {soil}
        Current season: {season}
        """

 # ✅ Ollama request
        response = ollama.chat(
             model="gemma:2b", 
            messages=[
                {"role": "system", "content":
                 "You are an expert balcony gardening assistant. Suggest edible plants based on the user's conditions. "
                 "For each suggested plant include:\n"
                 "1. Materials needed (pots, buckets, soil, etc.)\n"
                 "2. How to plant it\n"
                 "3. How to care for it (watering, sunlight, pruning, fertilizer, manure)\n"
                 "4. How long until harvest\n"
                 "Format output clearly with ###plant name as headings example ###tomatoes and use emojis for clarity."},
                {"role": "user", "content": user_profile}
            ]
        )
         
        

        raw_suggestions = response["message"]["content"].strip()

        if not raw_suggestions:
            raw_suggestions = "No suggestions were generated. Please try again."

        # ✅ Always return the template
        suggestions = format_suggestions_for_template(raw_suggestions)
        return render_template("suggestion.html", name=name, suggestions=suggestions)

    except Exception as e:
        return f"❌ Error: {str(e)}"
    
    
    


if __name__ == "__main__":
    app.run(debug=True)
