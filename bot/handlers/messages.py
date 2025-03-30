from aiogram import Router, F
from aiogram.types import Message
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
CHANNEL_ID = "-1002508751485"

# Функция для проверки подписки пользователя на канал
async def check_subscription(message: Message):
    """Проверка подписки пользователя на канал"""
    user_id = message.from_user.id  # ID пользователя
    try:
        # Получаем информацию о пользователе в канале
        member = await message.bot.get_chat_member(CHANNEL_ID, user_id)
        
        # Проверка, является ли пользователь подписчиком
        if member.status in ['member', 'administrator', 'creator']:
            return True
        else:
            return False
    except Exception as e:
        logger.error(f"Ошибка при проверке подписки: {e}")
        return False

# Обработчик для кнопки "Привет"
@router.message(F.text == "📙 Физика")
async def physics_button_handler(message: Message, state: FSMContext):
    """Обработчик для кнопки Физика"""
    
    # Проверка подписки
    if not await check_subscription(message):
        await message.answer(
            "❌ Для начала работы подпишитесь на наш Telegram-канал!\n🔗 https://t.me/neurals_etc"
        )
        return  # Прерываем выполнение обработчика
    
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
    
    # Проверка подписки
    if not await check_subscription(message):
        await message.answer(
            "❌ Для начала работы подпишитесь на наш Telegram-канал!\n🔗 https://t.me/neurals_etc"
        )
        return  # Прерываем выполнение обработчика
    
    text = os.getenv("Information_text")
    await message.answer(
        text,
        reply_markup=get_main_keyboard()
    )

# Обработчик для кнопки "Помощь"
@router.message(F.text == "❓ Помощь")
async def help_button_handler(message: Message):
    """Обработчик для кнопки Помощь"""
    
    # Проверка подписки
    if not await check_subscription(message):
        await message.answer(
            "❌ Для начала работы подпишитесь на наш Telegram-канал!\n🔗 https://t.me/neurals_etc"
        )
        return  # Прерываем выполнение обработчика
    
    text = os.getenv("Help_text")
    await message.answer(
        text,
        reply_markup=get_main_keyboard()
    )

# Обработчик для фотографий
@router.message(F.photo)
async def photo_handler(message: Message, state: FSMContext):
    """Обработчик для фотографий"""
    
    # Проверка подписки
    if not await check_subscription(message):
        await message.answer(
            "❌ Для начала работы подпишитесь на наш Telegram-канал!\n🔗 https://t.me/neurals_etc"
        )
        return  # Прерываем выполнение обработчика
    
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

# Обработчик для всех остальных сообщений
@router.message(StateFilter(Form.section))
async def other_message_handler(message: Message, state: FSMContext):
    """Обработчик для всех остальных сообщений"""
    
    # Проверка подписки
    if not await check_subscription(message):
        await message.answer(
            "❌ Для начала работы подпишитесь на наш Telegram-канал!\n🔗 https://t.me/neurals_etc"
        )
        return  # Прерываем выполнение обработчика
    
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