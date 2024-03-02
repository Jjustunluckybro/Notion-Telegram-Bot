from logging import getLogger

from aiogram import types, Router
from aiogram.fsm.context import FSMContext

from src.services.ui.callbacks import Callbacks
from src.services.ui.inline_keyboards import create_main_menu_kb

logger = getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(lambda x: x.data == Callbacks.CANCEL_FSM)
async def cancel_fsm(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Callback to cancel any fsm state
    :param callback: telegram inline key callback query
    :param state: current fsm state
    :return:
    """

    await state.clear()
    await callback.message.delete()

    kb = create_main_menu_kb()
    await callback.bot.send_message(
        text="Тут текст приветствия и главного меню",
        chat_id=callback.from_user.id,
        reply_markup=kb.as_markup()
    )


@router.callback_query(lambda x: x.data == Callbacks.OPEN_MAIN_MENU)
async def open_main_menu(callback: types.CallbackQuery) -> None:
    """
    Callback to open main menu
    :param callback: telegram inline key callback query
    :return: None
    """
    kb = create_main_menu_kb()
    await callback.bot.send_message(
        text="Тут текст приветствия и главного меню",
        chat_id=callback.from_user.id,
        reply_markup=kb.as_markup()
    )
    await callback.message.delete()
