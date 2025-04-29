from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.keyboards.reply import get_main_keyboard
from bot.keyboards.inline import get_subscription_keyboard
import os
from aiogram.types import Message
from bot.utils.utils import check_subscription
from dotenv import load_dotenv
from bot.utils.states import Form

# Загружаем переменные окружения
load_dotenv()

# Создаем роутер для callback-запросов
router = Router()

@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery, state: FSMContext):
    try:
        is_subscribed = await check_subscription(callback.from_user.id, callback.bot)
        if is_subscribed:
            text = os.getenv("Start_text")
            await callback.message.answer(text, reply_markup=get_main_keyboard(), parse_mode="HTML")
            await callback.message.delete()
            # await callback.answer("Подписка подтверждена!")
        else:
            subscribe_text = os.getenv("Subscribe_text")
            await callback.message.answer(
                subscribe_text,
                reply_markup=get_subscription_keyboard(),
                parse_mode="HTML"
            )
            # await callback.answer("Подписка не найдена. Пожалуйста, подпишитесь на канал.")
    except Exception as e:
        print(f"Ошибка при проверке подписки: {str(e)}")
        await callback.answer("Произошла ошибка при проверке подписки.")



@router.callback_query(F.data == "feedback_yes")
async def positive_feedback_handler(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None) 
    await callback.message.answer(os.getenv("POS_FEEDBACK_TEXT"), parse_mode="HTML")
    await callback.bot.send_message(
        chat_id=os.getenv("FEEDBACK_GROUP_ID"),
        text=f"👍 Положительный отзыв от пользователя: @{callback.from_user.username or callback.from_user.first_name}"
    )
    await callback.answer()


@router.callback_query(F.data == "feedback_no")
async def negative_feedback_handler(callback: CallbackQuery, state: FSMContext):
    try:
        # Устанавливаем состояние для сбора обратной связи
        await state.set_state(Form.feedback_message)
        # Устанавливаем секцию отзыва
        await state.update_data(section="feedback")

        # Запрашиваем у пользователя подробности
        await callback.message.edit_reply_markup(reply_markup=None) 
        await callback.message.answer(os.getenv("NEGATIVE_FEEDBACK_PROMPT"), parse_mode="HTML")
        await callback.answer()
    except Exception as e:
        print(f"Ошибка при отправке отзыва: {str(e)}")
        await callback.answer("Произошла ошибка. Пожалуйста, попробуйте еще раз.")

@router.message(Form.feedback_message)
async def feedback_message_handler(message: Message, state: FSMContext):
    try:
        # Проверяем, что это действительно отзыв
        state_data = await state.get_data()
        
        if state_data.get('section') != 'feedback':
            # Если это не отзыв, возвращаемся к обычной обработке
            await state.clear()
            return

        text = f"📝 Отзыв от пользователя: @{message.from_user.username or message.from_user.first_name}\n\n{message.text}"
        await message.bot.send_message(
            chat_id=os.getenv("FEEDBACK_GROUP_ID"),
            text=text
        )
        await message.answer(os.getenv("FEEDBACK_SUCCESS_TEXT"), reply_markup=get_main_keyboard())
        # Сбрасываем состояние
        await state.clear()
    except Exception as e:
        await message.answer(os.getenv("FEEDBACK_ERROR_TEXT"), reply_markup=get_main_keyboard())
        print(f"Ошибка при отправке отзыва: {str(e)}")
        await state.clear()

@router.callback_query(F.data == "question_help")
async def question_help_handler(callback: CallbackQuery, state: FSMContext):
    try:
        text = os.getenv("Question_answer_text")
        await state.set_state(Form.section)
        
        # Получаем предыдущее сообщение через callback.message
        solution_text = callback.message.text
        
        await state.update_data(section="question", solution=solution_text)
        await callback.message.edit_reply_markup(reply_markup=None)
        # Сначала отправляем новое сообщение
        await callback.message.answer(text, reply_markup=get_main_keyboard(), parse_mode="HTML")
        

        await callback.answer()
            
    except Exception as e:
        print(f"Error in messages: {str(e)}")
        await callback.message.answer("Произошла ошибка при обработке запроса", reply_markup=get_main_keyboard())
        await callback.answer()

