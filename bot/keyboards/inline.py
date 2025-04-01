from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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