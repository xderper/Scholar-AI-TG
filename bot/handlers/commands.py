from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import os
from dotenv import load_dotenv

from bot.keyboards.reply import get_main_keyboard

# Загружаем переменные окружения
load_dotenv()

# Создаем роутер для команд
router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    user_name = message.from_user.first_name
    start_text = os.getenv("Start_text").format(user_name=user_name)
    
    await message.answer(
        start_text,
        reply_markup=get_main_keyboard()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = os.getenv("Help_text")
    
    await message.answer(
        help_text,
        reply_markup=get_main_keyboard()
    )
