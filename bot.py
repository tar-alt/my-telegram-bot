import os
import telebot
import requests
from threading import Thread
from flask import Flask

# Render အတွက် Web Server တည်ဆောက်ခြင်း (Port Timeout ကျော်ရန်)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run_web_server():
    # Render က ပေးမည့် Port သို့မဟုတ် 8080 ကို သုံးမည်
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Token နှင့် Channel သတ်မှတ်ချက်များ
API_TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = '@Learning_DG' 
CHANNEL_LINK = 'https://t.me/Learning_DG' 

bot = telebot.TeleBot(API_TOKEN)

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception as e:
        print(f"Error checking sub: {e}")
        return True

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if is_subscribed(user_id):
        bot.reply_to(message, "👋 မင်္ဂလာပါဗျာ။ ကျွန်တော့်ဆီကို ဒေါင်းလုဒ်ဆွဲချင်တဲ့ TikTok Link ပို့ပေးနိုင်ပါပြီ။ HD Quality အပြည့်ဖြင့် ဒေါင်းလုပ်ဆွဲပေးပါမည်။")
    else:
        markup = telebot.types.InlineKeyboardMarkup()
        btn_join = telebot.types.InlineKeyboardButton(text="📢 Channel သို့ဝင်ရန်", url=CHANNEL_LINK)
        btn_check = telebot.types.InlineKeyboardButton(text="🔄 ဝင်ပြီးပါပြီ (Check)", callback_data="check_sub")
        markup.add(btn_join)
        markup.add(btn_check)
        bot.send_message(message.chat.id, "❌ အောက်က Channel ကို အရင် Join ပေးမှ Bot ကို သုံးလို့ရပါမယ်ဗျာ။", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def callback_check(call):
    user_id = call.from_user.id
    if is_subscribed(user_id):
        bot.answer_callback_query(call.id, "ကျေးဇူးတင်ပါတယ်! ယခု အသုံးပြုနိုင်ပါပြီ။")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="✅ အောင်မြင်ပါသည်။ TikTok Link ပို့ပေးနိုင်ပါပြီ။")
    else:
        bot.answer_callback_query(call.id, "❌ Channel မဝင်ရသေးပါဘူးဗျာ။ အရင်ဝင်ပေးပါ။", show_alert=True)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    url = message.text

    if not is_subscribed(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        btn_join = telebot.types.InlineKeyboardButton(text="📢 Channel သို့ဝင်ရန်", url=CHANNEL_LINK)
        markup.add(btn_join)
        bot.reply_to(message, "❌ ဗီဒီယိုဒေါင်းရန် အောက်က Channel ကို အရင် Join ပေးပါ။", reply_markup=markup)
        return

    if "tiktok.com" in url:
        status_msg = bot.reply_to(message, "⏳ TikTok ဗီဒီယိုကို HD Quality ဖြင့် ရှာဖွေနေပါသည်၊ ခေတ္တစောင့်ဆိုင်းပေးပါ...")
        try:
            api_url = f"https://tikwm.com/api/?url={url}"
            response = requests.get(api_url).json()
            if response.get('code') == 0:
                data = response['data']
                video_url = data.get('hdplay') if data.get('hdplay') else data.get('play')
                video_title = data.get('title', 'TikTok Video')
                
                bot.send_video(
                    chat_id=message.chat.id, 
                    video=video_url, 
                    caption=f"🎬 {video_title}\n\n✨ Created by: Taro",
                    reply_to_message_id=message.message_id
                )
                bot.delete_message(chat_id=message.chat.id, message_id=status_msg.message_id)
            else:
                bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id, text="❌ ဗီဒီယိုကို ရှာမတွေ့ပါ။ လင့်ခ် မှန်ကန်မှု ရှိမရှိ ပြန်စစ်ပေးပါ။")
        except Exception as e:
            print(f"Error downloading: {e}")
            bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id, text="⚠️ ဆာဗာပိုင်း အနည်းငယ် အလုပ်များနေသဖြင့် နောက်တစ်ကြိမ် ပြန်လည် စမ်းသပ်ပေးပါရန်။")
    else:
        bot.reply_to(message, "⚠️ ကျေးဇူးပြု၍ မှန်ကန်သော TikTok ဗီဒီယို Link ကိုသာ ပို့ပေးပါ။")

# Web Server နှင့် Bot ကို Background တွင် တစ်ပြိုင်နက် Run ခြင်း
if __name__ == "__main__":
    t = Thread(target=run_web_server)
    t.start()
    
    print("Bot စတင် အလုပ်လုပ်နေပါပြီ...")
    bot.infinity_polling()

