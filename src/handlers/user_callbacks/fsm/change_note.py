from logging import getLogger

from aiogram import types, Router

from aiogram.fsm.context import FSMContext

from src.models.notes_models import NoteModel
from src.services.storage.interfaces import INotesStorageHandler, IAlarmsStoragehandler
from src.services.storage.notes_storage_handler import NotesStorageHandler
from src.services.storage.alarms_storage_handler import AlarmsStoragehandler
from src.services.ui.callbacks import Callbacks
from src.services.ui.inline_keyboards import create_save_kb, create_change_name_or_description_kb, create_note_menu_kb
from src.services.ui.scripts import get_change_note_accept_script
from src.utils.exceptions.decorators import handel_storage_unexpected_response
from src.utils.exceptions.storage import StorageValidationError, StorageNotFound
from src.utils.fsm.fsm import ChangeNote
from src.utils.handlers_utils import send_error_message, async_method_arguments_logger, \
    del_prev_message_and_write_current_message_as_prev


logger = getLogger(f"fsm_{__name__}")
router = Router(name=__name__)


@router.callback_query(lambda x: x.data.startswith(Callbacks.CHANGE_NOTE))
@handel_storage_unexpected_response
@async_method_arguments_logger(logger)
async def change_theme(
        callback: types.CallbackQuery,
        state: FSMContext,
        note_storage: INotesStorageHandler = NotesStorageHandler()
) -> None:
    """"""
    note_id = Callbacks.get_id_from_callback(callback.data)
    try:
        theme = await note_storage.get(note_id)
    except StorageNotFound as err:
        logger.error(f"Not found note, but should. details: {err}")
        await send_error_message(callback)
    except StorageValidationError:
        await send_error_message(callback)
    else:
        await state.set_state(ChangeNote.change_note)
        await state.update_data(note=theme)
        kb = create_change_name_or_description_kb()
        msg = await callback.message.answer(
            text="Выберити что изменить",
            reply_markup=kb.as_markup()
        )
        await del_prev_message_and_write_current_message_as_prev(callback, state, msg.message_id)
    finally:
        await callback.message.delete()


@router.callback_query(lambda x: x.data == Callbacks.CHANGE_NAME, ChangeNote.change_note)
@async_method_arguments_logger(logger)
async def change_theme_name(
        callback: types.CallbackQuery,
        state: FSMContext
) -> None:
    """"""
    await state.set_state(ChangeNote.change_name)
    msg = await callback.message.answer(
        text="Введите новое имя"
    )
    await del_prev_message_and_write_current_message_as_prev(callback, state, msg.message_id)


@router.callback_query(lambda x: x.data == Callbacks.CHANGE_DESCRIPTION, ChangeNote.change_note)
@async_method_arguments_logger(logger)
async def change_theme_description(
        callback: types.CallbackQuery,
        state: FSMContext
) -> None:
    """"""
    await state.set_state(ChangeNote.change_description)
    msg = await callback.message.answer(
        text="Введите новое описание"
    )
    await del_prev_message_and_write_current_message_as_prev(callback, state, msg.message_id)


@router.message(ChangeNote.change_description)
@router.message(ChangeNote.change_name)
@async_method_arguments_logger(logger)
async def change_theme_accept(
        message: types.Message,
        state: FSMContext
) -> None:
    """"""
    current_state = await state.get_state()
    if current_state == ChangeNote.change_name:
        await state.update_data(new_name=message.text)
    if current_state == ChangeNote.change_description:
        await state.update_data(new_description=message.text)

    user_data = await state.get_data()
    text = get_change_note_accept_script(user_data)
    kb = create_save_kb()
    kb.attach(create_change_name_or_description_kb())
    msg = await message.answer(
        text=text,
        reply_markup=kb.as_markup()
    )
    await state.set_state(ChangeNote.change_note)
    await del_prev_message_and_write_current_message_as_prev(message, state, msg.message_id)


@router.callback_query(lambda x: x.data == Callbacks.CANCEL, ChangeNote.change_note)
@handel_storage_unexpected_response
@async_method_arguments_logger(logger)
async def change_theme_cancel(
        callback: types.CallbackQuery,
        state: FSMContext,
        alarms_storage: IAlarmsStoragehandler = AlarmsStoragehandler()
) -> None:
    """"""
    note_alarms = None
    user_data = await state.get_data()
    try:
        note: NoteModel = user_data["note"]
    except KeyError as err:
        logger.error(f"Invalid state user data. details: {err}. user_data: {user_data}")
        await send_error_message(callback, state)
        await callback.message.delete()
        return
    else:
        text = f"{note.name}\n\n{note.data.text}"

    try:
        note_alarms = await alarms_storage.get_all_by_parent(note.id)
    except StorageValidationError:
        await send_error_message(callback, state)
        await callback.message.delete()
        return
    except StorageNotFound:
        text += "\nнапоминаний под заметкой пока нет"
    else:
        text += "\nВаши напоминания под темой"

    kb = create_note_menu_kb(note_id=note.id, note_alarms=note_alarms, parent_theme_id=note.links.theme_id)
    await callback.message.answer(
        text=text,
        reply_markup=kb.as_markup()
    )
    await state.clear()
    await callback.message.delete()


@router.callback_query(
    lambda x: x.data == Callbacks.SAVE,
    ChangeNote.change_note)
@handel_storage_unexpected_response
@async_method_arguments_logger(logger)
async def change_theme_accept(
        callback: types.CallbackQuery,
        state: FSMContext,
        note_storage: INotesStorageHandler = NotesStorageHandler(),
        alarm_storage: IAlarmsStoragehandler = AlarmsStoragehandler()
) -> None:
    """"""
    user_data = await state.get_data()
    new_data = dict()
    note_alarms = None

    # Try to get note from state
    try:
        note: NoteModel = user_data["note"]
    except KeyError as err:
        logger.error(f"Invalid state user data. details: {err}. user_data: {user_data}")
        await send_error_message(callback, state)
        await callback.message.delete()
        return

    # Mapping new data to change
    if user_data.get("new_name") is not None:
        new_data["name"] = user_data.get("new_name")
    if user_data.get("new_description") is not None:
        new_data["data.text"] = user_data.get("new_description")

    # Try to change new data
    try:
        await note_storage.patch(note.id, new_data)
    except StorageNotFound as err:
        logger.error(f"not found theme, but should. deteils: {err}")
        await send_error_message(callback, state)
        return
    except StorageValidationError:
        await send_error_message(callback, state)
        return

    # Try to get updated theme and make start of script
    try:
        note = await note_storage.get(note.id)
    except StorageNotFound as err:
        logger.error(f"not found note, but should. deteils: {err}")
        await send_error_message(callback, state, "Изменения сохранены, но дальше что-то пошло не так :(")
        return
    except StorageValidationError:
        await send_error_message(callback, state, "Изменения сохранены, но дальше что-то пошло не так :(")
        return
    else:
        text = f"{note.name}\n\n{note.data.text}"

    # Try to get all theme notes and make end of script
    try:
        note_alarms = await alarm_storage.get_all_by_parent(note.id)
    except StorageValidationError:
        await send_error_message(callback, state, "Изменения сохранены, но дальше что-то пошло не так :(")
        return
    except StorageNotFound:
        text += "\n\nНапоминаний под заметкой пока нет"
    else:
        text += "\n\nСписок ваших напоминаний под заметкой:"

    # Make theme menu and show it
    kb = create_note_menu_kb(note_id=note.id, note_alarms=note_alarms, parent_theme_id=note.links.theme_id)
    await callback.message.answer(
        text=text,
        reply_markup=kb.as_markup()
    )
    await state.clear()
    await callback.message.delete()
