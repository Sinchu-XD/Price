import asyncio
import json
import aiohttp
import logging
import os
from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup

# Enable logging
logging.basicConfig(level=logging.INFO)

# ================= CONFIG =================
API_ID = 12345678  # replace with your Telegram API ID
API_HASH = "your_api_hash_here"  # replace with your Telegram API HASH
BOT_TOKEN = "your_bot_token_here"  # replace with your bot token
SMS_API_KEY = "your_sms_activate_api_key_here"  # replace with your SMS-Activate API key

# Target services (You can expand this dictionary)
TARGET_SERVICES = {
    "Telegram": "tg",
    "WhatsApp": "wa"
}

# ================ BOT SETUP =================
app = Client(
    "SMSActivateOTPBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ============== START COMMAND ==============
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

        result = f"💰 {service_name} OTP Prices:\n\n"
        for country_code, services in data.items():
            if service_key in services:
                cost = services[service_key].get("cost", "N/A")
                count = services[service_key].get("count", 0)
                if count > 0:
                    result += f"🌍 Country {country_code}: {cost}₽ | Available: {count}\n"

        if len(result) > 4096:
            result = result[:4090] + "..."

        await message.reply(result)

    except Exception as e:
        await message.reply(f"⚠️ Error: {e}")

# ============== MAIN ==============
if __name__ == "__main__":
    # Setup virtual environment & install dependencies (if needed)
    if not os.path.exists("venv"):
        print("📦 Setting up virtual environment...")
        os.system("python3 -m venv venv")
        os.system("source venv/bin/activate && pip install pyrogram tgcrypto aiohttp")

    print("🚀 Bot is starting...")
    app.run()
