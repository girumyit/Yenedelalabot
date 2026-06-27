import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# Setup logging
logging.basicConfig(level=logging.INFO)

TOKEN = "8910862510:AAGNyljkcCYDvEsEMgAVwiksKXiBlLxJw0w"
WEBHOOK_URL = "https://yenedelalabot.onrender.com/webhook"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Hello! I am Yenedelabot. I am now online!")

async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)
    logging.info("Webhook successfully set!")

async def on_shutdown(bot: Bot) -> None:
    await bot.delete_webhook()
    await bot.session.close()

# THIS IS THE RENDER HEALTH CHECK FIX
async def health_check(request):
    return web.Response(text="Bot is running smoothly!", status=200)

def main():
    app = web.Application()

    # 1. Add a route for Render's health check on the home page '/'
    app.router.add_get("/", health_check)

    # 2. Configure the webhook request handler for Telegram
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path="/webhook")

    setup_application(app, dp, bot=bot)
    app.on_startup.append(lambda _: on_startup(bot))
    app.on_shutdown.append(lambda _: on_shutdown(bot))

    port = int(os.environ.get("PORT", 8000))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
