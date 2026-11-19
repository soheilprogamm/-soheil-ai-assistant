import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN = os.getenv("ADMIN_CHAT_ID")

API = f"https://api.telegram.org/bot{TOKEN}/"

users = {}

def send(chat_id, text):
    requests.post(API + "sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

def handle_message(chat_id, text):

    if text == "/start":
        users[chat_id] = {}
        send(chat_id,
             "سلام! 👋 به Soheil AI Assistant خوش آمدی.\n\n"
             "1️⃣ گفتگو با دستیار\n"
             "2️⃣ مشاهده محصولات\n"
             "3️⃣ ثبت سفارش")
    
    elif text == "1":
        send(chat_id, "سلام! من دستیار هوشمند سهیل هستم. چطور می‌توانم کمکت کنم؟")

    elif text == "2":
        send(chat_id, "🛍 محصولات ما:\n\n"
                      "برای مشاهده قیمت و سفارش با مدیر فروش تماس بگیرید.")

    elif text == "3":
        users[chat_id] = {"step": "name"}
        send(chat_id, "لطفاً نام خود را وارد کنید:")

    elif chat_id in users and users[chat_id].get("step") == "name":
        users[chat_id]["name"] = text
        users[chat_id]["step"] = "phone"
        send(chat_id, "شماره تماس خود را وارد کنید:")

    elif chat_id in users and users[chat_id].get("step") == "phone":
        users[chat_id]["phone"] = text
        users[chat_id]["step"] = "product"
        send(chat_id, "نام محصول موردنظر را وارد کنید:")

    elif chat_id in users and users[chat_id].get("step") == "product":
        order = users[chat_id]
        order["product"] = text

        message = (
            "🛒 سفارش جدید\n"
            f"نام: {order['name']}\n"
            f"تلفن: {order['phone']}\n"
            f"محصول: {text}"
        )

        if ADMIN:
            send(ADMIN, message)

        send(chat_id, "✅ سفارش شما ثبت شد. ممنون از اعتمادتان!")
        users[chat_id] = {}

    else:
        send(chat_id, "پیامت دریافت شد! برای شروع /start را بزن.")

@app.route("/", methods=["GET"])
def home():
    return "Soheil AI Assistant is Running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json or {}
    message = data.get("message", {})

    if message.get("text"):
        chat_id = message["chat"]["id"]
        handle_message(chat_id, message["text"])

    return {"ok": True}

if TOKEN:
    requests.post(API + "setWebhook", json={
        "url": os.getenv("RENDER_EXTERNAL_URL", "") + "/webhook"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0",
            port=int(os.getenv("PORT", 10000)))
