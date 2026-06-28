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
async def process_back_to_main(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    uid = callback_query.from_user.id
    main_kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text=get_txt(uid, "btn_browse"), callback_data="menu_browse"),
                types.InlineKeyboardButton(text=get_txt(uid, "btn_post"), callback_data="menu_post")
            ],
            [
                types.InlineKeyboardButton(text=get_txt(uid, "btn_help"), callback_data="menu_help")
            ]
        ]
    )
    await callback_query.message.edit_text(
        text=get_txt(uid, "welcome"),
        reply_markup=main_kb,
        parse_mode="Markdown"
    )
    await callback_query.answer()

@dp.callback_query(lambda c: c.data.startswith("cat_"))
async def process_category_selection(callback_query: types.CallbackQuery):
    uid = callback_query.from_user.id
    raw_cat = callback_query.data.replace("cat_", "")
    
    channel_key = raw_cat
    if channel_key not in CHANNEL_LINKS:
        channel_key = "others"
        
    target_channel_url = CHANNEL_LINKS[channel_key]
    cat_title = get_txt(uid, f"cat_{raw_cat}" if f"cat_{raw_cat}" in STRINGS else "cat_others")
    
    channel_kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=get_txt(uid, "btn_view_channel"), url=target_channel_url)],
            [types.InlineKeyboardButton(text=get_txt(uid, "btn_back_cat"), callback_data="menu_browse")]
        ]
    )
    await callback_query.message.edit_text(
        text=get_txt(uid, "channel_redirect_text", cat=cat_title),
        reply_markup=channel_kb,
        parse_mode="Markdown"
    )
    await callback_query.answer()

# --- START FORM FLOW HANDLERS ---

@dp.callback_query(lambda c: c.data == "menu_post")
async def start_posting_workflow(callback_query: types.CallbackQuery, state: FSMContext):
    uid = callback_query.from_user.id
    await state.set_state(PostItemState.choosing_category)
    
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="🚘 Car Sales", callback_data="f_cat_car")],
            [types.InlineKeyboardButton(text="🏠 House & Property", callback_data="f_cat_house")],
            [types.InlineKeyboardButton(text="📦 Electronics / Others", callback_data="f_cat_other")]
        ]
    )
    
    msg = "📂 Choose the category for the item you want to sell or rent out:" if USER_LANGUAGES.get(uid, "am") == "en" else "📂 እባክዎ ሊሸጡት ወይም ሊያከራዩት የፈለጉትን እቃ ምድብ ይምረጡ፦"
    await callback_query.message.edit_text(text=msg, reply_markup=kb)
    await callback_query.answer()

@dp.callback_query(PostItemState.choosing_category)
async def post_category_chosen(callback_query: types.CallbackQuery, state: FSMContext):
    uid = callback_query.from_user.id
    category_selected = callback_query.data.replace("f_cat_", "")
    await state.update_data(category=category_selected)
    
    await state.set_state(PostItemState.choosing_type)
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="🏠 Home / Personal", callback_data="f_type_home")],
            [types.InlineKeyboardButton(text="🏢 Office / Commercial", callback_data="f_type_office")]
        ]
    )
    msg = "What type of property/item is this?" if USER_LANGUAGES.get(uid, "am") == "en" else "ይህ ምን አይነት እቃ/ንብረት ነው?"
    await callback_query.message.edit_text(text=msg, reply_markup=kb)
    await callback_query.answer()

@dp.callback_query(PostItemState.choosing_type)
async def post_type_chosen(callback_query: types.CallbackQuery, state: FSMContext):
    uid = callback_query.from_user.id
    type_selected = callback_query.data.replace("f_type_", "")
    await state.update_data(type=type_selected)
    
    await state.set_state(PostItemState.choosing_deal)
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="🏷️ For Sale", callback_data="f_deal_sale")],
            [types.InlineKeyboardButton(text="🔑 For Rent", callback_data="f_deal_rent")]
        ]
    )
    msg = "Is this item for sale or rent?" if USER_LANGUAGES.get(uid, "am") == "en" else "ይህ እቃ ለሽያጭ ነው ወይስ ለኪራይ?"
    await callback_query.message.edit_text(text=msg, reply_markup=kb)
    await callback_query.answer()

@dp.callback_query(PostItemState.choosing_deal)
async def post_deal_chosen(callback_query: types.CallbackQuery, state: FSMContext):
    uid = callback_query.from_user.id
    deal_selected = callback_query.data.replace("f_deal_", "")
    await state.update_data(deal=deal_selected)
    
    await state.set_state(PostItemState.entering_title)
    msg = "✍️ **Write a short title buyers can understand quickly.**\n\n*Example: 3 bedroom house for sale — Bole, Addis Ababa.*" if USER_LANGUAGES.get(uid, "am") == "en" else "✍️ **ገዢዎች በፍጥነት ሊረዱት የሚችሉትን አጭር ርዕስ ይጻፉ።**\n\n*ምሳሌ፦ ባለ 3 መኝታ ቤት የሚሸጥ — ቦሌ፣ አዲስ አበባ።*"
    await callback_query.message.edit_text(text=msg, parse_mode="Markdown")
    await callback_query.answer()

@dp.message(PostItemState.entering_title)
async def post_title_entered(message: types.Message, state: FSMContext):
    uid = message.from_user.id
    await state.update_data(title=message.text)
    
    await state.set_state(PostItemState.entering_description)
    msg = "📝 **Describe the property/item.**\n\nInclude details like size, location specs, condition, and price expectations." if USER_LANGUAGES.get(uid, "am") == "en" else "📝 **ስለ እቃው/ንብረቱ ዝርዝር መግለጫ ይጻፉ።**\n\nልክ፣ የተወሰነ ቦታ፣ ሁኔታ እና የሚፈልጉትን ዋጋ ማካተት ይችላሉ።"
    await message.answer(text=msg, parse_mode="Markdown")

@dp.message(PostItemState.entering_description)
async def post_description_entered(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text, photos=[])
    await show_review_screen(message, state)

# --- REUSABLE REVIEW SHEET OVERLAY ---
async def show_review_screen(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.set_state(PostItemState.confirming_post)
    
    review_template = (
        "📋 <b>HERE IS YOUR LOOKING FOR POST</b>\n\n"
        f"📦 <b>Category:</b> {str(data.get('category')).upper()}\n"
        f"🏢 <b>Type:</b> {data.get('type')}\n"
        f"🏷️ <b>Deal:</b> {data.get('deal')}\n"
        f"📌 <b>Title:</b> {data.get('title')}\n"
        f"📝 <b>Description:</b> {data.get('description')}\n"
        f"📸 <b>Photos Attached:</b> {len(data.get('photos', []))}\n\n"
        "💳 <b>Fee: 50 Birr</b>"
    )
    
    confirm_kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="✅ Looks Great — Post It!", callback_data="action_confirm_submit")],
            [types.InlineKeyboardButton(text="📸 Add a Sample Photo (Optional)", callback_data="action_add_photo")],
            [types.InlineKeyboardButton(text="📝 Let Me Edit Something", callback_data="menu_post")]
        ]
    )
    await message.answer(text=review_template, reply_markup=confirm_kb, parse_mode="HTML")

@dp.callback_query(PostItemState.confirming_post, lambda c: c.data == "action_add_photo")
async def request_photo_upload(callback_query: types.CallbackQuery):
    uid = callback_query.from_user.id
    msg = "📸 Please send your photo directly into this chat room now. You can send multiple photos one by one." if USER_LANGUAGES.get(uid, "am") == "en" else "📸 እባክዎን ፎቶዎን አሁን በዚህ ቻት ውስጥ ይላኩ። ፎቶዎችን একে একে መላክ ይችላሉ።"
    await callback_query.message.answer(text=msg)
    await callback_query.answer()

@dp.message(PostItemState.confirming_post)
async def process_photo_or_text_in_confirm(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.photo:
        photos_list = data.get("photos", [])
        photos_list.append(message.photo[-1].file_id)
        await state.update_data(photos=photos_list)
        await message.answer("📸 Photo added successfully!")
        await show_review_screen(message, state)
        return
    await message.answer("⚠️ Please use the buttons to proceed or upload an image file.")

@dp.callback_query(PostItemState.confirming_post, lambda c: c.data == "action_confirm_submit")
async def finalize_post_with_pricing(callback_query: types.CallbackQuery, state: FSMContext):
    uid = callback_query.from_user.id
    data = await state.get_data()
    
    summary = (
        "🚀 <b>New Listing Submission!</b>\n\n"
        f"👤 <b>User:</b> @{callback_query.from_user.username or 'No Username'} (ID: {uid})\n"
        f"📁 <b>Category:</b> {data.get('category')}\n"
        f"🏢 <b>Type:</b> {data.get('type')}\n"
        f"🏷️ <b>Deal:</b> {data.get('deal')}\n"
        f"📌 <b>Title:</b> {data.get('title')}\n"
        f"📝 <b>Description:</b> {data.get('description')}"
    )
    
    target_chat = ADMIN_ID if ADMIN_ID else uid
    try:
        await bot.send_message(chat_id=target_chat, text=summary, parse_mode="HTML")
        for photo_id in data.get("photos", []):
            try:
                await bot.send_photo(chat_id=target_chat, photo=photo_id)
            except Exception as p_err:
                logging.error(f"Photo delivery failed: {p_err}")
    except Exception as e:
        logging.error(f"Primary listing delivery failed: {e}")
        
    await state.clear()
    
    pricing_explainer = (
        "🎉 <b>*One last step — 50 Birr listing fee.*</b>\n\n"
        "<b>*Why do buyers pay too?*</b>\n\n"
        "✅ <b>*Safety:*</b> Keeps spam and fake requests out\n"
        "✅ <b>*Quality:*</b> Only serious buyers post — protects sellers from time-wasters\n"
        "✅ <b>*Trust:*</b> Keeps our platform clean and reliable\n"
        "✅ <b>*Sustainability:*</b> Keeps servers running 24/7\n\n"
        "Your 'Looking For' post stays live for 60 days or until you find what you need.\n\n"
        "👉 <i>Then send your payment screenshot RIGHT HERE in this chat.</i> 👇"
    )
    await callback_query.message.answer(text=pricing_explainer, parse_mode="HTML")
    await callback_query.answer()

# --- END FORM FLOW HANDLERS ---

@dp.callback_query(lambda c: c.data == "menu_help")
async def process_help(callback_query: types.CallbackQuery):
    uid = callback_query.from_user.id
    back_kb = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text=get_txt(uid, "btn_back"), callback_data="back_to_main")]]
    )
    await callback_query.message.edit_text(
        text=get_txt(uid, "help_text"),
        reply_markup=back_kb,
        parse_mode="Markdown"
    )
    await callback_query.answer()

async def on_startup(bot: Bot) -> None:
    logging.info(f"Connecting Webhook securely -> {WEBHOOK_URL}")
    await bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)

async def on_shutdown(bot: Bot) -> None:
    logging.info("Disconnecting application links smoothly...")
    await bot.delete_webhook()
    await bot.session.close()

async def health_check(request):
    return web.Response(text="Bot gateway operational", status=200)

def main():
    app = web.Application()
    app.router.add_get("/", health_check)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path="/webhook")
    setup_application(app, dp, bot=bot)

    port = int(os.environ.get("PORT", 8000))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()

