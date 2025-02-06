import telebot
import os
import subprocess
import threading

API_TOKEN = '7685491877:AAGCya_bYave_CQm0cyEUNG0hnhRYt1oCsA'
bot = telebot.TeleBot(API_TOKEN)

ADMIN_ID = 7858368373  # Replace with your admin ID
USER_IDS_FILE = "user_id.txt"

# Function to save user IDs
def save_user(user_id):
    with open(USER_IDS_FILE, "a+") as file:
        file.seek(0)
        users = file.read().splitlines()
        if str(user_id) not in users:
            file.write(f"{user_id}\n")

# Start command handler
@bot.message_handler(commands=['start'])
def start_command(message):
    save_user(message.from_user.id)
    bot.reply_to(message, "👋 Welcome to Video to Audio Converter Bot!\n\nSend a video and I'll convert it to audio for you.")

# Help command handler
@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "🛠 Available Commands:\n"
        "/start - Welcome message\n"
        "/help - List of available commands\n"
        "/support - Get support information\n"
        "/users - Show all users (Admin Only)\n"
        "/broadcast - Send message to all users (Admin Only)\n"
        "Simply send a video to convert it into audio!"
    )
    bot.reply_to(message, help_text)

# Support command handler
@bot.message_handler(commands=['support'])
def support_command(message):
    bot.reply_to(message, "📞 For support, contact @MR_ARMAN_OWNER or visit @ARMANTEAMVIP")

# Notify admin about user conversion
def notify_admin(user, status):
    try:
        bot.send_message(
            ADMIN_ID,
            f"*New user convert*\n"
            f"User name: @{user.username if user.username else 'No Username'}\n"
            f"User ID: {user.id}\n"
            f"User converts: Yes\n"
            f"User converting: {status}",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Admin notification failed: {e}")

# Process video
def process_video(message, video_file_id):
    user = message.from_user
    video = bot.get_file(video_file_id)
    video_file_path = f'{video_file_id}.mp4'

    try:
        downloaded_file = bot.download_file(video.file_path)
        with open(video_file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.reply_to(message, "🔄 Processing your video, please wait...")

        if os.path.getsize(video_file_path) > 20 * 1024 * 1024:
            bot.reply_to(message, "❌ Sorry, the video size exceeds 20MB.")
            os.remove(video_file_path)
            notify_admin(user, "failed")
            return

        audio_file_path = f'{video_file_id}.mp3'
        command = f'ffmpeg -i "{video_file_path}" -q:a 0 -map a "{audio_file_path}" -threads 4 -preset fast'
        subprocess.run(command, shell=True)

        bot.send_chat_action(message.chat.id, 'upload_audio')
        with open(audio_file_path, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, caption="DOWNLOADED BY @Sidgkdigdjgzigdotxotbot")

        os.remove(video_file_path)
        os.remove(audio_file_path)

        bot.send_message(message.chat.id, "👉 PLEASE JOIN: @ARMANTEAMVIP\n\nDEVELOPER: @MR_ARMAN_OWNER")
        notify_admin(user, "successfully")

    except Exception as e:
        bot.reply_to(message, "⚠️ An error occurred during processing. Please try again later.")
        print(f"Error: {e}")
        notify_admin(user, "failed")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    save_user(message.from_user.id)
    video_file_id = message.video.file_id
    threading.Thread(target=process_video, args=(message, video_file_id)).start()

# Show all users (Admin Only)
@bot.message_handler(commands=['users'])
def show_users(message):
    if message.from_user.id == ADMIN_ID:
        try:
            with open(USER_IDS_FILE, "r") as file:
                user_ids = file.read().splitlines()

            if user_ids:
                user_list = "\n".join([f"ID: {uid}" for uid in set(user_ids)])
                bot.send_message(message.chat.id, f"👥 *Users List:*\n\n{user_list}", parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "No users found.")
        except FileNotFoundError:
            bot.send_message(message.chat.id, "No users found.")
    else:
        bot.reply_to(message, "❌ You are not authorized to view this list.")

# Broadcast message (Admin Only)
@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "📢 Please enter your message to broadcast.")
        bot.register_next_step_handler(message, send_broadcast)
    else:
        bot.reply_to(message, "❌ You are not authorized to use this command.")

def send_broadcast(message):
    try:
        with open(USER_IDS_FILE, "r") as file:
            user_ids = file.read().splitlines()

        success, failed = 0, 0
        for user_id in set(user_ids):
            try:
                bot.send_message(user_id, f"📢 *Broadcast Message:*\n\n{message.text}", parse_mode="Markdown")
                success += 1
            except Exception:
                failed += 1

        bot.send_message(message.chat.id, f"✅ Message sent to {success} users.\n❌ Failed: {failed}")

    except FileNotFoundError:
        bot.send_message(message.chat.id, "No users found.")

# Start polling
bot.polling(non_stop=True)
                               
