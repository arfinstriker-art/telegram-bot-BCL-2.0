import os
import logging
from collections import defaultdict
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes
)
from openai import OpenAI
import time

# 🔐 Load ENV
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_ID = 7951276025

CHANNEL = "@BCL_Cyber_Legion"

client = OpenAI(api_key=OPENAI_API_KEY)

# 🧠 Personality
SYSTEM_PROMPT = "You are a funny savage Bangla AI 😎🔥"

# 🚫 Bad words
BAD_WORDS = ["bal", "fuck", "madar", "chod"]

# 🤖 Auto replies
AUTO_REPLY = {
    "hi": "কি খবর 😏",
    "hello": "ওই 😎",
    "kire": "বল ভাই 😏",
    "help": "👉 /contact use কর",
}

# 📊 Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ⏱ Rate limit (anti spam)
user_last_message = defaultdict(float)

# 🧠 Memory (last 5 messages)
user_memory = defaultdict(list)

# ✅ Join check
async def is_joined(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# 🚀 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_joined(context.bot, update.effective_user.id):
        await update.message.reply_text("🔒 আগে join কর 😏\n👉 https://t.me/BCL_Cyber_Legion")
        return

    await update.message.reply_text(
        "😎 BCL AI BOT Ready 🔥\n\n"
        "💬 Smart Chat | 😂 Fun | 🧠 Memory\n"
        "👉 /contact for help"
    )

# 📞 CONTACT
async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📞 Contact 👉 @striker_arfin104 😎")

# 👑 ADMIN ONLY
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    total_users = len(user_memory)
    await update.message.reply_text(f"📊 Total Users: {total_users}")

# 💬 MAIN AI
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    msg = update.message.text.lower()

    # 🔒 Join check
    if not await is_joined(context.bot, user_id):
        await update.message.reply_text("🔒 আগে join কর 😏")
        return

    # ⏱ Rate limit (3 sec)
    if time.time() - user_last_message[user_id] < 3:
        await update.message.reply_text("⏳ ধীরে ভাই 😏")
        return
    user_last_message[user_id] = time.time()

    # 🚫 Bad word
    for word in BAD_WORDS:
        if word in msg:
            await update.message.reply_text("😡 মুখ সামলে কথা বল!")
            return

    # 🤖 Auto reply
    if msg in AUTO_REPLY:
        await update.message.reply_text(AUTO_REPLY[msg])
        return

    # 🧠 Memory add
    user_memory[user_id].append({"role": "user", "content": msg})
    user_memory[user_id] = user_memory[user_id][-5:]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + user_memory[user_id]
        )

        reply_text = response.choices[0].message.content

        # Save bot reply
        user_memory[user_id].append({"role": "assistant", "content": reply_text})

        await update.message.reply_text(reply_text)

    except Exception as e:
        logging.error(e)
        await update.message.reply_text("😏 AI নাই তো কি হইছে, আমি আছি!")

# ▶️ RUN
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("contact", contact))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

print("🔥 Advanced Bot Running 😎")
app.run_polling()
