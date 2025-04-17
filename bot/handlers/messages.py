from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import FSInputFile
import os
import logging
from dotenv import load_dotenv

from bot.keyboards.reply import get_main_keyboard, get_next_question_keyboard, get_math_submenu_keyboard
from bot.utils.states import Form
from requests import Requests
import base64
from typing import Union, Tuple, BinaryIO
import tempfile

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
        await message.answer(text, reply_markup=get_main_keyboard())
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
    except Exception as e:
        # logger.error(f"Ошибка при удалении сообщений: {str(e)}")
        print(str(e))
        reply_markup=get_main_keyboard()

@router.message(F.text == "❓ Помощь")
async def help_button_handler(message: Message):
    try:
        text = os.getenv("Help_text")
        await message.answer(text, reply_markup=get_main_keyboard())
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
    except Exception as e:
        # logger.error(f"Ошибка при удалении сообщений: {str(e)}")
        print(str(e))
        reply_markup=get_main_keyboard()

@router.message(F.text == "🤖 ChatGPT o1-pro")
async def chatgpt_button_handler(message: Message, state: FSMContext):
    try:
        text = os.getenv("ChatGPT_answer_text")
        await state.set_state(Form.section)
        await state.update_data(section="chatgpt")
        await message.answer(text, reply_markup=get_main_keyboard())
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
    except Exception as e:
        print(str(e))
        reply_markup=get_main_keyboard()

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
        print(str(e))
        reply_markup=get_main_keyboard()

@router.message(F.text == "📕 Математика")
async def math_button_handler(message: Message, state: FSMContext):
    try:
        await state.set_state(Form.math_submenu)
        text = os.getenv("Math_choose_text")
        sent_message = await message.answer(text, reply_markup=get_math_submenu_keyboard())
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
    except Exception as e:

        print(str(e))
        reply_markup=get_main_keyboard()


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
        print(str(e))
        reply_markup=get_main_keyboard()



@router.message(F.text == "📚 Конспект")
async def math_button_handler(message: Message, state: FSMContext):
    try:
        await state.set_state(Form.abstract_submenu)
        text = os.getenv("Abstract_choose_text")
        sent_message = await message.answer(text, reply_markup=get_abstract_submenu_keyboard())
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
    except Exception as e:
        print(str(e))
        reply_markup=get_main_keyboard()


#Abstract menu






# Math menu
@router.message(F.text == "🧮 Решить задачу")
async def solve_math_handler(message: Message, state: FSMContext):
    try:
        text = os.getenv("Mathematic_answer_text")
        await state.set_state(Form.section)
        await state.update_data(section="mathematics")
        await message.answer(text)
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
    except Exception as e:
        print(str(e))
        reply_markup=get_main_keyboard()

@router.message(F.text == "📊 Построить график функции", StateFilter(Form.math_submenu))
async def plot_function_handler(message: Message, state: FSMContext):
    try:
        text = os.getenv("Math_graph_text")
        await state.set_state(Form.section)
        await state.update_data(section="mathematics", solution="graph", is_graph_mode=True)
        await message.answer(text)
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
    except Exception as e:
        print(str(e))
        reply_markup=get_main_keyboard()





# Solution menu
@router.message(F.text == "❓ Вопрос по задаче")
async def question_button_handler(message: Message, state: FSMContext):
    try:
        text = os.getenv("Question_answer_text")
        await state.set_state(Form.section)
        
        # Получаем предыдущее сообщение через message.reply_to_message
        solution_text = None
        if message.reply_to_message:
            solution_text = message.reply_to_message.text
            
        await state.update_data(section="question", solution=solution_text)
        
        # Сначала отправляем новое сообщение
        new_message = await message.answer(text, reply_markup=get_main_keyboard())
        
        # Затем удаляем старые сообщения
        try:
            # if message.message_id > 1:  # Проверяем, есть ли предыдущее сообщение
            #     await message.bot.delete_message(message.chat.id, message.message_id - 1)
            await message.delete()
        except Exception as delete_error:
            logger.error(f"Ошибка при удалении сообщений: {str(delete_error)}")
            
    except Exception as e:
        logger.error(f"Ошибка в обработчике вопроса: {str(e)}")
        await message.answer("Произошла ошибка при обработке запроса", reply_markup=get_main_keyboard())


@router.message(F.text == "➡️ Следующая задача")
async def next_question_button_handler(message: Message, state: FSMContext):
    try:
        state_data = await state.get_data()
        current_section = state_data.get('section')  # получаем текущую секцию из state_data
        
        # Добавляем проверку на None для текста из переменных окружения
        if current_section == 'physics':
            text = os.getenv("Physic_answer_text") or "Задайте свой вопрос по физике"
            next_section = 'physics'
        elif current_section == 'mathematics':
            text = os.getenv("Mathematic_answer_text") or "Задайте свой вопрос по математике"
            next_section = 'mathematics'
        elif current_section == 'chemistry':
            text = os.getenv("Chemistry_answer_text") or "Задайте свой вопрос по химии"
            next_section = 'chemistry'
        elif current_section == 'chatgpt':
            text = os.getenv("ChatGPT_answer_text") or "Задайте свой вопрос"
            next_section = 'chatgpt'
        else:
            text = os.getenv("ChatGPT_answer_text") or "Задайте свой вопрос"
            next_section = 'chatgpt'
            
        # Проверяем, что text не None перед отправкой
        if not text:
            text = "Пожалуйста, задайте свой вопрос"
            
        await state.set_state(Form.section)
        await state.update_data(section=next_section)
        await message.answer(text, reply_markup=get_main_keyboard())
        
        # Удаляем сообщения только после успешной отправки нового
        try:
            # await message.bot.delete_message(message.chat.id, message.message_id - 1)
            await message.delete()
        except Exception as delete_error:
            logger.error(f"Ошибка при удалении сообщений: {str(delete_error)}")
            
    except Exception as e:
        logger.error(f"Ошибка в обработчике следующей задачи: {str(e)}")
        await message.answer("Произошла ошибка при обработке запроса", reply_markup=get_main_keyboard())






# Requests
@router.message(F.photo)
async def photo_handler(message: Message, state: FSMContext):
    """Обработчик для фотографий"""
    try:
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        # await message.delete()
        wait_message = await message.answer(os.getenv("Wait_text"))
        
        # Start typing status after wait message
        await message.bot.send_chat_action(
            chat_id=message.chat.id,
            action="typing"
        )
        
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
            photo=True,
            solution=state_data.get('solution')
        )
        await message.bot.delete_message(message.chat.id, wait_message.message_id)
        await message.answer(response, parse_mode="HTML", reply_markup=get_next_question_keyboard())
    except Exception as e:
        # logger.error(f"Ошибка: {str(e)}")
        print(str(e))
        reply_markup=get_main_keyboard()

#gpt обработка
@router.message(StateFilter(Form.section))
async def other_message_handler(message: Message, state: FSMContext):
    """Обработчик для всех остальных текстовых сообщений"""
    try:
        # Отправляем сообщение о ожидании
        wait_message = await message.answer(os.getenv("Wait_text"))
        
        # Получаем данные из состояния
        state_data = await state.get_data()
        section = state_data.get('section')
        solution = state_data.get('solution')
        is_graph_mode = state_data.get('is_graph_mode', False)

        # Если режим графика активен, показываем статус отправки фото
        if is_graph_mode:
            await message.bot.send_chat_action(
                chat_id=message.chat.id,
                action="upload_photo"
            )
        else:
            # Иначе показываем статус печати
            await message.bot.send_chat_action(
                chat_id=message.chat.id,
                action="typing"
            )

        # Предварительная обработка математического выражения
        if section == "mathematics" and not is_graph_mode:
            # Заменяем знак равенства на минус для правильного решения уравнения
            request_text = message.text.replace("=", "-(").rstrip(")") + ")"
            # Убираем лишние пробелы
            request_text = request_text.replace(" ", "")
        else:
            request_text = message.text

        # Создаем экземпляр класса Requests
        requests = Requests()
        
        # Получаем ответ от модели
        response = requests.main(
            request=request_text,
            subject=section,
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
                    
                    # Отправляем изображение с подписью
                    await message.answer_photo(
                        photo=image,
                        caption=caption,
                        reply_markup=get_next_question_keyboard()
                    )
                    
                    # Сбрасываем флаг после отправки графика
                    await state.update_data(is_graph_mode=False)
                finally:
                    # Удаляем временный файл после использования
                    if os.path.exists(temp_file.name):
                        os.unlink(temp_file.name)
        else:
            # Это текстовый ответ
            await message.answer(response, parse_mode="HTML", reply_markup=get_next_question_keyboard())
            # Сбрасываем флаг если это не график
            await state.update_data(is_graph_mode=False)

    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {str(e)}")
        await message.answer(
            "Произошла ошибка при обработке запроса. Пожалуйста, попробуйте еще раз.",
            reply_markup=get_next_question_keyboard()
        )
        await state.update_data(is_graph_mode=False)
