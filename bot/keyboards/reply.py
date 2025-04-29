from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_math_submenu_keyboard():
    buttons = [
        [KeyboardButton(text="🧮 Решить задачу")],
        [KeyboardButton(text="📊 Построить график функции")],
        [KeyboardButton(text="🔙 Назад")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard

# Основная клавиатура
def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Создает и возвращает основную клавиатуру бота"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📙 Физика"),
                KeyboardButton(text="📕 Математика"),
                KeyboardButton(text="📗 Химия")
            ],
            [
                KeyboardButton(text="📚 Конспект")
            ],
            [   
                KeyboardButton(text="🤖 ChatGPT o1-pro")
            ],
            [
                KeyboardButton(text="📝 Информация"),
                KeyboardButton(text="❓ Помощь")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,  # Клавиатура будет закреплена
        input_field_placeholder="Выберите действие..."
    )
    return keyboard

def get_abstract_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру для раздела конспектов"""
    keyboard = [
        [KeyboardButton(text="➡️ Далее к задачам")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    