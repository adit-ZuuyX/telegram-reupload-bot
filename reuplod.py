import os
import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN belum diatur di Railway!")

file_storage = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Halo!\n\n"
        "Kirim foto, video, atau dokumen untuk direupload."
    )


async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = update.effective_user.id

    file_type = None
    file_id = None

    if message.photo:
        file_type = "photo"
        file_id = message.photo[-1].file_id

    elif message.video:
        file_type = "video"
        file_id = message.video.file_id

    elif message.document:
        file_type = "document"
        file_id = message.document.file_id

    if not file_id:
        return

    file_storage[user_id] = {
        "file_id": file_id,
        "type": file_type
    }

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "📥 Download Ulang",
            callback_data="download"
        )]
    ])

    await message.reply_text(
        "✅ File berhasil direupload.",
        reply_markup=keyboard
    )

    if file_type == "photo":
        await context.bot.send_photo(message.chat_id, file_id)

    elif file_type == "video":
        await context.bot.send_video(message.chat_id, file_id)

    elif file_type == "document":
        await context.bot.send_document(message.chat_id, file_id)


async def download_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    data = file_storage.get(user_id)

    if not data:
        await query.message.reply_text(
            "❌ Tidak ada file tersimpan."
        )
        return

    file_id = data["file_id"]
    file_type = data["type"]

    if file_type == "photo":
        await context.bot.send_photo(user_id, file_id)

    elif file_type == "video":
        await context.bot.send_video(user_id, file_id)

    elif file_type == "document":
        await context.bot.send_document(user_id, file_id)


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.PHOTO |
            filters.VIDEO |
            filters.Document.ALL,
            handle_media
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            download_callback,
            pattern="download"
        )
    )

    logging.info("Bot berjalan...")

    app.run_polling()


if __name__ == "__main__":
    main()