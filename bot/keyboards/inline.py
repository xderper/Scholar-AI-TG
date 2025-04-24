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

# Загружаем переменные окружения
load_dotenv()

# Получаем ID пользователя для отзывов
FEEDBACK_USER_ID = os.getenv("FEEDBACK_USER_ID")
FEEDBACK_USER_ID_2 = os.getenv("FEEDBACK_USER_ID_2")
logger.info(f"FEEDBACK_USER_ID: {FEEDBACK_USER_ID}")
logger.info(f"FEEDBACK_USER_ID_2: {FEEDBACK_USER_ID_2}")

# Создаем роутер
router = Router()

# Инлайн-клавиатура с URL-кнопкой
def get_url_keyboard(url: str, text: str = "Открыть ссылку") -> InlineKeyboardMarkup:
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
            InlineKeyboardButton(text="✅ Да", callback_data="feedback_yes"),
            InlineKeyboardButton(text="❌ Нет", callback_data="feedback_no"),
            InlineKeyboardButton(text="📚 Продолжить", callback_data="feedback_continue")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
def get_subscription_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="IT Thinker", url="https://t.me/neurals_etc")
            ],
            [
                InlineKeyboardButton(text="Проверить подписку✅", callback_data="check_subscription")
            ]
        ]
    )   

@router.callback_query(F.data == "feedback_yes")
async def positive_feedback_handler(callback: CallbackQuery):
    await callback.message.edit_text("📚 Спасибо за отзыв!")
    await callback.message.answer("📚 Выберите раздел:", reply_markup=get_main_keyboard())
    await callback.answer()

@router.callback_query(F.data == "feedback_no")
async def negative_feedback_handler(callback: CallbackQuery, state: FSMContext):
    try:
        logger.info("Нажата кнопка 'нет' в меню обратной связи")
        
        # Сбрасываем все предыдущие состояния
        await state.clear()
        logger.info("Предыдущие состояния сброшены")
        
        # Устанавливаем состояние для сбора обратной связи
        await state.set_state(Form.feedback_message)
        # Устанавливаем секцию отзыва
        await state.update_data(section="feedback")
        logger.info("Установлено состояние feedback_message и секция feedback")
        
        # Удаляем предыдущее сообщение с кнопками
        await callback.message.delete()
        # Запрашиваем у пользователя подробности
        await callback.message.answer("📚 Пожалуйста, расскажите, что именно вас не устроило")
        await callback.answer()
        logger.info("Запрос на отзыв отправлен пользователю")
    except Exception as e:
        logger.error(f"Ошибка при обработке отрицательной обратной связи: {str(e)}", exc_info=True)
        await callback.answer("Произошла ошибка. Пожалуйста, попробуйте еще раз.")

@router.callback_query(F.data == "feedback_continue")
async def continue_handler(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("📚 Выберите раздел:", reply_markup=get_main_keyboard())
    await callback.answer()

@router.message(Form.feedback_message)
async def feedback_message_handler(message: Message, state: FSMContext):
    try:
        logger.info(f"Получено сообщение обратной связи: {message.text}")
        
        # Проверяем, что это действительно отзыв
        state_data = await state.get_data()
        logger.info(f"Текущее состояние: {state_data}")
        
        if state_data.get('section') != 'feedback':
            logger.warning("Сообщение не является отзывом, пропускаем обработку")
            # Если это не отзыв, возвращаемся к обычной обработке
            await state.clear()
            return
            
        # Пересылаем сообщение пользователю по ID
        if FEEDBACK_USER_ID and FEEDBACK_USER_ID_2:
            logger.info(f"Попытка отправить сообщение пользователю с ID: {FEEDBACK_USER_ID}")
            logger.info(f"Попытка отправить сообщение пользователю с ID: {FEEDBACK_USER_ID_2}")
            try:
                # Проверяем, что ID являются числами
                user_id = int(FEEDBACK_USER_ID)
                logger.info(f"Преобразованное ID пользователя: {user_id}")
                user_id_2 = int(FEEDBACK_USER_ID_2)
                logger.info(f"Преобразованное ID пользователя: {user_id_2}")
                
                # Проверяем, что бот может отправить сообщение в первый чат
                try:
                    chat = await message.bot.get_chat(user_id)
                    logger.info(f"Чат найден: {chat}")
                    await message.bot.send_message(
                        chat_id=user_id,
                        text=f"Обратная связь от пользователя {message.from_user.username or message.from_user.first_name}:\n\n{message.text}"
                    )
                    logger.info("Сообщение успешно отправлено в первый чат")
                except Exception as chat_error:
                    logger.error(f"Ошибка при отправке в первый чат: {str(chat_error)}")
                    # Продолжаем выполнение даже если не удалось отправить в первый чат
                
                # Проверяем, что бот может отправить сообщение во второй чат
                try:
                    chat_2 = await message.bot.get_chat(user_id_2)
                    logger.info(f"Чат найден: {chat_2}")
                    await message.bot.send_message(
                        chat_id=user_id_2,
                        text=f"Обратная связь от пользователя {message.from_user.username or message.from_user.first_name}:\n\n{message.text}"
                    )
                    logger.info("Сообщение успешно отправлено во второй чат")
                except Exception as chat_error:
                    logger.error(f"Ошибка при отправке во второй чат: {str(chat_error)}")
                    # Продолжаем выполнение даже если не удалось отправить во второй чат
                
            except ValueError:
                logger.error(f"FEEDBACK_USER_ID не является числом: {FEEDBACK_USER_ID} или {FEEDBACK_USER_ID_2}")
            except Exception as send_error:
                logger.error(f"Ошибка при отправке сообщения: {str(send_error)}")
                raise send_error
        else:
            logger.error("FEEDBACK_USER_ID не установлен в переменных окружения")
            await message.answer("Произошла ошибка при отправке обратной связи. Пожалуйста, попробуйте позже.", reply_markup=get_main_keyboard())
            return
        
        # Отправляем благодарность пользователю
        await message.answer("Спасибо за обратную связь! 😊", reply_markup=get_main_keyboard())
        
        # Сбрасываем состояние
        await state.clear()
        logger.info("Состояние сброшено")
    except Exception as e:
        logger.error(f"Ошибка при обработке обратной связи: {str(e)}", exc_info=True)
        await message.answer("Произошла ошибка при отправке обратной связи. Пожалуйста, попробуйте позже.", reply_markup=get_main_keyboard()) 