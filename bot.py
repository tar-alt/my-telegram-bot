import os
import telebot
import requests
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is Running Perfectly!"

def run_server():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# ✅ Taro ရဲ့ Bot Token အသစ်စက်စက်
API_TOKEN = '8764251572:AAE18imddZBhpwzJ7zoDKX4ol9uB91eTubQ'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 မင်္ဂလာပါဗျာ။ ကျွန်တော်က All-in-One Downloader Bot ပါ။\n\n"
        "📥 အောက်ပါလင့်ခ်များကို ပို့ရုံဖြင့် တိုက်ရိုက်ဒေါင်းလုဒ်ဆွဲပေးနိုင်ပါသည် -\n"
        "• **TikTok** (Videos & Photo Slides)\n"
        "• **YouTube** (Shorts & Videos)\n"
        "• **Facebook** (Videos & Reels)\n"
        "• **Pinterest** (Videos)\n\n"
        "⚡ ကြော်ငြာမပါ၊ လူတိုင်းလွတ်လပ်စွာ အသုံးပြုနိုင်ပါသည်ဗျာ။"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    chat_id = message.chat.id
    msg_id = message.message_id

    is_tiktok = "tiktok.com" in url
    is_youtube = "youtube.com" in url or "youtu.be" in url
    is_facebook = "facebook.com" in url or "fb.watch" in url or "fb.gg" in url
    is_pinterest = "pinterest.com" in url or "pin.it" in url

    if not (is_tiktok or is_youtube or is_facebook or is_pinterest):
        bot.reply_to(message, "⚠️ ကျေးဇူးပြု၍ မှန်ကန်သော TikTok, YouTube, Facebook သို့မဟုတ် Pinterest လင့်ခ်ကို ပို့ပေးပါ။")
        return

    status_msg = bot.reply_to(message, "⏳ မီဒီယာဖိုင်ကို ရှာဖွေပြီး Quality အမြင့်ဆုံး ဆွဲထုတ်နေပါသည်...")

    try:
        # 🚀 Render ပေါ်တွင် ပိတ်ဆို့မှုမရှိစေရန် User-Agent Header ထည့်သွင်းထားသော High-Speed API Pipeline
        api_url = f"https://www.donguri.desktop.is-a.dev/api/universal?url={url}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(api_url, headers=headers, timeout=20)
        res = response.json()

        if res.get('status') == 'success' and res.get('data'):
            data = res['data']
            media_type = data.get('type')
            title = data.get('title', 'Downloaded Media')

            # ၁။ TikTok Photo Slide ဖြစ်ခဲ့လျှင် Album ပုံစံ ပို့မည်
            if media_type == 'images' and data.get('images'):
                images_list = data['images']
                media_group = []
                for i, img_url in enumerate(images_list):
                    if i == 0:
                        media_group.append(telebot.types.InputMediaPhoto(img_url, caption=f"📸 **{title}**\n\n👤 Created by: Taro", parse_mode="Markdown"))
                    else:
                        media_group.append(telebot.types.InputMediaPhoto(img_url))
                bot.send_media_group(chat_id=chat_id, media=media_group, reply_to_message_id=msg_id)
                bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)

            # ၂။ ဗီဒီယိုဖိုင် ဖြစ်ခဲ့လျှင် (TT, YT, FB, Pinterest)
            elif data.get('video_url'):
                video_url = data.get('video_url')
                bot.send_video(
                    chat_id=chat_id,
                    video=video_url,
                    caption=f"🎬 **{title}**\n\n✨ **Quality:** Ultra HD Optimized\n\n👤 Created by: Taro",
                    reply_to_message_id=msg_id,
                    parse_mode="Markdown"
                )
                bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)
            else:
                bot.edit_message_text("❌ မီဒီယာဖိုင် ဆွဲထုတ်၍မရပါ။ လင့်ခ်မှန်ကန်ကြောင်း ပြန်စစ်ပေးပါ။", chat_id=chat_id, message_id=status_msg.message_id)
        else:
            bot.edit_message_text("❌ မီဒီယာဖိုင် ရှာမတွေ့ပါ။ လင့်ခ် သက်တမ်းကုန်သွားခြင်း သို့မဟုတ် Private ဖြစ်နေနိုင်ပါသည်။", chat_id=chat_id, message_id=status_msg.message_id)

    except Exception as e:
        # Error အစစ်အမှန်ကို Render Log တွင် မြင်နိုင်ရန် print ထုတ်ထားခြင်း
        print(f"Error occurred: {str(e)}")
        bot.edit_message_text("⚠️ API ဆာဗာ ချိတ်ဆက်မှု ကြန့်ကြာနေပါသည်။ ခဏစောင့်ပြီး ပြန်ပို့ကြည့်ပေးပါဗျာ။", chat_id=chat_id, message_id=status_msg.message_id)

if __name__ == "__main__":
    t = Thread(target=run_server)
    t.start()
    
    try:
        bot.remove_webhook()
    except Exception:
        pass
        
    bot.infinity_polling(timeout=60, long_polling_timeout=60)

