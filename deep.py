from telebot import types
import telebot
import schedule
import time
import threading
import os
import json

# Replace with your actual bot token
TOKEN = '7056119124:AAFXyI0gFTehd_wC-Hj2bqbJoAcze_ekENk'
bot = telebot.TeleBot(TOKEN)

# Admin Owner ID
OWNER_ID = '7858368373'

# Store user and channel IDs
user_ids = []
channel_ids = []

# File paths
WARNINGS_FILE = "warnings.json"
USER_IDS_FILE = "user_ids.txt"
CHANNEL_IDS_FILE = "channel_ids.txt"

# Load user IDs
def load_ids(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return [int(line.strip()) for line in f.readlines()]
    return []

# Save user IDs
def save_ids(file_path, ids):
    with open(file_path, "w") as f:
        for _id in ids:
            f.write(f"{_id}\n")

# Load Data
user_ids = load_ids(USER_IDS_FILE)
channel_ids = load_ids(CHANNEL_IDS_FILE)

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
    except:
        return False

# Function to send scheduled messages
def send_scheduled_message(photo_url, caption):
    for chat_id in user_ids + channel_ids:
        try:
            bot.send_photo(chat_id, photo_url, caption=caption)
        except:
            pass

# Scheduled Message Functions
def send_good_morning():
    send_scheduled_message("https://graph.org/file/bf067788a313dde08c58f-48a5aff2c2ed5a785a.jpg",
                           "🌞 Good morning! 🌼✨\n\nWishing you a day filled with positivity and joy. 🌈\nMay every moment bring you a reason to smile 😊\nand each challenge be an opportunity to grow. 🌟\n\nRemember, today is a blank canvas—paint it beautifully! 🎨\nHave an amazing day ahead! 💖")

def send_good_afternoon():
    send_scheduled_message("https://graph.org/file/767bfc3f0cb2d61ab2882-c01696337a5e17b55b.jpg",
                           "☀️ Good afternoon! 🌻\n\nI hope your day is going wonderfully! 🌈\nTake a moment to breathe deeply, appreciate\nthe little things, and keep pushing forward. 💪\nYou've got this! 🌟\nEnjoy the rest of your day! 😃")

def send_good_night():
    send_scheduled_message("https://graph.org/file/75bde7e75cf97addc3f1b-1957d73f6aed105c63.jpg",
                           "🌙 Good night! 😴\n\nAs the day comes to a close, take a moment\nto reflect on all the wonderful things that happened. 🌟\nMay your dreams be sweet and your rest be peaceful. 💤\nRemember, tomorrow is a new opportunity to shine! 🌅\nSleep well! 💖")

# Schedule Messages
def schedule_messages():
    schedule.every().day.at("06:00").do(send_good_morning)
    schedule.every().day.at("14:00").do(send_good_afternoon)
    schedule.every().day.at("23:59").do(send_good_night)

    while True:
        schedule.run_pending()
        time.sleep(1)

# Start schedule in a separate thread
threading.Thread(target=schedule_messages, daemon=True).start()

# Start Command
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    chat_type = message.chat.type

    if chat_type in ['supergroup', 'group', 'channel']:
        if chat_id not in channel_ids:
            channel_ids.append(chat_id)
            save_ids(CHANNEL_IDS_FILE, channel_ids)
            bot.send_message(chat_id, "✅ This channel/group has been added for scheduled messages.")
    else:
        if chat_id not in user_ids:
            user_ids.append(chat_id)
            save_ids(USER_IDS_FILE, user_ids)

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("➕ Add Me to Your Group", url=f"https://t.me/{bot.get_me().username}?startgroup=true"))
    keyboard.add(types.InlineKeyboardButton("📢 Support", url="https://t.me/MR_ARMAN_OWNER"))

    bot.send_message(chat_id, "👋 Welcome to **TimeWiseBot**!\n\n"
                              "I send **daily greetings** and can **moderate abusive words** in groups.\n"
                              "To register a channel for greetings, use:\n\n"
                              "`/set -100xxxxxxxxx`\n\n"
                              "Admins can use moderation commands like `/mute`, `/unmute`, and `/warn`.",
                     parse_mode="Markdown", reply_markup=keyboard)

# Add Channel ID
@bot.message_handler(commands=['set'])
def set_channel_id(message):
    chat_id = message.chat.id
    command = message.text.split()

    if len(command) < 2:
        bot.send_message(chat_id, "❌ Please provide a valid channel ID.\nExample: `/set -1002342033433`", parse_mode="Markdown")
        return

    channel_id = int(command[1].strip())

    if channel_id not in channel_ids:
        channel_ids.append(channel_id)
        save_ids(CHANNEL_IDS_FILE, channel_ids)
        bot.send_message(chat_id, "✅ Channel ID saved successfully!")
    else:
        bot.send_message(chat_id, "⚠️ This channel is already registered.")

def get_user_ids():
    with open("user_ids.txt", "r") as file:
        return file.readlines()
        
# Broadcast Messages (Admin Only)
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

#_&₹_____

# List Users (Admin Only)
@bot.message_handler(commands=['users'])
def show_users(message):
    if str(message.from_user.id) == OWNER_ID:
        user_list = "\n".join([f"ID: {uid}" for uid in user_ids])
        bot.send_message(message.chat.id, f"**Registered Users:**\n{user_list}", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ You are not authorized.")

# Abusive Words Protection
ABUSIVE_WORDS = ["mc", "bc", "bhosdike", "madarchod", "chutiya", "gandu"]

@bot.message_handler(func=lambda message: any(word in message.text.lower() for word in ABUSIVE_WORDS))
def handle_abusive_message(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    bot.delete_message(chat_id, message.message_id)

    warnings[str(user_id)] = warnings.get(str(user_id), 0) + 1
    save_warnings()

    if warnings[str(user_id)] >= 3:
        bot.restrict_chat_member(chat_id, user_id, can_send_messages=False)
        bot.send_message(chat_id, f"🚫 **User Muted!**\n\n{message.from_user.first_name} has been muted for abusive language!")
    else:
        bot.send_message(chat_id, f"⚠️ **Warning {warnings[str(user_id)]}/3** - Stop using abusive words!")

# Admin Commands
@bot.message_handler(commands=['mute'])
def mute_user(message):
    if is_admin(message.chat.id, message.from_user.id):
        user_id = message.reply_to_message.from_user.id
        bot.restrict_chat_member(message.chat.id, user_id, can_send_messages=False)
        bot.send_message(message.chat.id, "✅ User has been muted.")

@bot.message_handler(commands=['unmute'])
def unmute_user(message):
    if is_admin(message.chat.id, message.from_user.id):
        user_id = message.reply_to_message.from_user.id
        bot.restrict_chat_member(message.chat.id, user_id, can_send_messages=True)
        bot.send_message(message.chat.id, "✅ User has been unmuted.")

# Start Bot
bot.polling()
        
