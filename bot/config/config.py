import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
load_dotenv('.env.local', override=True)  # Приоритет локальным настройкам

# Получение токена из переменных окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения")

# Другие настройки бота
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(","))) if os.getenv("ADMIN_IDS") else []
