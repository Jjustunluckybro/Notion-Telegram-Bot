from logging import getLogger

from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from src.models.alarm_model import AlarmModel
from src.models.notes_models import NoteModel
from src.services.storage.alarms_storage_handler import AlarmsStoragehandler
from src.services.storage.interfaces import INotesStorageHandler, IThemesStorageHandler, IAlarmsStoragehandler
from src.services.storage.notes_storage_handler import NotesStorageHandler
from src.services.storage.themes_storage_handler import ThemesStorageHandler
from src.services.ui.callbacks import Callbacks
from src.services.ui.inline_keyboards import create_yes_no_keyboard, create_theme_menu_kb, create_note_menu_kb, \
    create_cancel_fsm_kb, create_alarm_menu_kb
from src.services.ui.scripts import get_alarm_menu_script
from src.utils.exceptions.decorators import handel_storage_unexpected_response
from src.utils.exceptions.storage import StorageValidationError, StorageNotFound
from src.utils.fsm.fsm import DeleteNote, DeleteAlarm
from src.utils.handlers_utils import async_method_arguments_logger, send_error_message, \
    del_prev_message_and_write_current_message_as_prev

logger = getLogger(__name__)
router = Router(name=__name__)


@handel_storage_unexpected_response
@async_method_arguments_logger(logger)
@router.callback_query(lambda x: x.data.startswith(Callbacks.DELETE_ALARM_START_WITH))
async def delete_alarm(
        callback: types.CallbackQuery,
        state: FSMContext,
        alarm_storage: IAlarmsStoragehandler = AlarmsStoragehandler()
) -> None:
    """"""
    try:
        alarm = await alarm_storage.get(Callbacks.get_id_from_callback(callback.data))
    except StorageValidationError:
        await send_error_message(callback)
    except StorageNotFound as err:
        logger.error(f"not found alarm by id, but should. deteils: {err}")
        await send_error_message(callback)
    else:
        await callback.message.answer(
            text=f"Вы уверены, что хотите удалить напоминание: {alarm.name}?",
            reply_markup=create_yes_no_keyboard().as_markup()
        )
        await state.set_state(DeleteAlarm.accept)
        await state.update_data(alarm=alarm)
    finally:
        await callback.message.delete()


@handel_storage_unexpected_response
@async_method_arguments_logger(logger)
@router.callback_query(lambda x: x.data == Callbacks.YES, DeleteAlarm.accept)
async def delete_alarm_accept(
        callback: types.CallbackQuery,
        state: FSMContext,
        alarm_storage: IAlarmsStoragehandler = AlarmsStoragehandler(),
        note_storage: INotesStorageHandler = NotesStorageHandler()
) -> None:
    """"""
    user_data = await state.get_data()
    alarm: AlarmModel = user_data["alarm"]
    note_alarms = None

    try:
        await alarm_storage.delete(alarm.id)
        note = await note_storage.get(alarm.links.parent_id)
    except StorageValidationError:
        await send_error_message(callback, state)
        await callback.message.delete()
        return
    except StorageNotFound as err:
        logger.error(f"not found by id, but should. deteils: {err}")
        await send_error_message(callback, state)
        await callback.message.delete()
        return
    else:
        text = f"Напоминание '{alarm.name}' успешно удалено\n\n{note.name}\n\n{note.data.text}"

    try:
        note_alarms = await alarm_storage.get_all_by_parent(note.id)
    except StorageNotFound:
        text += "\n\nНапоминаний под темой пока нет, создайте их"
    except StorageValidationError:
        await send_error_message(callback, state, f"Напоминание '{alarm.name}' успешно удалено\n"
                                                  f"Но дальше что-то пошло не так")
        await callback.message.delete()
    else:
        text += f"\n\nСписок ваших напомниний:"

    kb = create_note_menu_kb(
        note_id=note.id, note_alarms=note_alarms, parent_theme_id=note.links.theme_id
    )
    await callback.bot.send_message(
        text=text,
        chat_id=callback.from_user.id,
        reply_markup=kb.as_markup()
    )
    await callback.message.delete()
    await state.clear()


@async_method_arguments_logger(logger)
@router.callback_query(lambda x: x.data == Callbacks.NO, DeleteAlarm.accept)
async def delete_alarm_cancel(
        callback: types.CallbackQuery,
        state: FSMContext
) -> None:
    """"""
    user_data = await state.get_data()
    alarm: AlarmModel = user_data["alarm"]

    kb = create_alarm_menu_kb(alarm)
    await callback.bot.send_message(
        text=get_alarm_menu_script(alarm),
        chat_id=callback.from_user.id,
        reply_markup=kb.as_markup()
    )
    await callback.message.delete()
    await state.clear()
