from bot.database.db_config import get_db_connection
import logging

logger = logging.getLogger(__name__)

async def log_start_command(user_id: int, username: str, first_name: str):
    """Логирует использование команды /start в базу данных, если пользователя ещё нет"""
    try:
        conn = await get_db_connection()
        try:
            # Проверяем, есть ли уже такой пользователь
            result = await conn.fetchrow('SELECT id FROM users WHERE user_id = $1', user_id)
            if result is None:
                await conn.execute('''
                    INSERT INTO users (user_id, username, first_name)
                    VALUES ($1, $2, $3)
                ''', user_id, username, first_name)
        finally:
            await conn.close()
    except Exception as e:
        logger.error(f"Error logging start command: {str(e)}") 