from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, WebAppInfo
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import get_product, add_order
from config import BOT_TOKEN, ADMIN_IDS, APP_URL

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(m: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="🛍 Открыть каталог", web_app=WebAppInfo(url=f"{APP_URL}/shop"))
    await m.answer("Добро пожаловать в магазин! 👇", reply_markup=kb.as_markup())

@dp.message(Command("admin"))
async def admin_cmd(m: Message):
    if m.from_user.id not in ADMIN_IDS:
        return await m.answer("⛔ Нет доступа")
    kb = InlineKeyboardBuilder()
    kb.button(text="⚙️ Админ-панель", web_app=WebAppInfo(url=f"{APP_URL}/login"))
    await m.answer("Панель управления:", reply_markup=kb.as_markup())

@dp.message(F.web_app_data)
async def on_buy(m: Message):
    data = m.web_app_data.data
    try:
        pid = int(data)
        product = get_product(pid)
        if product:
            add_order(m.from_user.id, m.from_user.username or "", pid)
            await m.answer(f"✅ Заказ принят!\nТовар: {product['name']}\nМы свяжемся с вами.")
        else:
            await m.answer("❌ Товар не найден")
    except Exception:
        await m.answer("Ошибка при оформлении заказа")
