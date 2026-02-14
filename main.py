import os
import requests
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- 1. Fake Server for Koyeb Health Check ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    # Koyeb Port 8000 par check karega
    app.run(host='0.0.0.0', port=8000)

# Flask ko alag thread mein chalayenge taaki Bot na ruke
t = threading.Thread(target=run_flask)
t.daemon = True
t.start()
# ---------------------------------------------

# --- 2. Bot Setup ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

API_URL = "https://api-inference.huggingface.co/models/facebook/musicgen-small"
HF_TOKEN = os.environ.get("HF_TOKEN")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def query_music(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🎵 नमस्ते! मैं Koyeb पर ज़िंदा हूँ!\n\nकैसा गाना चाहिए? (Example: 'Romantic guitar')"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    chat_id = update.effective_chat.id
    
    await context.bot.send_message(chat_id=chat_id, text=f"🎹 गाना बना रहा हूँ: '{user_text}'... (15 sec)")

    try:
        audio_bytes = query_music({"inputs": user_text})
        file_path = "music.flac"
        with open(file_path, "wb") as f:
            f.write(audio_bytes) 
        await context.bot.send_audio(chat_id=chat_id, audio=open(file_path, 'rb'), title=f"Raj AI: {user_text}")
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text="❌ Error आया, दोबारा कोशिश करो।")
        print(e)

if __name__ == '__main__':
    if not TELEGRAM_TOKEN or not HF_TOKEN:
        print("❌ Tokens Missing!")
    else:
        app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app_bot.add_handler(CommandHandler('start', start))
        app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("✅ Bot Started...")
        app_bot.run_polling()
        
