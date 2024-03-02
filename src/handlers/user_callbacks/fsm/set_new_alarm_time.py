from datetime import datetime, timedelta
from logging import getLogger
import re

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from src.models.alarm_model import AlarmStatus
from src.services.storage.alarms_storage_handler import AlarmsStoragehandler
from src.services.storage.interfaces import IAlarmsStoragehandler
from src.services.ui.callbacks import Callbacks
from src.services.ui.inline_keyboards import create_yes_no_keyboard, create_alarm_menu_kb
from src.services.ui.scripts import get_alarm_menu_script
from src.utils.exceptions.decorators import handel_storage_unexpected_response
from src.utils.exceptions.storage import StorageValidationError, StorageNotFound
from src.utils.fsm.fsm import SetNewAlarmTime
from src.utils.handlers_utils import async_method_arguments_logger, del_prev_message_and_write_current_message_as_prev, \
    send_error_message

logger = getLogger(__name__)

router = Router(name=__name__)


@router.callback_query(lambda x: x.data.startswith(Callbacks.SET_NEW_ALARM_TIME))
@async_method_arguments_logger(logger)
async def set_new_alarm_time(
        callback: types.CallbackQuery,
        state: FSMContext,
) -> None:
    """"""
    await state.set_state(SetNewAlarmTime.write_next_notion_date)
    await state.update_data(alarm_id=Callbacks.get_id_from_callback(callback.data))

    msg = await callback.message.answer(
        text="Выберете дату напоминания",
        reply_markup=await SimpleCalendar(locale=None).start_calendar()
    )
    await del_prev_message_and_write_current_message_as_prev(callback, state, msg.message_id)
    await callback.message.delete()


@router.callback_query(SimpleCalendarCallback.filter(), SetNewAlarmTime.write_next_notion_date)
@async_method_arguments_logger(logger)
async def set_new_alarm_time_write_date(
        callback: types.CallbackQuery,
        callback_data: SimpleCalendarCallback,
        state: FSMContext
) -> None:
    """"""
    calendar = SimpleCalendar(
        locale=None, show_alerts=True
    )
    calendar.set_dates_range(
        datetime.now() - timedelta(days=1),
        datetime.now() + timedelta(weeks=5200)  # 5200 weeks ~ 100 years
    )
    selected, date = await calendar.process_selection(callback, callback_data)

    if selected:
        await state.update_data(date=date)
        out_message = await callback.bot.send_message(
            text=f"Выбраная дата: {date.strftime('%d/%m/%Y')}\nТеперь введите время в формате 'hh:mm'",
            chat_id=callback.from_user.id
        )
        await state.set_state(SetNewAlarmTime.write_next_notion_time)
        await del_prev_message_and_write_current_message_as_prev(
            message=callback, state=state, current_message_id=out_message.message_id
        )
    else:
        ...


@router.message(SetNewAlarmTime.write_next_notion_time)
@async_method_arguments_logger(logger)
async def set_new_alarm_time_write_time(
        message: types.Message,
        state: FSMContext
) -> None:
    """"""
    out_message = None
    user_time = message.text
    try:
        pattern = r"^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$"
        if re.match(pattern, user_time):
            user_time = datetime.strptime(user_time, "%H:%M")
        else:
            raise ValueError
    except ValueError:
        out_message = await message.answer(
            text=f"Введите время в формате 'hh:mm'",
        )
    else:
        await state.update_data(time=user_time)
        out_message = await message.answer(
            text=f"Выбрано время: {user_time.strftime('%H:%M')}\nСохранить?",
            reply_markup=create_yes_no_keyboard().as_markup()
        )
        await state.set_state(SetNewAlarmTime.accept)
    finally:
        await del_prev_message_and_write_current_message_as_prev(
            message=message, state=state, current_message_id=out_message.message_id
        )
        await message.delete()


@router.callback_query(lambda x: x.data == Callbacks.YES, SetNewAlarmTime.accept)
@handel_storage_unexpected_response
@async_method_arguments_logger(logger)
async def save_new_alarm_time(
        callback: types.CallbackQuery,
        state: FSMContext,
        alarm_storage: IAlarmsStoragehandler = AlarmsStoragehandler()
) -> None:
    """"""
    user_data = await state.get_data()
    alarm_id: str = user_data["alarm_id"]
    next_notion_date: datetime = user_data["date"]
    next_notion_time: datetime = user_data["time"]
    next_notion = datetime.strptime(
        f"{next_notion_date.strftime('%d/%m/%Y')} {next_notion_time.strftime('%H:%M')}",
        "%d/%m/%Y %H:%M"
    )
    try:
        await alarm_storage.patch(
            alarm_id,
            {
                "times.next_notion_time": str(next_notion),
                "status": AlarmStatus.QUEUE
            }
        )
        alarm = await alarm_storage.get(alarm_id)
    except StorageValidationError or StorageNotFound as err:
        if isinstance(err, StorageNotFound):
            logger.error(f"Not found alarm, but should. details: {err}")
        await send_error_message(callback, state)
    else:
        kb = create_alarm_menu_kb(alarm)
        await callback.bot.send_message(
            text=f"Новое время уведомления: {next_notion}\n" + get_alarm_menu_script(alarm),
            chat_id=callback.from_user.id,
            reply_markup=kb.as_markup()
        )
    finally:
        await callback.message.delete()
        await state.clear()


@router.callback_query(lambda x: x.data == Callbacks.NO, SetNewAlarmTime.accept)
@handel_storage_unexpected_response
@async_method_arguments_logger(logger)
async def set_new_alarm_time_cancel(
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
