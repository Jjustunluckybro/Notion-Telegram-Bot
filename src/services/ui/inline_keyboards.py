from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.models.alarm_model import AlarmModel
from src.models.notes_models import NoteModel
from src.models.themes_modles import ThemeModel
from src.services.ui.callbacks import Callbacks


def create_main_menu_kb() -> InlineKeyboardBuilder:
    """"""
    builder = InlineKeyboardBuilder()
    builder.button(text="Открыть список тем", callback_data=Callbacks.open_all_themes)
    builder.button(text="Создать новую тему", callback_data=Callbacks.create_theme)
    builder.button(text="Создать новое напоминание", callback_data=Callbacks.create_alarm)
    builder.adjust(1)
    return builder


def create_theme_list_kb(themes: list[ThemeModel] | None) -> InlineKeyboardBuilder:
    """
    Create inline keyboard with all users themes as a keys (if list not None) + keys: Create new theme, back to menu
    :return: aiogram keyboard builder
    """
    builder = InlineKeyboardBuilder()

    if themes is not None:
        for theme in themes:
            builder.button(text=theme.name, callback_data=Callbacks().get_open_theme_callback(theme.id))

    builder.button(text="Создать новую тему", callback_data=Callbacks.create_theme)
    builder.button(text="Назад в меню", callback_data=Callbacks.open_main_menu)
    builder.adjust(1)
    return builder


def create_theme_menu_kb(theme_id: str, theme_notes: list[NoteModel] | None) -> InlineKeyboardBuilder:
    """"""
    builder = InlineKeyboardBuilder()

    callbacks = Callbacks()
    if theme_notes is not None:
        for note in theme_notes:
            builder.button(text=note.name, callback_data=callbacks.get_open_note_callback(note.id))

    builder.button(text="Создать новую заметку", callback_data=callbacks.create_note)
    builder.button(text="Удалить тему", callback_data=callbacks.get_delete_theme_callback(theme_id))
    builder.button(text="Назад к списку тем", callback_data=callbacks.open_all_themes)
    builder.adjust(1)
    return builder


def create_note_menu_kb(note_id: str, note_alarms: list[AlarmModel] | None) -> InlineKeyboardBuilder:
    """"""
    builder = InlineKeyboardBuilder()

    callbacks = Callbacks()
    if note_alarms is not None:
        for alarm in note_alarms:
            builder.button(text=alarm.name, callback_data=callbacks.get_open_alarm_callback(alarm.id))

    builder.button(text="Создать новое напоминание", callback_data=callbacks.create_alarm)
    builder.button(text="Удалить текущую заметку", callback_data=callbacks.get_delete_note_callback(note_id))
    builder.button(text="Назад к списку заметок", callback_data=callbacks.get_open_note_callback(note_id))
    builder.adjust(1)
    return builder


async def create_alarm_menu_kb(alarm: AlarmModel) -> InlineKeyboardBuilder:

    builder = InlineKeyboardBuilder()
    builder.button(text="Удалить напоминание", callback_data=Callbacks().get_delete_alarm_note_callback(alarm.id))
    return builder