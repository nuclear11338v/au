import telebot
import os
import subprocess
import threading

API_TOKEN = '7685491877:AAGCya_bYave_CQm0cyEUNG0hnhRYt1oCsA'
bot = telebot.TeleBot(API_TOKEN)

# Start command handler
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "👋 Welcome to Video to Audio Converter Bot!\n\nSend a video and I'll convert it to audio for you.")

# Help command handler
@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "🛠 Available Commands:\n"
        "/start - Welcome message\n"
        "/help - List of available commands\n"
        "/support - Get support information\n"
        "Simply send a video to convert it into audio!"
    )
    bot.reply_to(message, help_text)

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

# Polling
bot.polling()
