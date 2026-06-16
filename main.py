import asyncio
import logging
from fastapi import FastAPI
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update

# Setup logging
logging.basicConfig(level=logging.INFO)

TOKEN = "8910862510:AAEpiO2JGuoeyJQjEKcLo558USF6UT0FhgM"
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
