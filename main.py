import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils.executor import start_webhook
from dotenv import load_dotenv
from io import BytesIO

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CALORIEMAMA_API_KEY = os.getenv("CALORIE_API_KEY")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{os.getenv('WEBHOOK_BASE')}{WEBHOOK_PATH}"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.environ.get("PORT", 8000))

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(content_types=["photo"])
async def handle_photo(message: Message):
    await message.reply("🔍 Аналізую страву...")

    photo = message.photo[-1]
    photo_bytes = await photo.download(destination=BytesIO())

    response = requests.post(
        "https://api.caloriemama.ai/food-recognition/v1/recognize",
        headers={"X-API-KEY": CALORIEMAMA_API_KEY},
        files={"image": ("photo.jpg", photo_bytes.getvalue(), "image/jpeg")}
    )

    if response.status_code != 200:
        await message.reply(f"❌ API помилка: {response.status_code}")
        return

    try:
        result = response.json()
        item = result["results"][0]
        name = item["name"]
        nutrients = item["nutrients"]
        kcal = round(nutrients.get("calories", 0))
        protein = round(nutrients.get("protein_g", 0), 1)
        fat = round(nutrients.get("fat_total_g", 0), 1)
        carbs = round(nutrients.get("carbohydrates_total_g", 0), 1)

        reply = (
            f"🍽 Страва: {name}\n"
            f"🔥 Калорії: {kcal} ккал\n"
            f"💪 Білки: {protein} г\n"
            f"🥑 Жири: {fat} г\n"
            f"🍞 Вуглеводи: {carbs} г"
        )
        await message.reply(reply)
    except Exception as e:
        await message.reply(f"⚠️ Помилка при обробці відповіді: {str(e)}")

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dp):
    await bot.delete_webhook()

if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
