from logging import getLogger

from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from src.models.notes_models import NoteModel
from src.services.storage.alarms_storage_handler import AlarmsStoragehandler
from src.services.storage.interfaces import INotesStorageHandler, IThemesStorageHandler, IAlarmsStoragehandler
from src.services.storage.notes_storage_handler import NotesStorageHandler
from src.services.storage.themes_storage_handler import ThemesStorageHandler
from src.services.ui.callbacks import Callbacks
from src.services.ui.inline_keyboards import create_yes_no_keyboard, create_theme_menu_kb, create_note_menu_kb, \
    create_cancel_fsm_kb
from src.utils.exceptions.decorators import handel_storage_unexpected_response
from src.utils.exceptions.storage import StorageValidationError, StorageNotFound
from src.utils.fsm.fsm import DeleteNote
from src.utils.handlers_utils import async_method_arguments_logger, send_error_message

logger = getLogger(__name__)
router = Router(name=__name__)


@handel_storage_unexpected_response
@router.callback_query(lambda x: x.data.startswith(Callbacks.DELETE_NOTE_START_WITH))
@async_method_arguments_logger(logger)
async def delete_note(
        callback: types.CallbackQuery,
        state: FSMContext,
        storage: INotesStorageHandler = NotesStorageHandler()
) -> None:
    """

    :param callback:
    :param state:
    :param storage:
    :return:
    """

    note_id = Callbacks.get_id_from_callback(callback.data)
    note = await storage.get(note_id)

    await state.set_state(DeleteNote.accept)
    await state.update_data(note=note)

    kb = create_yes_no_keyboard()
    text = f"""
        Вместе с заметкой удалятся все напоминания, которые привязанны к заметке!
        \nУдаленное будет невозможно востановить!
        \nВы уверены что хотите удалить заметку '{note.name}'?
        """

    await callback.bot.send_message(
        chat_id=callback.from_user.id,
        text=text,
        reply_markup=kb.as_markup()
    )

    await callback.message.delete()


@handel_storage_unexpected_response
@router.callback_query(lambda x: x.data.startswith(Callbacks.YES), DeleteNote.accept)
@async_method_arguments_logger(logger)
async def delete_note_yes(
        callback: types.CallbackQuery,
        state: FSMContext,
        notes_storage: INotesStorageHandler = NotesStorageHandler(),
        themes_storage: IThemesStorageHandler = ThemesStorageHandler()
) -> None:
    """
    Delete note and all sub alarms
    :param callback: inline keyboard callback
    :param state: current aiogram state
    :param notes_storage: Dependency, note storage handler
    :param themes_storage: Dependency, themes storage handler
    :return:
    """
    user_data = await state.get_data()
    note: NoteModel = user_data["note"]
    text = ""

    try:
        await notes_storage.delete(note.id)
        text = f"Заметка '{note.name}' успешно удалена\n\n"
    except StorageNotFound or StorageValidationError:
        await send_error_message(callback, state)

    try:
        all_themes_notes = await notes_storage.get_all_by_theme(note.links.theme_id)
        text += f"Ваши заметки:"
    except StorageNotFound:
        text += f"Тут будет список ваших заметок, но пока их нет.\nCоздайте новую заметку"
        all_themes_notes = None

    try:
        parent_theme = await themes_storage.get(note.links.theme_id)
        text = f"{parent_theme.name}\n\n" + text
    except StorageNotFound or StorageValidationError:
        text = "Но дальше что-то пошло не так :(" + text
        await send_error_message(message=callback, state=state, text=text)
        return

    kb = create_theme_menu_kb(parent_theme.id, all_themes_notes)
    await callback.bot.send_message(
        chat_id=callback.from_user.id,
        text=text,
        reply_markup=kb.as_markup()
    )
    await callback.message.delete()
    await state.clear()


@handel_storage_unexpected_response
@router.callback_query(lambda x: x.data.startswith(Callbacks.NO), DeleteNote.accept)
@async_method_arguments_logger(logger)
async def delete_note_no(
        callback: types.CallbackQuery,
        state: FSMContext,
        alarms_storage: IAlarmsStoragehandler = AlarmsStoragehandler()
) -> None:
    """

    :param alarms_storage:
    :param callback:
    :param state:
    :return:
    """
    note_alarms = None
    user_data = await state.get_data()
    note: NoteModel = user_data["note"]
    text = f"{note.name}\n{note.data.text}\n\n"

    try:
        note_alarms = await alarms_storage.get_all_by_parent(note.id)
        text += f"Напоминания:"
    except StorageNotFound:
        text += f"Еще тут будет список ваших напоминаний, но пока их нет.\nCоздайте новое напоминание"
    finally:
        kb = create_note_menu_kb(note_id=note.id, note_alarms=note_alarms, parent_theme_id=note.links.theme_id)
        kb.attach(create_cancel_fsm_kb())
        await callback.bot.send_message(
            chat_id=callback.from_user.id,
            text=text,
            reply_markup=kb.as_markup()
        )
        await callback.message.delete()
        await state.clear()
