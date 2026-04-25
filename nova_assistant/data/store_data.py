"""
store_data.py
-------------
Product catalog and order management for Nova AI Shopping Assistant.
Simulates a trendy online fashion/lifestyle e-commerce store called "LUXE".
Replace with real database when client provides data.
"""

import streamlit as st
import random
import string
from datetime import datetime, timedelta

# ── STORE PROFILE ─────────────────────────────────────────────────────────────
STORE_INFO = {
    "name": "LUXE Store",
    "tagline": "Premium Fashion & Lifestyle",
    "email": "support@luxestore.com",
    "phone": "+1 800 LUXE 123",
    "shipping_standard": "5-7 business days — FREE over $50",
    "shipping_express": "2-3 business days — $12.99",
    "shipping_overnight": "Next day — $24.99",
    "return_policy": "30-day free returns on all items",
    "loyalty_program": "Earn 1 point per $1 spent. 100 points = $5 discount",
    "payment_methods": "Visa, Mastercard, PayPal, Apple Pay, Google Pay",
    "hours": "Customer support available Mon-Fri 9AM-6PM EST",
}

# ── PRODUCT CATALOG ───────────────────────────────────────────────────────────
PRODUCTS = {
    "P001": {
        "name": "Classic Leather Jacket",
        "category": "Outerwear",
        "price": 189.99,
        "colors": ["Black", "Brown", "Tan"],
        "sizes": ["XS", "S", "M", "L", "XL"],
        "stock": 15,
        "rating": 4.8,
        "reviews": 234,
        "description": "Premium genuine leather jacket with quilted lining. Perfect for casual and smart-casual looks.",
        "tags": ["leather", "jacket", "outerwear", "winter", "premium"],
        "emoji": "🧥",
    },
    "P002": {
        "name": "Slim Fit Chinos",
        "category": "Bottoms",
        "price": 69.99,
        "colors": ["Navy", "Khaki", "Olive", "Black"],
        "sizes": ["28", "30", "32", "34", "36", "38"],
        "stock": 42,
        "rating": 4.6,
        "reviews": 189,
        "description": "Modern slim fit chinos in stretch cotton. Versatile for office or weekend wear.",
        "tags": ["chinos", "pants", "slim", "office", "casual"],
        "emoji": "👖",
    },
    "P003": {
        "name": "Oversized Graphic Tee",
        "category": "Tops",
        "price": 34.99,
        "colors": ["White", "Black", "Grey", "Cream"],
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "stock": 67,
        "rating": 4.5,
        "reviews": 412,
        "description": "Relaxed oversized fit graphic tee in 100% organic cotton. Street style essential.",
        "tags": ["tshirt", "graphic", "oversized", "casual", "streetwear"],
        "emoji": "👕",
    },
    "P004": {
        "name": "Premium Sneakers",
        "category": "Footwear",
        "price": 129.99,
        "colors": ["White/Grey", "Black/White", "Navy/White"],
        "sizes": ["6", "7", "8", "9", "10", "11", "12"],
        "stock": 28,
        "rating": 4.9,
        "reviews": 567,
        "description": "Lightweight premium sneakers with memory foam insoles. All-day comfort guaranteed.",
        "tags": ["sneakers", "shoes", "footwear", "casual", "comfort"],
        "emoji": "👟",
    },
    "P005": {
        "name": "Wool Blend Coat",
        "category": "Outerwear",
        "price": 249.99,
        "colors": ["Camel", "Grey", "Black"],
        "sizes": ["XS", "S", "M", "L", "XL"],
        "stock": 8,
        "rating": 4.9,
        "reviews": 143,
        "description": "Luxurious wool blend overcoat. Timeless silhouette for elegant winter dressing.",
        "tags": ["coat", "wool", "winter", "elegant", "premium", "outerwear"],
        "emoji": "🧣",
    },
    "P006": {
        "name": "Crossbody Bag",
        "category": "Accessories",
        "price": 89.99,
        "colors": ["Black", "Tan", "Burgundy"],
        "sizes": ["One Size"],
        "stock": 19,
        "rating": 4.7,
        "reviews": 98,
        "description": "Compact genuine leather crossbody bag. Fits essentials with style.",
        "tags": ["bag", "crossbody", "leather", "accessories", "handbag"],
        "emoji": "👜",
    },
    "P007": {
        "name": "Silk Blend Blouse",
        "category": "Tops",
        "price": 79.99,
        "colors": ["Ivory", "Blush", "Black", "Sage"],
        "sizes": ["XS", "S", "M", "L", "XL"],
        "stock": 24,
        "rating": 4.6,
        "reviews": 176,
        "description": "Elegant silk blend blouse. Perfect for work or evening occasions.",
        "tags": ["blouse", "silk", "elegant", "work", "tops", "women"],
        "emoji": "👗",
    },
    "P008": {
        "name": "Minimalist Watch",
        "category": "Accessories",
        "price": 159.99,
        "colors": ["Silver/White", "Gold/Black", "Rose Gold/Nude"],
        "sizes": ["One Size"],
        "stock": 12,
        "rating": 4.8,
        "reviews": 89,
        "description": "Swiss movement minimalist watch. Clean design that complements any outfit.",
        "tags": ["watch", "accessories", "minimalist", "luxury", "gift"],
        "emoji": "⌚",
    },
}

# ── ACTIVE PROMOTIONS ─────────────────────────────────────────────────────────
PROMOTIONS = {
    "SAVE10": {"discount": 10, "type": "percent", "description": "10% off your order"},
    "WELCOME20": {"discount": 20, "type": "percent", "description": "20% off for new customers"},
    "FREESHIP": {"discount": 0, "type": "free_shipping", "description": "Free express shipping"},
    "LUXE15": {"discount": 15, "type": "percent", "description": "15% off — loyalty reward"},
}

# ── SAMPLE ORDERS (for order tracking demo) ───────────────────────────────────
SAMPLE_ORDERS = {
    "ORD-7821": {
        "status": "Shipped",
        "items": ["Classic Leather Jacket (Black, M)", "Premium Sneakers (White/Grey, 10)"],
        "total": 319.98,
        "estimated_delivery": (datetime.now() + timedelta(days=2)).strftime("%B %d, %Y"),
        "tracking": "UPS: 1Z999AA10123456784",
    },
    "ORD-6543": {
        "status": "Processing",
        "items": ["Wool Blend Coat (Camel, S)"],
        "total": 249.99,
        "estimated_delivery": (datetime.now() + timedelta(days=6)).strftime("%B %d, %Y"),
        "tracking": "Processing — tracking available soon",
    },
    "ORD-5199": {
        "status": "Delivered",
        "items": ["Slim Fit Chinos (Navy, 32)", "Oversized Graphic Tee (White, M)"],
        "total": 104.98,
        "estimated_delivery": "Delivered",
        "tracking": "FEDEX: 449044304137821",
    },
}


# ── CART FUNCTIONS ────────────────────────────────────────────────────────────
def init_cart():
    """Initialize empty cart in session state"""
    if "cart" not in st.session_state:
        st.session_state.cart = []
    if "promo_applied" not in st.session_state:
        st.session_state.promo_applied = None


def add_to_cart(product_id: str, color: str, size: str, quantity: int = 1) -> dict:
    """Add item to cart. Returns result message."""
    init_cart()
    if product_id not in PRODUCTS:
        return {"success": False, "message": "Product not found"}

    product = PRODUCTS[product_id]
    item = {
        "product_id": product_id,
        "name": product["name"],
        "color": color,
        "size": size,
        "quantity": quantity,
        "price": product["price"],
        "emoji": product["emoji"],
    }
    st.session_state.cart.append(item)
    return {"success": True, "message": f"Added {product['name']} to cart!"}


def remove_from_cart(product_name: str) -> dict:
    """Remove item from cart by product name"""
    init_cart()
    original_len = len(st.session_state.cart)
    st.session_state.cart = [
        item for item in st.session_state.cart
        if product_name.lower() not in item["name"].lower()
    ]
    if len(st.session_state.cart) < original_len:
        return {"success": True, "message": f"Removed {product_name} from cart"}
    return {"success": False, "message": "Item not found in cart"}


def get_cart_total() -> float:
    """Calculate cart total"""
    init_cart()
    total = sum(item["price"] * item["quantity"] for item in st.session_state.cart)
    promo = st.session_state.get("promo_applied")
    if promo and promo in PROMOTIONS:
        p = PROMOTIONS[promo]
        if p["type"] == "percent":
            total = total * (1 - p["discount"] / 100)
    return round(total, 2)


def apply_promo(code: str) -> dict:
    """Apply promo code to cart"""
    code = code.upper()
    if code in PROMOTIONS:
        st.session_state.promo_applied = code
        return {"success": True, "message": PROMOTIONS[code]["description"]}
    return {"success": False, "message": "Invalid promo code"}


def search_products(query: str) -> list:
    """Search products by name, category, or tags"""
    query = query.lower()
    results = []
    for pid, product in PRODUCTS.items():
        if (query in product["name"].lower() or
            query in product["category"].lower() or
            any(query in tag for tag in product["tags"])):
            results.append({"id": pid, **product})
    return results


def get_order(order_id: str):
    """Look up order by ID"""
    return SAMPLE_ORDERS.get(order_id.upper(), None)
