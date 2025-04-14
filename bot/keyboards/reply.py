from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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
                KeyboardButton(text="📕 Математика")
            ],
            [
                KeyboardButton(text="📗 Химия")
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
        input_field_placeholder="Выберите действие..."
    )
    return keyboard

def get_next_question_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="❓ Вопрос по задаче")
            ],
            [
                KeyboardButton(text="➡️ Следующая задача")
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )
def get_next_plot_keyboard():
    """Создает клавиатуру только с кнопкой 'Следующая задача' для графиков"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="➡️ Следующая задача")
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )