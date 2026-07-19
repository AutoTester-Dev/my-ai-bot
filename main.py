import os
import asyncio
import logging
from telebot.async_telebot import AsyncTeleBot
import yt_dlp

# Railway'dan tokenni o'qish (o'zgaruvchilar bo'limida BOT_TOKEN bo'lishi shart)
TOKEN = os.environ.get('BOT_TOKEN')

if not TOKEN:
    raise ValueError("Xatolik: BOT_TOKEN aniqlanmadi!")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
bot = AsyncTeleBot(TOKEN)

def download_media_sync(query, media_type):
    ext = 'mp3' if media_type == 'audio' else 'mp4'
    filename = f"media_{os.urandom(4).hex()}.{ext}"
    
    # YouTube cheklovlarini chetlab o'tish uchun kuchaytirilgan sozlamalar
    ydl_opts = {
        'format': 'bestaudio/best' if media_type == 'audio' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}] if media_type == 'audio' else [],
        'outtmpl': filename,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch1',
        'nocheckcertificate': True, 
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([query])
    return filename

@bot.message_handler(commands=['start', 'help'])
async def send_welcome(message):
    await bot.reply_to(message, "Salom! Musiqa yoki video uchun /mp3 yoki /mp4 deb yozing.")

@bot.message_handler(commands=['mp3', 'mp4'])
async def handle_media(message):
    cmd = message.text.split()[0]
    query = message.text.replace(cmd, '').strip()
    
    if not query:
        await bot.reply_to(message, "Iltimos, nomini yozing.")
        return
    
    status_msg = await bot.reply_to(message, "⏳ Qidirilmoqda...")
    media_type = 'audio' if cmd == '/mp3' else 'video'
    file_path = None
    
    try:
        loop = asyncio.get_running_loop()
        file_path = await loop.run_in_executor(None, download_media_sync, query, media_type)
        
        await bot.edit_message_text("📤 Yuklanmoqda...", message.chat.id, status_msg.message_id)
        
        with open(file_path, 'rb') as f:
            if media_type == 'audio':
                await bot.send_audio(message.chat.id, f)
            else:
                await bot.send_video(message.chat.id, f)
        
        await bot.delete_message(message.chat.id, status_msg.message_id)
        
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await bot.edit_message_text(f"❌ Yuklashda xatolik yuz berdi. YouTube cheklov qo'ygan bo'lishi mumkin.", message.chat.id, status_msg.message_id)
        
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    asyncio.run(bot.polling())
