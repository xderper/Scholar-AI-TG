from aiogram import Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
import os
import logging
from bot.keyboards.reply import get_main_keyboard
from bot.keyboards.inline import get_subscription_keyboard
from bot.database.db_operations import log_start_command

# Настройка логирования
logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    try:
        user_name = message.from_user.first_name or "друг"
        start_text = os.getenv("Start_text").format(user_name=user_name)
        
        # Логируем использование команды /start
        await log_start_command(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
        
        await message.answer(start_text, reply_markup=get_main_keyboard(), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error in commands: {str(e)}")

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    try: 
        await message.answer(os.getenv("Help_text"), reply_markup=get_main_keyboard(), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error in commands: {str(e)}")