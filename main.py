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

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    # Create clean inline buttons
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔍 Browse Listings", callback_data="menu_browse"),
                InlineKeyboardButton(text="➕ Post an Item", callback_data="menu_post")
            ],
            [
                InlineKeyboardButton(text="📞 Contact Broker / Help", callback_data="menu_help")
            ]
        ]
    )
    
    welcome_text = (
        "👋 **Welcome to Yenedelala Bot!**\n\n"
        "Your trusted digital broker for houses, cars, and rentals in Ethiopia.\n"
        "What are you looking to do today?"
    )
    
    await message.answer(welcome_text, reply_markup=inline_kb, parse_mode="Markdown")
# Handle "Browse Listings" click
@dp.callback_query(lambda c: c.data == "menu_browse")
async def process_browse_menu(callback_query: CallbackQuery):
    category_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🏠 Houses for Rent", callback_data="cat_house_rent"),
                InlineKeyboardButton(text="🏢 Houses for Sale", callback_data="cat_house_sale")
            ],
            [
                InlineKeyboardButton(text="🚘 Cars", callback_data="cat_cars"),
                InlineKeyboardButton(text="📦 Other Items", callback_data="cat_others")
            ],
            [
                InlineKeyboardButton(text="⬅️ Back to Main Menu", callback_data="back_to_main")
            ]
        ]
    )
    
    await callback_query.message.edit_text(
        text="📁 **Select a Category to browse:**",
        reply_markup=category_kb,
        parse_mode="Markdown"
    )
    # Always answer the callback query so the loading wheel stops spinning
    await callback_query.answer()

# Handle the "Back to Main Menu" button click
@dp.callback_query(lambda c: c.data == "back_to_main")
async def process_back_to_main(callback_query: CallbackQuery):
    # Recreate the original main menu
    main_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔍 Browse Listings", callback_data="menu_browse"),
                InlineKeyboardButton(text="➕ Post an Item", callback_data="menu_post")
            ],
            [
                InlineKeyboardButton(text="📞 Contact Broker / Help", callback_data="menu_help")
            ]
        ]
    )
    
    await callback_query.message.edit_text(
        text="👋 **Welcome to Yenedelala Bot!**\n\nWhat are you looking to do today?",
        reply_markup=main_kb,
        parse_mode="Markdown"
    )
    await callback_query.answer()
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
