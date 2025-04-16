from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    section= State()
    solution= State()
    math_submenu= State()
    abstract_submenu=State()

