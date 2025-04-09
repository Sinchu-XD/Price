from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio

API_ID = 123456       # Replace with your API ID
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"

app = Client("DeleteAllBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Replace with your Telegram user ID or list of SUDO users
SUDO_USERS = [123456789]  

@app.on_message(filters.command("purgeall") & filters.user(SUDO_USERS))
async def purge_all_messages(client: Client, message: Message):
    chat_id = message.chat.id
    await message.reply("🧹 Starting purge...")

    deleted = 0
    async for msg in client.get_chat_history(chat_id):
        try:
            await client.delete_messages(chat_id, msg.message_id)
            deleted += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            print(f"Failed to delete {msg.message_id}: {e}")
            continue

    await message.reply(f"✅ Deleted {deleted} messages.")

app.run()
