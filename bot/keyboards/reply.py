from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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
                KeyboardButton(text="📝 Информация"),
                KeyboardButton(text="❓ Помощь")
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )
    return keyboard
