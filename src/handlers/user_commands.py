from datetime import datetime
from logging import getLogger

from aiogram import types, Router
from aiogram.filters import CommandStart, Command
from aiogram.filters.callback_data import CallbackData
from aiogram_calendar import SimpleCalendar, get_user_locale, SimpleCalendarCallback

from src.models.user_model import UserModel
from src.services.storage.interfaces import IThemesStorageHandler, IUserStorageHandler
from src.services.storage.themes_storage_handler import ThemesStorageHandler
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
            first_name=msg.from_user.first_name,
            last_name=msg.from_user.last_name
        )
        await sh.create(user)
    finally:
        kb = create_main_menu_kb()
        await msg.answer(text="Тут текст приветствия и главного меню", reply_markup=kb.as_markup())


async def test(msg: types.Message, storage: IThemesStorageHandler = ThemesStorageHandler()) -> None:  # TODO
    """Only for dev"""
    logger.info(f"start handling 'start' event from user: {msg.from_user.id}")
    await msg.answer(
        "Please select a date: ",
        reply_markup=await SimpleCalendar(locale=await get_user_locale(msg.from_user)).start_calendar()
    )


async def process_simple_calendar(callback_query: types.CallbackQuery, callback_data: SimpleCalendarCallback):
    calendar = SimpleCalendar(
        locale=await get_user_locale(callback_query.from_user), show_alerts=True
    )
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(
            f'You selected {date.strftime("%d/%m/%Y")}',
        )


def register_user_command_router() -> Router:
    router = Router(name="user_command")
    router.message.register(start, CommandStart())
    router.message.register(test, Command("test"))
    router.callback_query.register(process_simple_calendar, SimpleCalendarCallback.filter())

    return router
