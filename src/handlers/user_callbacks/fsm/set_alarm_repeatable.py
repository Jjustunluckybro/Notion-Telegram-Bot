from logging import getLogger

from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from src.services.storage.alarms_storage_handler import AlarmsStoragehandler
from src.services.storage.interfaces import IAlarmsStoragehandler
from src.services.ui.callbacks import Callbacks
from src.services.ui.inline_keyboards import create_alarm_menu_kb
from src.services.ui.scripts import get_alarm_menu_script
from src.utils.exceptions.decorators import handel_storage_unexpected_response
from src.utils.exceptions.storage import StorageValidationError, StorageNotFound
from src.utils.fsm.fsm import SetNewAlarmRepeatInterval
from src.utils.handlers_utils import async_method_arguments_logger, send_error_message, \
    del_prev_message_and_write_current_message_as_prev

logger = getLogger(__name__)

router = Router(name=__name__)


@router.callback_query(lambda x: x.data.startswith(Callbacks.CHANGE_ALARM_REPEATABLE))
@handel_storage_unexpected_response
@async_method_arguments_logger(logger)
async def set_alarm_repeatable(
        callback: types.CallbackQuery,
        state: FSMContext,
        alarms_storage: IAlarmsStoragehandler = AlarmsStoragehandler()
) -> None:
    """"""
    try:
        alarm = await alarms_storage.get(Callbacks.get_id_from_callback(callback.data))
        await alarms_storage.patch(
            Callbacks.get_id_from_callback(callback.data),
            {"is_repeatable": not alarm.is_repeatable}
        )
    except StorageValidationError:
        await send_error_message(callback)
    except StorageNotFound as err:
        logger.error(f"Not found alarm by id, bus should. details: {err}")
        await send_error_message(callback)
    else:
        if not alarm.is_repeatable:
            await state.set_state(SetNewAlarmRepeatInterval.write_time)
            await state.update_data(alarm_id=Callbacks.get_id_from_callback(callback.data))
            msg = await callback.bot.send_message(
                text="Напоминание теперь повторяющаеся"
                     "\nВведите продолжительность нового интервала повторений"
                     "\nЧерез пробел довавьте:"
                     "\n'ч' - Если интервал в часах"
                     "\n'м' - Если интервал в минутах",
                chat_id=callback.from_user.id
            )
            await del_prev_message_and_write_current_message_as_prev(
                message=callback, state=state, current_message_id=msg.message_id
            )
        else:
            alarm.is_repeatable = False
            kb = create_alarm_menu_kb(alarm)
            await callback.bot.send_message(
                text="Сохранено\n" + get_alarm_menu_script(alarm),
                chat_id=callback.from_user.id,
                reply_markup=kb.as_markup()
            )
    finally:
        await callback.message.delete()
