from logging import getLogger

from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from src.services.storage.interfaces import IThemesStorageHandler, INotesStorageHandler
from src.services.storage.notes_storage_handler import NotesStorageHandler
from src.services.storage.themes_storage_handler import ThemesStorageHandler
from src.services.ui.callbacks import Callbacks
from src.services.ui.inline_keyboards import create_theme_list_kb, create_theme_menu_kb
from src.utils.exceptions.decorators import handel_storage_unexpected_response
from src.utils.exceptions.storage import StorageNotFound
from src.utils.handlers_utils import async_method_arguments_logger

logger = getLogger(__name__)

router = Router(name=__name__)


@router.callback_query(lambda x: x.data == Callbacks.OPEN_ALL_THEMES)
@handel_storage_unexpected_response
@async_method_arguments_logger(logger)
async def open_all_themes(
        callback: types.CallbackQuery,
        state: FSMContext | None,
        sh: IThemesStorageHandler = ThemesStorageHandler()) -> None:
    """
    Open inline menu with all users themes as a button
    :param state: Current fsm state, clear this state if not none
    :param callback: telegram inline query callback
    :param sh: Dependency
    """
    user_themes = None

    if state is not None:
        await state.clear()

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


@router.callback_query(lambda x: x.data.startswith(Callbacks.OPEN_THEME_START_WITH))
@handel_storage_unexpected_response
@async_method_arguments_logger(logger)
async def open_theme_menu(
        callback: types.CallbackQuery,
        state: FSMContext | None,
        theme_sh: IThemesStorageHandler = ThemesStorageHandler(),
        note_sh: INotesStorageHandler = NotesStorageHandler(),
) -> None:
    """
    Open all theme notes as inline keyboard. Create keys to create or delete note + return to theme list
    :param state:
    :param callback:
    :param theme_sh: Dependency to interact with theme storage
    :param note_sh: Dependency to interact with note storage
    """
    theme_id = Callbacks.get_id_from_callback(callback.data)
    text = "Список ваших заметок под темой:"

    if state is not None:
        await state.clear()

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
