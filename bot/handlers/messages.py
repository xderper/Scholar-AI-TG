from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.keyboards.reply import get_main_keyboard
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from requests import Requests
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Создаем роутер для текстовых сообщений
router = Router()

# Обработчик для кнопки "Привет"
@router.message(F.text == "📙 Физика")
async def physics_button_handler(message: Message, state: FSMContext):
    """Обработчик для кнопки Физика"""
    text = os.getenv("Physic_answer_text")
    await state.set_state('physic')
    await message.answer(
        text,
        reply_markup=get_main_keyboard()
    )

# Обработчик для кнопки "Информация"
@router.message(F.text == "📝 Информация")
async def information_button_handler(message: Message):
    """Обработчик для кнопки Информация"""
    text = os.getenv("Information_text")
    await message.answer(
        text,
        reply_markup=get_main_keyboard()
    )

# Обработчик для кнопки "Помощь"
@router.message(F.text == "❓ Помощь")
async def help_button_handler(message: Message):
    """Обработчик для кнопки Помощь"""
    text = os.getenv("Help_text")
    await message.answer(
        text,
        reply_markup=get_main_keyboard()
    )

# @router.message(F.text == "📕 Математика")
# async def mathematic_button_handler(message: Message, state: FSMContext):
#     """Обработчик для кнопки Физика"""
#     text = os.getenv("Mathematic_answer_text")
#     await state.set_state('mathematic')
#     await message.answer(
#         text,
#         reply_markup=get_main_keyboard()
#     )

@router.message()
async def handle_message(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == 'physic':

        # Получаем ответ от ChatGPT
        response = Requests().physic(message.text)
        
        try:
            # Форматируем ответ для лучшего отображения в Telegram
            
            # Отправляем отформатированный ответ
            await message.answer(
                response,
                parse_mode="HTML"
            )
        except Exception as e:
            # В случае ошибки форматирования отправляем текст без HTML-форматирования
            # Удаляем все HTML-теги из текста
            import re
            clean_text = re.sub(r'<[^>]+>', '', formatted_response)
            await message.answer(

                f"Ответ: {response}"
            )
    # elif current_state == 'mathematic':
    #     # Получаем ответ от ChatGPT
    #     response = Requests().mathematic(message.text)
        
    #     try:
    #         # Форматируем ответ для лучшего отображения в Telegram
            
    #         # Отправляем отформатированный ответ
    #         await message.answer(
    #             response,
    #             parse_mode="HTML"
    #         )
    #     except Exception as e:
    #         # В случае ошибки форматирования отправляем исходный ответ
    #         await message.answer(
    #             f"Ответ: {response}"
    #         )
    else:
        await message.answer("Вы не выбрали раздел")
