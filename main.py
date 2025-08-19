import os
import requests
import time
import logging
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError


class TelegramLogHandler(logging.Handler):
    def __init__(self, token, chat_id):
        super().__init__()
        self.bot = Bot(token=token)
        self.chat_id = chat_id
        self.setLevel(logging.ERROR)

    def emit(self, record):
        try:
            log_entry = self.format(record)
            self.bot.send_message(
                chat_id=self.chat_id,
                text=f"🚨 Ошибка бота:\n`{log_entry[:1000]}`",
                parse_mode='Markdown'
            )
        except (TelegramError, Exception):
            pass


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    try:
        load_dotenv()
        telegram_token = os.environ['TELEGRAM_TOKEN']
        devman_token = os.environ['DEVMAN_TOKEN']
        chat_id = os.environ['TELEGRAM_CHAT_ID']

        telegram_handler = TelegramLogHandler(telegram_token, chat_id)
        telegram_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        logging.getLogger().addHandler(telegram_handler)

        logger.info("Переменные окружения загружены")

    except KeyError as e:
        logger.error(f"Не найдена переменная: {e.args[0]}")
        return

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{telegram_token}/sendMessage",
            json={
                'chat_id': chat_id,
                'text': "🤖 Бот запущен",
                'parse_mode': 'HTML'
            },
            timeout=10
        )
        response.raise_for_status()
        logger.info("Стартовое сообщение отправлено")

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

                response = requests.post(
                    f"https://api.telegram.org/bot{telegram_token}/sendMessage",
                    json={
                        'chat_id': chat_id,
                        'text': message,
                        'parse_mode': 'HTML'
                    },
                    timeout=10
                )
                response.raise_for_status()
                last_timestamp = review_data['last_attempt_timestamp']

                logger.info(f"Отправлено уведомление: {lesson['lesson_title']}")

            else:
                last_timestamp = review_data['timestamp_to_request']

        except requests.exceptions.ReadTimeout:
            continue

        except requests.exceptions.ConnectionError:
            logger.warning("Нет интернет-соединения")
            time.sleep(30)

        except Exception as e:
            logger.error(f"Ошибка в основном цикле: {e}")
            time.sleep(30)

        time.sleep(5)


if __name__ == '__main__':
    main()