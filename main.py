import os
import requests
import time
import logging
import traceback
from dotenv import load_dotenv


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def send_telegram_notification(message):
    """Отправка уведомления в Telegram"""
    try:
        requests.post(
            f"https://api.telegram.org/bot{os.environ['TELEGRAM_TOKEN']}/sendMessage",
            json={
                'chat_id': os.environ['TELEGRAM_CHAT_ID'],
                'text': f"🤖 Бот: {message}",
                'parse_mode': 'Markdown'
            },
            timeout=5
        )
    except Exception as e:
        logger.error(f"Ошибка отправки в Telegram: {e}")


def main():
    try:
        logger.info("Запуск бота")
        send_telegram_notification("Бот запущен")

        try:
            load_dotenv()
            telegram_token = os.environ['TELEGRAM_TOKEN']
            devman_token = os.environ['DEVMAN_TOKEN']
            chat_id = os.environ['TELEGRAM_CHAT_ID']
            logger.info("Переменные окружения загружены")

        except KeyError as e:
            error_msg = f"Ошибка: Не найдена переменная {e}"
            logger.error(error_msg)
            send_telegram_notification(error_msg)
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
                    message = f"Проверка работы: {lesson['lesson_title']} - {'❌ Неудача' if lesson['is_negative'] else '✅ Успех'}"

                    requests.post(
                        f"https://api.telegram.org/bot{telegram_token}/sendMessage",
                        json={'chat_id': chat_id, 'text': message},
                        timeout=10
                    )

                    logger.info(f"Отправлено уведомление: {message}")
                    last_timestamp = review_data['last_attempt_timestamp']
                else:
                    last_timestamp = review_data['timestamp_to_request']

            except requests.exceptions.ReadTimeout:
                logger.debug("Таймаут запроса - повтор")
                continue

            except requests.exceptions.ConnectionError:
                error_msg = "Ошибка подключения к интернету"
                logger.warning(error_msg)
                send_telegram_notification(error_msg)
                time.sleep(30)

            except Exception as e:
                error_traceback = traceback.format_exc()
                error_msg = f"⚠️ Ошибка в цикле:\n```\n{error_traceback}\n```"
                logger.error(f"Ошибка в цикле: {e}")
                send_telegram_notification(error_msg)
                time.sleep(30)

    except Exception as e:
        error_traceback = traceback.format_exc()
        error_msg = f"🔥 Критическая ошибка:\n```\n{error_traceback}\n```"

        logger.critical(error_msg)
        send_telegram_notification(error_msg)

        raise


if __name__ == '__main__':
    main()
