
import os
from telegram.ext import ApplicationBuilder, CommandHandler

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = os.environ.get("ADMIN_ID")

async def start(update, context):
    await update.message.reply_text("ربات شما در Railway فعال است ✅")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.run_polling()
