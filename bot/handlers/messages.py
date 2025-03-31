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
CHANNEL_ID = "-1002508751485"

# Функция для получения инлайн-клавиатуры с кнопками подписки
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

# Функция для проверки подписки пользователя на канал
async def check_subscription(user_id: int, bot):
    """Проверка подписки пользователя на канал"""
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Ошибка при проверке подписки: {e}")
        return False

# Обработчик для кнопки проверки подписки
@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback_query: CallbackQuery):
    is_subscribed = await check_subscription(callback_query.from_user.id, callback_query.bot)

    if is_subscribed:
        await callback_query.message.edit_text(
            "✅ Вы подписаны, продолжаю работу!",
            reply_markup=get_subscription_keyboard()  # Кнопки остаются
        )
    else:
        await callback_query.message.edit_text(
            "❌ Вы не подписаны. Попробуйте снова.",
            reply_markup=get_subscription_keyboard()  # Кнопки остаются
        )

    await callback_query.answer("Проверка подписки завершена.")

# Обработчики сообщений
@router.message(F.text == "📙 Физика")
async def physics_button_handler(message: Message, state: FSMContext):
    await message.delete()
    if not await check_subscription(message.from_user.id, message.bot):
        await message.answer("❌ Вы не подписаны. Попробуйте снова.", reply_markup=get_subscription_keyboard())
        return

    text = os.getenv("Physic_answer_text")
    await state.set_state(Form.section)
    await state.update_data(section="physics")
    await message.answer(text, reply_markup=get_main_keyboard())

@router.message(F.text == "📝 Информация")
async def information_button_handler(message: Message):
    await message.delete()
    if not await check_subscription(message.from_user.id, message.bot):
        await message.answer("❌ Вы не подписаны. Попробуйте снова.", reply_markup=get_subscription_keyboard())
        return

    text = os.getenv("Information_text")
    await message.answer(text, reply_markup=get_main_keyboard())

@router.message(F.text == "❓ Помощь")
async def help_button_handler(message: Message):
    await message.delete()
    if not await check_subscription(message.from_user.id, message.bot):
        await message.answer("❌ Вы не подписаны. Попробуйте снова.", reply_markup=get_subscription_keyboard())
        return

    text = os.getenv("Help_text")
    await message.answer(text, reply_markup=get_main_keyboard())

# Обработчик для фотографий
@router.message(F.photo)
async def photo_handler(message: Message, state: FSMContext):
    """Обработчик для фотографий"""
    
    if not await check_subscription(message.from_user.id, message.bot):
        await message.answer("❌ Вы не подписаны. Попробуйте снова.", reply_markup=get_subscription_keyboard())
        return  

    current_state = await state.get_state()
    state_data = await state.get_data()
    
    if current_state == Form.section and state_data.get('section') == 'physics':
        logger.info(f"Получено фото от пользователя {message.from_user.id}")
        
        photo = message.photo[-1]
        await message.answer("Получил ваше фото с задачей. Обрабатываю...")

        try:
            file_id = photo.file_id
            file = await message.bot.get_file(file_id)
            file_path = file.file_path
            logger.info(f"Скачивание файла {file_id} начато")

            temp_file_path = os.path.join("temp", f"temp_{file_id}.jpg")
            os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)

            await message.bot.download_file(file_path, destination=temp_file_path)
            logger.info(f"Файл {file_id} успешно скачан")

            with open(temp_file_path, "rb") as image_file:
                logger.info(f"Конвертация файла {file_id} в base64 начата")
                response = Requests().physics(
                    request=f"data:image/jpeg;base64,{base64.b64encode(image_file.read()).decode('utf-8')}",
                    photo=True
                )
                logger.info(f"Обработка файла {file_id} завершена")

            await message.answer(response, parse_mode="HTML")
            logger.info(f"Ответ отправлен пользователю {message.from_user.id}")

            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logger.info(f"Временный файл {temp_file_path} удален")

        except Exception as e:
            error_message = f"Произошла ошибка при обработке изображения: {str(e)}. Попробуйте ввести условие задачи текстом."
            logger.error(f"Ошибка при обработке файла {file_id}: {str(e)}")
            await message.answer(error_message)
    else:
        await message.answer("Я не могу обработать ваше сообщение в текущем состоянии. Пожалуйста, выберите раздел из меню", reply_markup=get_main_keyboard())

# Обработчик для всех остальных сообщений
@router.message(StateFilter(Form.section))
async def other_message_handler(message: Message, state: FSMContext):
    """Обработчик для всех остальных сообщений"""
    
    if not await check_subscription(message.from_user.id, message.bot):
        await message.answer("❌ Вы не подписаны. Попробуйте снова.", reply_markup=get_subscription_keyboard())
        return  

    state_data = await state.get_data()
    logger.info(f"Получено сообщение: {message.text}")

    if state_data.get('section') == 'physics':
        try:
            await message.answer("Получил вашу задачу. Обрабатываю...")
            response = Requests().physics(request=message.text, photo=False)
            await message.answer(response, parse_mode="HTML")
        except Exception as e:
            await message.answer(f"Произошла ошибка: {str(e)}")
    else:
        await message.answer("Я не могу обработать ваше сообщение в текущем состоянии. Пожалуйста, выберите раздел из меню", reply_markup=get_main_keyboard())
