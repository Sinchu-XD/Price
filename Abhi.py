import os
import aiohttp
import asyncio
import json
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup

# ✅ Virtual Environment Setup (Optional)
if not os.path.exists("venv"):
    print("📦 Setting up virtual environment...")
    os.system("python3 -m venv venv")
    os.system("source venv/bin/activate && pip install pyrogram tgcrypto aiohttp")

# ✅ Logging
logging.basicConfig(level=logging.INFO)

# === CONFIG ===
API_ID = 123456  # Replace with your Telegram API ID
API_HASH = "your_api_hash"  # Replace with your Telegram API HASH
BOT_TOKEN = "your_bot_token"  # Replace with your Telegram Bot Token
SMS_API_KEY = "your_sms_activate_api_key"  # Replace with your SMS-Activate API Key

RUB_TO_USD = 0.011
RUB_TO_INR = 0.83

TARGET_SERVICES = {
    "Telegram": "tg",
    "WhatsApp": "wa"
}

app = Client("otp_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# === START ===
@app.on_message(filters.command("start"))
async def start(_, message: Message):
    keyboard = ReplyKeyboardMarkup([["📲 Buy Telegram OTP", "📲 Buy WhatsApp OTP"]], resize_keyboard=True)
    await message.reply("👋 Welcome to OTP Bot!\nSelect a service to get OTP:", reply_markup=keyboard)

# === FETCH PRICES ===
@app.on_message(filters.text & filters.regex("^📲 Buy (Telegram|WhatsApp) OTP$"))
async def buy_otp(_, message: Message):
    service_name = message.text.split(" ")[-2]
    service_code = TARGET_SERVICES.get(service_name)

    prices_url = f"https://api.sms-activate.org/stubs/handler_api.php?api_key={SMS_API_KEY}&action=getPrices"
    countries_url = f"https://api.sms-activate.org/stubs/handler_api.php?api_key={SMS_API_KEY}&action=getCountries"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(prices_url) as p:
                prices = json.loads(await p.text())
            async with session.get(countries_url) as c:
                countries = json.loads(await c.text())

        text = f"📦 {service_name} OTP Price List:\n\n"
        for code, info in prices.items():
            if service_code in info:
                country_name = countries.get(code, {}).get("eng", f"Country {code}")
                emoji = countries.get(code, {}).get("emoji", "🌍")
                rub = info[service_code]["cost"]
                usd = round(rub * RUB_TO_USD, 2)
                inr = round(rub * RUB_TO_INR, 2)
                text += f"{emoji} {country_name}: ${usd} | ₹{inr}\n"

        if len(text) > 4096:
            text = text[:4090] + "..."

        await message.reply(text)
    except Exception as e:
        await message.reply(f"⚠️ Error occurred:\n{e}")

# === Request OTP Number ===
@app.on_message(filters.command("getotp"))
async def get_otp(_, message: Message):
    args = message.text.split()
    if len(args) != 3:
        await message.reply("Usage: /getotp <country_code> <service_name>\nExample: /getotp 6 tg")
        return

    country_code, service_code = args[1], args[2]

    url = f"https://api.sms-activate.org/stubs/handler_api.php?api_key={SMS_API_KEY}&action=getNumber&service={service_code}&country={country_code}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                result = await resp.text()
                if "ACCESS_NUMBER" in result:
                    parts = result.strip().split(":")
                    activation_id = parts[1]
                    number = parts[2]
                    await message.reply(f"✅ OTP Number: {number}\nActivation ID: `{activation_id}`\nUse /getcode {activation_id} to get OTP.")
                else:
                    await message.reply(f"❌ Error: {result}")
    except Exception as e:
        await message.reply(f"⚠️ Error: {e}")

# === Check OTP Code ===
@app.on_message(filters.command("getcode"))
async def get_code(_, message: Message):
    args = message.text.split()
    if len(args) != 2:
        await message.reply("Usage: /getcode <activation_id>")
        return

    activation_id = args[1]
    url = f"https://api.sms-activate.org/stubs/handler_api.php?api_key={SMS_API_KEY}&action=getStatus&id={activation_id}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                result = await resp.text()
                if "STATUS_OK" in result:
                    code = result.split(":")[1]
                    await message.reply(f"📩 OTP Code: {code}")
                else:
                    await message.reply(f"🔁 Waiting for code... Status: {result}")
    except Exception as e:
        await message.reply(f"⚠️ Error: {e}")

# === MAIN ===
if __name__ == "__main__":
    print("🚀 Starting OTP Bot...")
    app.run()
