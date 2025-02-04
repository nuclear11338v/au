import telebot
import threading
import logging
import re
import os
import requests
from instaloader import Instaloader, Post
from telebot import types

# Logging setup
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Token
TOKEN = "8056603811:AAH32j_hunSJEHTzwaFzB1b8rbybVlVbzWg"  # Set this in your environment variables

bot = telebot.TeleBot(TOKEN)

# Instagram credentials (set in environment variables)
INSTAGRAM_USERNAME = "rjfjfndjdjfndnfnfnfjfndn"
INSTAGRAM_PASSWORD = "your_instagram_password_here"

ADMIN_ID = "7858368373"

loader = Instaloader()
SESSION_FILE = f"{os.getcwd()}/session-{INSTAGRAM_USERNAME}"
session_lock = threading.Lock()

# Dictionary to store users and their downloads
user_downloads = {}

# Load or create Instagram session
def load_or_create_session():
    with session_lock:
        if os.path.exists(SESSION_FILE):
            loader.load_session_from_file(INSTAGRAM_USERNAME, filename=SESSION_FILE)
        else:
            loader.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            loader.save_session_to_file(SESSION_FILE)

load_or_create_session()

# Helper functions
def extract_shortcode(url):
    """Extract shortcode from Instagram URL."""
    match = re.search(r"instagram\.com/(?:p|reel|tv)/([^/?#&]+)", url)
    return match.group(1) if match else None

def is_valid_instagram_url(url):
    """Validate Instagram URL."""
    return bool(re.match(r"https?://(www\.)?instagram\.com/(p|reel|tv)/", url))

def fetch_instagram_reel(shortcode):
    """Fetch Instagram reel media URL and caption."""
    try:
        post = Post.from_shortcode(loader.context, shortcode)
        if post.is_video:
            return post.video_url, post.caption
        else:
            return None, None
    except Exception as e:
        logger.error(f"Error fetching Instagram reel: {e}")
        return None, None

def download_file(url, file_name, retries=3):
    """Download a file with retry mechanism."""
    for attempt in range(retries):
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            with open(file_name, "wb") as f:
                for chunk in response.iter_content(chunk_size=512):
                    if chunk:
                        f.write(chunk)
            return True
        except requests.exceptions.RequestException as e:
            print(f"Download failed (attempt {attempt+1}): {e}")
            time.sleep(5)
    return False

# Command: Start
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "👋 Welcome to the Instagram Downloader Bot!\n\n"
        "📩 Send me any **public** Instagram link (reels, posts, etc.), and I'll help you download it.\n\n"
        "⚠️ Only public posts are supported!"
    )

# Command: Users (Admin only)
@bot.message_handler(commands=["users"])
def list_users(message):
    if str(message.chat.id) != ADMIN_ID:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return
    
    if not user_downloads:
        bot.reply_to(message, "📂 No user data available.")
        return

    users_text = "📜 User Download List:\n\n"
    for user_id, details in user_downloads.items():
        users_text += f"👤 Username: {details['username']}\n"
        users_text += f"🆔 User ID: {user_id}\n"
        users_text += f"📥 Downloaded Videos: {len(details['downloads'])}\n"
        users_text += "_________________________\n"

    bot.send_message(message.chat.id, users_text)

# Handle: Instagram Link
@bot.message_handler(func=lambda message: is_valid_instagram_url(message.text))
def download_content(message):
    user_id = message.chat.id
    username = message.from_user.username or "Unknown"

    if user_id not in user_downloads:
        user_downloads[user_id] = {"username": username, "downloads": []}

    url = message.text.strip()
    shortcode = extract_shortcode(url)

    if not shortcode:
        bot.reply_to(message, "❌ Invalid Instagram URL. Please send a valid link.")
        return

    bot.send_chat_action(message.chat.id, "typing")
    progress_msg = bot.send_message(message.chat.id, "⏳")

    reel_url, caption = fetch_instagram_reel(shortcode)
    if reel_url:
        bot.send_chat_action(message.chat.id, "upload_video")

        file_name = f"reel_{message.chat.id}.mp4"
        if download_file(reel_url, file_name):
            credit_text = "\n\nJoin :-> @ARMAN_TEAMVIP\nThis video is downloaded by: @Dbdjdjdjdjdjbot"
            full_caption = caption + credit_text if caption else credit_text

            with open(file_name, "rb") as video:
                bot.send_video(message.chat.id, video=video, caption=full_caption)

            os.remove(file_name)
            bot.delete_message(message.chat.id, progress_msg.message_id)

            # Log successful download
            user_downloads[user_id]["downloads"].append(reel_url)

            # Notify admin
            admin_message = (
                f"📥 New Download:\n"
                f"👤 User: @{username}\n"
                f"🆔 User ID: {user_id}\n"
                f"🔗 Download Link: {url}\n"
                f"✅ Status: Download Success"
            )
            bot.send_message(ADMIN_ID, admin_message)
        else:
            bot.edit_message_text("❌ Failed to download. Please try again later.", message.chat.id, progress_msg.message_id)

            # Notify admin about failure
            admin_message = (
                f"❌ Failed Download:\n"
                f"👤 User: @{username}\n"
                f"🆔 User ID: {user_id}\n"
                f"🔗 Download Link: {url}\n"
                f"❌ Status: Download Failed"
            )
            bot.send_message(ADMIN_ID, admin_message)
    else:
        bot.edit_message_text("❌ Failed to fetch the reel. Ensure it's public.", message.chat.id, progress_msg.message_id)

        # Notify admin about failure
        admin_message = (
            f"❌ Failed Fetch:\n"
            f"👤 User: @{username}\n"
            f"🆔 User ID: {user_id}\n"
            f"🔗 Download Link: {url}\n"
            f"❌ Status: Fetch Failed"
        )
        bot.send_message(ADMIN_ID, admin_message)

# Main function
if __name__ == "__main__":
    logger.info("Bot is running...")
    bot.infinity_polling()
