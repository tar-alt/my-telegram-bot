import os
import telebot
from flask import Flask
from threading import Thread
import subprocess
import json

app = Flask('')

@app.route('/')
def home():
    return "Bot is Running Independently!"

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
        "⚡ ကြော်ငြာမပါ၊ ကိုယ်ပိုင် Engine ဖြင့် တိုက်ရိုက်ဒေါင်းပေးပါသည်ဗျာ။"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    chat_id = message.chat.id
    msg_id = message.message_id

    # လင့်ခ် စစ်ဆေးခြင်း
    if not any(domain in url for domain in ["tiktok.com", "youtube.com", "youtu.be", "facebook.com", "fb.watch", "fb.gg", "pinterest.com", "pin.it"]):
        bot.reply_to(message, "⚠️ ကျေးဇူးပြု၍ မှန်ကန်သော TikTok, YouTube, Facebook သို့မဟုတ် Pinterest လင့်ခ်ကို ပို့ပေးပါ။")
        return

    status_msg = bot.reply_to(message, "⏳ မီဒီယာဖိုင်ကို ကိုယ်ပိုင် Engine ဖြင့် စစ်ဆေးပြီး အမြင့်ဆုံး Quality ဆွဲထုတ်နေပါသည်...")

    try:
        # yt-dlp သုံးပြီး မီဒီယာအချက်အလက်များကို ဆွဲထုတ်ခြင်း
        cmd = ["yt-dlp", "-j", url]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        meta = json.loads(result.stdout)
        
        title = meta.get("title", "Multi-Media Downloader")
        
        # ၁။ TikTok Photo Slide ဖြစ်နေလျှင် (Entries သို့မဟုတ် Images ပါဝင်မှုကို စစ်ဆေးခြင်း)
        if "entries" in meta or (meta.get("extractor") == "TikTok" and not meta.get("video_url") and meta.get("formats") == None):
            bot.edit_message_text("📸 ဓာတ်ပုံ Slide များအား ဖတ်ရှုနေပါသည်...", chat_id=chat_id, message_id=status_msg.message_id)
            # ဓာတ်ပုံများအတွက် သီးသန့်ပြန်ထုတ်ယူခြင်း
            cmd_img = ["yt-dlp", "--flat-playlist", "--dump-json", url]
            img_res = subprocess.run(cmd_img, capture_output=True, text=True).stdout
            
            media_group = []
            for line in img_res.splitlines():
                if line.strip():
                    img_meta = json.loads(line)
                    if img_meta.get("url"):
                        if len(media_group) == 0:
                            media_group.append(telebot.types.InputMediaPhoto(img_meta["url"], caption=f"📸 **{title}**\n\n👤 Created by: Taro", parse_mode="Markdown"))
                        else:
                            media_group.append(telebot.types.InputMediaPhoto(img_meta["url"]))
            
            if media_group:
                bot.send_media_group(chat_id=chat_id, media=media_group, reply_to_message_id=msg_id)
                bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)
                return

        # ၂။ ဗီဒီယိုဖိုင်ဖြစ်လျှင် (တိုက်ရိုက် ဗီဒီယိုလင့်ခ်ကို ရယူခြင်း)
        video_url = meta.get("url")
        if not video_url and meta.get("formats"):
            # အကောင်းဆုံး Quality ဗီဒီယိုလင့်ခ်ကို ရွေးထုတ်ခြင်း
            video_url = meta["formats"][-1].get("url")

        if video_url:
            bot.send_video(
                chat_id=chat_id,
                video=video_url,
                caption=f"🎬 **{title}**\n\n✨ **Quality:** High Definition\n\n👤 Created by: Taro",
                reply_to_message_id=msg_id,
                parse_mode="Markdown"
            )
            bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)
        else:
            bot.edit_message_text("❌ ဗီဒီယိုလင့်ခ်ကို ဆွဲထုတ်၍မရပါ။ လင့်ခ်မှန်ကန်ကြောင်း ပြန်စစ်ပေးပါ။", chat_id=chat_id, message_id=status_msg.message_id)

    except Exception as e:
        print(f"Error: {str(e)}")
        bot.edit_message_text("❌ ဒီလင့်ခ်မှ ဗီဒီယိုကို ဆွဲထုတ်ရန် ဆာဗာတွင် ကန့်သတ်ချက်ရှိနေပါသည်။ တခြားလင့်ခ်ဖြင့် ပြန်စမ်းကြည့်ပေးပါဗျာ။", chat_id=chat_id, message_id=status_msg.message_id)

if __name__ == "__main__":
    t = Thread(target=run_server)
    t.start()
    
    try:
        bot.remove_webhook()
    except Exception:
        pass
        
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
    
