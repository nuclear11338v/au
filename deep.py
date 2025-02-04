import telebot
import os
from face_swap import face_swap_function  # Face Swap ke liye external script

TOKEN = "8056603811:AAH32j_hunSJEHTzwaFzB1b8rbybVlVbzWg"
bot = telebot.TeleBot(TOKEN)

user_data = {}  # Users ka temporary data store karne ke liye

# Start command
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "Namaste! Main ek Face Swap bot hoon.\n"
                          "Mujhe ek photo aur ek video bhejiye, fir main aapka face swap karne ki koshish karunga!\n"
                          "Help ke liye /help likhein.")

# Help command
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message, "1. Pehle ek photo bhejiye jisme ek face ho.\n"
                          "2. Fir ek video bhejiye.\n"
                          "3. Main photo ka face video me dalne ki koshish karunga!")

# Photo receive karne ka function
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        file_path = f"photo_{message.chat.id}.jpg"
        with open(file_path, "wb") as new_file:
            new_file.write(downloaded_file)
        
        user_data[message.chat.id] = {"photo": file_path}
        bot.reply_to(message, "Aapki photo receive ho gayi! Ab ek video bhejiye.")

    except Exception as e:
        bot.reply_to(message, f"Photo process karne me error aaya: {str(e)}")

# Video receive karne ka function
@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        file_id = message.video.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        file_path = f"video_{message.chat.id}.mp4"
        with open(file_path, "wb") as new_file:
            new_file.write(downloaded_file)
        
        if message.chat.id in user_data and "photo" in user_data[message.chat.id]:
            user_data[message.chat.id]["video"] = file_path
            bot.reply_to(message, "Aapka video receive ho gaya! Ab face swap process shuru ho raha hai...")

            # Face Swap process call karna
            output_video = f"output_{message.chat.id}.mp4"
            success = face_swap_function(user_data[message.chat.id]["photo"], file_path, output_video)

            if success:
                with open(output_video, "rb") as video:
                    bot.send_video(message.chat.id, video)
                bot.reply_to(message, "Face Swap complete! Yeh raha aapka video.")
            else:
                bot.reply_to(message, "Face Swap me error aaya. Kripya phir se try karein.")

        else:
            bot.reply_to(message, "Pehle ek photo bhejiye, fir video bhejiye!")

    except Exception as e:
        bot.reply_to(message, f"Video process karne me error aaya: {str(e)}")

# Unknown commands ka handler
@bot.message_handler(func=lambda message: True)
def unknown_command(message):
    bot.reply_to(message, "Mujhe yeh command samajh nahi aayi! Help ke liye /help likhein.")

if __name__ == "__main__":
    bot.polling(none_stop=True)
