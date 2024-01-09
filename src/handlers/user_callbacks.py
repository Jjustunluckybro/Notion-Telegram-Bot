from aiogram import types

from src.services.storage.alarms_storage_handler import AlarmsStoragehandler
from src.services.storage.interfaces import IThemesStorageHandler, INotesStoragehandler, IAlarmsStoragehandler
from src.services.storage.notes_storage_handler import NotesStoragehandler
from src.services.storage.themes_storage_handler import ThemesStorageHandler
from src.services.ui.callbacks import Callbacks
from src.services.ui.inline_keyboards import create_theme_list_kb, create_theme_menu_kb, create_note_menu_kb
from src.utils.exceptions.decorators import handel_storage_unexpected_response
from src.utils.exceptions.storage import StorageNotFound


@handel_storage_unexpected_response
async def open_all_themes(callback: types.CallbackQuery, sh: IThemesStorageHandler = ThemesStorageHandler()) -> None:
    """
    Open inline menu with all users themes as a button
    :param callback: telegram inline query callback
    :param sh: Dependency
    """
    user_themes = None

    try:
        user_themes = await sh.get_all_by_user(str(callback.from_user.id))
    except StorageNotFound:
        ...
    kb = create_theme_list_kb(user_themes)
    await callback.bot.send_message(
        text="Список всех ваших тем ...:",
        reply_markup=kb.as_markup(),
        chat_id=callback.from_user.id
    )
    await callback.message.delete()


@handel_storage_unexpected_response
async def open_all_theme_notes(callback: types.CallbackQuery, sh: INotesStoragehandler = NotesStoragehandler()) -> None:
    """
    :param callback:
    :param sh: Dependency
    """
    theme_notes = None
    theme_id = Callbacks.get_id_from_callback(callback.data)

    try:
        theme_notes = await sh.get_all_by_theme(theme_id)
    except StorageNotFound:
        ...
    finally:
        kb = create_theme_menu_kb(theme_id, theme_notes)
        await callback.bot.send_message(
            text="Список ваших заметок под темой ...:",  # TODO Theme name and info
            reply_markup=kb.as_markup(),
            chat_id=callback.from_user.id
        )
        await callback.message.delete()


@handel_storage_unexpected_response
async def open_all_note_alarms(callback: types.CallbackQuery,
                               sh: IAlarmsStoragehandler = AlarmsStoragehandler()
                               ) -> None:
    """
    :param callback:
    :param sh: Dependency
    """

    note_alarms = None
    note_id = Callbacks.get_id_from_callback(callback.data)

    try:
        note_alarms = await sh.get_all_by_parent(note_id)
    except StorageNotFound:
        ...
    finally:
        kb = create_note_menu_kb(note_id, note_alarms)
        await callback.bot.send_message(
            text="Список ваших напомниний под заметкой ...:",  # TODO Note name and info
            reply_markup=kb.as_markup(),
            chat_id=callback.from_user.id
        )
        await callback.message.delete()
