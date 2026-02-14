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
def home(): return "Rajdev Website-Style Bot is Live!"

def run_flask():
    app.run(host='0.0.0.0', port=8000)

threading.Thread(target=run_flask, daemon=True).start()

# --- 2. AI Bot Setup ---
logging.basicConfig(level=logging.INFO)

# Wahi smart model jo website par hai
API_URL = "https://router.huggingface.co/hf-inference/models/mistralai/Mistral-7B-Instruct-v0.3"
HF_TOKEN = os.environ.get("HF_TOKEN")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def query_ai(user_msg):
    try:
        # Website jaisa system prompt aur format
        payload = {
            "inputs": f"<s>[INST] You are Rajdev AI Assistant. Help the user in Hindi/English. \nUser: {user_msg} [/INST]</s>",
            "parameters": {"max_new_tokens": 500, "temperature": 0.7}
        }
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            res_data = response.json()
            # AI ka reply extract karna
            full_text = res_data[0]['generated_text']
            # User ka sawal hata kar sirf answer dena
            answer = full_text.split("[/INST]</s>")[-1].strip()
            return answer
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 नमस्ते राज देव भाई! आपकी वेबसाइट वाला AI अब टेलीग्राम पर भी हाज़िर है। पूछिए क्या पूछना है?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    # Bot typing dikhayega
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    answer = query_ai(user_text)
    
    if answer:
        await update.message.reply_text(answer)
    else:
        await update.message.reply_text("❌ सर्वर थोड़ा लोड ले रहा है, 10 सेकंड बाद फिर से पूछें।")

if __name__ == '__main__':
    bot_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    bot_app.add_handler(CommandHandler('start', start))
    bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("✅ Web-Style Bot Started!")
    bot_app.run_polling()
    
