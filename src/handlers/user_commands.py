from datetime import datetime
from logging import getLogger

from aiogram import types, Router
from aiogram.filters import CommandStart
from aiogram_calendar import SimpleCalendar, get_user_locale, SimpleCalendarCallback

from src.models.user_model import UserModel
from src.services.storage.interfaces import IUserStorageHandler
from src.services.storage.user_storage_handler import UserStorageHandler
from src.services.ui.inline_keyboards import create_main_menu_kb
from src.utils.exceptions.decorators import handel_storage_unexpected_response
from src.utils.exceptions.storage import StorageNotFound

logger = getLogger(__name__)


@handel_storage_unexpected_response
async def start(msg: types.Message, sh: IUserStorageHandler = UserStorageHandler()) -> None:
    user_id = str(msg.from_user.id)
    logger.info(f"start handling 'start' event from user: {user_id}")
    try:
        user_id = await sh.get(user_id)
    except StorageNotFound:
        user = UserModel(
            telegram_id=user_id,
            user_name=msg.from_user.username,
            lang_code=msg.from_user.language_code,
            timezone=3,
            first_name=msg.from_user.first_name,
            last_name=msg.from_user.last_name
        )
        await sh.create(user)
    finally:
        kb = create_main_menu_kb()
        await msg.answer(text="Тут текст приветствия и главного меню", reply_markup=kb.as_markup())


def register_user_command_router() -> Router:
    router = Router(name="user_command")
    router.message.register(start, CommandStart())

    return router
