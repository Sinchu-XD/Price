import asyncio
import aiohttp
import logging
import os
from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup

# Setup virtual environment (only if running standalone)
if not os.path.exists("venv"):
    print("📦 Setting up virtual environment...")
    os.system("python3 -m venv venv")
    os.system("source venv/bin/activate && pip install pyrogram tgcrypto aiohttp")

# ================= CONFIG =================
API_ID = 25024171
API_HASH = "7e709c0f5a2b8ed7d5f90a48219cffd3"
BOT_TOKEN = "7653924933:AAGQNauT14_MHCN1qdOu-KcqvvyKj7irSG0"
SMS_API_KEY = "bdf4bff721f95c820f40c6A3d8076f45"

RUB_TO_INR = 0.90
RUB_TO_USD = 0.011

TARGET_SERVICES = {
    "Telegram": "tg",
    "WhatsApp": "wa"
}

# ================ BOT SETUP =================
app = Client("otp_price_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ============== START COMMAND ==============
@app.on_message(filters.command("start"))
async def start_cmd(_, message: Message):
    keyboard = ReplyKeyboardMarkup([["Telegram", "WhatsApp"]], resize_keyboard=True, one_time_keyboard=True)
    await message.reply_text(
        "👋 Welcome to the SMS-Activate OTP Bot!\nChoose a service to view all country prices in ₹ and $",
        reply_markup=keyboard
    )

# ========== SERVICE PRICE FETCHER ==========
@app.on_message(filters.text & filters.regex("^(Telegram|WhatsApp)$"))
async def fetch_prices(_, message: Message):
    service_name = message.text
    service_key = TARGET_SERVICES.get(service_name)

    await message.reply("⏳ Fetching full price list...")

    prices_url = f"https://api.sms-activate.org/stubs/handler_api.php?api_key={SMS_API_KEY}&action=getPrices"
    countries_url = f"https://api.sms-activate.org/stubs/handler_api.php?api_key={SMS_API_KEY}&action=getCountries"

    try:
        async with aiohttp.ClientSession() as session:
            # Get raw country list (text format)
            async with session.get(countries_url) as country_resp:
                country_text = await country_resp.text()
            country_map = {}
            for line in country_text.strip().splitlines():
                parts = line.strip().split(":")
                if len(parts) == 3:
                    code, _, name = parts
                    country_map[code] = name

            # Get prices (JSON)
            async with session.get(prices_url) as price_resp:
                price_data = await price_resp.json()

        result = f"💰 {service_name} OTP Prices (All Countries)\n\n"
        for country_code, country_name in country_map.items():
            service_data = price_data.get(str(country_code), {}).get(service_key)
            if service_data and "cost" in service_data:
                rub = service_data["cost"]
                inr = round(rub * RUB_TO_INR, 2)
                usd = round(rub * RUB_TO_USD, 3)
                result += f"🌍 **{country_name}**: ₹ {inr} / $ {usd}\n\n"

        if len(result) > 4096:
            result = result[:4090] + "..."

        await message.reply(result)

    except Exception as e:
        await message.reply(f"⚠️ Error occurred:\n<code>{e}</code>")

# ============== MAIN ==============
if __name__ == "__main__":
    print("🚀 Bot is starting...")
    app.run()
