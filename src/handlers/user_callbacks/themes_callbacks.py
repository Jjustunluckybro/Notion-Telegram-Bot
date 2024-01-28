from logging import getLogger

from aiogram import Router, types

from src.services.storage.interfaces import IThemesStorageHandler, INotesStorageHandler
from src.services.storage.notes_storage_handler import NotesStorageHandler
from src.services.storage.themes_storage_handler import ThemesStorageHandler
from src.services.ui.callbacks import Callbacks
from src.services.ui.inline_keyboards import create_theme_list_kb, create_theme_menu_kb
from src.utils.exceptions.decorators import handel_storage_unexpected_response
from src.utils.exceptions.storage import StorageNotFound

logger = getLogger(__name__)


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
        text="Список всех ваших тем:",
        reply_markup=kb.as_markup(),
        chat_id=callback.from_user.id
    )
    await callback.message.delete()


@handel_storage_unexpected_response
async def open_theme_menu(
        callback: types.CallbackQuery,
        theme_sh: IThemesStorageHandler = ThemesStorageHandler(),
        note_sh: INotesStorageHandler = NotesStorageHandler()
) -> None:
    """
    Open all theme notes as inline keyboard. Create keys to create or delete note + return to theme list
    :param callback:
    :param theme_sh: Dependency to interact with theme storage
    :param note_sh: Dependency to interact with note storage
    """
    theme_id = Callbacks.get_id_from_callback(callback.data)
    text = "Список ваших заметок под темой:"

    try:
        theme_notes = await note_sh.get_all_by_theme(theme_id)
    except StorageNotFound:
        text = "Заметок под темой пока нет"
        theme_notes = None

    try:
        theme = await theme_sh.get(theme_id)
        text = f"{theme.name}\n\n{theme.description}\n\n" + text
    except StorageNotFound:
        ...
    finally:
        kb = create_theme_menu_kb(theme_id, theme_notes)
        await callback.bot.send_message(
            text=text,
            reply_markup=kb.as_markup(),
            chat_id=callback.from_user.id
        )
        await callback.message.delete()


def get_themes_router(callbacks: Callbacks = Callbacks()) -> Router:
    """
    Register all callback handlers to use main menu
    :callbacks: Dependency
    :return: routers with registered handlers
    """
    router = Router(name="themes")

    router.callback_query.register(open_all_themes, lambda x: x.data == callbacks.OPEN_ALL_THEMES)
    router.callback_query.register(open_theme_menu, lambda x: x.data.startswith(callbacks.OPEN_THEME_START_WITH))

    return router
