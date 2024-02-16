from logging import getLogger
from typing import Final

from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from src.services.storage.alarms_storage_handler import AlarmsStoragehandler
from src.services.storage.interfaces import IAlarmsStoragehandler
from src.services.ui.callbacks import Callbacks
from src.services.ui.inline_keyboards import create_yes_no_keyboard, create_alarm_menu_kb
from src.services.ui.scripts import get_alarm_menu_script
from src.utils.exceptions.decorators import handel_storage_unexpected_response
from src.utils.exceptions.storage import StorageValidationError, StorageNotFound
from src.utils.fsm.fsm import SetNewAlarmRepeatInterval
from src.utils.handlers_utils import async_method_arguments_logger, del_prev_message_and_write_current_message_as_prev, \
    send_error_message

logger = getLogger(__name__)

router = Router(name=__name__)


@router.callback_query(lambda x: x.data.startswith(Callbacks.SET_ALARM_NEW_REPEAT_INTERVAL))
@async_method_arguments_logger(logger)
async def set_alarm_new_repeat_interval(
        callback: types.CallbackQuery,
        state: FSMContext,
) -> None:
    """"""
    await state.set_state(SetNewAlarmRepeatInterval.write_time)
    await state.update_data(alarm_id=Callbacks.get_id_from_callback(callback.data))
    msg = await callback.bot.send_message(
        text="Введите продолжительность нового интервала"
             "\nЧерез пробел довавьте:"
             "\n'ч' - Если интервал в часах"
             "\n'м' - Если интервал в минутах",
        chat_id=callback.from_user.id
    )
    await del_prev_message_and_write_current_message_as_prev(
        message=callback, state=state, current_message_id=msg.message_id
    )
    await callback.message.delete()


@router.message(SetNewAlarmRepeatInterval.write_time)
@async_method_arguments_logger(logger)
async def write_new_repeat_interval(
        message: types.Message,
        state: FSMContext
) -> None:
    """"""
    time = message.text.split(" ")
    seconds_in_minutes: Final[int] = 60
    seconds_in_hour: Final[int] = 3600

    try:
        interval = int(time[0])
        unit_of_time = time[1].capitalize()
    except ValueError:
        msg = await message.answer("Введите продолжительность нового интервала числом!"
                                   "\nЧерез пробел довавьте:"
                                   "\n'ч' - Если интервал в часах"
                                   "\n'м' - Если интервал в минутах")
        await del_prev_message_and_write_current_message_as_prev(msg, state, msg.message_id)
        await message.delete()
        return
    except IndexError:
        msg = await message.answer("После продолжительности нового интервала добавьте через пробел:"
                                   "\n'ч' - Если интервал в часах"
                                   "\n'м' - Если интервал в минутах")
        await del_prev_message_and_write_current_message_as_prev(msg, state, msg.message_id)
        await message.delete()
        return

    match unit_of_time:
        case "Ч":
            await state.update_data(
                interval=interval * seconds_in_hour
            )
        case "М":
            await state.update_data(
                interval=interval * seconds_in_minutes
            )
        case _:
            msg = await message.answer("Используйте только 'ч' или 'м'!"
                                       "\nВведите продолжительность нового интервала числом"
                                       "\nЧерез пробел довавьтеЖ:"
                                       "\n'ч' - Если интервал в часах"
                                       "\n'м' - Если интервал в минутах")
            await del_prev_message_and_write_current_message_as_prev(msg, state, msg.message_id)
            await message.delete()
            return

    msg = await message.answer(
        text=f"\nВы выбрали время: {time[0]} {time[1]}"
             f"\nСохранить?",
        reply_markup=create_yes_no_keyboard().as_markup()
    )
    await state.set_state(SetNewAlarmRepeatInterval.accept)
    await del_prev_message_and_write_current_message_as_prev(msg, state, msg.message_id)
    await message.delete()


@router.callback_query(lambda x: x.data == Callbacks.YES, SetNewAlarmRepeatInterval.accept)
@handel_storage_unexpected_response
@async_method_arguments_logger(logger)
async def save_new_repeat_interval(
        callback: types.CallbackQuery,
        state: FSMContext,
        alarm_storage: IAlarmsStoragehandler = AlarmsStoragehandler()
) -> None:
    """"""
    user_data = await state.get_data()
    alarm_id: str = user_data["alarm_id"]
    interval: int = user_data["interval"]

    try:
        await alarm_storage.patch(alarm_id, {"times.repeat_interval": interval})
        alarm = await alarm_storage.get(alarm_id)
    except StorageValidationError or StorageNotFound as err:
        if isinstance(err, StorageNotFound):
            logger.error(f"Not found alarm, but should. details: {err}")
        await send_error_message(callback, state)
    else:
        kb = create_alarm_menu_kb(alarm)
        await callback.bot.send_message(
            text="Новый интервал успешно установлен\n" + get_alarm_menu_script(alarm),
            chat_id=callback.from_user.id,
            reply_markup=kb.as_markup()
        )
    finally:
        await callback.message.delete()
        await state.clear()


@router.callback_query(lambda x: x.data == Callbacks.NO, SetNewAlarmRepeatInterval.accept)
@handel_storage_unexpected_response
@async_method_arguments_logger(logger)
async def cancel_set_new_repeat_interval(
        callback: types.CallbackQuery,
        state: FSMContext,
        alarm_storage: IAlarmsStoragehandler = AlarmsStoragehandler()
) -> None:
    """"""
    user_data = await state.get_data()
    alarm_id: str = user_data["alarm_id"]
    try:
        alarm = await alarm_storage.get(alarm_id)
    except StorageValidationError or StorageNotFound as err:
        if isinstance(err, StorageNotFound):
            logger.error(f"Not found alarm, but should. details: {err}")
        await send_error_message(callback, state)
    else:
        kb = create_alarm_menu_kb(alarm)
        await callback.bot.send_message(
            text=get_alarm_menu_script(alarm),
            chat_id=callback.from_user.id,
            reply_markup=kb.as_markup()
        )
    finally:
        await callback.message.delete()
        await state.clear()
