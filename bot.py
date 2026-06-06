import os
import telebot
import requests

# Render Environment Variable ထဲက Token ကို ဖတ်ခြင်း
API_TOKEN = os.environ.get('BOT_TOKEN')

# Channel အချက်အလက်များ
CHANNEL_ID = '@Learning_DG' 
CHANNEL_LINK = 'https://t.me/Learning_DG' 

bot = telebot.TeleBot(API_TOKEN)

# User က Channel ဝင်ထားသလား စစ်ဆေးပေးမည့် function
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception as e:
        print(f"Error checking sub: {e}")
        return True

# /start command
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

# Check ခလုတ်ကို နှိပ်သည့်အခါ စစ်ဆေးပေးခြင်း
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def callback_check(call):
    user_id = call.from_user.id
    if is_subscribed(user_id):
        bot.answer_callback_query(call.id, "ကျေးဇူးတင်ပါတယ်! ယခု အသုံးပြုနိုင်ပါပြီ။")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="✅ အောင်မြင်ပါသည်။ TikTok Link ပို့ပေးနိုင်ပါပြီ။")
    else:
        bot.answer_callback_query(call.id, "❌ Channel မဝင်ရသေးပါဘူးဗျာ။ အရင်ဝင်ပေးပါ။", show_alert=True)

# TikTok Link ပို့လာလျှင် ဒေါင်းလုဒ်လုပ်ပြီး ဗီဒီယို ပြန်ပို့ပေးမည့်အပိုင်း
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    url = message.text

    # Channel ဝင်မဝင် အရင်စစ်ဆေးခြင်း
    if not is_subscribed(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        btn_join = telebot.types.InlineKeyboardButton(text="📢 Channel သို့ဝင်ရန်", url=CHANNEL_LINK)
        markup.add(btn_join)
        bot.reply_to(message, "❌ ဗီဒီယိုဒေါင်းရန် အောက်က Channel ကို အရင် Join ပေးပါ။", reply_markup=markup)
        return

    # TikTok URL ဟုတ်မဟုတ် စစ်ဆေးခြင်း
    if "tiktok.com" in url:
        status_msg = bot.reply_to(message, "⏳ TikTok ဗီဒီယိုကို HD Quality ဖြင့် ရှာဖွေနေပါသည်၊ ခေတ္တစောင့်ဆိုင်းပေးပါ...")
        
        try:
            # တိုက်ရိုက် HD လင့်ခ်ထုတ်ပေးနိုင်သော အခမဲ့ API ကို အသုံးပြုခြင်း
            api_url = f"https://tikwm.com/api/?url={url}"
            response = requests.get(api_url).json()
            
            if response.get('code') == 0:
                data = response['data']
                
                # HD အရည်အသွေး (Watermark မပါသော တိုက်ရိုက်ဗီဒီယို လင့်ခ်) ကို ယူခြင်း
                # အကယ်၍ hd လင့်ခ်မရှိပါက ရိုးရိုးလင့်ခ်ကို ယူမည် (Black screen မဖြစ်စေရန် စစ်ထုတ်ထားသည်)
                video_url = data.get('hdplay') if data.get('hdplay') else data.get('play')
                video_title = data.get('title', 'TikTok Video')
                
                # Telegram ဆီသို့ ဗီဒီယိုကို လင့်ခ်မှတစ်ဆင့် တိုက်ရိုက် ပို့ခိုင်းခြင်း (အသံနှင့် ရုပ်ထွက် အကောင်းဆုံးဖြစ်စေသည်)
                bot.send_video(
                    chat_id=message.chat.id, 
                    video=video_url, 
                    caption=f"🎬 {video_title}\n\n✨ Created by: Taro",
                    reply_to_message_id=message.message_id
                )
                
                # စောင့်ခိုင်းထားသော စာသားကို ဖျက်ပစ်ခြင်း
                bot.delete_message(chat_id=message.chat.id, message_id=status_msg.message_id)
                
            else:
                bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id, text="❌ ဗီဒီယိုကို ရှာမတွေ့ပါ။ လင့်ခ် မှန်ကန်မှု ရှိမရှိ ပြန်စစ်ပေးပါ။")
                
        except Exception as e:
            print(f"Error downloading: {e}")
            bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id, text="⚠️ ဆာဗာပိုင်း အနည်းငယ် အလုပ်များနေသဖြင့် နောက်တစ်ကြိမ် ပြန်လည် စမ်းသပ်ပေးပါရန်။")
    else:
        bot.reply_to(message, "⚠️ ကျေးဇူးပြု၍ မှန်ကန်သော TikTok ဗီဒီယို Link ကိုသာ ပို့ပေးပါ။")

print("Bot စတင် အလုပ်လုပ်နေပါပြီ...")
bot.infinity_polling()

