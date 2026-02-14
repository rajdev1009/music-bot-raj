import os
import requests
import logging
import threading
import time
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- 1. Fake Server for Koyeb ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    app.run(host='0.0.0.0', port=8000)

t = threading.Thread(target=run_flask)
t.daemon = True
t.start()
# --------------------------------

# --- 2. Bot Setup ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# YAHAN CHANGE KIYA HAI (New URL)
API_URL = "https://router.huggingface.co/models/facebook/musicgen-small"

HF_TOKEN = os.environ.get("HF_TOKEN")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def query_music(payload):
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.content, None
        else:
            return None, response.text
    except Exception as e:
        return None, str(e)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🎵 नमस्ते! मैं तैयार हूँ।\n\nबताओ कैसा गाना चाहिए? (Note: अगर मॉडल सो रहा होगा तो मैं बता दूंगा)"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    chat_id = update.effective_chat.id
    
    await context.bot.send_message(chat_id=chat_id, text=f"🎹 कोशिश कर रहा हूँ: '{user_text}'... (Wait 15s)")

    audio_bytes, error_msg = query_music({"inputs": user_text})
    
    if error_msg:
        if "loading" in error_msg.lower():
            await context.bot.send_message(chat_id=chat_id, text="⚠️ मॉडल अभी सो कर उठ रहा है (Loading)... \n\nकृपया **30 सेकंड रुकें** और फिर से वही मैसेज भेजें।")
        else:
            await context.bot.send_message(chat_id=chat_id, text=f"❌ Error: {error_msg}")
        return

    try:
        file_path = "music.flac"
        with open(file_path, "wb") as f:
            f.write(audio_bytes) 
        
        await context.bot.send_audio(chat_id=chat_id, audio=open(file_path, 'rb'), title=f"Raj AI: {user_text}")
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text="❌ फाइल भेजने में दिक्कत आई।")
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
        
