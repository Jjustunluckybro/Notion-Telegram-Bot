from logging import getLogger

from aiogram import Bot
from aiogram.utils.formatting import Bold

from src.models.alarm_model import AlarmModel, AlarmStatus
from src.services.storage.alarms_storage_handler import AlarmsStoragehandler
from src.services.storage.interfaces import IAlarmsStoragehandler
from src.services.ui.inline_keyboards import create_sent_alarm_kb
from src.utils.exceptions.decorators import handel_storage_unexpected_response
from src.utils.exceptions.storage import StorageNotFound
from src.utils.handlers_utils import async_method_arguments_logger

logger = getLogger(__name__)


#  331230161

@handel_storage_unexpected_response
@async_method_arguments_logger(logger)
async def check_active_alarms(
        alarms_storage: IAlarmsStoragehandler = AlarmsStoragehandler()
) -> list[AlarmModel] | None:
    """"""
    try:
        alarms = await alarms_storage.get_all_ready()
        return alarms
    except StorageNotFound:
        return None


@async_method_arguments_logger(logger)
async def send_alarm_to_user(alarm: AlarmModel, bot: Bot) -> None:
    text = f"{alarm.name}:\n{alarm.description}"
    kb = create_sent_alarm_kb(alarm_id=alarm.id, is_repeatable=alarm.is_repeatable)
    await bot.send_message(
        chat_id=alarm.links.user_id,
        text=text,
        reply_markup=kb.as_markup()
    )


@async_method_arguments_logger(logger)
async def job_check_active_alarms(
        bot: Bot,
        alarms_storage: IAlarmsStoragehandler = AlarmsStoragehandler()
) -> None:
    """"""
    alarms = await check_active_alarms()
    if alarms is None:
        logger.info(f"Not found active alarms")
        return
    else:
        for alarm in alarms:
            await send_alarm_to_user(alarm, bot)
            logger.info(f"Successful sent alarm with id: {alarm.id}")
            if alarm.is_repeatable:
                await alarms_storage.postpone_repeatable(alarm.id)
            else:
                await alarms_storage.update_status(alarm.id, AlarmStatus.FINISH.value)
