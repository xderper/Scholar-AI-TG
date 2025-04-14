from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import FSInputFile
import os
import logging
from dotenv import load_dotenv
from bot.keyboards.reply import get_main_keyboard, get_next_question_keyboard, get_next_plot_keyboard
from bot.utils.states import Form
from requests import Requests
import base64
from bot.keyboards.reply import get_main_keyboard, get_math_submenu_keyboard
from bot.utils.states import Form
from bot.utils.plotting import generate_function_plot
import tempfile
import asyncio
import matplotlib.pyplot as plt
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
        # logger.error(f"Ошибка: {str(e)}")
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
        # Сначала отправляем новое сообщение
        sent_message = await message.answer("Выберите действие:", reply_markup=get_math_submenu_keyboard())
        # Удаляем предыдущее сообщение и сообщение пользователя
        try:
            await message.bot.delete_message(message.chat.id, message.message_id - 1)
            await message.delete()
        except Exception as delete_error:
            print(f"Ошибка при удалении сообщений: {str(delete_error)}")
    except Exception as e:
        print(str(e))
        reply_markup=get_main_keyboard()

@router.message(F.text == "🧮 Решить задачу")
async def solve_math_handler(message: Message, state: FSMContext):
    try:
        text = os.getenv("Mathematic_answer_text")
        await state.set_state(Form.section)
        await state.update_data(section="mathematics")
        # Сначала отправляем новое сообщение
        sent_message = await message.answer(text, reply_markup=get_main_keyboard())
        # Удаляем предыдущее сообщение и сообщение пользователя
        try:
            await message.bot.delete_message(message.chat.id, message.message_id - 1)
            await message.delete()
        except Exception as delete_error:
            print(f"Ошибка при удалении сообщений: {str(delete_error)}")
    except Exception as e:
        print(str(e))
        reply_markup=get_main_keyboard()

@router.message(F.text == "📊 Построить график функции", StateFilter(Form.math_submenu))
async def plot_function_handler(message: Message, state: FSMContext):
    try:
        await state.set_state(Form.plot_function)
        await message.answer("Конечно. Введите функцию для построения графика (например, 'y = x^2 + 3x - 5')", 
                           reply_markup=get_main_keyboard())
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        await message.delete()
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        await message.answer("Произошла ошибка", reply_markup=get_main_keyboard())

@router.message(StateFilter(Form.plot_function))
async def handle_plot_function(message: Message, state: FSMContext):
    temp_file_path = None
    try:
        # Отправляем сообщение о начале обработки
        wait_message = await message.answer("Генерирую график, пожалуйста подождите...")
        
        try:
            # Получаем формулу от нейросети
            requests = Requests()
            formula = requests.main(message.text, subject="mathematics", photo=False)
            
            if not formula or formula == "x" or "ошибка" in formula.lower():
                raise ValueError("Не удалось получить корректную формулу из запроса")
            
            # Генерируем график используя полученную формулу
            plot_buffer, cleaned_function = generate_function_plot(formula)
            
            # Создаем временный файл с уникальным именем
            temp_file_path = os.path.join(tempfile.gettempdir(), f'plot_{message.message_id}.png')
            
            # Записываем данные из буфера в файл
            with open(temp_file_path, 'wb') as tmp_file:
                plot_buffer.seek(0)
                tmp_file.write(plot_buffer.getvalue())
            
            # Создаем InputFile из файла
            input_file = FSInputFile(temp_file_path)
            
            # Отправляем изображение
            await message.answer_photo(
                photo=input_file,
                caption=(
                    f"График функции: {cleaned_function}\n"
                    f"Исходный запрос: {message.text}"
                ),
                reply_markup=get_next_plot_keyboard()
            )
            
            # Сохраняем текущую функцию в состоянии
            await state.update_data(solution=f"График функции: {cleaned_function}\nИсходный запрос: {message.text}")
            # Возвращаемся в главное меню
            await state.set_state(Form.section)
            
        except ValueError as ve:
            logger.error(f"Ошибка при построении графика: {str(ve)}\nЗапрос пользователя: {message.text}")
            await message.answer(
                "Ошибка при построении графика:\n\n"
                "Примеры корректных запросов:\n"
                "- построй параболу\n"
                "- нарисуй синусоиду\n"
                "- график квадратного корня\n"
                "- построй график x в кубе\n"
                "- нарисуй гиперболу\n"
                "- построй график y = 2x + 1",
                reply_markup=get_main_keyboard()
            )
        
        # Удаляем сообщение ожидания
        await wait_message.delete()
            
    except Exception as e:
        logger.error(f"Общая ошибка при обработке запроса: {str(e)}\n"
                    f"Тип ошибки: {type(e).__name__}\n"
                    f"Запрос пользователя: {message.text}")
        await message.answer(
            "Ошибка при построении графика. Попробуйте переформулировать запрос.",
            reply_markup=get_main_keyboard()
        )
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                plt.close('all')
                await asyncio.sleep(1)
                os.unlink(temp_file_path)
            except Exception as del_error:
                logger.error(f"Ошибка при удалении временного файла: {str(del_error)}")

@router.message(F.text == "🔙 Назад")
async def back_to_main_handler(message: Message, state: FSMContext):
    try:
        await state.set_state(Form.section)
        # Сначала отправляем новое сообщение
        sent_message = await message.answer("Выберите раздел:", reply_markup=get_main_keyboard())
        # Удаляем предыдущее сообщение и сообщение пользователя
        try:
            await message.bot.delete_message(message.chat.id, message.message_id - 1)
            await message.delete()
        except Exception as delete_error:
            print(f"Ошибка при удалении сообщений: {str(delete_error)}")
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


@router.message(F.photo)
async def photo_handler(message: Message, state: FSMContext):
    """Обработчик для фотографий"""
    try:
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        # await message.delete()
        wait_message = await message.answer(os.getenv("Wait_text"))

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
    try:
        await message.bot.delete_message(message.chat.id, message.message_id - 1)
        # await message.delete()
        state_data = await state.get_data()
        wait_message = await message.answer(os.getenv("Wait_text"))
        await message.bot.send_chat_action(
            chat_id=message.chat.id,
            action="typing"
        )
        response = Requests().main(request=message.text, subject = state_data.get('section'), solution=state_data.get('solution'), photo=False)
        await message.bot.delete_message(message.chat.id, wait_message.message_id)
        await message.answer(response, parse_mode="HTML", reply_markup=get_next_question_keyboard())

    except Exception as e:
        # logger.error(f"Ошибка: {str(e)}")
        print(str(e))
        reply_markup=get_main_keyboard()
