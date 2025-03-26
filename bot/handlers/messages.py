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

@router.message()
async def handle_message(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == 'physic':
        # Получаем ответ от ChatGPT
        raw_response = Requests().physic(message.text)
        
        try:
            # Форматируем ответ для лучшего отображения в Telegram
            formatted_response = format_response_for_telegram(raw_response)
            
            # Отправляем отформатированный ответ
            await message.answer(
                formatted_response,
                parse_mode="HTML"
            )
        except Exception as e:
            # В случае ошибки форматирования отправляем исходный ответ
            await message.answer(
                f"Ответ: {raw_response}"
            )
    else:
        await message.answer("Вы не в разделе Физика")

def format_response_for_telegram(text):
    """
    Форматирует текст для лучшего отображения в Telegram
    
    Args:
        text (str): Исходный текст от ChatGPT
    
    Returns:
        str: Отформатированный текст для Telegram
    """
    # Используем более простой подход к форматированию
    # Telegram поддерживает только <b>, <i>, <code>, <pre>, <a>
    
    # Сначала удалим все LaTeX-разметки
    text = text.replace('\\(', '').replace('\\)', '')
    text = text.replace('\\{', '{').replace('\\}', '}')
    text = text.replace('\\text{', '').replace('}', '')
    text = text.replace('\\frac{', '').replace('}{', '/').replace('}', '')
    text = text.replace('\\theta', 'θ')
    text = text.replace('\\circ', '°')
    text = text.replace('\\approx', '≈')
    text = text.replace('\\sqrt{', '√(').replace('}', ')')
    
    # Заменим ** на <b></b> только если они идут парами
    parts = text.split('**')
    if len(parts) > 1 and len(parts) % 2 == 1:  # Проверяем, что ** идут парами
        for i in range(1, len(parts), 2):
            parts[i] = f"<b>{parts[i]}</b>"
        text = ''.join(parts)
    
    # Добавляем переносы строк для лучшей читаемости
    text = text.replace('. ', '.\n')
    
    # Выделяем заголовки жирным шрифтом
    for section in ["Дано:", "Найти:", "Решение:", "По закону сохранения энергии:"]:
        text = text.replace(section, f"\n<b>{section}</b>\n")
    
    # Разделяем пункты решения пустыми строками
    for i in range(1, 10):
        text = text.replace(f"{i}. ", f"\n<b>{i}.</b> ")
    
    # Заменяем формулы энергии на более читаемый формат
    text = text.replace('E_{пот}', 'E пот')
    text = text.replace('E_{кин}', 'E кин')
    text = text.replace('F_{разр}', 'F разр')
    
    return text