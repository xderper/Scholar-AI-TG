import logging
import os
from dotenv import load_dotenv
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router, F


# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Загружаем переменные окружения с указанием кодировки UTF-8
load_dotenv(encoding='utf-8')


# Создаем роутер
router = Router()

def get_feedback_keyboard() -> InlineKeyboardMarkup:
    """Создает inline клавиатуру для обратной связи"""
    keyboard = [
        [
            InlineKeyboardButton(text=os.getenv("BUTTON_YES"), callback_data="feedback_yes"),
            InlineKeyboardButton(text=os.getenv("BUTTON_NO"), callback_data="feedback_no"),
            InlineKeyboardButton(text="❓ Вопрос", callback_data="question_help")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_subscription_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=os.getenv("BUTTON_CHANNEL_NAME"), url=os.getenv("TELEGRAM_CHANNEL_URL"))
            ],
            [
                InlineKeyboardButton(text=os.getenv("BUTTON_CHECK_SUBSCRIPTION"), callback_data="check_subscription")
            ]
        ]
    )   



