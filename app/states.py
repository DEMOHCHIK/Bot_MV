from aiogram.fsm.state import StatesGroup, State


class Gift(StatesGroup):
    name = State()
    description = State()


class Partner(StatesGroup):
    username = State()
