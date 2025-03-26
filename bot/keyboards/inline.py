from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Инлайн-клавиатура для подтверждения действий
def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Создает и возвращает инлайн-клавиатуру для подтверждения действий"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data="confirm_yes"),
                InlineKeyboardButton(text="❌ Нет", callback_data="confirm_no")
            ]
        ]
    )
    return keyboard

# Инлайн-клавиатура с URL-кнопкой
def get_url_keyboard(url: str, text: str = "Открыть ссылку") -> InlineKeyboardMarkup:
    """Создает и возвращает инлайн-клавиатуру с URL-кнопкой"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=text, url=url)
            ]
        ]
    )
    return keyboard
