import asyncio
import uuid
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Prediction import app


UPI_ID = "yourname@upi"
UPI_GATEWAY_BASE_URL = "https://your-upi-api.com"
YOUR_SECRET = "secret_xyz"


def create_upi_request(amount, user_id):
    order_id = str(uuid.uuid4())
    payload = {
        "order_id": order_id,
        "amount": amount,
        "upi_id": UPI_ID,
        "secret": YOUR_SECRET,
        "user_id": user_id,
        "note": f"Payment for user {user_id}"
    }
    res = requests.post(f"{UPI_GATEWAY_BASE_URL}/create_payment", json=payload)
    data = res.json()

    if data.get("status") == "success":
        return order_id, data.get("upi_link", ""), data.get("qr_code")
    return None, None, None

def check_payment(order_id):
    res = requests.get(f"{UPI_GATEWAY_BASE_URL}/check_payment?order_id={order_id}").json()
    return res.get("status") == "success"

@app.on_message(filters.command("pay"))
async def start_payment(client, message):
    args = message.text.split()
    if len(args) != 2:
        await message.reply("❌ Usage: `/pay <amount>`", quote=True)
        return

    try:
        amount = float(args[1])
    except ValueError:
        await message.reply("❌ Invalid amount format.", quote=True)
        return

    user_id = message.from_user.id
    order_id, upi_link, qr_code = create_upi_request(amount, user_id)

    if not order_id:
        await message.reply("❌ Failed to create UPI request. Try again.", quote=True)
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Pay Now", url=upi_link or "https://paytm.com")]
    ])

    msg = await message.reply_photo(
        photo=qr_code or "https://via.placeholder.com/300.png?text=Scan+QR",
        caption=(
            f"💰 *Payment Request*\n"
            f"• Amount: ₹{amount}\n"
            f"• UPI ID: `{UPI_ID}`\n"
            f"• Order ID: `{order_id}`\n\n"
            f"🔄 Waiting for payment confirmation..."
        ),
        reply_markup=keyboard,
        parse_mode="markdown"
    )

    for _ in range(30):  # Retry for 2.5 minutes
        await asyncio.sleep(5)
        if check_payment(order_id):
            await msg.edit_caption(
                f"✅ *Payment Successful!*\n"
                f"• ₹{amount} received.\n"
                f"• Order ID: `{order_id}`",
                parse_mode="markdown"
            )
            return

    await msg.edit_caption(
        f"❌ *Payment Failed*\n"
        f"• ₹{amount} was not received in time.\n"
        f"Please try again later.",
        parse_mode="markdown"
    )

app.run()
