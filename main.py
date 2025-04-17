import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils.executor import start_webhook
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CALORIEMAMA_API_KEY = os.getenv("CALORIE_API_KEY")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{os.getenv('WEBHOOK_BASE')}{WEBHOOK_PATH}"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.environ.get("PORT", 10000))

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(content_types=["photo"])
async def handle_photo(message: Message):
    await message.reply("🔍 Аналізую страву...")

    photo = message.photo[-1]
    photo_file = await photo.download(destination=BytesIO())
    photo_file.seek(0)

    # Відкриваємо зображення та змінюємо розмір до 544x544
    try:
        image = Image.open(photo_file)
        image = image.convert("RGB")
        image = image.resize((544, 544))
        image_bytes = BytesIO()
        image.save(image_bytes, format='JPEG')
        image_bytes.seek(0)
    except Exception as e:
        await message.reply(f"⚠️ Помилка при обробці зображення: {str(e)}")
        return

    # Відправляємо запит до API
    try:
        response = requests.post(
            f"https://api-2445582032290.production.gw.apicast.io/v1/foodrecognition?user_key={CALORIEMAMA_API_KEY}",
            files={"media": ("photo.jpg", image_bytes, "image/jpeg")}
        )
    except Exception as e:
        await message.reply(f"⚠️ Помилка при з'єднанні з API: {str(e)}")
        return

    if response.status_code != 200:
        await message.reply(f"❌ API помилка: {response.status_code}")
        return

    try:
        result = response.json()
        if not result["results"]:
            await message.reply("⚠️ Не вдалося розпізнати страву.")
            return

        item = result["results"][0]["items"][0]
        name = item["name"]
        nutrients = item["nutrition"]
        kcal = round(nutrients.get("calories", 0))
        protein = round(nutrients.get("protein", 0) * 1000, 1)  # Переводимо з кг в г
        fat = round(nutrients.get("totalFat", 0) * 1000, 1)
        carbs = round(nutrients.get("totalCarbs", 0) * 1000, 1)

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
