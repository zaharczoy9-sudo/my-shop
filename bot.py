import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, WebAppInfo
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import init_db, get_products, add_order

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(m: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="🛍 Открыть каталог", web_app=WebAppInfo(url="/shop"))
    await m.answer("Добро пожаловать в магазин! 👇", reply_markup=kb.as_markup())

@dp.message(Command("admin"))
async def admin(m: Message):
    if m.from_user.id not in ADMIN_IDS:
        return await m.answer("⛔ Нет доступа")
    kb = InlineKeyboardBuilder()
    kb.button(text="⚙️ Админ-панель", web_app=WebAppInfo(url="https://ваш-домен.com/admin"))
    await m.answer("Панель управления:", reply_markup=kb.as_markup())

# Обработчик данных из Mini App (когда клиент нажал "Купить")
@dp.message(F.web_app_data)
async def on_buy(m: Message):
    data = m.web_app_data.data  # придёт product_id
    try:
        pid = int(data)
        p = get_products()[0]  # в реальности — get_product(pid)
        add_order(m.from_user.id, m.from_user.username or "", pid)
        await m.answer(f"✅ Заказ принят! Товар #{pid}. Мы свяжемся с вами.")
    except Exception as e:
        await m.answer("Ошибка заказа")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
