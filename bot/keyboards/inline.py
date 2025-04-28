import logging
import sys
import os
from dotenv import load_dotenv
import asyncio

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramRetryAfter, TelegramMigrateToChat

from bot.keyboards.reply import get_main_keyboard
from bot.utils.states import Form

# Загружаем переменные окружения с указанием кодировки UTF-8
load_dotenv(encoding='utf-8')

# Получаем ID пользователя для отзывов
FEEDBACK_GROUP_ID = os.getenv("FEEDBACK_GROUP_ID").replace('\\n', '\n')  # ID супергруппы для отзывов)

# Получаем URL и тексты из переменных окружения
WEBSITE_URL = os.getenv("WEBSITE_URL")
TELEGRAM_CHANNEL_URL = os.getenv("TELEGRAM_CHANNEL_URL")
BOT_USERNAME = os.getenv("BOT_USERNAME")

# Тексты сообщений
POSITIVE_FEEDBACK_TEXT = os.getenv("POSITIVE_FEEDBACK_TEXT").replace('\\n', '\n')
NEGATIVE_FEEDBACK_PROMPT = os.getenv("NEGATIVE_FEEDBACK_PROMPT").replace('\\n', '\n')
FEEDBACK_SUCCESS_TEXT = os.getenv("FEEDBACK_SUCCESS_TEXT").replace('\\n', '\n')
FEEDBACK_ERROR_TEXT = os.getenv("FEEDBACK_ERROR_TEXT").replace('\\n', '\n')
CHOOSE_SECTION_TEXT = os.getenv("CHOOSE_SECTION_TEXT").replace('\\n', '\n')

# Тексты кнопок
BUTTON_YES = os.getenv("BUTTON_YES")
BUTTON_NO = os.getenv("BUTTON_NO")
BUTTON_CONTINUE = os.getenv("BUTTON_CONTINUE")
BUTTON_OPEN_LINK = os.getenv("BUTTON_OPEN_LINK")
BUTTON_CHANNEL_NAME = os.getenv("BUTTON_CHANNEL_NAME")
BUTTON_CHECK_SUBSCRIPTION = os.getenv("BUTTON_CHECK_SUBSCRIPTION")

# Создаем роутер
router = Router()

# Инлайн-клавиатура с URL-кнопкой
def get_url_keyboard(url: str, text: str = BUTTON_OPEN_LINK) -> InlineKeyboardMarkup:
    """Создает и возвращает инлайн-клавиатуру с URL-кнопкой"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=text, url=url)
            ]
        ]
    )
    return keyboard

def get_feedback_keyboard() -> InlineKeyboardMarkup:
    """Создает inline клавиатуру для обратной связи"""
    keyboard = [
        [
            InlineKeyboardButton(text=BUTTON_YES, callback_data="feedback_yes"),
            InlineKeyboardButton(text=BUTTON_NO, callback_data="feedback_no"),
            InlineKeyboardButton(text=BUTTON_CONTINUE, callback_data="feedback_continue")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_subscription_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=BUTTON_CHANNEL_NAME, url=TELEGRAM_CHANNEL_URL)
            ],
            [
                InlineKeyboardButton(text=BUTTON_CHECK_SUBSCRIPTION, callback_data="check_subscription")
            ]
        ]
    )   

@router.callback_query(F.data == "feedback_yes")
async def positive_feedback_handler(callback: CallbackQuery):
    await callback.message.edit_text(POSITIVE_FEEDBACK_TEXT.format(
        website_url=WEBSITE_URL,
        channel_url=TELEGRAM_CHANNEL_URL,
        bot_username=BOT_USERNAME
    ))
    await callback.message.answer(CHOOSE_SECTION_TEXT, reply_markup=get_main_keyboard())
    await callback.answer()

@router.callback_query(F.data == "feedback_no")
async def negative_feedback_handler(callback: CallbackQuery, state: FSMContext):
    try:
        # Сбрасываем все предыдущие состояния
        await state.clear()
        
        # Устанавливаем состояние для сбора обратной связи
        await state.set_state(Form.feedback_message)
        # Устанавливаем секцию отзыва
        await state.update_data(section="feedback")
        
        # Удаляем предыдущее сообщение с кнопками
        await callback.message.delete()
        # Запрашиваем у пользователя подробности
        await callback.message.answer(NEGATIVE_FEEDBACK_PROMPT)
        await callback.answer()
    except Exception as e:
        await callback.answer("Произошла ошибка. Пожалуйста, попробуйте еще раз.")

@router.callback_query(F.data == "feedback_continue")
async def continue_handler(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(CHOOSE_SECTION_TEXT, reply_markup=get_main_keyboard())
    await callback.answer()

def format_feedback_message(username: str, text: str) -> str:
    """Форматирует сообщение с отзывом"""
    return f"📝 Отзыв от пользователя: \n\n{username}\n\n{text}"

@router.message(Form.feedback_message)
async def feedback_message_handler(message: Message, state: FSMContext):
    try:
        # Проверяем, что это действительно отзыв
        state_data = await state.get_data()
        
        if state_data.get('section') != 'feedback':
            # Если это не отзыв, возвращаемся к обычной обработке
            await state.clear()
            return
            
        # Проверяем доступность чата
        try:
            chat = await message.bot.get_chat(FEEDBACK_GROUP_ID)
            
            # Проверяем, что бот является администратором
            chat_member = await message.bot.get_chat_member(FEEDBACK_GROUP_ID, message.bot.id)
            if not chat_member.status in ['administrator', 'creator']:
                await message.answer(
                    "❌ Ошибка: бот не имеет прав администратора в группе. Пожалуйста, сообщите администратору.",
                    reply_markup=get_main_keyboard()
                )
                await state.clear()
                return
                
        except Exception:
            await message.answer(
                "❌ Ошибка: бот не может отправить отзыв. Пожалуйста, сообщите администратору.",
                reply_markup=get_main_keyboard()
            )
            await state.clear()
            return
            
        # Форматируем сообщение
        feedback_text = format_feedback_message(
            message.from_user.username or message.from_user.first_name,
            message.text
        )
            
        # Отправляем сообщение в супергруппу
        try:
            await message.bot.send_message(
                chat_id=FEEDBACK_GROUP_ID,
                text=feedback_text
            )
        except TelegramRetryAfter as e:
            # Ждем указанное время и пробуем снова
            await asyncio.sleep(e.retry_after)
            await message.bot.send_message(
                chat_id=FEEDBACK_GROUP_ID,
                text=feedback_text
            )
        except TelegramMigrateToChat as e:
            # Если группа обновлена до супергруппы, используем новый ID
            await message.bot.send_message(
                chat_id=e.migrate_to_chat_id,
                text=feedback_text
            )
        except Exception:
            await message.answer(
                "❌ Ошибка при отправке отзыва. Пожалуйста, попробуйте позже.",
                reply_markup=get_main_keyboard()
            )
            await state.clear()
            return
        
        # Отправляем благодарность пользователю
        await message.answer(FEEDBACK_SUCCESS_TEXT, reply_markup=get_main_keyboard())
        
        # Сбрасываем состояние
        await state.clear()
    except Exception:
        await message.answer(FEEDBACK_ERROR_TEXT, reply_markup=get_main_keyboard())
        await state.clear()