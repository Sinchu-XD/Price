from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio

API_ID = 25024171
API_HASH = "7e709c0f5a2b8ed7d5f90a48219cffd3"
BOT_TOKEN = "7653924933:AAGQNauT14_MHCN1qdOu-KcqvvyKj7irSG0"

app = Client("DeleteAllBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Replace with your Telegram user ID or list of SUDO users
SUDO_USERS = [7862043458, 8091116698]  
BOT_USERNAME = ""

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

async def startup():
    global BOT_USERNAME
    async with app:
        bot_user = await app.get_me()
        BOT_USERNAME = f"@{bot_user.username}" if bot_user.username else bot_user.first_name
        print(f"✅ Bot started as {BOT_USERNAME}")
    
    
app.run()


