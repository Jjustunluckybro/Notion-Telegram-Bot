from logging import getLogger

from aiogram import types, Router
from aiogram.fsm.context import FSMContext

from src.models.alarm_model import AlarmStatus
from src.services.storage.alarms_storage_handler import AlarmsStoragehandler
from src.services.storage.interfaces import IAlarmsStoragehandler
from src.services.ui.callbacks import Callbacks
from src.services.ui.inline_keyboards import create_alarm_menu_kb
from src.services.ui.scripts import get_alarm_menu_script
from src.utils.exceptions.decorators import handel_storage_unexpected_response
from src.utils.exceptions.storage import StorageValidationError, StorageNotFound
from src.utils.handlers_utils import async_method_arguments_logger, send_error_message

logger = getLogger(__name__)

router = Router(name=__name__)


@router.callback_query(lambda x: x.data.startswith(Callbacks.OPEN_ALARM_START_WITH))
@handel_storage_unexpected_response
@async_method_arguments_logger(logger)
async def open_alarm(
        callback: types.CallbackQuery,
        alarms_storage: IAlarmsStoragehandler = AlarmsStoragehandler(),
        state: FSMContext = None
) -> None:
    """"""
    alarm_id = Callbacks().get_id_from_callback(callback.data)
    if state is not None:
        await state.clear()

    try:
        alarm = await alarms_storage.get(alarm_id)
    except StorageValidationError:
        await send_error_message(callback)
    except StorageNotFound as err:
        logger.error(f"Not found alarm, but should. details: {err}")
        await send_error_message(callback)
    else:
        kb = create_alarm_menu_kb(alarm)
        await callback.bot.send_message(
            text=get_alarm_menu_script(alarm),
            chat_id=callback.from_user.id,
            reply_markup=kb.as_markup()
        )
    finally:
        await callback.message.delete()


@router.callback_query(lambda x: x.data.startswith(Callbacks.FINISH_ALARM))
@handel_storage_unexpected_response
@async_method_arguments_logger(logger)
async def finish_alarm(
        callback: types.CallbackQuery,
        alarms_storage: IAlarmsStoragehandler = AlarmsStoragehandler()
) -> None:
    """"""
    alarm_id = Callbacks.get_id_from_callback(callback.data)

    try:
        await alarms_storage.update_status(alarm_id, AlarmStatus.FINISH.value)
    except StorageValidationError:
        await send_error_message(callback)
    except StorageNotFound as err:
        f"Not found alarm, but should. details: {err}"
        await send_error_message(callback)
    else:
        try:
            alarm = await alarms_storage.get(alarm_id)
        except StorageValidationError:
            await send_error_message(callback)
        except StorageNotFound as err:
            logger.error(f"Not found alarm, but should. details: {err}")
            await send_error_message(callback)
        else:
            kb = create_alarm_menu_kb(alarm)
            await callback.bot.send_message(
                text=get_alarm_menu_script(alarm),
                chat_id=callback.from_user.id,
                reply_markup=kb.as_markup()
            )
    finally:
        await callback.message.delete()


@router.callback_query(lambda x: x.data.startswith(Callbacks.SET_ALARM_NOT_REPEATABLE))
@handel_storage_unexpected_response
@async_method_arguments_logger(logger)
async def set_alarm_not_repeatable(
        callback: types.CallbackQuery,
        alarms_storage: IAlarmsStoragehandler = AlarmsStoragehandler()
) -> None:
    alarm_id = Callbacks.get_id_from_callback(callback.data)

    try:
        await alarms_storage.patch(alarm_id, {"is_repeatable": False})
    except StorageValidationError:
        await send_error_message(callback)
    except StorageNotFound as err:
        logger.error(f"Not found alarm, but should. details: {err}")
        await send_error_message(callback)
    else:
        try:
            alarm = await alarms_storage.get(alarm_id)
        except StorageValidationError:
            await send_error_message(callback)
        except StorageNotFound as err:
            logger.error(f"Not found alarm, but should. details: {err}")
            await send_error_message(callback)
        else:
            kb = create_alarm_menu_kb(alarm)
            await callback.bot.send_message(
                text=get_alarm_menu_script(alarm),
                chat_id=callback.from_user.id,
                reply_markup=kb.as_markup()
            )
    finally:
        await callback.message.delete()
