from logging import getLogger

from aiogram import types, Router

from aiogram.fsm.context import FSMContext


from src.models.themes_modles import ThemeModel
from src.services.storage.interfaces import IThemesStorageHandler, INotesStorageHandler
from src.services.storage.notes_storage_handler import NotesStorageHandler
from src.services.storage.themes_storage_handler import ThemesStorageHandler
from src.services.ui.callbacks import Callbacks
from src.services.ui.inline_keyboards import create_save_kb, create_change_name_or_description_kb, create_theme_menu_kb
from src.services.ui.scripts import get_change_theme_accept_script
from src.utils.exceptions.decorators import handel_storage_unexpected_response
from src.utils.exceptions.storage import StorageValidationError, StorageNotFound
from src.utils.fsm.fsm import ChangeTheme
from src.utils.handlers_utils import send_error_message, async_method_arguments_logger, \
    del_prev_message_and_write_current_message_as_prev

logger = getLogger(f"fsm_{__name__}")
router = Router(name=__name__)


@router.callback_query(lambda x: x.data.startswith(Callbacks.CHANGE_THEME))
@handel_storage_unexpected_response
@async_method_arguments_logger(logger)
async def change_theme(
        callback: types.CallbackQuery,
        state: FSMContext,
        theme_storage: IThemesStorageHandler = ThemesStorageHandler()
) -> None:
    """"""
    theme_id = Callbacks.get_id_from_callback(callback.data)
    try:
        theme = await theme_storage.get(theme_id)
    except StorageNotFound as err:
        logger.error(f"not found theme, but should. deteils: {err}")
        await send_error_message(callback)
    except StorageValidationError:
        await send_error_message(callback)
    else:
        await state.set_state(ChangeTheme.change_theme)
        await state.update_data(theme=theme)
        kb = create_change_name_or_description_kb()
        msg = await callback.message.answer(
            text="Выберити что изменить",
            reply_markup=kb.as_markup()
        )
        await del_prev_message_and_write_current_message_as_prev(callback, state, msg.message_id)
    finally:
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


@router.callback_query(lambda x: x.data == Callbacks.CHANGE_DESCRIPTION, ChangeTheme.change_theme)
@async_method_arguments_logger(logger)
async def change_theme_description(
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
@router.message(ChangeTheme.change_name)
@async_method_arguments_logger(logger)
async def change_theme_accept(
        message: types.Message,
        state: FSMContext
) -> None:
    """"""
    current_state = await state.get_state()
    if current_state == ChangeTheme.change_name:
        await state.update_data(new_name=message.text)
    if current_state == ChangeTheme.change_description:
        await state.update_data(new_description=message.text)

    user_data = await state.get_data()
    text = get_change_theme_accept_script(user_data)
    kb = create_save_kb()
    kb.attach(create_change_name_or_description_kb())
    msg = await message.answer(
        text=text,
        reply_markup=kb.as_markup()
    )
    await state.set_state(ChangeTheme.change_theme)
    await del_prev_message_and_write_current_message_as_prev(message, state, msg.message_id)


@router.callback_query(lambda x: x.data == Callbacks.CANCEL, ChangeTheme.change_theme)
@handel_storage_unexpected_response
@async_method_arguments_logger(logger)
async def change_theme_cancel(
        callback: types.CallbackQuery,
        state: FSMContext,
        note_storage: INotesStorageHandler = NotesStorageHandler()
) -> None:
    """"""
    theme_notes = None
    user_data = await state.get_data()
    try:
        theme: ThemeModel = user_data["theme"]
    except KeyError as err:
        logger.error(f"Invalid state user data. details: {err}. user_data: {user_data}")
        await send_error_message(callback, state)
        await callback.message.delete()
        return
    else:
        text = f"{theme.name}\n\n{theme.description}"

    try:
        theme_notes = await note_storage.get_all_by_theme(theme.id)
    except StorageValidationError:
        await send_error_message(callback, state)
        await callback.message.delete()
        return
    except StorageNotFound:
        text += "\nЗаметок под темой пока нет"
    else:
        text += "\nВаши заметки под темой"

    kb = create_theme_menu_kb(theme.id, theme_notes)
    await callback.message.answer(
        text=text,
        reply_markup=kb.as_markup()
    )
    await state.clear()
    await callback.message.delete()


@router.callback_query(lambda x: x.data == Callbacks.SAVE, ChangeTheme.change_theme)
@handel_storage_unexpected_response
@async_method_arguments_logger(logger)
async def change_theme_accept(
        callback: types.CallbackQuery,
        state: FSMContext,
        theme_storage: IThemesStorageHandler = ThemesStorageHandler(),
        note_storage: INotesStorageHandler = NotesStorageHandler()
) -> None:
    """"""
    user_data = await state.get_data()
    new_data = dict()
    theme_notes = None

    # Try to get theme from state
    try:
        theme: ThemeModel = user_data["theme"]
    except KeyError as err:
        logger.error(f"Invalid state user data. details: {err}. user_data: {user_data}")
        await send_error_message(callback, state)
        await callback.message.delete()
        return

    # Mapping new data to change
    if user_data.get("new_name") is not None:
        new_data["name"] = user_data.get("new_name")
    if user_data.get("new_description") is not None:
        new_data["description"] = user_data.get("new_description")

    # Try to change new data
    try:
        await theme_storage.patch(theme.id, new_data)
    except StorageNotFound as err:
        logger.error(f"not found theme, but should. deteils: {err}")
        await send_error_message(callback, state)
        return
    except StorageValidationError:
        await send_error_message(callback, state)
        return

    # Try to get updated theme and make start of script
    try:
        theme = await theme_storage.get(theme.id)
    except StorageNotFound as err:
        logger.error(f"not found theme, but should. deteils: {err}")
        await send_error_message(callback, state, "Изменения сохранены, но дальше что-то пошло не так :(")
        return
    except StorageValidationError:
        await send_error_message(callback, state, "Изменения сохранены, но дальше что-то пошло не так :(")
        return
    else:
        text = f"{theme.name}\n\n{theme.description}"

    # Try to get all theme notes and make end of script
    try:
        theme_notes = await note_storage.get_all_by_theme(theme.id)
    except StorageValidationError:
        await send_error_message(callback, state, "Изменения сохранены, но дальше что-то пошло не так :(")
        return
    except StorageNotFound:
        text += "\n\nЗаметок под темой пока нет"
    else:
        text += "\n\nСписок ваших заметок под темой:"

    # Make theme menu and show it
    kb = create_theme_menu_kb(theme.id, theme_notes)
    await callback.message.answer(
        text=text,
        reply_markup=kb.as_markup()
    )
    await state.clear()
    await callback.message.delete()
