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
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return "!", 200

@app.route("/")
def webhook():
            bot.remove_webhook()
            bot.set_webhook(url=URL + TOKEN)
            return "TikTok Bot is running on Vercel!", 200

@app.route("/set_webhook")
def set_webhook():
            s = bot.set_webhook(url=URL + TOKEN)
            if s: return "Webhook successfully set!", 200
else: return "Webhook setup failed", 200

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
            bot.reply_to(message, "Welcome! Send me a TikTok link.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
            if 'tiktok.com' in message.text:
                            try:
                                                url = message.text
                                                response = requests.get(f"https://www.tikwm.com/api/?url={url}").json()
                                                video_url = response['data']['play']
                                                bot.send_video(message.chat.id, video_url)
except Exception as e:
            bot.reply_to(message, f"Error: {e}")
else:
        bot.reply_to(message, "Please send a valid TikTok link.")

if __name__ == "__main__":
            app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
        
