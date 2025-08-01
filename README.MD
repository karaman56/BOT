# Devman Checker Bot 🤖

Telegram бот для отслеживания проверок заданий на Devman (dvmn.org)

## 📌 Возможности
- Автоматическая проверка статуса заданий
- Уведомления в Telegram о новых проверках
- Поддержка long-polling (эффективное использование API)
- Гибкая настройка через переменные окружения

## ⚙️ Установка

1. Клонируйте репозиторий:
```bash
git clone hhttps://github.com/karaman56/BOT
cd devman-checker-bot
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` и заполните его:
```ini
DEVMAN_TOKEN=ваш_токен_devman
TELEGRAM_TOKEN=ваш_токен_бота
# TELEGRAM_CHAT_ID=ваш_chat_id  # Можно указать здесь или при запуске
```

## 🚀 Запуск

Способ 1 (с указанием chat_id в аргументах):
```bash
python bot.py --chat_id 123456789
```

Способ 2 (если chat_id указан в .env):
```bash
python bot.py
```

## 🔧 Получение токенов

1. **Devman Token**:
   - Перейдите в [API-ключи](https://dvmn.org/api/docs/)
   - Скопируйте ваш ключ

2. **Telegram Bot Token**:
   - Напишите [@BotFather](https://t.me/BotFather) в Telegram
   - Создайте нового бота командой `/newbot`
   - Скопируйте выданный токен

3. **Chat ID**:
   - Напишите [@userinfobot](https://t.me/userinfobot) в Telegram
   - Отправьте команду `/start`
   - Скопируйте ваш ID

## 📂 Структура проекта
```
devman-checker-bot/
├── bot.py             # Основной скрипт бота
├── .env.example       # Пример файла конфигурации
├── requirements.txt   # Зависимости
└── README.md          # Этот файл
```

## ⚠️ Важно
- Не публикуйте ваши токены в открытом доступе
- Добавьте `.env` в `.gitignore`
- Для остановки бота нажмите `Ctrl+C`

## 💡 Дополнительно
Вы можете модифицировать:
- Текст уведомлений в функции `send_telegram()`
- Таймауты запросов (параметр `timeout=`)
- Формат сообщений (HTML-разметка)

