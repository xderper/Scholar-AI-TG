from aiogram import Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
import os
from bot.keyboards.reply import get_main_keyboard
from bot.keyboards.inline import get_subscription_keyboard
from bot.utils.utils import check_subscription

CHANNEL_ID = "-1002508751485"

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.bot.send_chat_action(
            chat_id=message.chat.id,
            action="typing"
        )
    """Обработчик команды /start"""
    if not await check_subscription(message.from_user.id, message.bot):
        await message.answer(
            os.getenv("Subscribe_text"),
            reply_markup=get_subscription_keyboard()
        )
        return
    user_name = message.from_user.first_name or "друг"
    start_text = os.getenv("Start_text").format(user_name=user_name)
    await message.answer(start_text, reply_markup=get_main_keyboard())

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.bot.send_chat_action(
            chat_id=message.chat.id,
            action="typing"
        )
    """Обработчик команды /help"""
    if not await check_subscription(message.from_user.id, message.bot):
        await message.answer(
            os.getenv("Subscribe_text"),
            reply_markup=get_subscription_keyboard()
        )
        return
    await message.answer(os.getenv("Help_text"), reply_markup=get_main_keyboard())