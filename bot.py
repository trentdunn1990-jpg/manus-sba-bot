import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import InvalidToken
import asyncio

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}!\n\nI'm your personal AI assistant, Manus. I'm here to help you with your tasks. Just tell me what you need!",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("I'm Manus, your personal AI assistant. How can I help you?")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


async def main() -> None:
    """Start the bot using webhooks."""
    # Create the Application
    application = Application.builder().token(os.environ.get("TELEGRAM_BOT_TOKEN")).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Get the port from environment or default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    # Start the bot using webhooks
    await application.bot.set_webhook(url=f"https://{os.environ.get('RAILWAY_DOMAIN', 'localhost')}/webhook")
    
    # Start the application with webhook
    async with application:
        await application.start()
        
        # Create a simple ASGI app for webhooks
        from telegram.ext import Application
        from aiohttp import web
        
        async def handle_webhook(request):
            """Handle incoming webhook updates."""
            try:
                update = Update.de_json(await request.json(), application.bot)
                await application.process_update(update)
                return web.Response(status=200)
            except Exception as e:
                logger.error(f"Error processing update: {e}")
                return web.Response(status=500)
        
        # Create web app
        app = web.Application()
        app.router.add_post("/webhook", handle_webhook)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        
        logger.info(f"Bot started on port {port}")
        
        # Keep the bot running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            pass
        finally:
            await application.stop()


if __name__ == "__main__":
    asyncio.run(main())
