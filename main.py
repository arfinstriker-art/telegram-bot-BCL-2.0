import telebot
from openai import OpenAI

# ================= কনফিগারেশন =================
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
HF_TOKEN = "YOUR_HF_TOKEN" # এখানে তোমার Hugging Face Token বসাও
CHANNEL_USERNAME = "@BCL_Cyber_Legion"
CEO_CONTACT = "@striker_arfin104"

# বট ইনিশিয়ালাইজেশন
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Hugging Face Router দিয়ে OpenAI ক্লায়েন্ট সেটআপ 🚀
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN
)

# খারাপ শব্দের তালিকা
BAD_WORDS =['bal', 'fuck', 'madar', 'chod']

# AI System Prompt
SYSTEM_PROMPT = """You are BCL AI Bot 😎🔥, a smart, funny, and slightly savage Bangla-speaking assistant.
- Speak in Bangla (casual, text style like: ki obostha, kemon aso or direct bangla font).
- You are funny, witty, and have a slightly savage attitude 😏
- Be friendly but highly confident.
- Keep replies short, punchy, and use emojis like 😎, 🔥, 😏.
- মাঝে মাঝে roasting allowed but not harmful."""

# ================= হেল্পার ফাংশন =================

def is_user_subscribed(user_id):
    """চেক করবে ইউজার চ্যানেলে জয়েন করেছে কি না"""
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        if status in['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        print(f"Channel Check Error: {e}")
        return False

def contains_bad_words(text):
    """চেক করবে টেক্সটে কোনো খারাপ শব্দ আছে কি না"""
    text_lower = text.lower()
    for word in BAD_WORDS:
        if word in text_lower:
            return True
    return False

# ================= কমান্ড হ্যান্ডলার =================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    if not is_user_subscribed(user_id):
        bot.reply_to(message, f"আগে আমাদের চ্যানেলে জয়েন কর, তারপর কথা হবে! 😏\nলিংক: https://t.me/BCL_Cyber_Legion")
        return

    welcome_msg = (
        "স্বাগতম! আমি **BCL AI Bot** 😎🔥\n\n"
        "আমার ফিচারসমূহ:\n"
        "💬 **Smart Chat:** আমার সাথে যেকোনো বিষয় নিয়ে আড্ডা দিতে পারো।\n"
        "🤣 **Fun & Roast:** একটু ফান আর স্যাভেজ রিপ্লাইয়ের জন্য রেডি থেকো।\n"
        "📞 **Help:** কোনো দরকার হলে /contact ইউজ কর।\n\n"
        "বলো, কী জানতে চাও? 😏"
    )
    bot.reply_to(message, welcome_msg, parse_mode="Markdown")

@bot.message_handler(commands=['contact'])
def send_contact(message):
    user_id = message.from_user.id
    
    if not is_user_subscribed(user_id):
        bot.reply_to(message, f"আগে আমাদের চ্যানেলে জয়েন কর, তারপর কথা হবে! 😏\nলিংক: https://t.me/BCL_Cyber_Legion")
        return

    bot.reply_to(message, f"👉 আমাদের Admin/CEO এর সাথে যোগাযোগ করতে পারো: {ADMIN_CONTACT} 😎")

# ================= টেক্সট মেসেজ হ্যান্ডলার =================

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text.strip().lower()

    # ১. সাবস্ক্রিপশন চেক
    if not is_user_subscribed(user_id):
        bot.reply_to(message, f"আগে আমাদের চ্যানেলে জয়েন কর, তারপর কথা হবে! 😏\nলিংক: https://t.me/BCL_Cyber_Legion")
        return

    # ২. ব্যাড ওয়ার্ড ফিল্টার 🚫
    if contains_bad_words(text):
        bot.reply_to(message, "😡 মুখ সামলে কথা বল!")
        return

    # ৩. অটো রিপ্লাই সিস্টেম
    if text == "hi":
        bot.reply_to(message, "কি খবর 😏")
        return
    elif text == "hello":
        bot.reply_to(message, "ওই 😎")
        return
    elif text in ["kire", "ki re"]:
        bot.reply_to(message, "বল ভাই 😏")
        return
    elif text == "help":
        bot.reply_to(message, "👉 /contact use কর")
        return

    # ৪. AI Chat System 🧠 (DeepSeek Model Via Hugging Face)
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V4-Pro:novita", # তোমার দেওয়া মডেল
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ],
            max_tokens=250, # DeepSeek এর জন্য রেসপন্স সাইজ একটু বাড়িয়ে দিলাম
            temperature=0.8
        )
        ai_reply = response.choices[0].message.content
        bot.reply_to(message, ai_reply)
        
    except Exception as e:
        # ৫. Fallback System 🔥
        print(f"AI Error: {e}")
        bot.reply_to(message, "😏 AI নাই তো কি হইছে, আমি আছি!")

# ================= বট চালু করা =================
if __name__ == "__main__":
    print("BCL AI Bot (DeepSeek Powered) is running... 😎🔥")
    bot.infinity_polling()
