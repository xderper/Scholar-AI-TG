from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    section_status = State()
    