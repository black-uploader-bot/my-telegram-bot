
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters
)

from handlers.start import start
from handlers.file_handler import handle_document
from handlers.admin import admin_panel, admin_panel_handler
from handlers.start import check_membership
from utils import get_connection

BOT_TOKEN = "7728130811:AAH1csJqcu-lEQAVVCYb3IXIH9gyobGf0WU"
ADMIN_ID = 8015846071


async def message_router(update, context):
    if update.effective_user.id != ADMIN_ID:
        return

    text = update.message.text.strip()

    if context.user_data.get("awaiting_channel_add"):
        context.user_data["awaiting_channel_add"] = False
        channel = text.lstrip("@")
        with get_connection() as conn:
            conn.execute("INSERT OR IGNORE INTO channels (channel_username) VALUES (?)", (channel,))
        await update.message.reply_text(f"✅ کانال @{channel} اضافه شد.")
    elif context.user_data.get("awaiting_channel_remove"):
        context.user_data["awaiting_channel_remove"] = False
        channel = text.lstrip("@")
        with get_connection() as conn:
            conn.execute("DELETE FROM channels WHERE channel_username=?", (channel,))
        await update.message.reply_text(f"🗑 کانال @{channel} حذف شد.")
    elif context.user_data.get("awaiting_broadcast"):
        context.user_data["awaiting_broadcast"] = False
        message = text
        with get_connection() as conn:
            users = conn.execute("SELECT user_id FROM users").fetchall()
        success = 0
        for (user_id,) in users:
            try:
                await context.bot.send_message(chat_id=user_id, text=message)
                success += 1
            except:
                continue
        await update.message.reply_text(f"📤 پیام به {success} نفر ارسال شد.")
    elif text.startswith("del_"):
        code = text.replace("del_", "").strip()
        from utils import delete_file_by_code
        delete_file_by_code(code)
        await update.message.reply_text(f"🗑 فایل با کد {code} حذف شد.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(CallbackQueryHandler(check_membership, pattern=r'^check_'))
    app.add_handler(CallbackQueryHandler(admin_panel_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_router))

    app.run_polling()

if __name__ == "__main__":
    main()
