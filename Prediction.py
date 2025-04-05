import re
import time
import requests
from telethon import TelegramClient, events

API_ID = 2184829
API_HASH = "6930b92388baabff4cb4a1d377085035"
TOKEN = "7653924933:AAGQNauT14_MHCN1qdOu-KcqvvyKj7irSG0"

bot = TelegramClient("wingoo_5min", API_ID, API_HASH).start(bot_token=TOKEN)

headers = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": "https://dmwin1.com",
    "Referer": "https://dmwin1.com",
    "User-Agent": "Mozilla/5.0"
}

predictionss = []
old = []
preds = False

def predictions():
    try:
        json_data = {
            'pageSize': 10,
            'pageNo': 1,
            'typeId': 2,  # Wingo 5MIN
            'language': 0,
            'random': 'rand123',
            'signature': 'sig456',
            'timestamp': time.time()
        }
        response = requests.post('https://api.fastpay92.com/api/webapi/GetNoaverageEmerdList', json=json_data)
        print("RAW RESPONSE:", response.text)  # 🐛 Debug print

        data = response.json()
        if "data" not in data:
            print("❌ API Response Missing 'data'")
            return None

        game = data['data']['list']
        pd = int(game[0]['issueNumber'])
        period_id = pd + 1
        number = int(game[0]['number'])

        play = 'SMALL' if number <= 6 else 'BIG'
        return f"Play- {period_id}: {play}"

    except Exception as e:
        print("Prediction Error:", e)
        return None

def checkerPrediction():
    red_count = 0
    green_count = 0
    try:
        json_data = {
            'pageSize': 10,
            'pageNo': 1,
            'typeId': 2,  # ✅ Wingo 5MIN Type ID
            'language': 0,
            'random': 'rand123',
            'signature': 'sig456',
            'timestamp': time.time()
        }
        response = requests.post('https://api.fastpay92.com/api/webapi/GetNoaverageEmerdList', json=json_data)
        game = response.json()['data']['list']
        number = int(game[1]['number'])

        return 'BIG' if number > 6 else 'SMALL'
    except Exception as e:
        print("Checker Error:", e)
        return None

@bot.on(events.NewMessage(pattern="/start"))
async def start_prediction(e):
    global preds
    preds = True
    await e.reply("🔮 Starting Wingo 5MIN Predictions...")

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
                predictionss.pop(0)
                predictionss.append(int(period_id))

                message = (
                    f"🎯 **WINGO 5MIN PREDICTION** 🎯\n\n"
                    f"**🆔 PERIOD ID:** `{period_id}`\n"
                    f"**📊 PREDICTION:** `{size}`\n"
                    f"**🧠 LAST RESULT:** `{last}`\n"
                    f"**💰 TIP:** Maintain fund upto Level 5"
                )

                print(message)
                oldMessage = await bot.send_file(
                    e.chat_id,
                    file="https://files.catbox.moe/6hq5j7.jpg",
                    caption=message
                )
                old.append(oldMessage)
            time.sleep(2)
        except Exception as err:
            print("Loop Error:", err)

@bot.on(events.NewMessage(pattern="/stop"))
async def stop_prediction(e):
    global preds
    preds = False
    await e.reply("🛑 Stopped Wingo 5MIN Predictions.")

print("✅ Wingo 5MIN Prediction Bot Running!")
bot.run_until_disconnected()
