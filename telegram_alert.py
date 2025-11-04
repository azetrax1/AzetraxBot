import requests
import json

with open("config.json", "r") as f:
    config = json.load(f)

BOT_TOKEN = config["telegram_token"]
CHAT_ID = config["telegram_chat_id"]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Telegram gönderim hatası: {e}")
