from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    section = State()
    solution = State()
    math_submenu = State()
    abstract_submenu = State()
    feedback_message = State()  # Состояние для сбора отзыва
    feedback_section = State()  # Секция для отзывов

