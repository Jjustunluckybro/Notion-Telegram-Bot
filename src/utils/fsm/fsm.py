from aiogram.fsm.state import StatesGroup, State


class CreateThemeFSM(StatesGroup):
    write_name: State = State()
    write_description: State = State()
    accept: State = State()
