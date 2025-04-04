import asyncio
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup

API_ID = 25024171
API_HASH = "7e709c0f5a2b8ed7d5f90a48219cffd3"
BOT_TOKEN = "7857026606:AAGsLVPXUgPzwNpAeVeo6Fnu7tXE_Nf-uu0"
TIGER_API_KEY = "Mo5qglhUmAd7tWpX65IAX5PB6F1k5vmV"

app = Client("TigerSMSBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

API_BASE = f"https://api.tiger-sms.com/stubs/handler_api.php?api_key={TIGER_API_KEY}"

@app.on_message(filters.command("start"))
async def start_command(_, message: Message):
    keyboard = ReplyKeyboardMarkup(
        [
            ["📊 Balance", "📞 Get Number"],
            ["📬 Get Code", "🔄 Change Status"],
            ["💸 Prices", "🧾 Services"],
            ["🌎 Countries", "📦 Availability"]
        ],
        resize_keyboard=True
    )
    await message.reply("👋 Welcome to Tiger OTP Bot!\nChoose an action below:", reply_markup=keyboard)

@app.on_message(filters.regex("(?i)^📊 Balance$"))
async def get_balance(_, message: Message):
    url = f"{API_BASE}&action=getBalance"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            text = await resp.text()
    await message.reply(f"💰 Balance: {text}")

@app.on_message(filters.regex("(?i)^🧾 Services$"))
async def get_services(_, message: Message):
    url = f"{API_BASE}&action=getServices"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            text = await resp.text()

    try:
        services = dict(line.split(":") for line in text.strip().split("\n"))
    except Exception:
        return await message.reply(f"⚠️ Error parsing response:\n{text}")

    result = "🧾 Available Services:\n\n"
    for code, name in services.items():
        result += f"{code} - {name}\n"
    await message.reply(result)

@app.on_message(filters.regex("(?i)^🌎 Countries$"))
async def get_countries(_, message: Message):
    url = f"{API_BASE}&action=getCountries"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            text = await resp.text()

    try:
        countries = dict(line.split(":") for line in text.strip().split("\n"))
    except Exception:
        await message.reply(f"❌ Could not parse response:\n{text}")
        return

    result = "🌍 Available Countries:\n\n"
    for code, name in countries.items():
        result += f"{code} - {name}\n"

    await message.reply(result)

@app.on_message(filters.regex("(?i)^💸 Prices$"))
async def get_prices(_, message: Message):
    url = f"{API_BASE}&action=getPrices"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            text = await resp.text()

    try:
        prices = eval(text)
    except Exception:
        return await message.reply(f"❌ Could not parse prices:\n{text}")

    result = "💸 Prices:\n\n"
    for country, data in prices.items():
        result += f"🌍 Country {country}:\n"
        for service, info in data.items():
            cost = info.get("cost", "N/A")
            count = info.get("count", 0)
            result += f"  {service} → {cost}₽ ({count} available)\n"
    await message.reply(result[:4090] + "..." if len(result) > 4090 else result)

@app.on_message(filters.regex("(?i)^📞 Get Number$"))
async def get_number(_, message: Message):
    await message.reply("Send service code (e.g., *tg* for Telegram):")

@app.on_message(filters.text & ~filters.command(["start"]))
async def service_input(_, msg: Message):
    service = msg.text.lower()
    url = f"{API_BASE}&action=getNumber&service={service}&country=0"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            response = await resp.text()
    await msg.reply(f"📞 Response: {response}")

@app.on_message(filters.regex("(?i)^📬 Get Code$"))
async def get_code(_, message: Message):
    await message.reply("Send activation ID:")

@app.on_message(filters.text & ~filters.command(["start"]))
async def code_input(_, msg: Message):
    activation_id = msg.text.strip()
    url = f"{API_BASE}&action=getStatus&id={activation_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            text = await resp.text()
    await msg.reply(f"📬 Status: {text}")

@app.on_message(filters.regex("(?i)^🔄 Change Status$"))
async def change_status(_, message: Message):
    await message.reply("Send ID and Status like: `123456 6`\n\nStatus:\n- 1: Ready\n- 3: Cancel\n- 6: Complete")

@app.on_message(filters.text & ~filters.command(["start"]))
async def status_input(_, msg: Message):
    parts = msg.text.strip().split()
    if len(parts) != 2:
        return await msg.reply("❌ Invalid format. Use: `id status_code`")
    id_, status = parts
    url = f"{API_BASE}&action=setStatus&id={id_}&status={status}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            text = await resp.text()
    await msg.reply(f"✅ Status Changed: {text}")

@app.on_message(filters.regex("(?i)^📦 Availability$"))
async def get_availability(_, message: Message):
    url = f"{API_BASE}&action=getNumbersStatus"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            stats_text = await resp.text()

    lines = stats_text.strip().splitlines()

    for line in lines:
        parts = line.split(":")
        country = parts[0]
        providers = parts[1:]

        response = f"📍 *{country}*\n"

        for i in range(0, len(providers), 2):
            try:
                provider_name = providers[i]
                count = providers[i + 1]
                response += f"  ┗ 📦 *{provider_name}*: `{count}`\n"
            except IndexError:
                continue

        await message.reply(response, parse_mode="Markdown")

if __name__ == "__main__":
    print("🚀 Starting Tiger OTP Bot...")
    app.run()
