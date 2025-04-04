from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.keyboards.reply import get_main_keyboard
from bot.keyboards.inline import get_subscription_keyboard
import os
from bot.utils.utils import check_subscription
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Создаем роутер для callback-запросов
router = Router()

@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery, state: FSMContext):
    try:
        is_subscribed = await check_subscription(callback.from_user.id, callback.bot)
        if is_subscribed:
            await callback.message.answer(os.getenv("Start_text").format(user_name=callback.from_user.first_name), reply_markup=get_main_keyboard())
            await callback.message.delete()
        else:
            await callback.message.answer(
                os.getenv("Subscribe_text"),
                reply_markup=get_subscription_keyboard()
            )
    except Exception as e:
        print(f"Error checking subscription: {str(e)}")
        await callback.message.answer(
            "Произошла ошибка при проверке подписки. Попробуйте позже.",
            reply_markup=get_subscription_keyboard()
        )