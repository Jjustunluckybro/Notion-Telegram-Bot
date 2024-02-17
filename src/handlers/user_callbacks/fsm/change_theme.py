from logging import getLogger

from aiogram import types, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from pydantic import ValidationError

from src.models.themes_modles import ThemeModelToCreate, ThemeLinksModel
from src.services.storage.interfaces import IThemesStorageHandler, INotesStorageHandler
from src.services.storage.notes_storage_handler import NotesStorageHandler
from src.services.storage.themes_storage_handler import ThemesStorageHandler
from src.services.ui.callbacks import Callbacks
from src.services.ui.inline_keyboards import create_cancel_fsm_kb, create_change_fsm_user_data_kb, create_save_kb, \
    create_themes_list_kb, create_open_theme_kb, create_change_theme_kb, create_theme_menu_kb
from src.utils.exceptions.decorators import handel_storage_unexpected_response
from src.utils.exceptions.storage import StorageValidationError, StorageNotFound
from src.utils.fsm.fsm import CreateThemeFSM, ChangeTheme
from src.utils.handlers_utils import send_error_message, async_method_arguments_logger, \
    del_prev_message_and_write_current_message_as_prev

logger = getLogger(f"fsm_{__name__}")
router = Router(name=__name__)


@router.callback_query(lambda x: x.data.startswith(Callbacks.CHANGE_THEME))
@async_method_arguments_logger(logger)
async def change_theme(
        callback: types.CallbackQuery,
        state: FSMContext
) -> None:
    """"""
    await state.set_state(ChangeTheme.change_theme)

    await state.update_data(theme_id=Callbacks.get_id_from_callback(callback.data))

    kb = create_change_theme_kb()
    msg = await callback.message.answer(
        text="Выберити что изменить",
        reply_markup=kb.as_markup()
    )
    await del_prev_message_and_write_current_message_as_prev(callback, state, msg.message_id)
    await callback.message.delete()


@router.callback_query(lambda x: x.data == Callbacks.CHANGE_NAME, ChangeTheme.change_theme)
@async_method_arguments_logger(logger)
async def change_theme_name(
        callback: types.CallbackQuery,
        state: FSMContext
) -> None:
    """"""
    await state.set_state(ChangeTheme.change_name)
    msg = await callback.message.answer(
        text="Введите новое имя"
    )
    await del_prev_message_and_write_current_message_as_prev(callback, state, msg.message_id)


@router.message(ChangeTheme.change_name)
@async_method_arguments_logger(logger)
async def change_theme_name_accept(
        message: types.Message,
        state: FSMContext
) -> None:
    """"""
    await state.set_state(ChangeTheme.change_theme)
    await state.update_data(new_name=message.text)

    kb = create_change_theme_kb()
    kb.attach(create_save_kb())
    msg = await message.answer(
        text="Выберити что изменить или сохраните изменения",
        reply_markup=kb.as_markup()
    )
    await del_prev_message_and_write_current_message_as_prev(message, state, msg.message_id)


@router.callback_query(lambda x: x.data == Callbacks.CHANGE_DESCRIPTION, ChangeTheme.change_theme)
@async_method_arguments_logger(logger)
async def change_theme_name(
        callback: types.CallbackQuery,
        state: FSMContext
) -> None:
    """"""
    await state.set_state(ChangeTheme.change_description)
    msg = await callback.message.answer(
        text="Введите новое описание"
    )
    await del_prev_message_and_write_current_message_as_prev(callback, state, msg.message_id)


@router.message(ChangeTheme.change_description)
@async_method_arguments_logger(logger)
async def change_theme_name_accept(
        message: types.Message,
        state: FSMContext
) -> None:
    """"""
    await state.set_state(ChangeTheme.change_description)
    await state.update_data(new_name=message.text)

    kb = create_change_theme_kb()
    kb.attach(create_save_kb())
    msg = await message.answer(
        text="Выберити что изменить или сохраните изменения",
        reply_markup=kb.as_markup()
    )
    await del_prev_message_and_write_current_message_as_prev(message, state, msg.message_id)


@router.callback_query(lambda x: x.data == Callbacks.BACK, ChangeTheme.change_theme)
@handel_storage_unexpected_response
@async_method_arguments_logger(logger)
async def change_theme_cancel(
        callback: types.CallbackQuery,
        state: FSMContext,
        theme_storage: IThemesStorageHandler = ThemesStorageHandler(),
        note_storage: INotesStorageHandler = NotesStorageHandler()
) -> None:
    """"""
    user_data = await state.get_data()
    theme_id = user_data["theme_id"]
    theme_notes = None
    text = ""

    try:
        theme = await theme_storage.get(theme_id)
    except StorageValidationError:
        await send_error_message(callback, state)
        await callback.message.delete()
        return
    except StorageNotFound as err:
        logger.error(f"Dont find theme, but should. details: {err}")
        await send_error_message(callback, state)
        await callback.message.delete()
        return
    else:
        text += f"{theme.name}\n\n{theme.description}"

    try:
        theme_notes = await note_storage.get_all_by_theme(theme_id)
    except StorageValidationError:
        await send_error_message(callback, state)
        await callback.message.delete()
        return
    except StorageNotFound:
        text += "\nЗаметок под темой пока нет"
    else:
        text += "\nВаши заметки под темой"

    kb = create_theme_menu_kb(theme_id, theme_notes)
    await callback.message.answer(
        text=text,
        reply_markup=kb.as_markup()
    )
    await state.clear()
    await callback.message.delete()
