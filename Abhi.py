import os
import subprocess
import sys

# ------------------- Setup Virtual Environment & Install Requirements ------------------- #
venv_dir = "venv"

if not os.path.exists(venv_dir):
    print("📦 Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", venv_dir])

pip_path = os.path.join(venv_dir, "bin", "pip")
python_path = os.path.join(venv_dir, "bin", "python")

print("🔧 Installing required packages...")
subprocess.run([pip_path, "install", "--upgrade", "pip"])
subprocess.run([pip_path, "install", "pyrogram", "tgcrypto", "aiohttp"])

# ------------------- Bot Code Starts ------------------- #
import asyncio
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup

# Replace these with your credentials
API_ID = 25024171  # ⚠️ Your API ID
API_HASH = "7e709c0f5a2b8ed7d5f90a48219cffd3"  # ⚠️ Your API Hash
BOT_TOKEN = "7653924933:AAGQNauT14_MHCN1qdOu-KcqvvyKj7irSG0"  # ⚠️ Your Bot Token
SMS_API_KEY = "bdf4bff721f95c820f40c6A3d8076f45"  # ⚠️ Your SMS-Activate API Key

# Supported services
TARGET_SERVICES = {
    "Telegram": "tg",
    "WhatsApp": "wa"
}

# Create a keyboard layout
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        ["Telegram", "WhatsApp"]
    ],
    resize_keyboard=True
)

app = Client("otp_price_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


@app.on_message(filters.command("start"))
async def start_handler(_, message: Message):
    await message.reply(
        "👋 Welcome! Use the /prices command to check OTP rates.\n\nChoose a service:",
        reply_markup=keyboard
    )


@app.on_message(filters.command("prices"))
async def prices_handler(_, message: Message):
    await message.reply("🔽 Choose a service below to view OTP prices:", reply_markup=keyboard)


@app.on_message(filters.text & filters.regex("^(Telegram|WhatsApp)$"))
async def fetch_prices(_, message: Message):
    service_name = message.text
    service_key = TARGET_SERVICES.get(service_name)

    await message.reply("⏳ Fetching prices...")

    url = f"https://api.sms-activate.org/stubs/handler_api.php?api_key={SMS_API_KEY}&action=getPrices"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await message.reply("❌ Failed to fetch prices from SMS-Activate API.")
                    return
                data = await resp.json()

        result = f"💰 {service_name} OTP Prices:\n\n"
        for country_code, services in data.items():
            if service_key in services:
                cost = services[service_key].get("cost", "N/A")
                count = services[service_key].get("count", 0)
                if count > 0:
                    result += f"🌍 Country {country_code}: {cost}₽ | Available: {count}\n"

        if len(result) > 4096:
            result = result[:4090] + "..."  # Trim long responses

        await message.reply(result)

    except Exception as e:
        await message.reply(f"⚠️ Error: {e}")


if __name__ == "__main__":
    print("🚀 Starting OTP Price Bot...")
    app.run()
                  
