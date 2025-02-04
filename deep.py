import telebot
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import logging

# Set up logging to see errors in the console
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace this with your actual bot token
API_TOKEN = '7685491877:AAGCya_bYave_CQm0cyEUNG0hnhRYt1oCsA'  # Add your bot token here

# Initialize the bot
bot = telebot.TeleBot(API_TOKEN)

# Load pre-trained GPT-2 model and tokenizer
model = GPT2LMHeadModel.from_pretrained("gpt2")
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

# Function to generate GPT-2 response
def generate_response(prompt: str) -> str:
    # Encode input prompt to token IDs
    inputs = tokenizer.encode(prompt + tokenizer.eos_token, return_tensors="pt")
    
    # Generate response using GPT-2 model
    outputs = model.generate(
        inputs,
        max_length=100,  # Limit the response length
        num_return_sequences=1,  # Generate one response
        no_repeat_ngram_size=2,  # Avoid repeating the same phrases
        top_p=0.95,  # Top-p sampling for better diversity
        temperature=0.7,  # Control randomness
    )
    
    # Decode the output token IDs to a string
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

# Handler for "/start" command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello! I am your GPT-2 powered chatbot. Ask me anything!")

# Handler for any other message
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_message = message.text  # Get the user's message
    
    # Generate a response using GPT-2 model
    response_message = generate_response(user_message)
    
    # Send the generated response back to the user
    bot.reply_to(message, response_message)

# Start the bot
bot.polling()

