import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config.config import BOT_TOKEN
from bot.utils.logger import setup_logger
from bot.handlers import commands, messages, callbacks
from bot.middlewares.subscription import SubscriptionMiddleware
from bot.keyboards.inline import router as inline_router
from bot.database.db_config import init_db

# Настройка логгера
logger = setup_logger(name="bot", level=logging.INFO)

# Функция для настройки и запуска бота
async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Инициализация базы данных
    await init_db()
    
    # Регистрация middleware для всех типов обновлений
    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())
    dp.edited_message.middleware(SubscriptionMiddleware())
    
    # Регистрация роутеров
    dp.include_router(commands.router)
    dp.include_router(callbacks.router)
    dp.include_router(inline_router)
    dp.include_router(messages.router)
    
    # Вывод сообщения о запуске бота
    logger.info("Бот запущен")
    
    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        # Запуск бота
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        # Вывод сообщения об остановке бота
        logger.info("Бот остановлен")
    except Exception as e:
        # Вывод сообщения об ошибке
        logger.error(f"Произошла ошибка: {e}", exc_info=True)