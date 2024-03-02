import re

from datetime import datetime, timedelta
from logging import getLogger

from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram_calendar import SimpleCalendar, get_user_locale, SimpleCalendarCallback
from pydantic import ValidationError

from src.models.alarm_model import AlarmModelToCreate
from src.services.storage.alarms_storage_handler import AlarmsStoragehandler
from src.services.storage.interfaces import IAlarmsStoragehandler
from src.services.ui.callbacks import Callbacks
from src.services.ui.inline_keyboards import create_cancel_fsm_kb, create_yes_no_keyboard, \
    create_change_fsm_user_data_kb, create_save_kb, create_main_menu_kb
from src.utils.fsm.fsm import CreateAlarm
from src.utils.handlers_utils import del_prev_message_and_write_current_message_as_prev

logger = getLogger(f"fsm_{__name__}")
router = Router(name=__name__)


@router.callback_query(lambda x: x.data.startswith(Callbacks.CREATE_ALARM), StateFilter(None))
async def create_alarm(callback: types.CallbackQuery, state: FSMContext) -> None:
    """"""
    parent_id = Callbacks.get_id_from_callback(callback.data)
    await state.update_data(parent_id=parent_id)
    out_message = await callback.bot.send_message(
        text="Введите название напоминания",
        chat_id=callback.from_user.id,
        reply_markup=create_cancel_fsm_kb().as_markup()
    )

    await callback.message.delete()
    await del_prev_message_and_write_current_message_as_prev(
        message=callback, state=state, current_message_id=out_message.message_id
    )
    await state.set_state(CreateAlarm.write_name)


@router.message(CreateAlarm.write_name)
async def create_alarm_write_name(message: types.Message, state: FSMContext) -> None:
    await state.update_data(alarm_name=message.text)

    out_message = await message.answer(
        text=f"Имя напоминания: {message.text}, теперь введите описание заметки",
        reply_markup=create_cancel_fsm_kb().as_markup()
    )

    await message.delete()
    await del_prev_message_and_write_current_message_as_prev(
        message=message, state=state, current_message_id=out_message.message_id
    )
    await state.set_state(CreateAlarm.write_description)


@router.message(CreateAlarm.write_description)
async def create_alarm_write_description(message: types.Message, state: FSMContext) -> None:
    await state.update_data(alarm_description=message.text)
    user_data = await state.get_data()

    out_message = await message.answer(
        text=f"""Имя напоминания: {user_data.get('alarm_name')}
        \nОписание напоминания: {user_data.get('alarm_description')}
        \nВыберете дату напоминания
        """,
        reply_markup=await SimpleCalendar(locale=None).start_calendar()
    )

    await message.delete()
    await del_prev_message_and_write_current_message_as_prev(
        message=message, state=state, current_message_id=out_message.message_id
    )
    await state.set_state(CreateAlarm.write_next_notion_date)


@router.callback_query(SimpleCalendarCallback.filter(), CreateAlarm.write_next_notion_date)
async def create_alarm_write_next_notion_date(
        callback: types.CallbackQuery,
        callback_data: SimpleCalendarCallback,
        state: FSMContext
) -> None:
    select: bool
    date: datetime

    calendar = SimpleCalendar(
        locale=await get_user_locale(callback.from_user), show_alerts=True
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
        await state.set_state(CreateAlarm.write_next_notion_time)
        await del_prev_message_and_write_current_message_as_prev(
            message=callback, state=state, current_message_id=out_message.message_id
        )
    else:
        ...


@router.message(CreateAlarm.write_next_notion_time)
async def create_alarm_write_next_notion_time(message: types.Message, state: FSMContext) -> None:
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
            text=f"Выбрано время: {user_time.strftime('%H:%M')}\n\nУведомление будет повторяющимся?",
            reply_markup=create_yes_no_keyboard().as_markup()
        )
        await state.set_state(CreateAlarm.choose_repeatable)
    finally:
        await message.delete()
        await del_prev_message_and_write_current_message_as_prev(
            message=message, state=state, current_message_id=out_message.message_id
        )


@router.callback_query(lambda x: x.data == Callbacks.YES, CreateAlarm.choose_repeatable)
async def create_alarm_choose_repeatable(callback: types.CallbackQuery, state: FSMContext) -> None:
    """"""
    await state.update_data(is_repeatable=True)
    out_message = await callback.bot.send_message(
        text="Теперь введите, каждые сколько минут будет повторяться уведомление",  # TODO validator and input form
        chat_id=callback.from_user.id
    )

    await del_prev_message_and_write_current_message_as_prev(
        message=callback, state=state, current_message_id=out_message.message_id
    )
    await state.set_state(CreateAlarm.choose_repeatable_interval)


@router.callback_query(lambda x: x.data == Callbacks.NO, CreateAlarm.choose_repeatable)
async def create_alarm_accept_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    """"""
    user_data = await state.get_data()

    next_notion_date: datetime = user_data["date"]
    next_notion_time: datetime = user_data["time"]
    next_notion = datetime.strptime(
        f"{next_notion_date.strftime('%d/%m/%Y')} {next_notion_time.strftime('%H:%M')}",
        "%d/%m/%Y %H:%M"
    )

    await state.update_data(repeat_interval=None)
    await state.update_data(is_repeatable=False)
    await state.update_data(next_notion=next_notion)

    kb = create_save_kb()
    kb.attach(create_change_fsm_user_data_kb())
    kb.attach(create_cancel_fsm_kb())

    out_message_text = f"""
        Имя: {user_data["alarm_name"]},
        \nОписание: {"alarm_description"},
        \nВремя следующего напоминнаия: {next_notion}
        \nНапоминание единоразовое
        """

    out_message = await callback.bot.send_message(
        text=out_message_text,
        chat_id=callback.from_user.id,
        reply_markup=kb.as_markup()
    )
    await del_prev_message_and_write_current_message_as_prev(
        message=callback, state=state, current_message_id=out_message.message_id
    )
    await state.set_state(CreateAlarm.accept)


@router.message(CreateAlarm.choose_repeatable_interval)
async def create_alarm_accept(
        message: types.Message,
        state: FSMContext
) -> None:
    """"""
    user_data = await state.get_data()

    next_notion_date: datetime = user_data["date"]
    next_notion_time: datetime = user_data["time"]
    next_notion = datetime.strptime(
        f"{next_notion_date.strftime('%d/%m/%Y')} {next_notion_time.strftime('%H:%M')}",
        "%d/%m/%Y %H:%M"
    )

    await state.update_data(repeat_interval=int(message.text))
    await state.update_data(next_notion=next_notion)

    kb = create_save_kb()
    kb.attach(create_change_fsm_user_data_kb())
    kb.attach(create_cancel_fsm_kb())

    out_message_text = f"""
    Имя: {user_data["alarm_name"]},
    \nОписание: {user_data["alarm_description"]},
    \nВремя следующего напоминнаия: {next_notion}  
    """

    out_message = await message.answer(
        text=out_message_text,
        reply_markup=kb.as_markup()
    )
    await del_prev_message_and_write_current_message_as_prev(
        message=message, state=state, current_message_id=out_message.message_id
    )
    await message.delete()
    await state.set_state(CreateAlarm.accept)


@router.callback_query(lambda x: x.data == Callbacks.SAVE, CreateAlarm.accept)
async def create_alarm_save(
        callback: types.CallbackQuery,
        state: FSMContext,
        sh: IAlarmsStoragehandler = AlarmsStoragehandler()
) -> None:
    """"""
    user_data = await state.get_data()
    try:
        alarm = {
            "name": user_data["alarm_name"],
            "description": user_data["alarm_description"],
            "is_repeatable": user_data["is_repeatable"],
            "links": {
                "user_id": str(callback.from_user.id),
                "parent_id": user_data["parent_id"]
            }
        }
        repeat_interval = user_data["repeat_interval"]
        next_notion_time = user_data["next_notion"]
        await sh.create(
            alarm=AlarmModelToCreate.model_validate(alarm),
            repeat_interval=repeat_interval,
            next_notion_time=next_notion_time
        )
    except KeyError as err:
        logger.error(f"Can't find user fsm data | details: {err} | user_data: {user_data}")
        await callback.bot.send_message(
            text="Что-то пошло не так, попробуйте позже",
            chat_id=callback.from_user.id,
        )
    except ValidationError as err:
        logger.error(f"Model validation error | details: {err}")
        await callback.bot.send_message(
            text="Что-то пошло не так, попробуйте позже",
            chat_id=callback.from_user.id,
        )
    else:
        message_out = await callback.bot.send_message(
            text=f"Напоминанние {user_data.get('alarm_name')} успешно создано",
            chat_id=callback.from_user.id,
            reply_markup=create_main_menu_kb().as_markup()
        )
        await del_prev_message_and_write_current_message_as_prev(
            message=callback, state=state, current_message_id=message_out.message_id
        )
    finally:
        await state.clear()
