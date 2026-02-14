import os
import requests
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- 1. Fake Server for Koyeb ---
app = Flask(__name__)

@app.route('/')
def home():
    return "ChatBot is Running!"

def run_flask():
    app.run(host='0.0.0.0', port=8000)

t = threading.Thread(target=run_flask)
t.daemon = True
t.start()

# --- 2. ChatBot Setup ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# AI Model for Chatting
API_URL = "https://router.huggingface.co/hf-inference/models/HuggingFaceH4/zephyr-7b-beta"
HF_TOKEN = os.environ.get("HF_TOKEN")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def query_chat(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="नमस्ते राज भाई! 🙏 मैं आपका AI Chatbot हूँ।\n\nमुझसे कुछ भी पूछें, मैं आपके हर सवाल का जवाब दूँगा!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    chat_id = update.effective_chat.id
    
    # Typing action dikhane ke liye
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    try:
        # AI ko message bhejna
        output = query_chat({
            "inputs": f"<|system|>\nYou are a helpful AI assistant. Respond in Hindi or English as requested.</s>\n<|user|>\n{user_text}</s>\n<|assistant|>\n",
            "parameters": {"max_new_tokens": 500}
        })
        
        # AI ka response nikalna
        result = output[0]['generated_text'].split("<|assistant|>\n")[-1]
        await context.bot.send_message(chat_id=chat_id, text=result)

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text="❌ थोड़ा नेटवर्क इशू है, फिर से कोशिश करें।")
        print(f"Error: {e}")

if __name__ == '__main__':
    app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app_bot.add_handler(CommandHandler('start', start))
    app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("✅ ChatBot is Live!")
    app_bot.run_polling()
    
