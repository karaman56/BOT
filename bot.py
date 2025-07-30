import os
import requests
import time
import argparse
import logging
from dotenv import load_dotenv


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger(__name__)


def main():
    logger = setup_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument('--chat_id', required=True, help='Ваш Telegram Chat ID')
    args = parser.parse_args()

    try:
        load_dotenv()
        telegram_token = os.environ['TELEGRAM_TOKEN']
        devman_token = os.environ['DEVMAN_TOKEN']
    except KeyError as e:
        logger.error(f"Не найдена переменная: {e.args[0]}")
        return

    try:
        requests.post(
            f"https://api.telegram.org/bot{telegram_token}/sendMessage",
            json={
                'chat_id': args.chat_id,
                'text': "🤖 Бот запущен",
                'parse_mode': 'HTML'
            },
            timeout=10
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка Telegram: {e}")
        return

    last_timestamp = None

    while True:
        try:
            response = requests.get(
                "https://dvmn.org/api/long_polling/",
                headers={"Authorization": f"Token {devman_token}"},
                params={"timestamp": last_timestamp} if last_timestamp else {},
                timeout=90
            )
            response.raise_for_status()
            review_data = response.json()

            if review_data['status'] == 'found':
                lesson = review_data['new_attempts'][0]
                message = f"📝 {lesson['lesson_title']} - {'❌' if lesson['is_negative'] else '✅'}"
                requests.post(
                    f"https://api.telegram.org/bot{telegram_token}/sendMessage",
                    json={
                        'chat_id': args.chat_id,
                        'text': message,
                        'parse_mode': 'HTML'
                    },
                    timeout=10
                )
                last_timestamp = review_data['last_attempt_timestamp']
            else:
                last_timestamp = review_data['timestamp_to_request']

        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            logger.warning("Нет интернета")
            time.sleep(30)
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            time.sleep(30)

        time.sleep(5)


if __name__ == '__main__':
    main()