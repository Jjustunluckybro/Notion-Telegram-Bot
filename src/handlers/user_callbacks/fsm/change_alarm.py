from logging import getLogger

from aiogram import types, Router

from aiogram.fsm.context import FSMContext

from src.models.alarm_model import AlarmModel
from src.services.storage.interfaces import IAlarmsStoragehandler
from src.services.storage.alarms_storage_handler import AlarmsStoragehandler
from src.services.ui.callbacks import Callbacks
from src.services.ui.inline_keyboards import create_save_kb, create_change_name_or_description_kb, create_alarm_menu_kb
from src.services.ui.scripts import get_change_alarm_accept_script, get_alarm_menu_script
from src.utils.exceptions.decorators import handel_storage_unexpected_response
from src.utils.exceptions.storage import StorageValidationError, StorageNotFound
from src.utils.fsm.fsm import ChangeAlarm
from src.utils.handlers_utils import send_error_message, async_method_arguments_logger, \
    del_prev_message_and_write_current_message_as_prev


logger = getLogger(f"fsm_{__name__}")
router = Router(name=__name__)


@router.callback_query(lambda x: x.data.startswith(Callbacks.CHANGE_ALARM))
@handel_storage_unexpected_response
@async_method_arguments_logger(logger)
async def change_alarm(
        callback: types.CallbackQuery,
        state: FSMContext,
        alarm_storage: IAlarmsStoragehandler = AlarmsStoragehandler()
) -> None:
    """"""
    alarm_id = Callbacks.get_id_from_callback(callback.data)
    try:
        alarm = await alarm_storage.get(alarm_id)
    except StorageNotFound as err:
        logger.error(f"Not found alarm, but should. details: {err}")
        await send_error_message(callback)
    except StorageValidationError:
        await send_error_message(callback)
    else:
        await state.set_state(ChangeAlarm.change_alarm)
        await state.update_data(alarm=alarm)
        kb = create_change_name_or_description_kb()
        msg = await callback.message.answer(
            text="Выберити что изменить",
            reply_markup=kb.as_markup()
        )
        await del_prev_message_and_write_current_message_as_prev(callback, state, msg.message_id)
    finally:
        await callback.message.delete()


@router.callback_query(lambda x: x.data == Callbacks.CHANGE_NAME, ChangeAlarm.change_alarm)
@async_method_arguments_logger(logger)
async def change_alarm_name(
        callback: types.CallbackQuery,
        state: FSMContext
) -> None:
    """"""
    await state.set_state(ChangeAlarm.change_name)
    msg = await callback.message.answer(
        text="Введите новое имя"
    )
    await del_prev_message_and_write_current_message_as_prev(callback, state, msg.message_id)


@router.callback_query(lambda x: x.data == Callbacks.CHANGE_DESCRIPTION, ChangeAlarm.change_alarm)
@async_method_arguments_logger(logger)
async def change_alarm_description(
        callback: types.CallbackQuery,
        state: FSMContext
) -> None:
    """"""
    await state.set_state(ChangeAlarm.change_description)
    msg = await callback.message.answer(
        text="Введите новое описание"
    )
    await del_prev_message_and_write_current_message_as_prev(callback, state, msg.message_id)


@router.message(ChangeAlarm.change_description)
@router.message(ChangeAlarm.change_name)
@async_method_arguments_logger(logger)
async def change_alarm_accept(
        message: types.Message,
        state: FSMContext
) -> None:
    """"""
    current_state = await state.get_state()
    if current_state == ChangeAlarm.change_name:
        await state.update_data(new_name=message.text)
    if current_state == ChangeAlarm.change_description:
        await state.update_data(new_description=message.text)

    user_data = await state.get_data()
    text = get_change_alarm_accept_script(user_data)
    kb = create_save_kb()
    kb.attach(create_change_name_or_description_kb())
    msg = await message.answer(
        text=text,
        reply_markup=kb.as_markup()
    )
    await state.set_state(ChangeAlarm.change_alarm)
    await del_prev_message_and_write_current_message_as_prev(message, state, msg.message_id)


@router.callback_query(lambda x: x.data == Callbacks.CANCEL, ChangeAlarm.change_alarm)
@handel_storage_unexpected_response
@async_method_arguments_logger(logger)
async def change_alarm_cancel(
        callback: types.CallbackQuery,
        state: FSMContext
) -> None:
    """"""
    user_data = await state.get_data()
    try:
        alarm: AlarmModel = user_data["alarm"]
    except KeyError as err:
        logger.error(f"Invalid state user data. details: {err}. user_data: {user_data}")
        await send_error_message(callback, state)
        await callback.message.delete()
        return

    text = get_alarm_menu_script(alarm)
    kb = create_alarm_menu_kb(alarm)
    await callback.message.answer(
        text=text,
        reply_markup=kb.as_markup()
    )
    await state.clear()
    await callback.message.delete()


@router.callback_query(lambda x: x.data == Callbacks.SAVE, ChangeAlarm.change_alarm)
@handel_storage_unexpected_response
@async_method_arguments_logger(logger)
async def change_alarm_accept(
        callback: types.CallbackQuery,
        state: FSMContext,
        alarm_storage: IAlarmsStoragehandler = AlarmsStoragehandler()
) -> None:
    """"""
    user_data = await state.get_data()
    new_data = dict()

    # Try to get alarm from state
    try:
        alarm: AlarmModel = user_data["alarm"]
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
        await alarm_storage.patch(alarm.id, new_data)
    except StorageNotFound as err:
        logger.error(f"not found theme, but should. deteils: {err}")
        await send_error_message(callback, state)
        return
    except StorageValidationError:
        await send_error_message(callback, state)
        return

    # Try to get updated theme and make start of script
    try:
        alarm = await alarm_storage.get(alarm.id)
    except StorageNotFound as err:
        logger.error(f"not found alarm, but should. deteils: {err}")
        await send_error_message(callback, state, "Изменения сохранены, но дальше что-то пошло не так :(")
        return
    except StorageValidationError:
        await send_error_message(callback, state, "Изменения сохранены, но дальше что-то пошло не так :(")
        return

    # Make theme menu and show it
    kb = create_alarm_menu_kb(alarm)
    text = get_alarm_menu_script(alarm)
    await callback.message.answer(
        text=text,
        reply_markup=kb.as_markup()
    )
    await state.clear()
    await callback.message.delete()
