from typing import Any, Awaitable, Callable, Dict
import os
from dotenv import load_dotenv
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject, Update

# Загружаем переменные окружения
load_dotenv()

class FeedbackGroupFilterMiddleware(BaseMiddleware):
    """Middleware для фильтрации сообщений из группы обратной связи."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Проверяем, является ли событие сообщением и имеет ли оно атрибут chat
        if isinstance(event, Message) and hasattr(event, 'chat'):
            # Получаем ID группы обратной связи из env
            feedback_group_id = os.getenv("FEEDBACK_GROUP_ID")
            
            # Если сообщение пришло из группы обратной связи, игнорируем его
            if feedback_group_id and str(event.chat.id) == feedback_group_id:
                return None
        
        # Для всех остальных событий продолжаем обработку
        return await handler(event, data) 