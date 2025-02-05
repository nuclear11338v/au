import telebot
import threading
import logging
import re
import os
import requests
from instaloader import Instaloader, Post
from telebot import types
import subprocess

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

from telebot import types

@bot.message_handler(commands=["start"])
def start(message):
    chat_id = message.chat.id
    user_name = message.from_user.username or "No Username"
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Unknown"

    # Step 1: Send "⌛" and delete after 2 seconds
    temp_msg = bot.send_message(chat_id, "⌛")
    time.sleep(2)
    bot.delete_message(chat_id, temp_msg.message_id)

    # Step 2: Show typing animation
    bot.send_chat_action(chat_id, "typing")
    time.sleep(1.5)  # Simulate typing delay

    # Step 3: Prepare welcome message
    caption_text = (
        f"👋 **Welcome to the Instagram Downloader Bot!**\n\n"
        f"🆔 **YOUR NAME** - `@{user_name}`\n"
        f"🆔 **YOUR ID** - `{user_id}`\n"
        f"🆔 **FIRST NAME** - `{first_name}`\n\n"
        "📩 **Send me any public Instagram link** (Reels, Posts, etc.), and I'll help you download it.\n\n"
        "⚠️ **Only public posts are supported!**"
    )

    # Step 4: Create Inline Keyboard with Buttons
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("➕ Add Me to Your Group", url=f"https://t.me/{bot.get_me().username}?startgroup=true"))
    keyboard.add(types.InlineKeyboardButton("📢 Join", url="https://t.me/ARMANTEAMVIP"))
    keyboard.add(types.InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/MR_ARMAN_OWNER"))

    # Step 5: Fetch user's profile photo (if available)
    photos = bot.get_user_profile_photos(user_id)
    if photos.total_count > 0:
        # Get the highest resolution photo
        photo = photos.photos[0][-1].file_id
        bot.send_photo(chat_id, photo, caption=caption_text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        bot.send_message(chat_id, caption_text, parse_mode="Markdown", reply_markup=keyboard)
        
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

# Support command handler
@bot.message_handler(commands=['support'])
def support_command(message):
    bot.reply_to(message, "📞 For support, please contact @MR_ARMAN_OWNER or visit our support group: @ARMANTEAMVIP")

# Handle Video and Process in a separate thread to speed up
def process_video(message, video_file_id):
    video = bot.get_file(video_file_id)
    video_file_path = f'{video_file_id}.mp4'

    try:
        downloaded_file = bot.download_file(video.file_path)
        with open(video_file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.reply_to(message, "🔄 Processing your video, please wait...")

        if os.path.getsize(video_file_path) > 300 * 1024 * 1024:
            bot.reply_to(message, "❌ Sorry, the video size exceeds 300MB.")
            os.remove(video_file_path)
            return

        audio_file_path = f'{video_file_id}.mp3'
        command = f'ffmpeg -i "{video_file_path}" -q:a 0 -map a "{audio_file_path}" -threads 4 -preset fast'
        subprocess.run(command, shell=True)

        bot.send_chat_action(message.chat.id, 'upload_audio')
        with open(audio_file_path, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, caption="DOWNLOADED BYE @Sidgkdigdjgzigdotxotbot")

        os.remove(video_file_path)
        os.remove(audio_file_path)

        bot.send_message(message.chat.id, "👉 PLEASE JOIN : @ARMANTEAMVIP\n\nDEVELOPER @MR_ARMAN_OWNER")

    except Exception as e:
        bot.reply_to(message, "⚠️ An error occurred during processing. Please try again later.")
        print(f"Error: {e}")


@bot.message_handler(content_types=['video'])
def handle_video(message):
    video_file_id = message.video.file_id
    threading.Thread(target=process_video, args=(message, video_file_id)).start()  # Process video in a new thread
    
    
# Main function
if __name__ == "__main__":
    logger.info("Bot is running...")
    bot.infinity_polling()


