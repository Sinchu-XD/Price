import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = 6067591
API_HASH = "94e17044c2393f43fda31d3afe77b26b"
BOT_TOKEN = "7726535663:AAGalIgbZaBHRGhbAc0fdWmSithGcRjdEzg"

import logging

logging.basicConfig(level=logging.DEBUG)

bot = Client("TesthBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message: Message):
    await message.reply("✅ Bot is alive and working!")

async def main():
    await bot.start()
    print("Bot is running...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
