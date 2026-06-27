import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Update

# Setup logging
logging.basicConfig(level=logging.INFO)

# Securely grab the token from Render's environment variables
TOKEN = os.getenv("8910862510:AAH6m0WZfqgPriXs4AXaslgrv4_C59TGLCo")
WEBHOOK_URL = "https://yenedelalabot.onrender.com/webhook"

bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Hello! I am Yenedelabot. I am now online!")

@app.on_event("startup")
async def on_startup():
    # Tell Telegram where to send updates
    await bot.set_webhook(url=WEBHOOK_URL)
    print("Webhook successfully set!")

@app.post("/webhook")
async def webhook_address(update: dict):
    # Feed the updates from Render directly into Aiogram
    telegram_update = Update(**update)
    await dp.feed_update(bot, telegram_update)
    return {"status": "ok"}

@app.on_event("shutdown")
async def on_shutdown():
    # Clean up connection on shutdown
    await bot.delete_webhook()
    await bot.session.close()
