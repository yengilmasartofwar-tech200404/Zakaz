import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

# TOKEN va ADMIN ID ni shu yerga yozasiz
TOKEN = "9065086543:AAFQw02y-SjKGgEv5Sm0tspIWf341FKZc2E"
ADMIN_ID = (
    6677396153  # Telegramdagi o'z raqamli IDingizni yozing (masalan: 987654321)
)

dp = Dispatcher()
router = Router()


# --- STATES (Holatlar) ---
class OrderState(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_details = State()


# --- MATNLAR VA TARJIMALAR (O'zbekcha / Qoraqalpoqcha) ---
TEXTS = {
    "uz": {
        "welcome": (
            "Assalomu alaykum! Veb-ilova va botlar buyurtma berish botiga"
            " xush kelibsiz.\nTilni tanlang / Tilg'i saylang:"
        ),
        "choose_lang": "Til muvaffaqiyatli o'zgartirildi: O'zbek tili 🇺🇿",
        "menu": (
            "Kerakli bo'limni tanlang:\n\n🌐 **Veb-ilova turlari va narxlari**\n❓"
            " **Ko'p beriladigan savollar**\n🛒 **Buyurtma berish**\n📞"
            " **Bog'lanish**"
        ),
        "services": (
            "💻 **Veb-ilova va xizmatlar narxi:**\n\n1. **Landing Page"
            " (Bir sahifali sayt):** $100 dan boshlab (3-5 kun)\n2. **Internet"
            " do'kon (E-commerce):** $300 dan boshlab (7-14 kun)\n3. **Korporativ"
            " veb-sayt:** $250 dan boshlab (5-10 kun)\n4. **Telegram bot"
            " yaratish:** $50 dan boshlab\n\nNarxlar loyihaning murakkabligiga"
            " qarab o'zgarishi mumkin."
        ),
        "faq": (
            "❓ **Ko'p beriladigan savollar:**\n\n🔹 **To'lov qanday amalga"
            " oshiriladi?**\n- 50% oldindan, 50% loyiha topshirilganda.\n🔹"
            " **Domen va Hosting o'zimizdanmi?**\n- Ha, sozlab beramiz.\n🔹"
            " **Saytga kafolat bormi?**\n- Ha, 1 yil davomida texnik yordam"
            " bepul."
        ),
        "ask_name": "Ismingizni kiriting:",
        "ask_phone": (
            "Telefon raqamingizni yuboring (masalan: +998 90 123 45 67):"
        ),
        "ask_details": "Qanaqa veb-ilova yoki loyiha kerakligini yozib qoldiring:",
        "order_success": (
            "✅ Buyurtmangiz qabul qilindi! Tez orada adminlarimiz siz bilan"
            " bog'lanishadi."
        ),
        "admin_notify": (
            "🔔 **Yangi buyurtma!**\n\n👤 **Mijoz:** {name}\n📞 **Telefon:**"
            " {phone}\n💬 **Loyiha haqida:** {details}\n🔗 **Profil:**"
            " [{username}](tg://user?id={user_id})\n🕒 **Vaqt:** {time}"
        ),
        "btn_services": "🌐 Veb-ilovalar va Narxlar",
        "btn_faq": "❓ Savol-Javoblar",
        "btn_order": "🛒 Buyurtma berish",
        "btn_contact": "📞 Bog'lanish",
        "btn_back": "🔙 Orqaga",
    },
    "kaa": {
        "welcome": (
            "Assalawma aleykum! Web-qollanba hám botlar zakaz beriw botına"
            " xosh kelipsiz.\nTildi saylan' / Tilni tanlang:"
        ),
        "choose_lang": "Til tabıslı ózgertildi: Qaraqalpaq tili 🇰🇷 (Qaraqalpoq)",
        "menu": (
            "Kerakli bol'imdi saylan':\n\n🌐 **Web-qollanba turlari hám"
            " bahaları**\n❓ **Kóp beriletin sorawlar**\n🛒 **Zakaz"
            " beriw**\n📞 **Baylanıs**"
        ),
        "services": (
            "💻 **Web-qollanba hám xızmetler bahası:**\n\n1. **Landing Page"
            " (Bir betlik sayt):** $100 baslap (3-5 kún)\n2. **Internet"
            " magazin (E-commerce):** $300 baslap (7-14 kún)\n3. **Korporativ"
            " web-sayt:** $250 baslap (5-10 kún)\n4. **Telegram bot jaratıw:**"
            " $50 baslap\n\nBahalar proektin' murakkabligine qarap ózgeriwi"
            " múmkin."
        ),
        "faq": (
            "❓ **Kóp beriletin sorawlar:**\n\n🔹 **Tólemler qalay ámelge"
            " asırıladı?**\n- 50% aldın ala, 50% proekt tapsırılǵanda.\n🔹"
            " **Domen hám Hosting ózimizden be?**\n- Awa, sazlap beremiz.\n🔹"
            " **Saytqa kepillik bar ma?**\n- Awa, 1 jıl dawamında texnikalıq"
            " járdem biypul."
        ),
        "ask_name": "Atıńızdı kiritin':",
        "ask_phone": (
            "Telefon nomerińizdi jiberin' (mısalı: +998 90 123 45 67):"
        ),
        "ask_details": (
            "Qanday web-qollanba yamasa proekt kerek ekenligin jazıp"
            " qaldırın':"
        ),
        "order_success": (
            "✅ Zakazınız qabıllandı! Tez arada adminlerimiz siz benen"
            " baylanısadı."
        ),
        "admin_notify": (
            "🔔 **Taza zakaz!**\n\n👤 **Mijoz:** {name}\n📞 **Telefon:**"
            " {phone}\n💬 **Proekt haqqında:** {details}\n🔗 **Profil:**"
            " [{username}](tg://user?id={user_id})\n🕒 **Waqıt:** {time}"
        ),
        "btn_services": "🌐 Web-qollanbalar hám Bahalar",
        "btn_faq": "❓ Soraw-Juwaplar",
        "btn_order": "🛒 Zakaz beriw",
        "btn_contact": "📞 Baylanıs",
        "btn_back": "🔙 Artqa",
    },
}

# Foydalanuvchilar tilini saqlash uchun oddiy dictionary
user_languages = {}


def get_kb(lang="uz"):
    t = TEXTS[lang]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t["btn_services"], callback_data="services"
                )
            ],
            [InlineKeyboardButton(text=t["btn_faq"], callback_data="faq")],
            [InlineKeyboardButton(text=t["btn_order"], callback_data="order")],
            [
                InlineKeyboardButton(
                    text=t["btn_contact"], callback_data="contact"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🇺🇿 O'zbekcha", callback_data="set_uz"
                ),
                InlineKeyboardButton(
                    text="🇰🇷 Qaraqalpaqsha", callback_data="set_kaa"
                ),
            ],
        ]
    )


# --- START ---
@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    lang = user_languages.get(user_id, "uz")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🇺🇿 O'zbekcha", callback_data="set_uz"
                ),
                InlineKeyboardButton(
                    text="🇰🇷 Qaraqalpaqsha", callback_data="set_kaa"
                ),
            ]
        ]
    )
    await message.answer(TEXTS[lang]["welcome"], reply_markup=keyboard)


@router.callback_query(F.data.startswith("set_"))
async def set_language(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = callback.data.split("_")[1]
    user_languages[user_id] = lang
    await callback.message.edit_text(
        TEXTS[lang]["choose_lang"], reply_markup=get_kb(lang)
    )
    await callback.answer()


# --- MENYU TUGMALARI ---
@router.callback_query(F.data == "services")
async def show_services(callback: CallbackQuery):
    lang = user_languages.get(callback.from_user.id, "uz")
    await callback.message.edit_text(
        TEXTS[lang]["services"],
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=TEXTS[lang]["btn_back"], callback_data="back_home"
                    )
                ]
            ]
        ),
        parse_mode=ParseMode.MARKDOWN,
    )


@router.callback_query(F.data == "faq")
async def show_faq(callback: CallbackQuery):
    lang = user_languages.get(callback.from_user.id, "uz")
    await callback.message.edit_text(
        TEXTS[lang]["faq"],
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=TEXTS[lang]["btn_back"], callback_data="back_home"
                    )
                ]
            ]
        ),
        parse_mode=ParseMode.MARKDOWN,
    )


@router.callback_query(F.data == "contact")
async def show_contact(callback: CallbackQuery):
    lang = user_languages.get(callback.from_user.id, "uz")
    text = (
        "📞 Admin bilan bog'lanish: @SizningUsername"
        if lang == "uz"
        else "📞 Admin menen baylanıs: @SizningUsername"
    )
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=TEXTS[lang]["btn_back"], callback_data="back_home"
                    )
                ]
            ]
        ),
    )


@router.callback_query(F.data == "back_home")
async def back_home(callback: CallbackQuery):
    lang = user_languages.get(callback.from_user.id, "uz")
    await callback.message.edit_text(TEXTS[lang]["menu"], reply_markup=get_kb(lang))


# --- BUYURTMA BERISH JARAYONI (FSM) ---
@router.callback_query(F.data == "order")
async def start_order(callback: CallbackQuery, state: FSMContext):
    lang = user_languages.get(callback.from_user.id, "uz")
    await state.set_state(OrderState.waiting_for_name)
    await callback.message.answer(TEXTS[lang]["ask_name"])
    await callback.answer()


@router.message(OrderState.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    lang = user_languages.get(message.from_user.id, "uz")
    await state.update_data(name=message.text)
    await state.set_state(OrderState.waiting_for_phone)
    await message.answer(TEXTS[lang]["ask_phone"])


@router.message(OrderState.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    lang = user_languages.get(message.from_user.id, "uz")
    await state.update_data(phone=message.text)
    await state.set_state(OrderState.waiting_for_details)
    await message.answer(TEXTS[lang]["ask_details"])


@router.message(OrderState.waiting_for_details)
async def process_details(message: Message, state: FSMContext, bot: Bot):
    lang = user_languages.get(message.from_user.id, "uz")
    data = await state.get_data()

    name = data.get("name")
    phone = data.get("phone")
    details = message.text
    user_id = message.from_user.id
    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else "Username yo'q"
    )

    # Vaqt va soatni aniqlash
    import datetime

    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Mijozga tasdiqlash xabari
    await message.answer(TEXTS[lang]["order_success"], reply_markup=get_kb(lang))

    # Adminga xabar yuborish (vaqti, lickasi va yozishmalari bilan)
    admin_text = TEXTS[lang]["admin_notify"].format(
        name=name,
        phone=phone,
        details=details,
        username=username,
        user_id=user_id,
        time=current_time,
    )

    try:
        await bot.send_message(
            chat_id=ADMIN_ID, text=admin_text, parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logging.error(f"Adminga yuborishda xatolik: {e}")

    await state.clear()


# --- BOTNI ISHGA TUSHIRISH ---
async def main():
    bot = Bot(token=TOKEN)
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
