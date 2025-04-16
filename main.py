import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
from dotenv import load_dotenv
from io import BytesIO

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CALORIE_API_KEY = os.getenv("CALORIE_API_KEY")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(content_types=["photo"])
async def handle_photo(message: Message):
    await message.reply("🔍 Аналізую страву...")

    # беру останнє (найбільше) фото з повідомлення
    photo = message.photo[-1]
    photo_bytes = await photo.download(destination=BytesIO())

    # готуємо запит до CalorieMama
    headers = {
        "Content-Type": "application/octet-stream",
        "X-API-KEY": CALORIE_API_KEY,
    }

    response = requests.post(
        "https://api.caloriemama.ai/v1/food/recognize",
        headers=headers,
        data=photo_bytes.getvalue()
    )

    if response.status_code != 200:
        await message.reply(f"❌ API помилка: {response.status_code}")
        return

    try:
        result = response.json()
        item = result["results"][0]

        name = item["name"]
        nutrients = item["nutrients"]
        kcal     = round(nutrients.get("calories", 0))
        protein  = round(nutrients.get("protein_g", 0), 1)
        fat      = round(nutrients.get("fat_total_g", 0), 1)
        carbs    = round(nutrients.get("carbohydrates_total_g", 0), 1)

        reply = (
            f"🍽 Страва: {name}\n"
            f"🔥 Калорії: {kcal} ккал\n"
            f"💪 Білки: {protein} г\n"
            f"🥑 Жири: {fat} г\n"
            f"🍞 Вуглеводи: {carbs} г"
        )
        await message.reply(reply)

    except Exception as e:
        await message.reply(f"⚠️ Помилка при обробці відповіді: {e}")
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

    except Exception as e:
        await message.reply(f"⚠️ Помилка при обробці відповіді: {str(e)}")

if __name__ == "__main__":
    executor.start_polling(dp)
