import os
import logging
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters
from trade_intelligence import get_trade_signals

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize bot and dispatcher
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

bot = Bot(TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)


async def start(update: Update, context) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}!\n\nI\\\"m your personal AI assistant, Manus. I\\\"m here to help you with your tasks. Just tell me what you need!",
    )


async def help_command(update: Update, context) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("I\\\"m Manus, your personal AI assistant. How can I help you?")


async def trade_signal_command(update: Update, context) -> None:
    """Get trade signals and send them to the user."""
    await update.message.reply_text("Analyzing market data for trade signals... Please wait.")
    signal_message = get_trade_signals()
    await update.message.reply_text(signal_message)


async def echo(update: Update, context) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


@app.route("/")
def index():
    return "Hello World!"


@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
async def webhook():
    """Webhook for Telegram updates."""
    update = Update.de_json(request.get_json(force=True), bot)
    await dispatcher.process_update(update)
    return "ok"


def main() -> None:
    """Start the bot."""
    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("trade_signal", trade_signal_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


if __name__ == "__main__":
    main()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
