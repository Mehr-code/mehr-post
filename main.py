import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from dotenv import load_dotenv
import os

# بارگذاری env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

print("DEBUG: BOT_TOKEN =", BOT_TOKEN)  # بررسی توکن


async def start(update, context):
    print("DEBUG: /start received from", update.effective_user.id)
    try:
        await update.message.reply_text("سلام 👋 ربات زنده است!")
        print("DEBUG: reply sent successfully")
    except Exception as e:
        print("DEBUG: error sending reply:", e)


def main():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN is missing!")
        return

    try:
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        print("Bot is running...")
        asyncio.run(app.run_polling())
    except Exception as e:
        print("ERROR: exception during run_polling:", e)


if __name__ == "__main__":
    main()
