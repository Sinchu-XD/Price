import re
import time
import secrets
import requests
from telethon import TelegramClient, events

API_ID = 2184829
API_HASH = "6930b92388baabff4cb4a1d377085035"
TOKEN = "7653924933:AAGQNauT14_MHCN1qdOu-KcqvvyKj7irSG0"

bot = TelegramClient("wingoo_5min", API_ID, API_HASH).start(bot_token=TOKEN)

predictionss = []
old = []
preds = False
CHAT_ID = None

def fetch_results():
    try:
        json_data = {
            'pageSize': 10,
            'pageNo': 1,
            'typeId': 2,
            'language': 0,
            'random': secrets.token_hex(16),
            'signature': 'sig456',
            'timestamp': time.time()
        }
        response = requests.post(
            'https://api.fastpay92.com/api/webapi/GetNoaverageEmerdList',
            json=json_data
        )
        data = response.json()
        if "data" not in data or "list" not in data["data"]:
            print(f"❌ API Response Missing 'data'\nRAW RESPONSE: {response.text}")
            return None
        return data["data"]["list"]
    except Exception as e:
        print("❌ Fetch Error:", e)
        return None

def predictions():
    try:
        results = fetch_results()
        if not results:
            return None

        last_10 = results[:10]
        big = sum(1 for res in last_10 if int(res["number"]) > 6)
        small = 10 - big
        size = "BIG" if big < small else "SMALL"

        period_id = int(results[0]['issueNumber'])
        return f"Play- {period_id}: {size}"
    except Exception as e:
        print("Prediction Error:", e)
        return None

def checkerPrediction():
    try:
        results = fetch_results()
        if not results:
            return "N/A"
        number = int(results[1]['number'])
        return 'BIG' if number > 6 else 'SMALL'
    except Exception as e:
        print("Checker Error:", e)
        return "N/A"

@bot.on(events.NewMessage(pattern=r"/start\s*(-?\d+)"))
async def start_prediction(e):
    global preds, CHAT_ID
    try:
        CHAT_ID = int(e.pattern_match.group(1))
        chat_entity = await bot.get_entity(CHAT_ID)
        chat_name = chat_entity.title if hasattr(chat_entity, "title") else chat_entity.username or str(CHAT_ID)

        preds = True
        await e.reply(f"🔮 Starting Wingo 5MIN Predictions in **{chat_name}**...")

        while preds:
            try:
                data = predictions()
                if not data:
                    continue
                matchp = re.search(r'Play-\s(\d+):', data)
                period_id = matchp.group(1)
                size = data.split(": ")[1]

                if len(predictionss) == 0:
                    predictionss.append(int(period_id))

                if int(period_id) not in predictionss:
                    last = checkerPrediction()
                    predictionss.clear()
                    predictionss.append(int(period_id))

                    message = (
                        f"🎯 **WINGO 5MIN PREDICTION** 🎯\n\n"
                        f"**🆔 PERIOD ID:** `{period_id}`\n"
                        f"**📊 PREDICTION:** `{size}`\n"
                        f"**🧠 LAST RESULT:** `{last}`\n"
                        f"**💰 TIP:** Maintain fund upto Level 5\n\n"
                        f"** If You Want SureShot Prediction Then**"
                        f"   **Contact**: @LookCyrus"
                    )

                    print(message)
                    await bot.send_file(
                        CHAT_ID,
                        file="https://files.catbox.moe/6hq5j7.jpg",
                        caption=message
                    )
                time.sleep(2)
            except Exception as err:
                print("Loop Error:", err)
    except Exception as err:
        await e.reply(f"❌ Error: {err}")

@bot.on(events.NewMessage(pattern="/stop"))
async def stop_prediction(e):
    global preds
    preds = False
    await e.reply("🛑 Stopped Wingo 5MIN Predictions.")

print("✅ Wingo 5MIN Prediction Bot Running!")
bot.run_until_disconnected()
