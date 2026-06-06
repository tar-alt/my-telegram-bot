import os
import telebot
import requests

# Token ကို လုံခြုံအောင် Render ရဲ့ Environment Variable ကနေ ဖတ်ဖို့ ပြင်ထားပါတယ်
API_TOKEN = os.environ.get('BOT_TOKEN')

# ကိုယ်တိုင်ပေးထားသော Channel အချက်အလက်များ
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
        # စစ်ဆေးရာတွင် တစ်ခုခုမှားယွင်းပါက (ဥပမာ- Bot က Channel ထဲမှာ Admin မဖြစ်သေးပါက) ပေးသုံးလိုက်မည်
        print(f"Error checking sub: {e}")
        return True

# /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    if is_subscribed(user_id):
        bot.reply_to(message, "မင်္ဂလာပါဗျာ။ ကျွန်တော့်ဆီကို ဒေါင်းလုဒ်ဆွဲချင်တဲ့ ဗီဒီယို Link ပို့ပေးနိုင်ပါပြီ။")
    else:
        # Force Subscribe ပြုလုပ်ရန် ခလုတ်ပြသခြင်း
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
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="✅ အောင်မြင်ပါသည်။ ဗီဒီယို Link ပို့ပေးနိုင်ပါပြီ။")
    else:
        bot.answer_callback_query(call.id, "❌ Channel မဝင်ရသေးပါဘူးဗျာ။ အရင်ဝင်ပေးပါ။", show_alert=True)

# Link ပို့လာလျှင် လက်ခံမည့်အပိုင်း
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    text = message.text

    if not is_subscribed(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        btn_join = telebot.types.InlineKeyboardButton(text="📢 Channel သို့ဝင်ရန်", url=CHANNEL_LINK)
        markup.add(btn_join)
        bot.reply_to(message, "❌ ဗီဒီယိုဒေါင်းရန် အောက်က Channel ကို အရင် Join ပေးပါ။", reply_markup=markup)
        return

    if "http" in text:
        bot.reply_to(message, "⏳ Link ကို လက်ခံရရှိပါပြီ။ (ဒေါင်းလုဒ် လုပ်ဆောင်ချက်အတွက် API ချိတ်ဆက်ရန် လိုအပ်ပါသည်...)")
    else:
        bot.reply_to(message, "⚠️ ကျေးဇူးပြု၍ မှန်ကန်သော ဗီဒီယို Link ကိုသာ ပို့ပေးပါ။")

print("Bot စတင် အလုပ်လုပ်နေပါပြီ...")
bot.infinity_polling()
