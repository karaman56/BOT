import os
import argparse
import requests
import time
from dotenv import load_dotenv


load_dotenv()
parser = argparse.ArgumentParser()
parser.add_argument('--chat_id', help='Ваш Telegram Chat ID')
args = parser.parse_args()


DEVMAN_TOKEN = os.getenv('DEVMAN_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = args.chat_id or os.getenv('TELEGRAM_CHAT_ID')

if not TELEGRAM_CHAT_ID:
    print("Укажите Chat ID одним из способов:")
    print("1. python bot.py --chat_id 123456789")
    print("2. Добавьте TELEGRAM_CHAT_ID=123456789 в .env")
    exit()

def send_telegram(text):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    )

send_telegram("🔔 Бот запущен!")
last_time = None

while True:
    try:
        response = requests.get(
            "https://dvmn.org/api/long_polling/",
            headers={"Authorization": f"Token {DEVMAN_TOKEN}"},
            params={"timestamp": last_time} if last_time else {},
            timeout=90
        )
        data = response.json()

        if data["status"] == "found":
            lesson = data["new_attempts"][0]
            message = f"""
📌 <b>Новая проверка!</b>
📚 Урок: {lesson['lesson_title']}
{'❌ Есть замечания' if lesson['is_negative'] else '✅ Принято'}
🔗 https://dvmn.org{lesson['lesson_url']}
"""
            send_telegram(message)
            last_time = data["last_attempt_timestamp"]
        else:
            last_time = data["timestamp_to_request"]

    except requests.exceptions.ReadTimeout:
        continue
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)