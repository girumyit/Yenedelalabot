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
    inline_kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="🔍 Browse Listings", callback_data="menu_browse"),
                types.InlineKeyboardButton(text="➕ Post an Item", callback_data="menu_post")
            ],
            [
                types.InlineKeyboardButton(text="📞 Contact Broker / Help", callback_data="menu_help")
            ]
        ]
    )
    
    welcome_text = (
        "👋 **Welcome to Yenedelala Bot!**\n\n"
        "Your trusted digital broker for houses, cars, and rentals in Ethiopia.\n"
        "What are you looking to do today?"
    )
    await message.answer(welcome_text, reply_markup=inline_kb, parse_mode="Markdown")

async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)
    logging.info("Webhook successfully set!")

async def on_shutdown(bot: Bot) -> None:
    await bot.delete_webhook()
    await bot.session.close()

async def health_check(request):
    return web.Response(text="Bot is running smoothly!", status=200)

@dp.callback_query(lambda c: c.data == "menu_browse")
async def process_browse_menu(callback_query: types.CallbackQuery):
    category_kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="🏠 Houses for Rent", callback_data="cat_house_rent"),
                types.InlineKeyboardButton(text="🏢 Houses for Sale", callback_data="cat_house_sale")
            ],
            [
                types.InlineKeyboardButton(text="🚘 Cars", callback_data="cat_cars"),
                types.InlineKeyboardButton(text="📦 Other Items", callback_data="cat_others")
            ],
            [
                types.InlineKeyboardButton(text="⬅️ Back to Main Menu", callback_data="back_to_main")
            ]
        ]
    )
    await callback_query.message.edit_text(
        text="📁 **Select a Category to browse:**",
        reply_markup=category_kb,
        parse_mode="Markdown"
    )
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "back_to_main")
async def process_back_to_main(callback_query: types.CallbackQuery):
    main_kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="🔍 Browse Listings", callback_data="menu_browse"),
                types.InlineKeyboardButton(text="➕ Post an Item", callback_data="menu_post")
            ],
            [
                types.InlineKeyboardButton(text="📞 Contact Broker / Help", callback_data="menu_help")
            ]
        ]
    )
    await callback_query.message.edit_text(
        text="👋 **Welcome to Yenedelala Bot!**\n\nWhat are you looking to do today?",
        reply_markup=main_kb,
        parse_mode="Markdown"
    )
    await callback_query.answer()

@dp.callback_query(lambda c: c.data.startswith("cat_"))
async def process_category_selection(callback_query: types.CallbackQuery):
    category_selected = callback_query.data.replace("cat_", "").replace("_", " ").title()
    back_kb = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="⬅️ Back to Categories", callback_data="menu_browse")]]
    )
    await callback_query.message.edit_text(
        text=f"✨ Showing latest listings for: **{category_selected}**\n\n_(Currently empty. Listings will appear here once connected to database.)_",
        reply_markup=back_kb,
        parse_mode="Markdown"
    )
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "menu_help")
async def process_help(callback_query: types.CallbackQuery):
    back_kb = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_main")]]
    )
    await callback_query.message.edit_text(
        text="📞 **Need Assistance?**\n\nFor business inquiries, manual listings, or support, please contact @girumyit.",
        reply_markup=back_kb,
        parse_mode="Markdown"
    )
    await callback_query.answer()

def main():
    app = web.Application()
    app.router.add_get("/", health_check)

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
