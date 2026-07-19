import os
import asyncio
import logging
import telebot
from telebot.async_telebot import AsyncTeleBot
import yt_dlp

# Railway Variables'dan BOT_TOKENni olish
TOKEN = os.environ.get('BOT_TOKEN')

if not TOKEN:
    raise ValueError("Xatolik: BOT_TOKEN aniqlanmadi! Railway Variables'ni tekshiring.")

logging.basicConfig(level=logging.INFO)
bot = AsyncTeleBot(TOKEN)

def download_music(url):
    # Fayl nomini tasodifiy yaratamiz
    filename = f"music_{os.urandom(4).hex()}.mp3"
    
    # Sozlamalar: hech qanday cookie kerak emas
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        'outtmpl': filename,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return filename

@bot.message_handler(commands=['start'])
async def start(message):
    await bot.reply_to(message, "Salom! Menga musiqa linkini yuboring (SoundCloud yoki boshqa saytlar), men sizga mp3 qilib yuklab beraman.")

@bot.message_handler(func=lambda message: message.text.startswith('http'))
async def handle_link(message):
    url = message.text
    status_msg = await bot.reply_to(message, "⏳ Yuklanmoqda, kuting...")
    
    file_path = None
    try:
        loop = asyncio.get_running_loop()
        file_path = await loop.run_in_executor(None, download_music, url)
        
        with open(file_path, 'rb') as f:
            await bot.send_audio(message.chat.id, f)
        
        await bot.delete_message(message.chat.id, status_msg.message_id)
        
    except Exception as e:
        await bot.edit_message_text(f"❌ Xatolik yuz berdi: {e}", message.chat.id, status_msg.message_id)
    
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    asyncio.run(bot.polling())
