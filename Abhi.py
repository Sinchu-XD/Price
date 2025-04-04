import asyncio
import aiohttp
import logging
import os
import json
from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup

# Setup virtual environment (only if running standalone)
logging.basicConfig(level=logging.INFO)

# ================= CONFIG =================
API_ID = 25024171  # ⚠️ Your API ID
API_HASH = "7e709c0f5a2b8ed7d5f90a48219cffd3"  # ⚠️ Your API Hash
BOT_TOKEN = "7653924933:AAGQNauT14_MHCN1qdOu-KcqvvyKj7irSG0"  # ⚠️ Your Bot Token
SMS_API_KEY = "bdf4bff721f95c820f40c6A3d8076f45"  # ⚠️ Your SMS-Activate API Key

# Target services (You can expand this dictionary)
TARGET_SERVICES = {
    "Telegram": "tg",
    "WhatsApp": "wa"
}

# Currency conversion rates (Fixed for simplicity)
RUB_TO_USD = 0.011
RUB_TO_INR = 0.91

# ================ BOT SETUP =================
app = Client(
    "otp_price_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ============== START COMMAND ==============
@app.on_message(filters.command("start"))
async def start_cmd(_, message: Message):
    keyboard = ReplyKeyboardMarkup(
@@ -53,35 +51,41 @@ async def start_cmd(_, message: Message):
        reply_markup=keyboard
    )

# ========== SERVICE PRICE FETCHER ==========
@app.on_message(filters.text & filters.regex("^(Telegram|WhatsApp)$"))
async def fetch_prices(_, message: Message):
    service_name = message.text
    service_key = TARGET_SERVICES.get(service_name)


    await message.reply("⏳ Fetching prices...")

    url = f"https://api.sms-activate.org/stubs/handler_api.php?api_key={SMS_API_KEY}&action=getPrices"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                text_data = await resp.text()
                try:
                    data = json.loads(text_data)
                except json.JSONDecodeError:
                    await message.reply("❌ Failed to decode response from SMS-Activate API.")
                    return

        result = f"💰 {service_name} OTP Prices (converted):\n\n"
        for country_code, services in data.items():
            if service_key in services:
                cost = services[service_key].get("cost", 0)
                count = services[service_key].get("count", 0)

                if count > 0:
                    usd = round(cost * RUB_TO_USD, 3)
                    inr = round(cost * RUB_TO_INR, 2)
                    result += f"🌍 {country_code}: {cost}₽ | ${usd} | ₹{inr} | Available: {count}\n"






        if len(result) > 4096:
            result = result[:4090] + "..."
@@ -91,7 +95,7 @@ async def fetch_prices(_, message: Message):
    except Exception as e:
        await message.reply(f"⚠️ Error: {e}")

# ============== MAIN ==============
if __name__ == "__main__":
    print("🚀 Bot is starting...")
    app.run()
