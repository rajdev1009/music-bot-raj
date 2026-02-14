import os
import requests
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Logging Setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Environment Variables (Koyeb se uthayega)
API_URL = "https://api-inference.huggingface.co/models/facebook/musicgen-small"
HF_TOKEN = os.environ.get("HF_TOKEN")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# Music Function
def query_music(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

# /start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🎵 नमस्ते राज भाई! मैं Koyeb पर चल रहा हूँ।\n\nबताओ कैसा गाना चाहिए? (Example: 'Romantic guitar')"
    )

# Message Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    chat_id = update.effective_chat.id
    
    await context.bot.send_message(chat_id=chat_id, text=f"🎹 गाना बना रहा हूँ: '{user_text}'... (10-15 sec रुको)")

    try:
        audio_bytes = query_music({"inputs": user_text})
        
        file_path = "music.flac"
        with open(file_path, "wb") as f:
            f.write(audio_bytes)
            
        await context.bot.send_audio(chat_id=chat_id, audio=open(file_path, 'rb'), title=f"Raj AI: {user_text}")
        
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text="❌ Error आया, दोबारा कोशिश करो।")
        print(e)

# Run Bot
if __name__ == '__main__':
    if not TELEGRAM_TOKEN or not HF_TOKEN:
        print("❌ Error: Tokens nahi mile! Koyeb Settings check karo.")
    else:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("✅ Bot Koyeb par Start ho gaya!")
        app.run_polling()
      
