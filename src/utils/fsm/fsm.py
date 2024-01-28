from aiogram.fsm.state import StatesGroup, State


class CreateThemeFSM(StatesGroup):
    write_name: State = State()
    write_description: State = State()
    accept: State = State()


class DeleteTheme(StatesGroup):
    accept: State = State()


class CreateNote(StatesGroup):
    write_name: State = State()
    write_text: State = State()
    write_attachments: State = State()
    write_checkpoints: State = State()
    accept: State = State()


class CreateAlarm(StatesGroup):
    write_name: State = State()
    write_description: State = State()
    write_next_notion_date: State = State()
    write_next_notion_time: State = State()
    choose_repeatable: State = State()
    choose_repeatable_interval: State = State()
    accept: State = State()
