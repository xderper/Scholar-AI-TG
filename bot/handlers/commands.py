from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from bot.keyboards.reply import get_main_keyboard

# Создаем роутер для команд
router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    user_name = message.from_user.first_name
    await message.answer(
        f"Привет, {user_name}! 👋\n\n"
        "Я эхо-бот. Отправь мне любое сообщение, и я его повторю.",
        reply_markup=get_main_keyboard()
    )
