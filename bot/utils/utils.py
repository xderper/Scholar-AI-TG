from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.keyboards.reply import get_main_keyboard
from bot.keyboards.inline import get_subscription_keyboard
import os


async def check_subscription(user_id: int, bot) -> bool:
    """
    Проверяет подписку пользователя на канал.
    
    Args:
        user_id (int): ID пользователя для проверки
        bot: Экземпляр бота для выполнения запроса
        
    Returns:
        bool: True если пользователь подписан, False если нет
    """
    try:
        # Получаем ID канала из переменных окружения

        channel_id = os.getenv("CHANNEL_ID")
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        else:
            return False

    except Exception as e:
        print(e)
        return False
