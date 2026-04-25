"""
app.py  ← Run with: streamlit run app.py
------
Nova — AI Shopping Assistant for LUXE Store

NEW FEATURES vs Hotel Receptionist:
- 🎤 Voice input via Web Speech API (browser microphone)
- 🔊 Voice output via gTTS (Nova speaks back)
- 🛒 Live cart sidebar with running total
- 🔍 Product catalog browser
- 💬 Smarter AI with product search & recommendations
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import streamlit as st
import streamlit.components.v1 as components
from ai.nova_ai import get_nova_response, get_audio_html
from data.store_data import (
    STORE_INFO, PRODUCTS, init_cart,
    get_cart_total, remove_from_cart
)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="LUXE — Nova AI Assistant",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tenor+Sans&family=Jost:wght@200;300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Jost', sans-serif;
}

.stApp {
    background: #f8f6f3;
}

/* Store header */
.store-header {
    font-family: 'Tenor Sans', serif;
    font-size: 2.2rem;
    letter-spacing: 0.4em;
    color: #1a1a1a;
    text-align: center;
    margin-bottom: 0;
}
.store-sub {
    font-size: 0.65rem;
    color: #999;
    text-align: center;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}

/* Chat bubbles */
.nova-bubble {
    background: #1a1a1a;
    color: #f0ece4;
    padding: 1rem 1.2rem;
    border-radius: 20px 20px 20px 4px;
    margin: 0.4rem 3rem 0.4rem 0;
    font-size: 0.9rem;
    line-height: 1.6;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.user-bubble {
    background: #fff;
    color: #1a1a1a;
    border: 1px solid #e8e4df;
    padding: 1rem 1.2rem;
    border-radius: 20px 20px 4px 20px;
    margin: 0.4rem 0 0.4rem 3rem;
    font-size: 0.9rem;
    line-height: 1.6;
}
.nova-label {
    font-size: 0.65rem;
    color: #c9a96e;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 0.2rem;
}
.user-label {
    font-size: 0.65rem;
    color: #999;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    text-align: right;
    margin-bottom: 0.2rem;
}

/* Voice button */
.voice-btn {
    background: #1a1a1a !important;
    color: white !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 0.5rem 1.5rem !important;
    font-family: 'Jost', sans-serif !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.1em !important;
    cursor: pointer !important;
}

/* Cart item */
.cart-item {
    background: white;
    border-radius: 8px;
    padding: 0.7rem 0.9rem;
    margin-bottom: 0.5rem;
    font-size: 0.82rem;
    border: 1px solid #f0ece4;
}
.cart-name { color: #1a1a1a; font-weight: 500; }
.cart-detail { color: #999; font-size: 0.75rem; }
.cart-price { color: #1a1a1a; font-weight: 600; float: right; }

/* Product card */
.product-card {
    background: white;
    border-radius: 10px;
    padding: 0.8rem;
    margin-bottom: 0.5rem;
    border: 1px solid #f0ece4;
    font-size: 0.8rem;
}
.product-name { font-weight: 600; color: #1a1a1a; }
.product-price { color: #c9a96e; font-weight: 600; }
.product-rating { color: #999; font-size: 0.72rem; }

/* Divider */
.divider { border: none; border-top: 1px solid #e8e4df; margin: 1rem 0; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #faf8f5 !important;
    border-right: 1px solid #e8e4df !important;
}

/* Input */
.stChatInput > div {
    border: 1px solid #e8e4df !important;
    border-radius: 12px !important;
    background: white !important;
}

.block-container { padding-top: 1.5rem; }

/* Voice recording indicator */
.recording {
    display: inline-block;
    width: 8px; height: 8px;
    background: #e74c3c;
    border-radius: 50%;
    animation: blink 1s infinite;
    margin-right: 6px;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
}

/* Checkout button */
div.stButton > button {
    background: #1a1a1a !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Jost', sans-serif !important;
    letter-spacing: 0.1em !important;
    font-size: 0.8rem !important;
    width: 100% !important;
}
div.stButton > button:hover {
    background: #333 !important;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Welcome to **LUXE** ✨\n\n"
                "I'm **Nova**, your personal AI stylist. I can help you:\n\n"
                "🔍 Find the perfect products\n"
                "🛒 Manage your cart\n"
                "📦 Track your orders\n"
                "💡 Get personalized style advice\n\n"
                "What are you looking for today?"
            )
        }
    ]

if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = False

if "voice_input" not in st.session_state:
    st.session_state.voice_input = None

if "audio_html" not in st.session_state:
    st.session_state.audio_html = None

init_cart()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — Cart + Products
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="store-header" style="font-size:1.4rem">LUXE</div>', unsafe_allow_html=True)
    st.markdown('<div class="store-sub">AI Shopping</div>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Voice toggle ──────────────────────────────────────────────────────────
    st.markdown("##### 🔊 Voice Mode")
    st.session_state.voice_enabled = st.toggle(
        "Nova speaks responses",
        value=st.session_state.voice_enabled,
        help="Nova will read her responses aloud"
    )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Cart ──────────────────────────────────────────────────────────────────
    cart = st.session_state.get("cart", [])
    cart_total = get_cart_total()

    st.markdown(f"##### 🛒 Your Cart ({len(cart)} items)")

    if cart:
        for item in cart:
            st.markdown(f"""
            <div class="cart-item">
                <span class="cart-price">${item['price']:.2f}</span>
                <div class="cart-name">{item['emoji']} {item['name']}</div>
                <div class="cart-detail">{item['color']} · Size {item['size']} · Qty {item['quantity']}</div>
            </div>
            """, unsafe_allow_html=True)

        promo = st.session_state.get("promo_applied")
        if promo:
            st.markdown(f"🏷️ Promo **{promo}** applied!", )

        st.markdown(f"""
        <div style="background:#1a1a1a; color:white; padding:0.8rem 1rem;
                    border-radius:8px; text-align:center; margin:0.5rem 0">
            <span style="font-size:0.75rem; letter-spacing:0.1em">TOTAL</span><br>
            <span style="font-size:1.4rem; font-weight:600">${cart_total:.2f}</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Proceed to Checkout →"):
            st.session_state.messages.append({
                "role": "user",
                "content": "I want to checkout"
            })
            st.rerun()
    else:
        st.caption("Your cart is empty — ask Nova for recommendations!")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Quick product browse ───────────────────────────────────────────────────
    st.markdown("##### 🏷️ Quick Browse")
    categories = list(set(p["category"] for p in PRODUCTS.values()))
    selected_cat = st.selectbox("Category", ["All"] + sorted(categories), label_visibility="collapsed")

    for pid, product in PRODUCTS.items():
        if selected_cat == "All" or product["category"] == selected_cat:
            st.markdown(f"""
            <div class="product-card">
                <span style="float:right" class="product-price">${product['price']}</span>
                <div class="product-name">{product['emoji']} {product['name']}</div>
                <div class="product-rating">⭐ {product['rating']} ({product['reviews']} reviews)</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Quick actions ──────────────────────────────────────────────────────────
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("##### ⚡ Quick Actions")
    if st.button("🔍 Browse All Products"):
        st.session_state.voice_input = "Show me all your products"
    if st.button("💡 Style Recommendations"):
        st.session_state.voice_input = "Give me outfit recommendations"
    if st.button("📦 Track My Order"):
        st.session_state.voice_input = "I want to track my order"
    if st.button("🏷️ Apply Promo Code"):
        st.session_state.voice_input = "I have a promo code to apply"
    if st.button("🔄 Clear Chat"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CHAT AREA
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="store-header">LUXE</div>', unsafe_allow_html=True)
st.markdown('<div class="store-sub">Nova · AI Shopping Assistant</div>', unsafe_allow_html=True)

# ── Play audio if voice response ready ────────────────────────────────────────
if st.session_state.audio_html:
    st.markdown(st.session_state.audio_html, unsafe_allow_html=True)
    st.session_state.audio_html = None

# ── VOICE INPUT — Web Speech API ──────────────────────────────────────────────
# This uses the browser's built-in microphone via JavaScript
# The browser records, converts to text, sends to Streamlit via URL params
st.markdown("##### 🎤 Voice Input")
col1, col2 = st.columns([3, 1])

with col1:
    # JavaScript that uses Web Speech API to record voice
    # When done, it sets the result in a text input
    voice_js = """
    <div id="voice-container">
        <button id="voiceBtn" onclick="startListening()" style="
            background: #1a1a1a; color: white; border: none;
            border-radius: 50px; padding: 8px 20px;
            font-family: 'Jost', sans-serif; font-size: 13px;
            letter-spacing: 1px; cursor: pointer;">
            🎤 Hold to Speak
        </button>
        <span id="status" style="font-size:12px; color:#999; margin-left:10px;"></span>
        <div id="result" style="margin-top:8px; font-size:13px; color:#333;"></div>
    </div>

    <script>
    let recognition;

    function startListening() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            document.getElementById('status').innerText = 'Voice not supported in this browser. Use Chrome!';
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.continuous = false;
        recognition.interimResults = false;

        document.getElementById('voiceBtn').innerText = '🔴 Listening...';
        document.getElementById('status').innerText = 'Speak now!';

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            document.getElementById('result').innerText = '✓ Heard: "' + transcript + '"';
            document.getElementById('status').innerText = 'Got it!';
            document.getElementById('voiceBtn').innerText = '🎤 Hold to Speak';

            // Send transcript to Streamlit via URL parameter
            const url = new URL(window.location.href);
            url.searchParams.set('voice_input', transcript);
            window.location.href = url.toString();
        };

        recognition.onerror = function(event) {
            document.getElementById('status').innerText = 'Error: ' + event.error;
            document.getElementById('voiceBtn').innerText = '🎤 Hold to Speak';
        };

        recognition.onend = function() {
            document.getElementById('voiceBtn').innerText = '🎤 Hold to Speak';
        };

        recognition.start();
    }
    </script>
    """
    components.html(voice_js, height=90)

with col2:
    st.markdown(f"""
    <div style="padding:0.5rem; text-align:center; font-size:0.75rem; color:#999">
        Voice output<br>
        {'🔊 ON' if st.session_state.voice_enabled else '🔇 OFF'}
    </div>
    """, unsafe_allow_html=True)

# ── Check for voice input from URL params ─────────────────────────────────────
# When user speaks, JavaScript puts text in URL → Streamlit reads it here
params = st.query_params
if "voice_input" in params:
    voice_text = params["voice_input"]
    if voice_text and voice_text != st.session_state.get("last_voice", ""):
        st.session_state.voice_input = voice_text
        st.session_state.last_voice = voice_text
        # Clear from URL
        st.query_params.clear()

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Render chat messages ──────────────────────────────────────────────────────
for message in st.session_state.messages:
    if message["role"] == "assistant":
        st.markdown('<div class="nova-label">✦ Nova</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="nova-bubble">{message["content"]}</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<div class="user-label">You</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="user-bubble">{message["content"]}</div>',
                    unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HANDLE INPUT
# ══════════════════════════════════════════════════════════════════════════════
user_input = None

# Check for voice input
if st.session_state.voice_input:
    user_input = st.session_state.voice_input
    st.session_state.voice_input = None

# Text input
chat_input = st.chat_input("Ask Nova anything — or use voice above...")
if chat_input:
    user_input = chat_input

# ── Process message ───────────────────────────────────────────────────────────
if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown('<div class="user-label">You</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="user-bubble">{user_input}</div>', unsafe_allow_html=True)

    # Get AI response
    with st.spinner("Nova is thinking..."):
        api_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        response, audio_b64 = get_nova_response(
            api_messages,
            voice_enabled=st.session_state.voice_enabled
        )

    # Store audio for next render
    if audio_b64:
        from ai.nova_ai import get_audio_html
        st.session_state.audio_html = get_audio_html(audio_b64)

    # Add and display response
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.markdown('<div class="nova-label">✦ Nova</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="nova-bubble">{response}</div>', unsafe_allow_html=True)

    st.rerun()
