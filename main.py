import logging
import os
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes
)

# === CONFIGURATION ===
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
REMOVE_BG_API_KEY = os.getenv("REMOVE_BG_KEY")

# === LOGGING SETUP ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# === COMMAND: /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! Send me a photo, and I’ll remove the background for you.\n\n"
        "📌 Type /help for more commands."
    )

# === COMMAND: /help ===
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠 *Available Commands:*\n"
        "/start - Start the bot\n"
        "/help - List of commands\n"
        "/status - Check if the bot is active\n"
        "/key - Show your Remove.bg API Key",
        parse_mode="Markdown"
    )

# === COMMAND: /status ===
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ I’m online and ready to remove backgrounds!")

# === COMMAND: /key ===
async def key_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🔑 Your current Remove.bg API Key is:\n`{REMOVE_BG_API_KEY}`",
        parse_mode="Markdown"
    )

# === PHOTO HANDLER ===
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 Downloading image...")

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    await file.download_to_drive("input_image.jpg")

    await update.message.reply_text("🎨 Removing background, please wait...")

    with open("input_image.jpg", 'rb') as img:
        response = requests.post(
            "https://api.remove.bg/v1.0/removebg",
            files={"image_file": img},
            data={"size": "auto"},
            headers={"X-Api-Key": REMOVE_BG_API_KEY}
        )

    if response.status_code == 200:
        with open("output_image.png", "wb") as out:
            out.write(response.content)

        await update.message.reply_text("✅ Done! Here’s your image without background:")
        await update.message.reply_photo(photo=open("output_image.png", 'rb'))
    else:
        await update.message.reply_text("❌ Failed to remove background:\n" + response.text)

# === MAIN FUNCTION ===
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("key", key_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
