import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# Setup logging
logging.basicConfig(level=logging.INFO)

# Your Bot Details
TOKEN = "8910862510:AAH6m0WZfqgPriXs4AXaslgrv4_C59TGLCo"
WEBHOOK_URL = "https://yenedelalabot.onrender.com/webhook"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Hello! I am Yenedelabot. I am now online!")

async def on_startup(bot: Bot) -> None:
    # Tell Telegram where to send updates
    await bot.set_webhook(url=WEBHOOK_URL)
    logging.info("Webhook successfully set!")

async def on_shutdown(bot: Bot) -> None:
    # Clean up on shutdown
    await bot.delete_webhook()
    await bot.session.close()

def main():
    # Initialize aiohttp application (the server)
    app = web.Application()

    # Configure the webhook request handler
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    # Register the webhook route (dispatches incoming requests to aiogram)
    webhook_requests_handler.register(app, path="/webhook")

    # Bind startup and shutdown lifecycle steps
    setup_application(app, dp, bot=bot)
    app.on_startup.append(lambda _: on_startup(bot))
    app.on_shutdown.append(lambda _: on_shutdown(bot))

    # Grab Render's port dynamically
    port = int(os.environ.get("PORT", 8000))
    
    # Run the web server
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
