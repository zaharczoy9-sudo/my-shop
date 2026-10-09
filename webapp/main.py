import os
import asyncio
import threading
from database import init_db
from admin import app
from bot import dp, bot

async def run_bot():
    await dp.start_polling(bot)

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

if __name__ == "__main__":
    init_db()
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(run_bot())
