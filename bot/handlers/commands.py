from aiogram import Router, types
from aiogram.types import Message
from aiogram.filters import Command
import os
from dotenv import load_dotenv

from bot.keyboards.reply import get_main_keyboard

load_dotenv()

# Используем числовой ID вместо @username
CHANNEL_ID = "-1002508751485"

router = Router()

async def is_subscribed(user_id: int, bot) -> bool:
    """Проверяет, подписан ли пользователь на канал."""
    try:
        chat_member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        print(f"Проверка подписки {user_id}: {chat_member.status}")  # Отладка
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Ошибка проверки подписки у {user_id}: {e}")
        return False

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start с проверкой подписки."""
    user_id = message.from_user.id
    bot = message.bot
    
    if not await is_subscribed(user_id, bot):
        await message.answer(
            "❌ Перед началом работы подпишитесь на наш Telegram-канал!\n"
            f"🔗 [Перейти к каналу](https://t.me/neurals_etc)",  # Сделали ссылку кликабельной
            parse_mode="Markdown"
        )
        return

    user_name = message.from_user.first_name
    start_text = os.getenv("Start_text", "Добро пожаловать, {user_name}!").format(user_name=user_name)
    
    await message.answer(
        start_text,
        reply_markup=get_main_keyboard()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help."""
    user_id = message.from_user.id
    bot = message.bot

    if not await is_subscribed(user_id, bot):
        await message.answer(
            "❌ Перед началом работы подпишитесь на наш Telegram-канал!\n"
            f"🔗 [Перейти к каналу](https://t.me/neurals_etc)",
            parse_mode="Markdown"
        )
        return

    help_text = os.getenv("Help_text", "Список доступных команд: ...")
    
    await message.answer(
        help_text,
        reply_markup=get_main_keyboard()
    )