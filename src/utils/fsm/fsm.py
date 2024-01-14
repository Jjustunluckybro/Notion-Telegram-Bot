from aiogram.fsm.state import StatesGroup, State


class CreateThemeFSM(StatesGroup):
    write_name: State = State()
    write_description: State = State()
    accept: State = State()


class CreateNote(StatesGroup):
    write_name: State = State()
    write_text: State = State()
    write_attachments: State = State()
    write_checkpoints: State = State()
    accept: State = State()
