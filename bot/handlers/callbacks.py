from aiogram import Router, F
from aiogram.types import CallbackQuery

# Создаем роутер для callback-запросов
router = Router()

# Обработчик для callback "confirm_yes"
# @router.callback_query(F.data == "confirm_yes")
# async def callback_confirm_yes(callback: CallbackQuery):
#     """Обработчик для подтверждения действия"""
#     # Отвечаем на callback, чтобы убрать часы загрузки на кнопке
#     await callback.answer("Действие подтверждено!")
    
#     # Обновляем сообщение
#     await callback.message.edit_text(
#         "✅ Действие успешно подтверждено!"
#     )
