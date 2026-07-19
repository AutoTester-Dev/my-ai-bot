import os
import telebot
import yt_dlp
import requests
import json

# Railway Variables'dan o'zgaruvchilarni chaqirib olish
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MODEL_NAME = "gemini-1.5-flash"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_gemini_response(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": str(prompt)}]}]}
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"API Xatosi ({response.status_code})"
    except Exception as e:
        return f"Xato: {str(e)}"

def download_music_by_query(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        'outtmpl': 'music.%(ext)s',
        'default_search': 'ytsearch1',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([query])
    return 'music.mp3'

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Men tayyorman. Savol bering yoki /mp3 buyrug'idan foydalaning.")

@bot.message_handler(commands=['mp3'])
def handle_mp3(message):
    query = message.text.replace('/mp3', '').strip()
    if not query:
        bot.reply_to(message, "Qo'shiq nomini yozing. Masalan: /mp3 Ummon")
        return
    msg = bot.reply_to(message, "🔍 Qidirilmoqda...")
    try:
        file_path = download_music_by_query(query)
        with open(file_path, 'rb') as audio:
            bot.send_audio(message.chat.id, audio)
        os.remove(file_path)
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Yuklashda xatolik: {str(e)}", message.chat.id, msg.message_id)

@bot.message_handler(func=lambda message: True)
def handle_ai(message):
    answer = get_gemini_response(message.text)
    bot.reply_to(message, answer)

print("Bot ishga tushdi...")
bot.infinity_polling()
        
