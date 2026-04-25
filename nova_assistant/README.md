# 🛍️ Nova — AI Shopping Assistant

AI-powered e-commerce assistant with voice input/output, cart management, and product recommendations.

## 🚀 Run It

```bash
pip install -r requirements.txt
# Add GROQ_API_KEY to .env file
streamlit run app.py
```

## ✨ Features
- 💬 Text chat with AI
- 🎤 Voice input (Chrome only — uses Web Speech API)
- 🔊 Voice output (Nova speaks back via gTTS)
- 🛒 Live cart management
- 🔍 Product search & recommendations
- 📦 Order tracking
- 🏷️ Promo code system

## 🧪 Test Data
- Order IDs: ORD-7821, ORD-6543, ORD-5199
- Promo codes: SAVE10, WELCOME20, FREESHIP, LUXE15

## 📁 Structure
```
nova_assistant/
├── app.py              ← Main Streamlit app
├── ai/
│   └── nova_ai.py     ← Groq AI + gTTS voice
├── data/
│   └── store_data.py  ← Product catalog + cart
└── requirements.txt
```

## 🔧 Tech Stack
- Streamlit — UI
- Groq + Llama3 — AI responses
- gTTS — Text to speech
- Web Speech API — Voice input (browser)
- Python — Backend logic
