import asyncio
import json
import aiohttp
import logging
import os
from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup

# ✅ Setup Virtual Environment and install dependencies
if not os.path.exists("venv"):
    print("📦 Setting up virtual environment...")
    os.system("python3 -m venv venv")
    os.system("source venv/bin/activate && pip install pyrogram tgcrypto aiohttp")

# ✅ Logging
logging.basicConfig(level=logging.INFO)

# ========== CONFIG ==========
API_ID = 25024171
API_HASH = "7e709c0f5a2b8ed7d5f90a48219cffd3"
BOT_TOKEN = "7653924933:AAGQNauT14_MHCN1qdOu-KcqvvyKj7irSG0"
SMS_API_KEY = "bdf4bff721f95c820f40c6A3d8076f45"

TARGET_SERVICES = {
    "Telegram": "tg",
    "WhatsApp": "wa"
}

# ✅ Currency conversion rates (update if needed)
RUB_TO_USD = 0.011
RUB_TO_INR = 0.83

# ✅ Pyrogram client
app = Client(
    "otp_price_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ========== /start command ==========
@app.on_message(filters.command("start"))
async def start_cmd(_, message: Message):
    keyboard = ReplyKeyboardMarkup(
        [["Telegram", "WhatsApp"]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.reply_text(
        "👋 Welcome to the SMS-Activate OTP Bot!\nChoose a service below to check OTP prices:",
        reply_markup=keyboard
    )

# ========== Price Fetcher ==========
@app.on_message(filters.text & filters.regex("^(Telegram|WhatsApp)$"))
async def fetch_prices(_, message: Message):
    service_name = message.text
    service_key = TARGET_SERVICES.get(service_name)
    await message.reply("⏳ Fetching prices and countries...")

    prices_url = f"https://api.sms-activate.org/stubs/handler_api.php?api_key={SMS_API_KEY}&action=getPrices"
    countries_url = f"https://api.sms-activate.org/stubs/handler_api.php?api_key={SMS_API_KEY}&action=getCountries"

    try:
        async with aiohttp.ClientSession() as session:
            # Fetch prices
            async with session.get(prices_url) as r1:
                prices_data = json.loads(await r1.text())

            # Fetch country names
            async with session.get(countries_url) as r2:
                countries_data = json.loads(await r2.text())

        result = f"📲 {service_name} OTP Prices:\n\n"
        for country_code, services in prices_data.items():
            if service_key in services:
                cost_rub = services[service_key].get("cost", 0)
                count = services[service_key].get("count", 0)

                if count > 0:
                    country_info = countries_data.get(country_code, {})
                    country_name = country_info.get("eng", f"Country {country_code}")
                    emoji = country_info.get("emoji", "🌍")

                    price_usd = round(cost_rub * RUB_TO_USD, 2)
                    price_inr = round(cost_rub * RUB_TO_INR, 2)

                    result += f"{emoji} {country_name}: ${price_usd} | ₹{price_inr} | Available: {count}\n"

        if len(result) > 4096:
            result = result[:4090] + "..."

        await message.reply(result)

    except Exception as e:
        await message.reply(f"⚠️ Error: {e}")

# ========== Run Bot ==========
if __name__ == "__main__":
    print("🚀 Bot is starting...")
    app.run()
