import os
import hmac
import hashlib
from fastapi import FastAPI, Request, HTTPException
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
VIP_CHANNEL_ID = int(os.getenv("VIP_CHANNEL_ID"))
SELLAPP_WEBHOOK_SECRET = os.getenv("SELLAPP_WEBHOOK_SECRET")

bot = Bot(token=BOT_TOKEN)
app = FastAPI()

def verify_signature(payload: bytes, signature: str):
    mac = hmac.new(
        SELLAPP_WEBHOOK_SECRET.encode(),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(mac, signature)

@app.post("/webhook/sellapp")
async def sellapp_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("X-Sellapp-Signature")

    if not signature or not verify_signature(payload, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    data = await request.json()

    if data.get("status") == "completed":
        tg_user_id = int(data.get("custom"))
        await bot.add_chat_member(
            chat_id=VIP_CHANNEL_ID,
            user_id=tg_user_id
        )
        await bot.send_message(
            chat_id=tg_user_id,
            text="✅ 支付成功，你已加入 VIP 频道"
        )

    return {"ok": True}
