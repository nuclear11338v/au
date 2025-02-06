from telebot import types
import telebot
import schedule
import time
import threading
import os
import json
import random

# Replace 'YOUR_TOKEN' with your actual bot token
TOKEN = '7056119124:AAFXyI0gFTehd_wC-Hj2bqbJoAcze_ekENk'
bot = telebot.TeleBot(TOKEN)

# A list to store user IDs
user_ids = []
channel_ids = []
OWNER_ID = '7858368373'

# Abusive Words List (Hindi & English)
ABUSIVE_WORDS = [
    "mc", "bc", "bhosdike", "madarchod", "chutiya", "gandu", "randi", "suar", "bkl", "fuck", "shit", "bitch", 
    "asshole", "bastard", "dumbass", "motherfucker", "pussy", "dick", "cock", "slut", "whore", "idiot", "cunt", 
    "fucker", "fag", "prick", "bastard", "douchebag", "twat", "wanker", "retard", "shithead", "dickhead", "cockhead", 
    "arsehole", "wankstain", "buttplug", "clit", "nigger", "kike", "spic", "gook", "chink", "raghead", "paki", 
    "negro", "gypsy", "chudail", "kali", "khajur", "chut", "jhaanj", "bhand", "paandu", "bichua", "dalal", "behenchod", 
    "bichdi", "gandagi", "kaamchor", "pichwaada", "maadarchod", "chooth", "zinda laash", "kutti", "topi wala", 
    "jhattu", "kaalu", "sabziwala", "gandgi ka dher", "tharki", "bekaar", "billa", "dharna", "ek number ka kutta", 
    "daaku", "nashaa", "bhadwa", "muh ka daant", "kaminey", "saala", "mooh ka rakhwala", "bawarchi", "chaddhi wala", 
    "bezzati", "lode", "kundi", "lathmar", "chhakka", "kaam ka gadha", "kulehri", "chep", "chhori", "dharamshala", 
    "jhanda", "ghamand", "balle balle", "guddu", "lauda", "pinky", "rasgulla", "gangsta", "badmash", "lalkila", 
    "pataka", "sharm ka jata", "fart", "murga", "dhakkan", "chooha", "bochi", "khandaani", "gappu", "lodi", "thande", 
    "marich", "paise ka kachra", "neech", "gadi wala", "bhoot", "shaitaan", "bawri", "achha pichla", "badtameez", "jism ka rakhwala"
]

WARNINGS_FILE = "warnings.json"

# Load Warnings
if os.path.exists(WARNINGS_FILE):
    with open(WARNINGS_FILE, "r") as f:
        warnings = json.load(f)
else:
    warnings = {}

# Save Warnings
def save_warnings():
    with open(WARNINGS_FILE, "w") as f:
        json.dump(warnings, f, indent=4)

# Check if User is Admin
def is_admin(chat_id, user_id):
    try:
        chat_admins = bot.get_chat_administrators(chat_id)
        return any(admin.user.id == user_id for admin in chat_admins)
    except Exception as e:
        return False
        
# Load user IDs from file
def load_user_ids():
    global user_ids
    if os.path.exists("user_ids.txt"):
        with open("user_ids.txt", "r") as f:
            user_ids = [int(line.strip()) for line in f.readlines()]

def load_channel_ids():
    global channel_ids
    if os.path.exists("channel_ids.txt"):
        with open("channel_ids.txt", "r") as f:
            channel_ids = [int(line.strip()) for line in f.readlines()]
            
            
# Save user IDs to file
def save_user_ids():
    with open("user_ids.txt", "w") as f:
        for user_id in user_ids:
            f.write(f"{user_id}\n")

def save_channel_ids():
    with open("channel_ids.txt", "w") as f:
        for channel_id in channel_ids:
            f.write(f"{channel_id}\n")
            
            
# Function to send a good morning message
def send_good_morning():
    for user_id in user_ids:
        bot.send_photo(user_id, "https://graph.org/file/bf067788a313dde08c58f-48a5aff2c2ed5a785a.jpg", caption="🌞 Good morning! 🌼✨\n\nWishing you a day filled with positivity and joy. 🌈\nMay every moment bring you a reason to smile 😊\nand each challenge be an opportunity to grow. 🌟\n\nRemember, today is a blank canvas—paint it beautifully! 🎨\nHave an amazing day ahead! 💖!")

# Function to send a good afternoon message
def send_good_afternoon():
    for user_id in user_ids:
        bot.send_photo(user_id, "https://graph.org/file/767bfc3f0cb2d61ab2882-c01696337a5e17b55b.jpg", caption="☀️ Good afternoon! 🌻\n\nI hope your day is going wonderfully! 🌈\nTake a moment to breathe deeply, appreciate\nthe little things, and keep pushing forward. 💪\nYou've got this! 🌟\nEnjoy the rest of your day! 😃")

# Function to send a good night message
def send_good_night():
    for user_id in user_ids:
        bot.send_photo(user_id, "https://graph.org/file/75bde7e75cf97addc3f1b-1957d73f6aed105c63.jpg", caption="🌙 Good night! 😴\n\nAs the day comes to a close, take a moment\nto reflect on all the wonderful things that happened. 🌟\nMay your dreams be sweet and your rest be peaceful. 💤\nRemember, tomorrow is a new opportunity to shine! 🌅\nSleep well! 💖")

# Function to schedule messages
def schedule_messages():
    schedule.every().day.at("06:00").do(send_good_morning)
    schedule.every().day.at("14:00").do(send_good_afternoon)
    schedule.every().day.at("23:59").do(send_good_night)

    while True:
        schedule.run_pending()
        time.sleep(1)

@bot.message_handler(commands=['set'])
def set_channel_id(message):
    user_id = message.chat.id
    command = message.text.split()

    if len(command) < 2:
        bot.send_message(user_id, "❌ Please provide a channel ID after the /set command, like this:\n/set -1002342033433 or /set 138384742838")
        return

    channel_id = command[1].strip()

    if channel_id not in user_ids:
        user_ids.append(channel_id)
        save_user_ids()
        bot.send_message(user_id, "✅ Channel ID saved successfully!")
    else:
        bot.send_message(user_id, "⚠️ This channel ID already exists.")

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    is_channel = message.chat.type in ['channel', 'supergroup', 'group']

    if is_channel:
        if chat_id not in channel_ids:
            channel_ids.append(chat_id)
            save_channel_ids()
            bot.send_message(chat_id, "✅ Channel ID recorded successfully!")
    else:
        if chat_id not in user_ids:
            user_ids.append(chat_id)
            save_user_ids()

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("➕ Add Me to Your Group", url=f"https://t.me/{bot.get_me().username}?startgroup=true"))
    keyboard.add(types.InlineKeyboardButton("➕ Add Me to Your Channel", url=f"https://t.me/{bot.get_me().username}?startchannel=true"))
    keyboard.add(types.InlineKeyboardButton("📢 Support", url="https://t.me/MR_ARMAN_OWNER"))

    bot.send_message(chat_id, "👋 Welcome to TimeWiseBot! I send daily greetings...\n\nADD ME TO YOUR GROUP ILL DELETE ALL ABUSIVE WORD'S AND MUTES WHO SEND ABUSIVE WORDS\n\n\n/set -1002727727 yo set your channes\n\n",
                     parse_mode="Markdown", reply_markup=keyboard)
                     

def get_user_ids():
    with open("user_ids.txt", "r") as file:
        return file.readlines()

# Command for broadcasting
@bot.message_handler(commands=['broadcast'])
def handle_broadcast(message):
    if str(message.from_user.id) == OWNER_ID:
        bot.send_message(message.chat.id, "Please send the broadcast message or a photo with a caption (if no caption, just send the photo).")
        bot.register_next_step_handler(message, process_broadcast)
    else:
        bot.send_message(message.chat.id, "You are not authorized.")

def process_broadcast(message):
    user_ids = get_user_ids()
    
    if message.content_type == 'text':
        # Send text broadcast
        text = message.text
        for user_id in user_ids:
            try:
                bot.send_message(user_id.strip(), text)
            except Exception as e:
                print(f"Failed to send to {user_id.strip()}: {e}")
    elif message.content_type == 'photo':
        # Send photo broadcast
        caption = message.caption if message.caption else None
        photo = message.photo[-1].file_id  # Get the highest quality photo
        for user_id in user_ids:
            try:
                bot.send_photo(user_id.strip(), photo, caption=caption)
            except Exception as e:
                print(f"Failed to send to {user_id.strip()}: {e}")

#_&_____&_&&______

@bot.message_handler(func=lambda message: any(word in message.text.lower() for word in ABUSIVE_WORDS))
def handle_abusive_message(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Delete the abusive message
    try:
        bot.delete_message(chat_id, message.message_id)
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ Error deleting message: {e}")

    # Issue Warning
    if str(user_id) not in warnings:
        warnings[str(user_id)] = 1
    else:
        warnings[str(user_id)] += 1

    save_warnings()

    # Check Warning Count
    if warnings[str(user_id)] >= 3:
        try:
            bot.restrict_chat_member(chat_id, user_id, can_send_messages=False)
            mute_text = f"🚫 **User Muted!**\n\n⚠️ {message.from_user.first_name} has been muted for using abusive language!"
            keyboard = types.InlineKeyboardMarkup()
            unmute_button = types.InlineKeyboardButton("🔓 Unmute", callback_data=f"unmute_{user_id}")
            keyboard.add(unmute_button)
            bot.send_message(chat_id, mute_text, reply_markup=keyboard)
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ Error muting user: {e}")
    else:
        warn_text = f"⚠️ **Warning {warnings[str(user_id)]}/3**\n\n🚫 {message.from_user.first_name}, stop using abusive words!"
        bot.send_message(chat_id, warn_text)

# Handle Unmute Request (Admins Only)
@bot.callback_query_handler(func=lambda call: call.data.startswith("unmute_"))
def unmute_user(call):
    chat_id = call.message.chat.id
    user_id = int(call.data.split("_")[1])

    if not is_admin(chat_id, call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Only admins can unmute users!")
        return

    try:
        bot.restrict_chat_member(chat_id, user_id, can_send_messages=True)
        bot.send_message(chat_id, f"✅ User <a href='tg://user?id={user_id}'>Unmuted</a>", parse_mode="HTML")
        warnings[str(user_id)] = 0
        save_warnings()
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ Error unmuting user: {e}")

# Error Handler
@bot.message_handler(func=lambda message: True)
def handle_errors(message):
    try:
        # Process other messages normally
        pass
    except telebot.apihelper.ApiException as e:
        if "bot is not an admin" in str(e).lower():
            bot.send_message(message.chat.id, "⚠️ Error: Bot is not an Admin!")
        else:
            bot.send_message(message.chat.id, f"⚠️ Error: {e}")
    except ModuleNotFoundError as e:
        bot.send_message(message.chat.id, f"⚠️ Error module not found: {e}")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Unknown Error: {e}")
        

def main():
    load_user_ids()
    load_channel_ids()
    schedule_messages_thread = threading.Thread(target=schedule_messages)
    schedule_messages_thread.start()
    bot.polling(none_stop=True)


if __name__ == '__main__':
    main()
    