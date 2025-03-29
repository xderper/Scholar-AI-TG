from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.keyboards.reply import get_main_keyboard
from bot.utils.states import Form
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Создаем роутер для callback-запросов
router = Router()

# Обработчик для callback "type_text"
@router.callback_query(F.data == "type_text")
async def callback_type_text(callback: CallbackQuery, state: FSMContext):
    """Обработчик для выбора текстового режима"""
    # Отвечаем на callback, чтобы убрать часы загрузки на кнопке
    await callback.answer("Выбран текстовый режим")
    
    # Обновляем сообщение
    await callback.message.edit_text(
        "Введите условие задачи по физике",
        reply_markup=None  # Убираем клавиатуру
    )
    
    # Устанавливаем состояние для обработки текстовой задачи
    await state.update_data(type="text")
    await state.set_state(Form.type)

# Обработчик для callback "type_image"
@router.callback_query(F.data == "type_image")
async def callback_type_image(callback: CallbackQuery, state: FSMContext):
    """Обработчик для выбора режима с изображением"""
    # Отвечаем на callback, чтобы убрать часы загрузки на кнопке
    await callback.answer("Выбран режим с изображением")
    
    # Обновляем сообщение
    await callback.message.edit_text(
        "Пожалуйста, отправьте фотографию с условием задачи по физике",
        reply_markup=None  # Убираем клавиатуру
    )
    
    # Устанавливаем состояние для обработки задачи с изображением
    await state.update_data(type="image")
    await state.set_state(Form.type)
