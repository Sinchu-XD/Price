import re
import time
import requests
from telethon import TelegramClient, events

API_ID = 2184829
API_HASH = "6930b92388baabff4cb4a1d377085035"
TOKEN = "7722172461:AAHTAklgwEshuC4kAhj3FulHim6gCwj6Bfc"

bot = TelegramClient("winggoo", API_ID, API_HASH).start(bot_token=TOKEN)

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
    red_count = 0
    green_count = 0
    try:
        json_data = {
            'pageSize': 10,
            'pageNo': 1,
            'typeId': 1,
            'language': 0,
            'random': 'rand123',
            'signature': 'sig456',
            'timestamp': time.time()
        }
        response = requests.post('https://api.fastpay92.com/api/webapi/GetNoaverageEmerdList', json=json_data)
        game = response.json()['data']['list']
        pd = int(game[0]['issueNumber'])
        period_id = pd + 1
        number = int(game[0]['number'])

        if number > 6:
            red_count += 3
        else:
            green_count += 9

        if red_count > green_count:
            play = 'SMALL'
        else:
            play = 'BIG'

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
            'typeId': 1,
            'language': 0,
            'random': 'rand123',
            'signature': 'sig456',
            'timestamp': time.time()
        }
        response = requests.post('https://api.fastpay92.com/api/webapi/GetNoaverageEmerdList', json=json_data)
        game = response.json()['data']['list']
        number = int(game[1]['number'])

        if number > 6:
            red_count += 3
        else:
            green_count += 9

        return 'BIG' if red_count > green_count else 'SMALL'
    except Exception as e:
        print("Checker Error:", e)
        return None

@bot.on(events.NewMessage(pattern="/tcstart"))
async def start_prediction(e):
    global preds
    preds = True
    await e.reply("🔮 Starting TC Lottery Predictions...")
    
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
                    f"🎯 **WINGO 1MIN PREDICTION** 🎯\n\n"
                    f"**🆔 PERIOD ID:** `{period_id}`\n"
                    f"**📊 PREDICTION:** `{size}`\n"
                    f"**🧠 LAST RESULT:** `{last}`\n"
                    f"**💰 TIP:** Maintain fund upto Level 5"
                )

                print(message)
                oldMessage = await bot.send_file(e.chat_id, file="https://files.catbox.moe/6hq5j7.jpg", caption=message)
                old.append(oldMessage)
            time.sleep(2)
        except Exception as err:
            print("Loop Error:", err)

@bot.on(events.NewMessage(pattern="/tcstop"))
async def stop_prediction(e):
    global preds
    preds = False
    await e.reply("🛑 Stopped TC Lottery Predictions.")

print("✅ TC Prediction Bot Running!")
bot.run_until_disconnected()
                                        
