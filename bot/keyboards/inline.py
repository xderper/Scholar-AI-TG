import logging
import sys
import os
from dotenv import load_dotenv

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.reply import get_main_keyboard
from bot.utils.states import Form

# Настройка логирования с поддержкой кириллицы
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения с указанием кодировки UTF-8
load_dotenv(encoding='utf-8')

# Получаем ID пользователя для отзывов
FEEDBACK_USER_ID = os.getenv("FEEDBACK_USER_ID")
FEEDBACK_USER_ID_2 = os.getenv("FEEDBACK_USER_ID_2")

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

logger.info(f"FEEDBACK_USER_ID: {FEEDBACK_USER_ID}")
logger.info(f"FEEDBACK_USER_ID_2: {FEEDBACK_USER_ID_2}")

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
        logger.error(f"Ошибка при обработке отрицательной обратной связи: {str(e)}", exc_info=True)
        await callback.answer("Произошла ошибка. Пожалуйста, попробуйте еще раз.")

@router.callback_query(F.data == "feedback_continue")
async def continue_handler(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(CHOOSE_SECTION_TEXT, reply_markup=get_main_keyboard())
    await callback.answer()

@router.message(Form.feedback_message)
async def feedback_message_handler(message: Message, state: FSMContext):
    try:
        # Проверяем, что это действительно отзыв
        state_data = await state.get_data()
        
        if state_data.get('section') != 'feedback':
            # Если это не отзыв, возвращаемся к обычной обработке
            await state.clear()
            return
            
        # Пересылаем сообщение пользователю по ID
        if FEEDBACK_USER_ID and FEEDBACK_USER_ID_2:
            try:
                # Проверяем, что ID являются числами
                user_id = int(FEEDBACK_USER_ID)
                user_id_2 = int(FEEDBACK_USER_ID_2)
                
                # Проверяем, что бот может отправить сообщение в первый чат
                try:
                    chat = await message.bot.get_chat(user_id)
                    await message.bot.send_message(
                        chat_id=user_id,
                        text=f"Обратная связь от пользователя: \n\n{message.from_user.username or message.from_user.first_name}:\n\n{message.text}"
                    )
                except Exception as chat_error:
                    logger.error(f"Ошибка при отправке в первый чат: {str(chat_error)}")
                
                try:
                    chat_2 = await message.bot.get_chat(user_id_2)
                    await message.bot.send_message(
                        chat_id=user_id_2,
                        text=f"Обратная связь от пользователя: \n\n{message.from_user.username or message.from_user.first_name}:\n\n{message.text}"
                    )
                except Exception as chat_error:
                    logger.error(f"Ошибка при отправке во второй чат: {str(chat_error)}")
                    
            except ValueError:
                logger.error(f"FEEDBACK_USER_ID не является числом: {FEEDBACK_USER_ID} или {FEEDBACK_USER_ID_2}")
            except Exception as send_error:
                logger.error(f"Ошибка при отправке сообщения: {str(send_error)}")
                raise send_error
        else:
            logger.error("FEEDBACK_USER_ID не установлен в переменных окружения")
            await message.answer(FEEDBACK_ERROR_TEXT, reply_markup=get_main_keyboard())
            return
        
        # Отправляем благодарность пользователю
        await message.answer(FEEDBACK_SUCCESS_TEXT, reply_markup=get_main_keyboard())
        
        # Сбрасываем состояние
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка при обработке обратной связи: {str(e)}", exc_info=True)
        await message.answer(FEEDBACK_ERROR_TEXT, reply_markup=get_main_keyboard())