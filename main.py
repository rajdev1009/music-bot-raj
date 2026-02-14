import os
import requests
import logging
import threading
import time
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- 1. Flask for Koyeb ---
app = Flask(__name__)
@app.route('/')
def home(): return "AI ChatBot is Live!"

def run_flask():
    app.run(host='0.0.0.0', port=8000)

threading.Thread(target=run_flask, daemon=True).start()

# --- 2. Bot Logic ---
logging.basicConfig(level=logging.INFO)

# AI Model - Hum isko badal kar thoda fast wala use karte hain
API_URL = "https://router.huggingface.co/hf-inference/models/mistralai/Mistral-7B-Instruct-v0.2"
HF_TOKEN = os.environ.get("HF_TOKEN")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def query_ai(prompt):
    # Hum 3 baar try karenge agar network issue aata hai
    for i in range(3):
        try:
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt, "parameters": {"max_new_tokens": 200}}, timeout=20)
            if response.status_code == 200:
                return response.json()[0]['generated_text']
            elif "loading" in response.text.lower():
                time.sleep(10) # 10 sec wait agar model load ho raha ho
                continue
        except:
            time.sleep(2)
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"नमस्ते राज देव भाई! 🙏\nमैं आपका AI दोस्त तैयार हूँ। कुछ भी पूछिए।")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    # Typing status
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    answer = query_ai(user_text)
    
    if answer:
        # Mistral ka format saaf karne ke liye
        clean_answer = answer.replace(user_text, "").strip()
        await update.message.reply_text(clean_answer if clean_answer else "मैं समझ नहीं पाया, कृपया फिर से पूछें।")
    else:
        await update.message.reply_text("❌ अभी सर्वर थोड़ा धीरे है, कृपया 10 सेकंड बाद फिर से मैसेज भेजें।")

if __name__ == '__main__':
    bot_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    bot_app.add_handler(CommandHandler('start', start))
    bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    bot_app.run_polling()
    
