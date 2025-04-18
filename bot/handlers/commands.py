from aiogram import Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
import os
from bot.keyboards.reply import get_main_keyboard
from bot.keyboards.inline import get_subscription_keyboard
from bot.utils.utils import check_subscription


router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    try:
        if not await check_subscription(message.from_user.id, message.bot):
            await message.answer(
                os.getenv("Subscribe_text"),
                reply_markup=get_subscription_keyboard(),
                parse_mode="HTML"
            )
            return
        user_name = message.from_user.first_name or "друг"
        start_text = os.getenv("Start_text").format(user_name=user_name)
        await message.answer(start_text, reply_markup=get_main_keyboard(), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error in commands: {str(e)}")

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    try: 
        if not await check_subscription(message.from_user.id, message.bot):
            await message.answer(
                os.getenv("Subscribe_text"),
                reply_markup=get_subscription_keyboard()
            )
            return
        await message.answer(os.getenv("Help_text"), reply_markup=get_main_keyboard(), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error in commands: {str(e)}")
