import os
import telebot
import requests
from flask import Flask, request

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)
URL = "https://tiktok-sigma-sand.vercel.app/"

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
      try:
                json_string = request.get_data().decode('utf-8')
                update = telebot.types.Update.de_json(json_string)
                bot.process_new_updates([update])
                return "!", 200
except Exception as e:
        print(f"Error: {e}")
        return "Error", 500

@app.route("/")
def webhook():
      return "TikTok Bot is running on Vercel!", 200

@app.route("/set_webhook")
def set_webhook():
      s = bot.set_webhook(url=URL + TOKEN)
      if s: return "Webhook successfully set!", 200
else: return "Webhook setup failed", 200

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
      bot.reply_to(message, "Welcome! Send me a TikTok link to download.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
      try:
                url = message.text
                if "tiktok.com" in url:
                              print(f"Processing: {url}")
                              res = requests.get(f"https://www.tikwm.com/api/?url={url}").json()
                              if res.get('data') and res['data'].get('play'):
                                                bot.send_video(message.chat.id, res['data']['play'])
                else:
                                  bot.reply_to(message, "Video not found.")
      else:
                    bot.reply_to(message, "Please send a valid TikTok link.")
except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, f"Error: {e}")
