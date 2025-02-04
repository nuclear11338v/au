from yt_dlp import YoutubeDL
import telebot
import os
import logging
import time
from telegram.error import TimedOut

# Set up logging
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot Token
BOT_TOKEN = "7685491877:AAGCya_bYave_CQm0cyEUNG0hnhRYt1oCsA"  # Replace with your actual bot token
bot = telebot.TeleBot(BOT_TOKEN)

# Retry parameters
MAX_RETRIES = 3
TIMEOUT = 120  # 2 minutes timeout for sending the video

# Function to download YouTube content
def download_youtube_content(url, format_type):
    try:
        # Clean the URL by removing leading/trailing whitespaces
        url = url.strip()  # Remove any leading/trailing whitespace

        # yt-dlp options
        ydl_opts = {
            "format": "bestaudio/best" if format_type == "audio" else "bestvideo+bestaudio",
            "outtmpl": "./downloads/%(title)s.%(ext)s",
            "noplaylist": True,
            "progress_hooks": [progress_hook]
        }

        # Extracting info and download
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_duration = info_dict.get("duration", 0)

            # If video exceeds 5 hours, cancel the download
            if video_duration > 18000:  # 5 hours in seconds
                os.remove(ydl.prepare_filename(info_dict))
                return None, "❌ Video exceeds 5 hours. Download cancelled."
            return ydl.prepare_filename(info_dict), None
    except Exception as e:
        logger.error(f"Error downloading YouTube content: {e}")
        return None, f"❌ Error: {str(e)}"

# Progress Hook for Download
def progress_hook(d):
    if d['status'] == 'finished':
        logger.info(f"Download finished: {d['filename']}")

# Function to send the video with retry logic
def send_video_with_retry(chat_id, file_path, retries=0):
    try:
        bot.send_video(chat_id, open(file_path, "rb"), timeout=TIMEOUT)
        os.remove(file_path)  # Clean up after sending the file
    except TimedOut:
        if retries < MAX_RETRIES:
            logger.warning("Timeout error. Retrying...")
            time.sleep(5)  # Wait before retrying
            send_video_with_retry(chat_id, file_path, retries + 1)
        else:
            logger.error(f"Failed to send video after {MAX_RETRIES} attempts.")
            bot.reply_to(chat_id, "❌ Failed to send the video due to timeout issues.")
            os.remove(file_path)  # Clean up even after failure
    except Exception as e:
        logger.error(f"Error sending video: {e}")
        bot.reply_to(chat_id, f"❌ Error sending the video: {e}")
        os.remove(file_path)

# Handle incoming messages (URLs)
@bot.message_handler(func=lambda message: True)
def handle_youtube_url(message):
    url = message.text

    # Check if the URL contains "youtube.com" or "youtu.be"
    if "youtube.com" in url or "youtu.be" in url:
        bot.reply_to(message, "⏳ Downloading... Please wait.")
        file_path, error_msg = download_youtube_content(url, "video")
        
        if file_path:
            # Check if the file exists and its size
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                if file_size > 2 * 1024 * 1024 * 1024:  # File size greater than 2GB
                    bot.reply_to(message, "❌ The video is too large to send (max 2GB).")
                    os.remove(file_path)
                    return
                bot.reply_to(message, "✅ Download complete! Sending the file...")
                send_video_with_retry(message.chat.id, file_path)  # Send with retry logic
            else:
                bot.reply_to(message, "❌ File does not exist. Please try again.")
        else:
            bot.reply_to(message, error_msg)
    else:
        bot.reply_to(message, "❌ This doesn't seem to be a valid YouTube URL.")

# Bot status command (optional, can be kept or removed)
@bot.message_handler(commands=["status"])
def status(message):
    bot.reply_to(message, "✅ Bot is running smoothly.\n⚡ Speed: Fast\n👥 Users: 100+")

# To handle any other messages (optional, can be removed)
@bot.message_handler(func=lambda message: True)
def all_messages(message):
    bot.reply_to(message, f"Received message: {message.text}")

# Run the bot
try:
    bot.polling(none_stop=True)
except Exception as e:
    print(f"Error occurred: {e}")
