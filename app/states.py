from aiogram.fsm.state import StatesGroup, State


class NewGift(StatesGroup):
    name = State()
    description = State()
