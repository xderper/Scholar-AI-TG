from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import FSInputFile
import os
import logging
from dotenv import load_dotenv

from bot.keyboards.reply import get_main_keyboard, get_math_submenu_keyboard, get_abstract_keyboard
from bot.keyboards.inline import get_feedback_keyboard
from bot.utils.states import Form
from requests import Requests
import base64
from typing import Union, Tuple, BinaryIO
import tempfile
import openai
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

# Создаем роутер для текстовых сообщений
router = Router()

# ID канала, на который нужно проверить подписку
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Main Menu
@router.message(F.text == "📝 Информация")
async def information_button_handler(message: Message):
    try:
        text = os.getenv("Information_text")
        await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="HTML")
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
    except Exception as e:
        logger.error(f"Error in messages: {str(e)}")

@router.message(F.text == "❓ Помощь")
async def help_button_handler(message: Message):
    try:
        text = os.getenv("Help_text")
        await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="HTML")
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
    except Exception as e:
        logger.error(f"Error in messages: {str(e)}")

@router.message(F.text == "🤖 ChatGPT o1-pro")
async def chatgpt_button_handler(message: Message, state: FSMContext):
    try:
        text = os.getenv("ChatGPT_answer_text")
        await state.set_state(Form.section)
        await state.update_data(section="chatgpt")
        await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="HTML")
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
    except Exception as e:
        logger.error(f"Error in messages: {str(e)}")

@router.message(F.text == "📙 Физика")
async def physics_button_handler(message: Message, state: FSMContext):
    try:
        text = os.getenv("Physic_answer_text")
        await state.set_state(Form.section)
        await state.update_data(section="physics")
        await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="HTML")
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
    except Exception as e:
        logger.error(f"Error in messages: {str(e)}")

@router.message(F.text == "📕 Математика")
async def math_button_handler(message: Message, state: FSMContext):
    try:
        await state.set_state(Form.math_submenu)
        text = os.getenv("Math_choose_text")
        sent_message = await message.answer(text, reply_markup=get_math_submenu_keyboard(), parse_mode="HTML")
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
    except Exception as e:
        logger.error(f"Error in messages: {str(e)}")

@router.message(F.text == "🔙 Назад", StateFilter(Form.math_submenu))
async def back_from_math_handler(message: Message, state: FSMContext):
    try:
        # Получаем имя пользователя
        user_name = message.from_user.first_name or "друг"
        # Формируем приветственное сообщение
        start_text = os.getenv("Start_text").format(user_name=user_name)
        # Возвращаемся к главному меню
        await state.set_state(None)
        await message.answer(start_text, reply_markup=get_main_keyboard(), parse_mode="HTML")
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
    except Exception as e:
        logger.error(f"Error in messages: {str(e)}")

@router.message(F.text == "📗 Химия")
async def chemistry_button_handler(message: Message, state: FSMContext):
    try:
        text = os.getenv("Chemistry_answer_text")
        await state.set_state(Form.section)
        await state.update_data(section="chemistry")
        await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="HTML")
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
    except Exception as e:
        logger.error(f"Error in messages: {str(e)}")

@router.message(F.text == "📚 Конспект")
async def abstract_button_handler(message: Message, state: FSMContext):
    try:
        await state.set_state(Form.section)
        await state.update_data(section="abstract")
        text = os.getenv("Abstract_text")
        await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="HTML")
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
    except Exception as e:
        logger.error(f"Error in messages: {str(e)}")


# Math menu
@router.message(F.text == "🧮 Решить задачу")
async def solve_math_handler(message: Message, state: FSMContext):
    try:
        text = os.getenv("Mathematic_answer_text")
        await state.set_state(Form.section)
        await state.update_data(section="mathematics")
        await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="HTML")
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
    except Exception as e:
        logger.error(f"Error in messages: {str(e)}")

@router.message(F.text == "📊 Построить график функции", StateFilter(Form.math_submenu))
async def plot_function_handler(message: Message, state: FSMContext):
    try:
        text = os.getenv("Math_graph_text")
        await state.set_state(Form.section)
        await state.update_data(section="mathematics", solution="graph")
        await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="HTML")
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
    except Exception as e:
        logger.error(f"Error in messages: {str(e)}")



# Создаем общий обработчик для аудио и голосовых сообщений
@router.message(F.voice | F.audio)
async def audio_voice_handler(message: Message, state: FSMContext):
    """Общий обработчик для аудио и голосовых сообщений"""
    try:
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        wait_message = await message.answer(os.getenv("Wait_text"), parse_mode="HTML")
        
        # Start typing status after wait message
        await message.bot.send_chat_action(
            chat_id=message.chat.id,
            action="typing"
        )
        
        current_state = await state.get_state()
        state_data = await state.get_data()

        # Если нет состояния, устанавливаем состояние chatgpt
        if not current_state:
            await state.set_state(Form.section)
            await state.update_data(section="chatgpt")
            state_data = await state.get_data()

        section = state_data.get('section', 'chatgpt')
        solution = state_data.get('solution')

        # Определяем тип сообщения и скачиваем файл
        if message.voice:
            # Это голосовое сообщение
            file = await message.bot.get_file(message.voice.file_id)
            file_path = file.file_path
            temp_file_path = os.path.join("temp", f"temp_{message.voice.file_id}.oga")
            file_type = "голосовое сообщение"
        else:
            # Это аудио файл
            file = await message.bot.get_file(message.audio.file_id)
            file_path = file.file_path
            temp_file_path = os.path.join("temp", f"temp_{message.audio.file_id}.ogg")
            file_type = "аудио файл"
        
        # Скачиваем файл
        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
        await message.bot.download_file(file_path, destination=temp_file_path)

        # Получаем подпись к сообщению, если есть
        caption = message.caption or ""
        
        # Создаем экземпляр Requests
        requests_client = Requests()
        
        # Получаем транскрипцию аудио
        transcript = requests_client.main(audio=temp_file_path)
        
        # Если транскрипция успешна и это строка
        if transcript and isinstance(transcript, str) and len(transcript.strip()) > 0:
            # Показываем пользователю результаты транскрипции
            await message.bot.delete_message(message.chat.id, wait_message.message_id)
            wait_message = await message.answer(
                f"Текст из {file_type}: <i>{transcript}</i>\n\nФормирую ответ...",
                parse_mode="HTML"
            )
            
            # Объединяем подпись и транскрипцию
            if caption:
                user_text = f"{caption}\n\n{transcript}"
            else:
                user_text = transcript
                
            # Отправляем запрос модели
            response = requests_client.main(
                request=user_text,
                subject=section,
                solution=solution
            )
        else:
            
            if caption:
                response = requests_client.main(
                    request=caption,
                    subject=section,
                    solution=solution
                )
            else:
                response = f"Не удалось обработать {file_type}. Пожалуйста, добавьте текстовое описание или отправьте текстовый запрос."

        # Удаляем временный файл после использования
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        
        await message.bot.delete_message(message.chat.id, wait_message.message_id)
        
        feedback_question = "\n\n✨ Понравился ли вам ответ? 🌟"
        await message.answer(response + feedback_question, parse_mode="HTML", reply_markup=get_feedback_keyboard())
            
    except Exception as e:
        logger.error(f"Error in audio/voice handler: {str(e)}", exc_info=True)
        await message.answer(
            "Произошла ошибка при обработке аудио. Пожалуйста, попробуйте текстовый запрос.",
            reply_markup=get_main_keyboard()
        )

@router.message(F.photo)
async def photo_handler(message: Message, state: FSMContext):
    """Обработчик для фотографий"""
    try:
        wait_message = await message.answer(os.getenv("Wait_text"), parse_mode="HTML")
        await message.bot.send_chat_action(
            chat_id=message.chat.id,
            action="typing"
        )
        current_state = await state.get_state()
        state_data = await state.get_data()
        if not current_state:
            await state.set_state(Form.section)
            await state.update_data(section="chatgpt")
            state_data = await state.get_data()
        solution = state_data.get('solution')
        section = state_data.get('section', 'chatgpt')
        # Получаем последнюю фотографию из списка
        photo = message.photo[-1]  # берем самую большую версию
        file = await message.bot.get_file(photo.file_id)
        file_path = file.file_path
        temp_file_path = os.path.join("temp", f"temp_{photo.file_id}.jpg")
        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
        await message.bot.download_file(file_path, destination=temp_file_path)
        # Сохраняем file_id фото как задачу пользователя
        await state.update_data(user_task_photo=photo.file_id)
        # Конвертируем в base64
        with open(temp_file_path, "rb") as image_file:
            image_data = f"data:image/jpeg;base64,{base64.b64encode(image_file.read()).decode('utf-8')}"
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        text_content = message.caption or ""
        response = Requests().main(
            request=text_content,
            subject=section,
            photo=image_data,
            audio=None,
            solution=solution
        )
        await message.bot.delete_message(message.chat.id, wait_message.message_id)
        if section == "abstract":
            await message.answer(response, parse_mode="HTML", reply_markup=get_abstract_keyboard())
        else:
            feedback_question = "\n\n✨ Понравился ли вам ответ? 🌟"
            await message.answer(response + feedback_question, parse_mode="HTML", reply_markup=get_feedback_keyboard())
    except Exception as e:
        logger.error(f"Error in photo handler: {str(e)}", exc_info=True)
        await message.answer(str(e), reply_markup=get_main_keyboard())


@router.message()
async def fallback_message_handler(message: Message, state: FSMContext):
    """Обработчик для всех остальных сообщений, которые не обработаны другими хэндлерами"""
    try:
        # Проверяем текущее состояние
        current_state = await state.get_state()
        
        # Если состояние feedback_message, пропускаем обработку
        if current_state == Form.feedback_message:
            return
            
        # Если состояние не установлено, устанавливаем его на chatgpt
        if not current_state:
            await state.set_state(Form.section)
            await state.update_data(section="chatgpt")
            
            # Отправляем сообщение о том, что бот готов обрабатывать запросы
            wait_message = await message.answer(
                "Я готов помочь! Обрабатываю ваш запрос...", 
                parse_mode="HTML"
            )
        else:
            wait_message = await message.answer(os.getenv("Wait_text"), parse_mode="HTML")
            
        await message.bot.send_chat_action(
                chat_id=message.chat.id,
                action="typing"
        )
        
        # Получаем данные из состояния
        state_data = await state.get_data()
        section = state_data.get('section', 'chatgpt')  # По умолчанию используем chatgpt
        solution = state_data.get('solution')
        
        # Сохраняем текст задачи пользователя
        await state.update_data(user_task=message.text)
        
        # Создаем экземпляр класса Requests
        requests = Requests()
        
        # Получаем ответ от модели
        response = requests.main(
            request=message.text,
            subject=section,
            photo=None,
            audio=None,
            solution=solution
        )
        
        # Удаляем сообщение об ожидании
        await message.bot.delete_message(message.chat.id, wait_message.message_id)
        
        # Проверяем тип ответа
        if isinstance(response, tuple) and len(response) == 2:
            # Это график
            image_buffer, caption = response
            
            # Создаем временный файл для сохранения изображения
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                try:
                    # Записываем содержимое буфера во временный файл
                    image_buffer.seek(0)
                    temp_file.write(image_buffer.read())
                    temp_file.close()  # Закрываем файл перед использованием
                    
                    # Создаем FSInputFile из временного файла
                    image = FSInputFile(temp_file.name)
                    
                    # Отправляем изображение с подписью и вопросом о качестве ответа
                    await message.answer_photo(
                        photo=image,
                        caption=caption + "\n\n✨ Понравился ли вам ответ? 🌟",
                        reply_markup=get_feedback_keyboard()
                    )
                finally:
                    # Удаляем временный файл после использования
                    if os.path.exists(temp_file.name):
                        os.unlink(temp_file.name)
        else:
            # Это текстовый ответ
            feedback_question = "\n\n✨ Понравился ли вам ответ? 🌟"
            await message.answer(response + feedback_question, parse_mode="HTML", reply_markup=get_feedback_keyboard())
    except Exception as e:
        logger.error(f"Error in fallback handler: {str(e)}", exc_info=True)
        await message.answer(str(e),
            reply_markup=get_main_keyboard()
        )

