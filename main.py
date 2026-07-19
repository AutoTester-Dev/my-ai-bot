import telebot
import requests
import json

# 1. Sozlamalar
TELEGRAM_TOKEN = "TELEGRAM_TOKENINGIZNI_SHU_YERGA_YOZING"
GEMINI_API_KEY = "AIza..." # AIza bilan boshlanadigan to'g'ri kalit
MODEL_NAME = "gemini-1.5-flash"

# API manzili
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_gemini_response(prompt):
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    response = requests.post(URL, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"Xatolik ({response.status_code}): {response.text}"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Men tayyorman (Requests usuli). Savolingizni yuboring.")

@bot.message_handler(func=lambda message: True)
def chat(message):
    response_text = get_gemini_response(message.text)
    bot.reply_to(message, response_text)

print("Bot ishga tushdi...")
bot.infinity_polling()
