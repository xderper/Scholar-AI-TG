from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from bot.keyboards.reply import get_main_keyboard
from bot.utils.states import Form
import sys
import os
import base64
import logging
from dotenv import load_dotenv
from requests import Requests

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()
load_dotenv('.env.local', override=True)

# Создаем роутер для текстовых сообщений
router = Router()

# Обработчик для кнопки "Привет"
@router.message(F.text == "📙 Физика")
async def physics_button_handler(message: Message, state: FSMContext):
    """Обработчик для кнопки Физика"""
    text = os.getenv("Physic_answer_text")
    await state.set_state(Form.section)
    await state.update_data(section="physics")
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

@router.message(F.photo)
async def photo_handler(message: Message, state: FSMContext):
    """Обработчик для фотографий"""
    current_state = await state.get_state()
    state_data = await state.get_data()
    
    if current_state == Form.section and state_data.get('section') == 'physics':
        logger.info(f"Получено фото от пользователя {message.from_user.id}")
        
        # Получаем файл с наибольшим размером (лучшее качество)
        photo = message.photo[-1]
        
        # Информируем пользователя о получении фото
        await message.answer("Получил ваше фото с задачей. Обрабатываю...")
        
        try:
            # Скачиваем файл
            file_id = photo.file_id
            file = await message.bot.get_file(file_id)
            file_path = file.file_path
            logger.info(f"Скачивание файла {file_id} начато")
            
            # Создаем временный файл для сохранения изображения
            temp_file_path = os.path.join("temp", f"temp_{file_id}.jpg")
            
            # Если папка temp не существует, создаем её
            os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
            
            # Скачиваем файл во временную директорию
            await message.bot.download_file(file_path, destination=temp_file_path)
            logger.info(f"Файл {file_id} успешно скачан")
            
            # Открываем изображение и конвертируем в base64
            with open(temp_file_path, "rb") as image_file:
                logger.info(f"Конвертация файла {file_id} в base64 начата")
                # Отправляем изображение на обработку
                response = Requests().physics(
                    request=f"data:image/jpeg;base64,{base64.b64encode(image_file.read()).decode('utf-8')}",
                    photo=True
                )
                logger.info(f"Обработка файла {file_id} завершена")
            
            # Отправляем ответ пользователю
            await message.answer(response)
            logger.info(f"Ответ отправлен пользователю {message.from_user.id}")
            
            # Удаляем временный файл
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logger.info(f"Временный файл {temp_file_path} удален")
                
        except Exception as e:
            # В случае ошибки
            error_message = f"Произошла ошибка при обработке изображения: {str(e)}. Пожалуйста, попробуйте ввести условие задачи текстом."
            logger.error(f"Ошибка при обработке файла {file_id}: {str(e)}")
            await message.answer(error_message)
    else:
        await message.answer(
            "Я не могу обработать ваше сообщение в текущем состоянии. Пожалуйста, выберите раздел из меню",
            reply_markup=get_main_keyboard()
        )

@router.message(StateFilter(Form.section))
async def other_message_handler(message: Message, state: FSMContext):
    """Обработчик для всех остальных сообщений"""
    state_data = await state.get_data()
    logger.info(f"Получено сообщение: {message.text}")
    
    if state_data.get('section') == 'physics':
        try:
            response = Requests().physics(request=message.text, photo=False)
            await message.answer(response)
        except Exception as e:
            await message.answer(f"Произошла ошибка: {str(e)}")
    else:
        await message.answer(
            "Я не могу обработать ваше сообщение в текущем состоянии. Пожалуйста, выберите раздел из меню",
            reply_markup=get_main_keyboard()
        )

