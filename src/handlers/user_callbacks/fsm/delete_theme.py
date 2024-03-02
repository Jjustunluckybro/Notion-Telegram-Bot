from logging import getLogger

from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from src.models.themes_modles import ThemeModel
from src.services.storage.interfaces import IThemesStorageHandler, INotesStorageHandler
from src.services.storage.notes_storage_handler import NotesStorageHandler
from src.services.storage.themes_storage_handler import ThemesStorageHandler
from src.services.ui.callbacks import Callbacks
from src.services.ui.inline_keyboards import create_yes_no_keyboard, create_theme_menu_kb, create_theme_list_kb
from src.utils.exceptions.decorators import handel_storage_unexpected_response
from src.utils.exceptions.storage import StorageNotFound, StorageValidationError
from src.utils.fsm.fsm import DeleteTheme
from src.utils.handlers_utils import del_prev_message_and_write_current_message_as_prev, send_error_message

logger = getLogger(__name__)
router = Router(name=__name__)


@handel_storage_unexpected_response
@router.callback_query(lambda x: x.data.startswith(Callbacks.DELETE_THEME_START_WITH))
async def delete_theme(
        callback: types.CallbackQuery,
        state: FSMContext,
        sh: IThemesStorageHandler = ThemesStorageHandler()
) -> None:
    """"""
    theme_id = Callbacks.get_id_from_callback(callback.data)
    theme = await sh.get(theme_id)

    await state.set_state(DeleteTheme.accept)
    await state.update_data(theme=theme)

    kb = create_yes_no_keyboard()
    text = f"""
    Вместе с темой удалятся все заметки и напоминания, привязанные к теме.
    \nТему и все что к ней привязано будет невозможно востановить
    \nВы уверены что хотите удалить тему '{theme.name}'?
    """
    message_out = await callback.bot.send_message(
        text=text,
        chat_id=callback.from_user.id,
        reply_markup=kb.as_markup(),
    )
    await del_prev_message_and_write_current_message_as_prev(
        message=callback, state=state, current_message_id=message_out.message_id
    )
    await callback.message.delete()


@handel_storage_unexpected_response
@router.callback_query(lambda x: x.data == Callbacks.YES, DeleteTheme.accept)
async def delete_theme_yes(
        callback: types.CallbackQuery,
        state: FSMContext,
        theme_sh: IThemesStorageHandler = ThemesStorageHandler(),
) -> None:
    user_data = await state.get_data()
    theme: ThemeModel = user_data["theme"]
    text = ""

    try:
        await theme_sh.delete(theme.id)
        text = f"Тема '{theme.name}' успешно удалена"
    except StorageNotFound or StorageValidationError:
        await send_error_message(callback, state)

    try:
        themes = await theme_sh.get_all_by_user(str(callback.from_user.id))
        text += "\n\nВаши темы:"
    except StorageNotFound:
        themes = None
        text += "\n\nТут будет список ваших тем, но пока их нет.\nCоздайте новую тему"

    kb = create_theme_list_kb(themes)
    message_out = await callback.bot.send_message(
        text=text,
        chat_id=callback.from_user.id,
        reply_markup=kb.as_markup()
    )

    await del_prev_message_and_write_current_message_as_prev(
        message=callback, state=state, current_message_id=message_out.message_id
    )


@router.callback_query(lambda x: x.data == Callbacks.NO, DeleteTheme.accept)
async def delete_theme_no(
        callback: types.CallbackQuery,
        state: FSMContext,
        note_sh: INotesStorageHandler = NotesStorageHandler()
) -> None:
    """"""
    theme_notes = None
    user_data = await state.get_data()
    theme: ThemeModel = user_data.get("theme")
    text = "Список ваших заметок под темой:"

    try:
        theme_notes = await note_sh.get_all_by_theme(theme.id)
    except StorageNotFound:
        text = "Заметок под темой пока нет"
    finally:
        text = f"{theme.name}\n\n{theme.description}\n\n" + text
        kb = create_theme_menu_kb(theme.id, theme_notes)
        await callback.bot.send_message(
            text=text,
            reply_markup=kb.as_markup(),
            chat_id=callback.from_user.id
        )
        await callback.message.delete()
        await state.clear()

