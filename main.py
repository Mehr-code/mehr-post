import asyncio
import sqlite3
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

# ساخت دیتابیس SQLite برای نگهداری تاریخچه پیام‌ها
conn = sqlite3.connect("messages.db")
c = conn.cursor()
c.execute(
    """
CREATE TABLE IF NOT EXISTS history (
    user_id INTEGER,
    message TEXT
)
"""
)
conn.commit()

# دیکشنری نگهداری پیام‌های فعلی کاربران
anonymous_map = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام 👋\nپیام ناشناس برای من بفرست!")


async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # ذخیره پیام داخل دیکشنری
    if user_id not in anonymous_map:
        anonymous_map[user_id] = []
    anonymous_map[user_id].append(text)

    # ذخیره در تاریخچه امن
    c.execute("INSERT INTO history (user_id, message) VALUES (?, ?)", (user_id, text))
    conn.commit()

    # ارسال پیام به OWNER بدون لو دادن فرستنده
    await context.bot.send_message(
        chat_id=OWNER_ID,
        text=f"پیام ناشناس دریافت شد:\n{text}\n\nبرای جواب دادن، reply کن.",
    )


async def handle_owner_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message is None:
        return

    replied_text = update.message.reply_to_message.text
    target_user_id = None
    target_msg = None

    # پیدا کردن پیام و user_id مربوطه
    for uid, msgs in anonymous_map.items():
        for msg in msgs[::-1]:
            if f"پیام ناشناس دریافت شد:\n{msg}" in replied_text:
                target_user_id = uid
                target_msg = msg
                break
        if target_user_id:
            break

    if target_user_id and target_msg:
        # ارسال reply به کاربر
        await context.bot.send_message(chat_id=target_user_id, text=update.message.text)

        # حذف پیام از دیکشنری بعد از reply
        anonymous_map[target_user_id].remove(target_msg)
        if not anonymous_map[target_user_id]:
            del anonymous_map[target_user_id]


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & (~filters.User(OWNER_ID)), handle_user_message)
    )
    app.add_handler(
        MessageHandler(filters.TEXT & filters.User(OWNER_ID), handle_owner_reply)
    )

    print("Bot is running...")
    asyncio.run(app.run_polling())


if __name__ == "__main__":
    main()
