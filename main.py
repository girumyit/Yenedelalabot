import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

logging.basicConfig(level=logging.INFO)

TOKEN = "8910862510:AAHQ2hexfFKQMzlfIXZg9SpoCN0bzzUeFg4"
WEBHOOK_URL = "https://yenedelalabot.onrender.com/webhook"
ADMIN_ID = 427124870  

CHANNEL_LINKS = {
    "house_rent": "https://t.me/rentinadis",
    "house_sale": "https://t.me/houseaddis",
    "cars": "https://t.me/carsinadis",
    "others": "https://t.me/marketgebeya"
}

class PostItemState(StatesGroup):
    choosing_category = State()
    choosing_type = State()
    choosing_deal = State()
    entering_title = State()
    entering_description = State()
    collecting_photos = State()
    entering_price = State()
    entering_phone = State()
    entering_location = State()
    confirming_post = State()
    waiting_for_payment = State()

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

USER_LANGUAGES = {}

STRINGS = {
    "welcome": {
        "en": "👋 **Welcome to Your Delala!**\n\n🌍 No middleman. Direct.\nPlease choose your language / የቋንቋ ምርጫ፦",
        "am": "👋 **እንኳን ወደ Your Delala በደህና መጡ!**\n\n🇪🇹 ያለ ደላላ። በቀጥታ።\n🌍 No middleman. Direct.\n\nእባክዎ ቋንቋ ይምረጡ / Please choose your language፦"
    },
    "intro_text": {
        "en": "📢 **Post directly! Fast, clear, and commission-free.**\nWhat would you like to do today?",
        "am": "ደላላውን ይዘልላሉ! 🇪🇹\n\nሻጮች — ያላችሁን ንብረት ለመሸጥ ለምን ኮሚሽን ትከፍላላችሁ?\nገዢዎች — እቃ ለመመልከት ብቻ ለምን አላስፈላጊ ክፍያ ትከፍላላችሁ?\nሁለታችሁም — ግብይት ለመፈጸም ለምን ሳምንታትን ትጠብቃላችሁ?\n\nማስታወቂያዎን ይልቀቁ። በቀጥታ ይገናኙ። ፈጣን። ግልጽ። ያለ ኮሚሽን።\n\nYourDelala — የኢትዮጵያ ዘመናዊ ገበያ። 🛒"
    },
    "btn_browse": {"en": "🛍️ Buy or Rent", "am": "🛍️ መግዛት ወይም መከራየት እፈልጋለሁ"},
    "btn_post": {"en": "💰 Sell or Rent Out", "am": "💰 መሸጥ ወይም ማከራየት እፈልጋለሁ"},
    "btn_done_photos": {"en": "✅ Done sending photos", "am": "✅ ጨርሻለሁ — ፎቶዎችን ሁሉ ልኬያለሁ"},
    "pricing_explainer": {
        "en": "🎉 **Final Step — 300 Birr Listing Fee**\n\nThis prevents spam and keeps our network safe.\n\n💳 **How to Pay:**\n1. Open your Telebirr App\n2. Send **300 Birr** to **0985222918**\n3. Take a screenshot of the receipt\n4. Send the screenshot right here! 👇",
        "am": "🎉 **የመጨረሻው ደረጃ — 300 ብር የማስታወቂያ ክፍያ፦**\n\nይህ ስፓምን ይከላከላል። የኛን ሰርቨሮች ያቆያል። ለሁሉም የኢትዮጵያውያን ሻጮች ማህበረሰብን ያሳድጋል። 🇪🇹\n\n💳 **እንዴት መክፈል እንደሚቻል፦**\n1. የቴሌብር መተግበሪያዎን ይክፈቱ\n2. *300 ብር* ወደ *0985222918* ይላኩ\n3. የክፍያ ማረጋገጫ ስክሪንሾት ይውሰዱ\n4. ወደዚህ ቻት ይመለሱ\n5. ስክሪንሾቱን እዚህ ይላኩ 👇\n\n⚠️ *0985222918* በቴሌግራም አትላኩ። ስክሪንሾቱን እዚህ ታች ውስጥ ብቻ ይላኩ።"
    },
    "thank_you": {
        "en": "✅ **Thank you! Your listing and payment verification have been submitted to the admin.**",
        "am": "✅ **እናመሰግናለን! የእርስዎ የክፍያ ማረጋገጫ እና የዕቃው ዝርዝር ለግምገማ ወደ አስተዳዳሪ ተልኳል።**"
    }
}

def get_txt(user_id: int, key: str) -> str:
    lang = USER_LANGUAGES.get(user_id, "am")
    return STRINGS.get(key, {}).get(lang, STRINGS.get(key, {}).get("am", ""))

@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()
    lang_kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
                types.InlineKeyboardButton(text="🇪🇹 አማርኛ", callback_data="lang_am")
            ]
        ]
    )
    await message.answer(text=STRINGS["welcome"]["am"], reply_markup=lang_kb)

@dp.callback_query(lambda c: c.data.startswith("lang_"))
async def set_language(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    USER_LANGUAGES[user_id] = callback_query.data.replace("lang_", "")
    
    main_kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=get_txt(user_id, "btn_browse"), callback_data="menu_browse")],
            [types.InlineKeyboardButton(text=get_txt(user_id, "btn_post"), callback_data="menu_post")]
        ]
    )
    await callback_query.message.answer(text=get_txt(user_id, "intro_text"))
    await callback_query.message.answer(
        text="ዛሬ ምን ማድረግ ይፈልጋሉ?" if USER_LANGUAGES[user_id] == "am" else "What would you like to do today?",
        reply_markup=main_kb
    )
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "menu_post")
async def start_posting_workflow(callback_query: types.CallbackQuery, state: FSMContext):
    uid = callback_query.from_user.id
    await state.set_state(PostItemState.choosing_category)
    
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="🚗 የመኪና እና የሞተር ሽያጭ", callback_data="f_cat_cars")],
            [types.InlineKeyboardButton(text="🏠 ቤት እና ንብረት (ሽያጭ/ኪራይ)", callback_data="f_cat_house")],
            [types.InlineKeyboardButton(text="📱 ኤሌክትሮኒክስ", callback_data="f_cat_electronics")],
            [types.InlineKeyboardButton(text="👗 ፋሽን እና ውበት", callback_data="f_cat_fashion")],
            [types.InlineKeyboardButton(text="🛋️ የቤት እቃዎች እና ቁሳቁሶች", callback_data="f_cat_furniture")]
        ]
    )
    await callback_query.message.edit_text(text="ዛሬ ምን ይሸጣሉ ወይም ያከራያሉ?", reply_markup=kb)

@dp.callback_query(PostItemState.choosing_category)
async def post_category_chosen(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(category=callback_query.data.replace("f_cat_", ""))
    await state.set_state(PostItemState.choosing_type)
    
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="🏠 መኖሪያ ቤት", callback_data="f_type_residential")],
            [types.InlineKeyboardButton(text="🏢 ቢሮ", callback_data="f_type_office")]
        ]
    )
    await callback_query.message.edit_text(text="🏠 ንብረቱ ምን አይነት ነው?", reply_markup=kb)

@dp.callback_query(PostItemState.choosing_type)
async def post_type_chosen(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(type=callback_query.data.replace("f_type_", ""))
    await state.set_state(PostItemState.choosing_deal)
    
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="🏷️ ለሽያጭ", callback_data="f_deal_sale")],
            [types.InlineKeyboardButton(text="🔑 ለኪራይ", callback_data="f_deal_rent")]
        ]
    )
    await callback_query.message.edit_text(text="ንብረቱ ለሽያጭ ነው ወይስ ለኪራይ?", reply_markup=kb)

@dp.callback_query(PostItemState.choosing_deal)
async def post_deal_chosen(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(deal=callback_query.data.replace("f_deal_", ""))
    await state.set_state(PostItemState.entering_title)
    await callback_query.message.answer("🏷️ **ለማስታወቂያው ርዕስ ይስጡ፦**\n\n_ምሳሌ፦ 3 መኝታ ቤት ለሽያጭ — ቦሌ፣ አዲስ አበባ_", parse_mode="Markdown")

@dp.message(PostItemState.entering_title)
async def post_title_entered(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(PostItemState.entering_description)
    await message.answer("📝 **ንብረቱን ይግለጹ፦**\n\n_ያካትቱ፦ ካሬ ሜትር፣ የክፍሎች ቁጥር፣ ፎቅ፣ ፓርኪንግ ወዘተ..._\n⚠️ ከ700 ፊደል በታች ያድርጉ።", parse_mode="Markdown")

@dp.message(PostItemState.entering_description)
async def post_description_entered(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text, photos=[])
    await state.set_state(PostItemState.collecting_photos)
    await message.answer("📸 **አሁን ፎቶዎችን ይላኩ፦**\n\nፎቶዎችን አንድ በአንድ ይላኩ። ሲጨርሱ ከታች ያለውን ቁልፍ ይጫኑ።", reply_markup=types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text=get_txt(message.from_user.id, "btn_done_photos"), callback_data="done_photos")]]
    ))

@dp.message(PostItemState.collecting_photos)
async def process_photos(message: types.Message, state: FSMContext):
    if message.photo:
        data = await state.get_data()
        photos = data.get("photos", [])
        float_photo = message.photo[-1].file_id
        photos.append(float_photo)
        await state.update_data(photos=photos)
        await message.answer(f"📸 ፎቶ ደርሷል! (በጠቅላላ የተላኩ፦ {len(photos)})። ተጨማሪ መላክ ይችላሉ ወይም ሲጨርሱ 'ጨርሻለሁ' ይበሉ።", reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text=get_txt(message.from_user.id, "btn_done_photos"), callback_data="done_photos")]]
        ))

@dp.callback_query(PostItemState.collecting_photos, lambda c: c.data == "done_photos")
async def done_photos_pressed(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(PostItemState.entering_price)
    await callback_query.message.answer("💰 **የመጠየቂያ ዋጋ ምን ያህል ነው?**\n\nቁጥሩን ብቻ ይጻፉ (ምሳሌ፦ 250000)።")

@dp.message(PostItemState.entering_price)
async def price_entered(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(PostItemState.entering_phone)
    await message.answer("📞 **ገዢዎች በምን ስልክ ቁጥር ይደውሉልዎት?**\n\nይህ በይፋዊ ማስታወቂያዎ ላይ ይታያል።")

@dp.message(PostItemState.entering_phone)
async def phone_entered(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(PostItemState.entering_location)
    await message.answer("📍 **እቃው/ንብረቱ የት ነው የሚገኘው?**\n\n_ምሳሌ፦ አዲስ አበባ፣ ቦሌ_")

@dp.message(PostItemState.entering_location)
async def location_entered(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    await show_review_screen(message, state)

async def show_review_screen(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.set_state(PostItemState.confirming_post)
    
    review_template = (
        "📋 **የእርስዎ ማስታወቂያ ይህንን ይመስላል፦**\n\n"
        f"📦 **ምድብ/ዓይነት፦** {data.get('category')} — {data.get('type')}\n"
        f"📌 **ርዕስ፦** {data.get('title')}\n"
        f"💰 **ዋጋ፦** {data.get('price')} Birr\n"
        f"📍 **ቦታ፦** {data.get('location')}\n"
        f"📞 **ስልክ፦** {data.get('phone')}\n"
        f"📝 **መግለጫ፦** {data.get('description')}\n"
        f"📸 **ፎቶዎች፦** {len(data.get('photos', []))}\n"
        "💳 **Fee: 300 Birr**"
    )
    
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="✅ ጥሩ ነው — አስውጣ!", callback_data="confirm_to_pay")],
            [types.InlineKeyboardButton(text="✏️ አስተካክል", callback_data="menu_post")]
        ]
    )
    await message.answer(text=review_template, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(PostItemState.confirming_post, lambda c: c.data == "confirm_to_pay")
async def prompt_payment(callback_query: types.CallbackQuery, state: FSMContext):
    uid = callback_query.from_user.id
    await state.set_state(PostItemState.waiting_for_payment)
    await callback_query.message.answer(text=get_txt(uid, "pricing_explainer"), parse_mode="Markdown")

@dp.message(PostItemState.waiting_for_payment)
async def final_admin_delivery(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("⚠️ እባክዎ ለመቀጠል ትክክለኛ የክፍያ ማረጋገጫ ፎቶ (Screenshot) ይላኩ።")
        return

    screenshot_id = message.photo[-1].file_id
    data = await state.get_data()
    uid = message.from_user.id
    
    admin_summary = (
        f"🚀 **New Paid Listing Received!**\n\n"
        f"👤 User: @{message.from_user.username or 'No Username'} (ID: {uid})\n"
        f"📁 Category: {data.get('category')} / {data.get('type')} ({data.get('deal')})\n"
        f"📌 Title: {data.get('title')}\n"
        f"💰 Price: {data.get('price')} Birr\n"
        f"📍 Location: {data.get('location')}\n"
        f"📞 Phone: {data.get('phone')}\n"
        f"📝 Description: {data.get('description')}"
    )

    try:
        await bot.send_message(chat_id=ADMIN_ID, text=admin_summary)
        for p_id in data.get("photos", []):
            await bot.send_photo(chat_id=ADMIN_ID, photo=p_id)
        await bot.send_photo(chat_id=ADMIN_ID, photo=screenshot_id, caption="🧾 **Telebirr Verified Screenshot Payment**")
    except Exception as e:
        logging.error(f"Delivery failed: {e}")

    await state.clear()
    await message.answer(text=get_txt(uid, "thank_you"), parse_mode="Markdown")

async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)

async def on_shutdown(bot: Bot) -> None:
    await bot.delete_webhook()
    await bot.session.close()

async def combined_health_route(request):
    return web.Response(text="Bot operational", status=200)

def main():
    app = web.Application()
    app.router.add_get("/", combined_health_route)
    app.router.add_get("/webhook", combined_health_route)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path="/webhook")
    setup_application(app, dp, bot=bot)

    port = int(os.environ.get("PORT", 8000))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
