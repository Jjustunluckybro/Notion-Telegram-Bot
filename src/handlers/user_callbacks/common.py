from logging import getLogger

from aiogram import types, Router

from src.services.ui.callbacks import Callbacks
from src.utils.handlers_utils import async_method_arguments_logger

logger = getLogger(__name__)

router = Router(name=__name__)


@router.callback_query(lambda x: x.data == Callbacks.CLOSE_MESSAGE)
@async_method_arguments_logger(logger)
async def delete_callback_message(callback: types.CallbackQuery) -> None:
    """"""
    await callback.message.delete()
