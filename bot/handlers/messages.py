from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
import os
import logging
from dotenv import load_dotenv
from bot.keyboards.reply import get_main_keyboard
from bot.utils.states import Form
from requests import Requests
import base64

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

# Создаем роутер для текстовых сообщений
router = Router()

# ID канала, на который нужно проверить подписку
CHANNEL_ID = os.getenv("CHANNEL_ID")

@router.message(F.text == "📝 Информация")
async def information_button_handler(message: Message):
    try:
        text = os.getenv("Information_text")
        await message.answer(text, reply_markup=get_main_keyboard())
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
    except Exception as e:
        # logger.error(f"Ошибка при удалении сообщений: {str(e)}")
        print(str(e), reply_markup=get_main_keyboard())

@router.message(F.text == "❓ Помощь")
async def help_button_handler(message: Message):
    try:
        text = os.getenv("Help_text")
        await message.answer(text, reply_markup=get_main_keyboard())
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
    except Exception as e:
        # logger.error(f"Ошибка при удалении сообщений: {str(e)}")
        print(str(e), reply_markup=get_main_keyboard())



@router.message(F.text == "📙 Физика")
async def physics_button_handler(message: Message, state: FSMContext):
    try:
        text = os.getenv("Physic_answer_text")
        await state.set_state(Form.section)
        await state.update_data(section="physics")
        await message.answer(text, reply_markup=get_main_keyboard())
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
    except Exception as e:
        # logger.error(f"Ошибка: {str(e)}")
        print(str(e), reply_markup=get_main_keyboard())

@router.message(F.text == "📕 Математика")
async def math_button_handler(message: Message, state: FSMContext):
    try:
        text = os.getenv("Mathematic_answer_text")
        await state.set_state(Form.section)
        await state.update_data(section="mathematics")
        await message.answer(text, reply_markup=get_main_keyboard())
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
    except Exception as e:
        # logger.error(f"Ошибка: {str(e)}")
        print(str(e), reply_markup=get_main_keyboard())

@router.message(F.text == "📗 Химия")
async def chemistry_button_handler(message: Message, state: FSMContext):
    try:
        text = os.getenv("Chemistry_answer_text")
        await state.set_state(Form.section)
        await state.update_data(section="chemistry")
        await message.answer(text, reply_markup=get_main_keyboard())
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
    except Exception as e:
        # logger.error(f"Ошибка: {str(e)}")
        print(str(e), reply_markup=get_main_keyboard())


@router.message(F.photo)
async def photo_handler(message: Message, state: FSMContext):
    """Обработчик для фотографий"""
    try:
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
        wait_message = await message.answer(os.getenv("Wait_text"))
        current_state = await state.get_state()
        state_data = await state.get_data()

        photo = message.photo[-1]  # берем самую большую версию
        file = await message.bot.get_file(photo.file_id)
        file_path = file.file_path

        # Скачиваем файл
        temp_file_path = os.path.join("temp", f"temp_{photo.file_id}.jpg")
        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
        await message.bot.download_file(file_path, destination=temp_file_path)

        # Конвертируем в base64
        with open(temp_file_path, "rb") as image_file:
            image_data = f"data:image/jpeg;base64,{base64.b64encode(image_file.read()).decode('utf-8')}"

        # Удаляем временный файл
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        response = Requests().main(
            request=image_data,
            subject=state_data.get('section'),
            photo=True
        )
        await message.bot.delete_message(message.chat.id, wait_message.message_id)
        await message.answer(response, parse_mode="HTML", reply_markup=get_main_keyboard())
    except Exception as e:
        # logger.error(f"Ошибка: {str(e)}")
        print(str(e), reply_markup=get_main_keyboard())
#gpt обработка
@router.message(StateFilter(Form.section))
async def other_message_handler(message: Message, state: FSMContext):
    try:
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
        state_data = await state.get_data()
        wait_message = await message.answer(os.getenv("Wait_text"))
        response = Requests().main(request=message.text, subject = state_data.get('section'), photo=False)
        await message.bot.delete_message(message.chat.id, wait_message.message_id)
        await message.answer(response, parse_mode="HTML", reply_markup=get_main_keyboard())

    except Exception as e:
        # logger.error(f"Ошибка: {str(e)}")
        print(str(e), reply_markup=get_main_keyboard())