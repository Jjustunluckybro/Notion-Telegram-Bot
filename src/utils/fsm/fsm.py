from aiogram.fsm.state import StatesGroup, State


#  Themes FSM
class CreateThemeFSM(StatesGroup):
    """While user delete"""
    write_name: State = State()
    write_description: State = State()
    accept: State = State()


class ChangeTheme(StatesGroup):
    change_theme: State = State()
    change_name: State = State()
    change_description: State = State()
    accept: State = State()


class DeleteTheme(StatesGroup):
    accept: State = State()


#  Notes FSM
class CreateNote(StatesGroup):
    write_name: State = State()
    write_text: State = State()
    write_attachments: State = State()
    write_checkpoints: State = State()
    accept: State = State()


class DeleteNote(StatesGroup):
    accept: State = State()


#  Alarms FSM
class CreateAlarm(StatesGroup):
    write_name: State = State()
    write_description: State = State()
    write_next_notion_date: State = State()
    write_next_notion_time: State = State()
    choose_repeatable: State = State()
    choose_repeatable_interval: State = State()
    accept: State = State()


class SetNewAlarmRepeatInterval(StatesGroup):
    write_time: State = State()
    accept: State = State()


class SetNewAlarmTime(StatesGroup):
    write_next_notion_date: State = State()
    write_next_notion_time: State = State()
    accept: State = State()


class DeleteAlarm(StatesGroup):
    accept: State = State()
