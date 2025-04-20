from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject, CallbackQuery, Update
from aiogram.exceptions import TelegramAPIError
import os
from dotenv import load_dotenv
from bot.keyboards.inline import get_subscription_keyboard
from bot.utils.utils import check_subscription

# Загружаем переменные окружения
load_dotenv()

class SubscriptionMiddleware(BaseMiddleware):
    """Middleware для проверки подписки пользователя на канал перед обработкой запроса."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Получаем ID канала из env
        channel_id = os.getenv("CHANNEL_ID")
            
        user_id = event.from_user.id
        bot = event.bot
              
        # Проверяем подписку
        try:
            is_subscribed = await check_subscription(user_id, bot)
            if is_subscribed:
                return await handler(event, data)
            else:
                subscribe_text = os.getenv("Subscribe_text")
                await event.answer(subscribe_text, reply_markup=get_subscription_keyboard(), parse_mode="HTML")
              
        except TelegramAPIError as e:
            # В случае ошибки API логируем и пропускаем проверку
            print(f"Ошибка при проверке подписки API: {e}")
            return await handler(event, data)
   
