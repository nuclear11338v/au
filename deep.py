import logging
import yt_dlp
import telebot
import requests
import os
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = '7685491877:AAGCya_bYave_CQm0cyEUNG0hnhRYt1oCsA'
YOUTUBE_API_KEY = "AIzaSyBcXM10C3POyDSFoLYHspgf2A3ncqnSVO8"

bot = telebot.TeleBot(TOKEN)

def get_video_info(video_id):
    """Fetches video details from YouTube API"""
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&id={video_id}&key={YOUTUBE_API_KEY}"
    response = requests.get(url).json()
    
    if "items" in response and len(response["items"]) > 0:
        return response["items"][0]
    return None

def extract_video_id(url):
    """Extracts video ID from YouTube URL"""
    patterns = [
        r"(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]+)",
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

@bot.message_handler(commands=['Dyt'])
def download_youtube_video(message):
    url = message.text[5:].strip()
    if not url:
        bot.reply_to(message, "❌ Please provide a YouTube video URL.")
        return
    
    video_id = extract_video_id(url)
    if not video_id:
        bot.reply_to(message, "⚠️ Invalid YouTube link. Please provide a valid video URL.")
        return

    video_info = get_video_info(video_id)
    if not video_info:
        bot.reply_to(message, "❌ Failed to retrieve video details. The video may not exist.")
        return

    title = video_info["snippet"]["title"]
    bot.send_message(message.chat.id, f"📥 Downloading: {title}")

    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'socket_timeout': 14400,
        'http_chunk_size': 1048576,
        'geo_bypass': True,  # Bypass location-based restrictions
        'nocheckcertificate': True,  # Skip SSL verification
        'progress_hooks': [lambda d: progress_hook(d, message.chat.id)]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_file_path = ydl.prepare_filename(info_dict)

        with open(video_file_path, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file, caption="✅ Download complete!")
        
        os.remove(video_file_path)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Progress updates
def progress_hook(d, chat_id):
    if d['status'] == 'downloading':
        percent = (d.get('downloaded_bytes', 0) / d.get('total_bytes', 1)) * 100
        bot.send_message(chat_id, f"⬇️ Downloading... {percent:.2f}% completed")

bot.infinity_polling()
        
