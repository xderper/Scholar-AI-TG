from aiogram import Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
import os

CHANNEL_ID = "-1002508751485"

def get_main_keyboard():
    """Возвращает основную клавиатуру"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📙 Физика", callback_data="physics")],
        [InlineKeyboardButton(text="📝 Информация", callback_data="information")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")]
    ])

async def check_subscription(user_id: int, bot):
    """Проверка подписки пользователя на канал"""
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def get_subscription_keyboard():
    """Возвращает клавиатуру с кнопками подписки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="IT Thinker", url="https://t.me/neurals_etc")],
        [InlineKeyboardButton(text="Проверить подписку✅", callback_data="check_subscription")]
    ])

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    if not await check_subscription(message.from_user.id, message.bot):
        await message.answer(
            "❌ Для начала работы подпишитесь на наш Telegram-канал!",
            reply_markup=get_subscription_keyboard()
        )
        return
    await message.answer(os.getenv("Start_text").format(user_name=message.from_user.first_name))

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    if not await check_subscription(message.from_user.id, message.bot):
        await message.answer(
            "❌ Для начала работы подпишитесь на наш Telegram-канал!",
            reply_markup=get_subscription_keyboard()
        )
        return
    await message.answer(os.getenv("Help_text"), reply_markup=get_main_keyboard())

@router.callback_query(lambda c: c.data == "check_subscription")
async def check_subscription_callback(query: CallbackQuery):
    """Обработчик для кнопки 'Проверить подписку'"""
    is_subscribed = await check_subscription(query.from_user.id, query.bot)
    
    new_text = "✅ Вы подписаны, продолжаю работу!" if is_subscribed else "❌ Вы не подписаны. Попробуйте снова.\n\nПодпишитесь на канал и нажмите 'Проверить подписку'."
    
    if query.message.text != new_text:
        await query.message.edit_text(
            new_text,
            reply_markup=get_subscription_keyboard()
        )
    
    await query.answer("Проверка подписки завершена.")
