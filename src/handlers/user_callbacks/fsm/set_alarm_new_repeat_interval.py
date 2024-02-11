from logging import getLogger

from aiogram import Router, types

from src.services.storage.alarms_storage_handler import AlarmsStoragehandler
from src.services.storage.interfaces import IAlarmsStoragehandler
from src.services.ui.callbacks import Callbacks
from src.utils.exceptions.decorators import handel_storage_unexpected_response
from src.utils.handlers_utils import async_method_arguments_logger

logger = getLogger(__name__)

router = Router(name=__name__)


@router.callback_query(lambda x: x.data.startswith(Callbacks.SET_ALARM_NEW_REPEAT_INTERVAL))
@handel_storage_unexpected_response
@async_method_arguments_logger(logger)
async def set_alarm_new_repeat_interval(
        callback: types.CallbackQuery,
        alarms_storage: IAlarmsStoragehandler = AlarmsStoragehandler()
) -> None:
    ...
