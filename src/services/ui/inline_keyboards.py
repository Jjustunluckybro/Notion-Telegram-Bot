from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.models.alarm_model import AlarmModel
from src.models.notes_models import NoteModel
from src.models.themes_modles import ThemeModel
from src.services.ui.callbacks import Callbacks


def create_themes_list_kb(key_text: str = "К списку тем") -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text=key_text, callback_data=Callbacks.OPEN_ALL_THEMES)
    return builder


def create_open_theme_kb(theme_id: str, theme_name: str) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text=f"Открыть тему: {theme_name}", callback_data=Callbacks().get_open_theme_callback(theme_id))
    return builder


def create_main_menu_kb() -> InlineKeyboardBuilder:
    """"""
    builder = InlineKeyboardBuilder()
    builder.button(text="Открыть список тем", callback_data=Callbacks.OPEN_ALL_THEMES)
    builder.button(text="Создать новую тему", callback_data=Callbacks.CREATE_THEME)
    builder.button(text="Создать новое напоминание", callback_data=Callbacks.CREATE_ALARM)
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

    builder.button(text="Создать новую тему", callback_data=Callbacks.CREATE_THEME)
    builder.button(text="Назад в меню", callback_data=Callbacks.OPEN_MAIN_MENU)
    builder.adjust(1)
    return builder


def create_theme_menu_kb(theme_id: str, theme_notes: list[NoteModel] | None) -> InlineKeyboardBuilder:
    """"""
    builder = InlineKeyboardBuilder()

    callbacks = Callbacks()
    if theme_notes is not None:
        for note in theme_notes:
            builder.button(text=note.name, callback_data=callbacks.get_open_note_callback(note.id))

    builder.button(text="Создать новую заметку", callback_data=callbacks.get_create_new_note_callback(theme_id))
    builder.button(text="Удалить тему", callback_data=callbacks.get_delete_theme_callback(theme_id))
    builder.attach(create_themes_list_kb("Назад к списку тем"))
    builder.adjust(1)
    return builder


def create_note_menu_kb(note_id: str, note_alarms: list[AlarmModel] | None) -> InlineKeyboardBuilder:
    """"""
    builder = InlineKeyboardBuilder()

    callbacks = Callbacks()
    if note_alarms is not None:
        for alarm in note_alarms:
            builder.button(text=alarm.name, callback_data=callbacks.get_open_alarm_callback(alarm.id))

    builder.button(text="Создать новое напоминание", callback_data=callbacks.get_create_new_alarm_callback(note_id))
    builder.button(text="Удалить текущую заметку", callback_data=callbacks.get_delete_note_callback(note_id))
    builder.button(text="Назад к списку заметок", callback_data=callbacks.get_open_note_callback(note_id))
    builder.adjust(1)
    return builder


def create_alarm_menu_kb(alarm: AlarmModel) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="Удалить напоминание", callback_data=Callbacks().get_delete_alarm_note_callback(alarm.id))
    return builder


def create_save_kb() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="Сохранить", callback_data=Callbacks.SAVE)
    return builder


def create_cancel_fsm_kb(key_text: str = "Вернуться в меню") -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text=key_text, callback_data=Callbacks.CANCEL_FSM)
    return builder


def create_cancel_kb() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="Отменить", callback_data=Callbacks.CANCEL)
    return builder


def create_change_fsm_user_data_kb() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="Изменить", callback_data=Callbacks.CHANGE_FSM_USER_DATA)

    return builder


def create_done_kb() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="Готово", callback_data=Callbacks.DONE)
    return builder


def create_set_attachments_or_checkpoints_kb() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="Добавить файл", callback_data=Callbacks.ADD_ATTACHMENTS)
    builder.button(text="Добавить чеклист", callback_data=Callbacks.ADD_CHECKPOINT)
    return builder


def create_yes_no_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="Да", callback_data=Callbacks.YES)
    builder.button(text="Нет", callback_data=Callbacks.NO)
    return builder
