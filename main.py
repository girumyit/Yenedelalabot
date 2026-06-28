import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# Setup logging
logging.basicConfig(level=logging.INFO)

TOKEN = "8910862510:AAHQ2hexfFKQMzlfIXZg9SpoCN0bzzUeFg4"
WEBHOOK_URL = "https://yenedelalabot.onrender.com/webhook"
ADMIN_ID = 5691062953  # Ensure this is your correct personal numeric ID

CHANNEL_LINKS = {
    "house_rent": "https://t.me/rentinadis",
    "house_sale": "https://t.me/houseaddis",
    "cars": "https://t.me/carsinadis",
    "others": "https://t.me/marketgebeya"
}

# Define Finite State Machine Flow
class PostItemState(StatesGroup):
    choosing_category = State()
    choosing_type = State()
    choosing_deal = State()
    entering_title = State()
    entering_description = State()
    confirming_post = State()

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

USER_LANGUAGES = {}

STRINGS = {
    "welcome": {
        "en": "👋 **Welcome to Yenedelala Bot!**\n\nYour trusted digital broker for houses, cars, and rentals in Ethiopia.\nWhat are you looking to do today?",
        "am": "👋 **እንኳን ወደ የነደላላ ቦት በደህና መጡ!**\n\nበኢትዮጵያ ውስጥ ለቤት፣ ለመኪና እና ለኪራይ አስተማማኝ ዲጂታል ደላላዎ።\nዛሬ ምን ማድረግ ይፈልጋሉ?"
    },
    "btn_browse": {"en": "🔍 Browse Listings", "am": "🔍 ዝርዝሮችን ተመልከት"},
    "btn_post": {"en": "➕ Post an Item", "am": "➕ አዲስ ዕቃ ፍጠር"},
    "btn_help": {"en": "📞 Contact Broker / Help", "am": "📞 ደላላ አግኝ / እርዳታ"},
    "btn_back": {"en": "⬅️ Back", "am": "⬅️ ወደኋላ ተመለስ"},
    "btn_back_cat": {"en": "⬅️ Back to Categories", "am": "⬅️ ወደ ምድቦች ተመለስ"},
    "select_cat": {"en": "📁 **Select a Category to browse:**", "am": "📁 **ለመመልከት ምድብ ይምረጡ:**"},
    "cat_house_rent": {"en": "🏠 Houses for Rent", "am": "🏠 የሚከራዩ ቤቶች"},
    "cat_house_sale": {"en": "🏢 Houses for Sale", "am": "🏢 የሚሸጡ ቤቶች"},
    "cat_cars": {"en": "🚘 Cars", "am": "🚘 መኪናዎች"},
    "cat_others": {"en": "📦 Other Items", "am": "📦 ሌሎች ዕቃዎች"},
    "btn_view_channel": {"en": "📢 Open Telegram Channel", "am": "📢 የቴሌግራም ቻናሉን ክፈት"},
    "channel_redirect_text": {
        "en": "🔗 Click the button below to join and view all available listings for **{cat}** on our official channel:",
        "am": "🔗 በቻናላችን ላይ ያሉትን ሁሉንም የ**{cat}** ዝርዝሮች ለማየት ከታች ያለውን ቁልፍ ይጫኑ፦"
    },
    "help_text": {
        "en": "📞 **Need Assistance?**\n\nFor business inquiries, manual listings, or support, please contact @girumyit.",
        "am": "📞 **እርዳታ ይፈልጋሉ?**\n\nለንግድ ስራ መጠይቆች፣ እቃዎችን ለማስመዝገብ ወይም ለድጋፍ እባክዎን @girumyit ን ያግኙ።"
    }
}

def get_txt(user_id: int, key: str, **kwargs) -> str:
    lang = USER_LANGUAGES.get(user_id, "am")
    text = STRINGS.get(key, {}).get(lang, "")
    if kwargs:
        return text.format(**kwargs)
    return text

@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()
    lang_kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en"),
                types.InlineKeyboardButton(text="🇪🇹 አማርኛ (Amharic)", callback_data="lang_am")
            ]
        ]
    )
    await message.answer("Please choose your language / እባክዎ ቋንቋ ይምረጡ፦", reply_markup=lang_kb)

@dp.callback_query(lambda c: c.data.startswith("lang_"))
async def set_language(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    selected_lang = callback_query.data.replace("lang_", "")
    USER_LANGUAGES[user_id] = selected_lang
    
    main_kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text=get_txt(user_id, "btn_browse"), callback_data="menu_browse"),
                types.InlineKeyboardButton(text=get_txt(user_id, "btn_post"), callback_data="menu_post")
            ],
            [
                types.InlineKeyboardButton(text=get_txt(user_id, "btn_help"), callback_data="menu_help")
            ]
        ]
    )
    await callback_query.message.edit_text(
        text=get_txt(user_id, "welcome"),
        reply_markup=main_kb,
        parse_mode="Markdown"
    )
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "menu_browse")
async def process_browse_menu(callback_query: types.CallbackQuery):
    uid = callback_query.from_user.id
    category_kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text=get_txt(uid, "cat_house_rent"), callback_data="cat_house_rent"),
                types.InlineKeyboardButton(text=get_txt(uid, "cat_house_sale"), callback_data="cat_house_sale")
            ],
            [
                types.InlineKeyboardButton(text=get_txt(uid, "cat_cars"), callback_data="cat_cars"),
                types.InlineKeyboardButton(text=get_txt(uid, "cat_others"), callback_data="cat_others")
            ],
            [
                types.InlineKeyboardButton(text=get_txt(uid, "btn_back"), callback_data="back_to_main")
            ]
        ]
    )
    await callback_query.message.edit_text(
        text=get_txt(uid, "select_cat"),
        reply_markup=category_kb,
        parse_mode="Markdown"
    )
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "back_to_main")
async def process_back_to
