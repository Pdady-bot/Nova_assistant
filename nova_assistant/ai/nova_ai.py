"""
nova_ai.py
----------
AI brain for Nova — E-commerce Shopping Assistant.

NEW THINGS IN THIS FILE vs hotel receptionist:
1. Voice input  — browser records audio → converted to text (Web Speech API)
2. Voice output — gTTS converts AI reply to MP3 → plays in browser
3. Product search & cart management via AI actions
4. Smarter system prompt with full product catalog
"""

from groq import Groq
import streamlit as st
import json
import base64
import io
from gtts import gTTS
from data.store_data import (
    STORE_INFO, PRODUCTS, PROMOTIONS,
    add_to_cart, remove_from_cart, get_cart_total,
    apply_promo, search_products, get_order, init_cart
)


# ── TEXT TO SPEECH ────────────────────────────────────────────────────────────
def text_to_speech(text: str) :
    """
    Converts text to speech using gTTS (Google Text-to-Speech).
    Returns base64 encoded audio string to play in browser.

    NEW CONCEPT — Base64:
    Browsers can't play files from your hard drive directly.
    We convert the audio file to a base64 string (text representation of binary)
    and embed it directly in the HTML audio player.
    """
    try:
        # Clean text — remove markdown symbols before speaking
        clean = text.replace("**", "").replace("*", "").replace("#", "")
        clean = clean.replace("✅", "").replace("🛍️", "").replace("👟", "")
        clean = clean.replace("📦", "").replace("🛒", "").replace("💡", "")

        # Generate speech
        tts = gTTS(text=clean[:500], lang="en", slow=False)  # limit to 500 chars

        # Save to memory buffer (not to disk)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        # Convert to base64
        audio_b64 = base64.b64encode(audio_buffer.read()).decode("utf-8")
        return audio_b64

    except Exception as e:
        return None


def get_audio_html(audio_b64: str) -> str:
    """Returns HTML audio player that autoplays the response"""
    return f"""
    <audio autoplay style="display:none">
        <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
    </audio>
    """


# ── SYSTEM PROMPT ─────────────────────────────────────────────────────────────
def build_system_prompt() -> str:
    """Build Nova's personality and knowledge base"""

    # Format products for prompt
    products_text = ""
    for pid, p in PRODUCTS.items():
        products_text += f"""
    [{pid}] {p['emoji']} {p['name']} — ${p['price']}
      Category: {p['category']} | Rating: {p['rating']}⭐ ({p['reviews']} reviews)
      Colors: {', '.join(p['colors'])} | Sizes: {', '.join(p['sizes'])}
      Description: {p['description']}"""

    promos_text = "\n".join([f"    {code}: {info['description']}"
                              for code, info in PROMOTIONS.items()])

    return f"""You are Nova, a friendly and knowledgeable AI shopping assistant for {STORE_INFO['name']} — {STORE_INFO['tagline']}.

STORE INFORMATION:
- Shipping: {STORE_INFO['shipping_standard']}
- Express: {STORE_INFO['shipping_express']}
- Returns: {STORE_INFO['return_policy']}
- Payment: {STORE_INFO['payment_methods']}
- Loyalty: {STORE_INFO['loyalty_program']}

PRODUCT CATALOG:
{products_text}

ACTIVE PROMO CODES:
{promos_text}

YOUR CAPABILITIES:
1. Help customers find products based on style, occasion, budget, or preference
2. Add items to cart — collect product name, color, size, quantity
3. Remove items from cart
4. Apply promo codes
5. Track orders — ask for order ID
6. Answer shipping, returns, and payment questions
7. Make personalized outfit/product recommendations

ACTION SYSTEM — when you need to perform an action, output EXACTLY this format on its own line:
NOVA_ACTION:{{"action":"add_to_cart","product_id":"P001","color":"Black","size":"M","quantity":1}}
NOVA_ACTION:{{"action":"remove_from_cart","product_name":"Leather Jacket"}}
NOVA_ACTION:{{"action":"apply_promo","code":"SAVE10"}}
NOVA_ACTION:{{"action":"search","query":"winter jacket"}}
NOVA_ACTION:{{"action":"track_order","order_id":"ORD-7821"}}

PERSONALITY:
- Enthusiastic, warm, and fashion-forward
- Use the customer's name once you know it
- Give specific style advice — don't just list products
- Mention ratings and reviews to build confidence
- Suggest complementary items (upsell naturally)
- Keep responses concise but helpful
- Use relevant emojis sparingly
- Always confirm cart additions clearly
"""


# ── ACTION PROCESSOR ──────────────────────────────────────────────────────────
def process_action(action_json: str) -> str:
    """Execute Nova's shopping actions and return result"""
    try:
        data = json.loads(action_json)
        action = data.get("action")

        if action == "add_to_cart":
            result = add_to_cart(
                data["product_id"], data["color"],
                data["size"], data.get("quantity", 1)
            )
            total = get_cart_total()
            return f"CART_UPDATED: {result['message']} Cart total: ${total}"

        elif action == "remove_from_cart":
            result = remove_from_cart(data["product_name"])
            total = get_cart_total()
            return f"CART_UPDATED: {result['message']} Cart total: ${total}"

        elif action == "apply_promo":
            result = apply_promo(data["code"])
            total = get_cart_total()
            return f"PROMO_RESULT: {result['message']} New total: ${total}"

        elif action == "search":
            results = search_products(data["query"])
            if results:
                items = [f"{r['emoji']} {r['name']} (${r['price']})" for r in results[:4]]
                return f"SEARCH_RESULTS: Found {len(results)} items: {', '.join(items)}"
            return "SEARCH_RESULTS: No products found for that search"

        elif action == "track_order":
            order = get_order(data["order_id"])
            if order:
                return (f"ORDER_FOUND: {data['order_id']} — Status: {order['status']}, "
                        f"Items: {', '.join(order['items'])}, "
                        f"Total: ${order['total']}, "
                        f"Delivery: {order['estimated_delivery']}, "
                        f"Tracking: {order['tracking']}")
            return f"ORDER_NOT_FOUND: No order found with ID {data['order_id']}"

    except Exception as e:
        return f"ACTION_ERROR: {str(e)}"


# ── MAIN AI RESPONSE ──────────────────────────────────────────────────────────
def get_nova_response(messages: list, voice_enabled: bool = False):
    """
    Gets AI response from Groq and optionally converts to speech.

    Returns:
        tuple: (text_response, audio_base64_or_None)
    """
    init_cart()
    client = Groq()

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            max_tokens=1024,
            messages=[{"role": "system", "content": build_system_prompt()}] + messages,
        )
        reply = response.choices[0].message.content

        # ── Handle Nova actions ────────────────────────────────────────────────
        if "NOVA_ACTION:" in reply:
            parts = reply.split("NOVA_ACTION:")
            pre_text = parts[0].strip()
            action_json = parts[1].strip()

            action_result = process_action(action_json)

            # Send result back to get natural response
            follow_up = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                max_tokens=512,
                messages=[
                    {"role": "system", "content": build_system_prompt()},
                    *messages,
                    {"role": "assistant", "content": reply},
                    {"role": "user", "content": f"SYSTEM: {action_result}. Respond naturally to confirm this to the customer."},
                ],
            )
            reply = follow_up.choices[0].message.content

        # ── Generate voice if enabled ──────────────────────────────────────────
        audio_b64 = None
        if voice_enabled:
            audio_b64 = text_to_speech(reply)

        return reply, audio_b64

    except Exception as e:
        error_msg = f"I'm having a moment! Please try again. ({str(e)[:50]})"
        return error_msg, None
