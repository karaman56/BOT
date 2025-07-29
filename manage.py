from telegram import Bot
import requests
import time
import JSON


DEVMAN_TOKEN = "8eae28bd3ecf9a3643b49406cf29f9adca942679"
DEVMAN_URL = "https://dvmn.org/api/long_polling/"
DEVMAN_HEADERS = {"Authorization": f"Token {DEVMAN_TOKEN}"}




last_check_time = None


def send_telegram_message(text):
    """Отправляет сообщение в Telegram"""
    try:
        requests.post(
            TELEGRAM_API_URL,
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text},
            timeout=5
        )
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")


def format_review_notification(review_data):
    """Форматирует уведомление о проверке"""
    attempt = review_data["new_attempts"][0]
    lesson_title = attempt["lesson_title"]
    is_negative = "Есть замечания" if attempt["is_negative"] else "Принято!"
    lesson_url = f"https://dvmn.org{attempt['lesson_url']}"
    return f"""
🔔 Новая проверка!
Урок: {lesson_title}
Результат: {is_negative}
Ссылка: {lesson_url}
"""


print("Бот запущен. Ожидание проверок...")
send_telegram_message("🔍 Бот начал отслеживать проверки Devman")

while True:
    try:

        params = {"timestamp": last_check_time} if last_check_time else {}

        # Делаем запрос с таймаутом 90 секунд
        response = requests.get(
            DEVMAN_URL,
            headers=DEVMAN_HEADERS,
            params=params,
            timeout=95
        )
        data = response.json()

        if data["status"] == "found":
            # Формируем и отправляем уведомление
            message = format_review_notification(data)
            print(message)
            send_telegram_message(message)

            # Обновляем временную метку
            last_check_time = data["last_attempt_timestamp"]
        else:
            # Обновляем временную метку при timeout
            last_check_time = data["timestamp_to_request"]

    except requests.exceptions.ReadTimeout:
        continue  # Ожидание новых проверок

    except requests.exceptions.ConnectionError:
        print("Проблемы с интернетом. Повтор через 5 секунд...")
        time.sleep(5)

    except Exception as e:
        print(f"Неизвестная ошибка: {e}. Повтор через 5 секунд...")
        time.sleep(5)