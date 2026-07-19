import os
import telebot
import yt_dlp
import requests

# Railway'dan o'zgaruvchilarni o'qiydi
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_gemini_response(prompt):
    # API kaliti mavjudligini tekshirish
    if not GEMINI_API_KEY:
        return "Xatolik: GEMINI_API_KEY sozlanmagan."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": str(prompt)}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"API Xatosi: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Dasturiy xato: {str(e)}"

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

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Men AI botman. Savollaringizni yozing yoki /mp3 [qo'shiq nomi] yuboring.")

@bot.message_handler(commands=['mp3'])
def handle_mp3(message):
    query = message.text.replace('/mp3', '').strip()
    if not query:
        bot.reply_to(message, "Iltimos, qo'shiq nomini yozing. Masalan: /mp3 Ummon")
        return
    msg = bot.reply_to(message, "🔍 Qidirilmoqda...")
    try:
        file_path = download_music_by_query(query)
        with open(file_path, 'rb') as audio:
            bot.send_audio(message.chat.id, audio)
        os.remove(file_path)
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Xatolik yuz berdi: {str(e)}", message.chat.id, msg.message_id)

@bot.message_handler(func=lambda message: True)
def handle_ai(message):
    answer = get_gemini_response(message.text)
    bot.reply_to(message, answer)

print("Bot ishga tushdi...")
bot.polling()
