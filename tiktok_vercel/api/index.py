import os
import telebot
import re
import requests
from flask import Flask, request

# في Vercel، نقوم بإضافة التوكن كـ Environment Variable من إعدادات الموقع نفسه
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# إذا لم يكن التوكن موجوداً، قد يؤدي لخطأ. سنضع رسالة لتنبيهنا.
if not TOKEN:
    print("الرجاء إضافة TELEGRAM_BOT_TOKEN في إعدادات Vercel Environment Variables")

bot = telebot.TeleBot(TOKEN) if TOKEN else None
app = Flask(__name__)

def extract_url(text):
    url_pattern = re.compile(r'(https?://[^\s]+)')
    match = url_pattern.search(text)
    return match.group(1) if match else None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً بك! 🤖\n\nأرسل لي أي رابط لفيديو أو بوست من تيك توك، وسأقوم بتحميله وإرساله لك مباشرة هنا.\n\n(هذا البوت يعمل الآن على خوادم Vercel 🚀)")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text
    if 'tiktok.com' in text:
        url = extract_url(text)
        if not url:
            bot.reply_to(message, "⚠️ لم أتمكن من العثور على رابط صحيح في رسالتك.")
            return

        msg = bot.reply_to(message, "⏳ جاري جلب الفيديو عبر Vercel، يرجى الانتظار...")
        
        try:
            api_url = "https://www.tikwm.com/api/"
            params = {"url": url, "hd": 1}
            response = requests.get(api_url, params=params, timeout=20)
            data = response.json()
            
            if data.get("code") == 0:
                video_data = data.get("data", {})
                
                # التحقق إذا كان بوست صور
                if "images" in video_data and isinstance(video_data["images"], list):
                    images = video_data["images"]
                    media_group = []
                    for idx, img_url in enumerate(images):
                        if idx == 0:
                            media_group.append(telebot.types.InputMediaPhoto(img_url, caption="إليك الصور!"))
                        else:
                            media_group.append(telebot.types.InputMediaPhoto(img_url))
                        
                        if len(media_group) == 10:
                            bot.send_media_group(message.chat.id, media_group, reply_to_message_id=message.message_id)
                            media_group = []
                    
                    if media_group:
                        bot.send_media_group(message.chat.id, media_group, reply_to_message_id=message.message_id)
                        
                    bot.delete_message(message.chat.id, msg.message_id)
                    
                # إذا كان فيديو
                elif "play" in video_data:
                    video_url = video_data.get("hdplay") or video_data.get("play")
                    # استخدام الرابط المباشر ليقوم تيليجرام بتحميله تلقائياً لتقليل الوقت
                    bot.send_video(message.chat.id, video_url, reply_to_message_id=message.message_id)
                    bot.delete_message(message.chat.id, msg.message_id)
                else:
                    bot.edit_message_text("❌ لم أتمكن من استخراج رابط الفيديو من البوست.", message.chat.id, msg.message_id)
            else:
                bot.edit_message_text("❌ لم أتمكن من جلب الفيديو، تأكد أن الحساب ليس خاصاً (Private).", message.chat.id, msg.message_id)
                
        except Exception as e:
            error_msg = str(e)
            bot.edit_message_text(f"❌ عذراً، حدث خطأ أثناء التحميل.\n\nتأكد من أن الرابط صحيح وأن الحساب ليس خاصاً.\nالسبب: {error_msg}", message.chat.id, msg.message_id)
    else:
        bot.reply_to(message, "⚠️ الرجاء إرسال رابط تيك توك صحيح.")


# -------------------------------------------------------------------
# Vercel Webhook Routes
# -------------------------------------------------------------------

@app.route('/', methods=['GET'])
def index():
    return 'TikTok Bot is running on Vercel!'

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if bot:
        if request.headers.get('content-type') == 'application/json':
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return '', 200
    return 'Forbidden', 403

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    if not bot:
        return "No TOKEN configured.", 500
        
    bot.remove_webhook()
    webhook_url = request.host_url.rstrip('/') + '/' + TOKEN
    bot.set_webhook(url=webhook_url)
    return f"Webhook successfully set to: {webhook_url}"
