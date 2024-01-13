from logging import getLogger

from aiogram import types, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from pydantic import ValidationError

from src.models.themes_modles import ThemeModelToCreate, ThemeLinksModel
from src.services.storage.interfaces import IThemesStorageHandler
from src.services.storage.themes_storage_handler import ThemesStorageHandler
from src.services.ui.callbacks import Callbacks
from src.services.ui.inline_keyboards import create_cancel_fsm_kb, create_change_fsm_user_data_kb, create_save_kb, \
    create_main_menu_kb
from src.utils.exceptions.decorators import handel_storage_unexpected_response
from src.utils.fsm.fsm import CreateThemeFSM


logger = getLogger(f"fsm_{__name__}")
router = Router(name=__name__)


@router.callback_query(lambda x: x.data == Callbacks.create_theme, StateFilter(None))
@router.callback_query(lambda x: x.data == Callbacks.CHANGE_FSM_USER_DATA, CreateThemeFSM.accept)
async def create_theme(
        callback: types.CallbackQuery,
        state: FSMContext
) -> None:
    """"""
    message = await callback.bot.send_message(
        text="Введите название темы",
        chat_id=callback.from_user.id,
        reply_markup=create_cancel_fsm_kb().as_markup()
    )
    await state.update_data(last_message_id=message.message_id)

    await callback.message.delete()
    await state.set_state(CreateThemeFSM.write_name)


@router.message(CreateThemeFSM.write_name)
async def create_theme_write_name(message: Message, state: FSMContext) -> None:
    """"""
    # Get user data
    user_data = await state.get_data()
    previous_message_id = user_data.get("last_message_id")

    # Update user data
    await state.update_data(theme_name=message.text)

    # Answer to user
    out_message = await message.answer(
        text=f"Имя темы: {message.text}, теперь введите описание темы",
        reply_markup=create_cancel_fsm_kb().as_markup()
    )
    await state.update_data(last_message_id=out_message.message_id)

    # Delete previous messages
    await message.bot.delete_message(
        chat_id=message.from_user.id,
        message_id=previous_message_id
    )
    await message.delete()

    await state.set_state(CreateThemeFSM.write_description)


@router.message(CreateThemeFSM.write_description)
async def create_theme_write_description(message: Message, state: FSMContext) -> None:
    """"""
    await state.update_data(theme_description=message.text)
    user_data = await state.get_data()
    previous_message_id = user_data.get("last_message_id")

    # Create inline keyboard
    kb = create_save_kb()
    kb.attach(create_change_fsm_user_data_kb())
    kb.attach(create_cancel_fsm_kb())

    out_message = await message.answer(
        text=f"Имя темы: {user_data.get('theme_name')}\nОписание темы: {user_data.get('theme_description')}",
        reply_markup=kb.as_markup()
    )
    await state.update_data(last_message_id=out_message.message_id)

    # Delete previous messages
    await message.bot.delete_message(
        chat_id=message.from_user.id,
        message_id=previous_message_id
    )
    await message.delete()

    await state.set_state(CreateThemeFSM.accept)


@router.callback_query(lambda x: x.data == Callbacks.SAVE, CreateThemeFSM.accept)
@handel_storage_unexpected_response
async def create_theme_save(
        callback: types.CallbackQuery,
        state: FSMContext,
        sh: IThemesStorageHandler = ThemesStorageHandler()
) -> None:
    """"""
    user_data = await state.get_data()
    previous_message_id = user_data.get("last_message_id")
    await callback.bot.delete_message(
        chat_id=callback.from_user.id,
        message_id=previous_message_id
    )

    try:
        theme = ThemeModelToCreate(
            name=user_data["theme_name"],
            description=user_data["theme_description"],
            links=ThemeLinksModel(
                user_id=str(callback.from_user.id)
            )
        )
    except KeyError as err:
        logger.error(f"Can't find user fsm data. details: {err}. user_data: {user_data}")
        await callback.bot.send_message(
            text="Что-то пошло не так, попробуйте позже",
            chat_id=callback.from_user.id,
        )
    except ValidationError as err:
        logger.error(f"Model validation error. details: {err}")
        await callback.bot.send_message(
            text="Что-то пошло не так, попробуйте позже",
            chat_id=callback.from_user.id,
        )
    else:
        theme_id = await sh.create(theme)
        logger.info(f"Successfully create theme with id: {theme_id}")
        await callback.bot.send_message(
            text=f"Тема {user_data.get('theme_name')} успешно создана",
            chat_id=callback.from_user.id,
            reply_markup=create_main_menu_kb().as_markup()
        )
    finally:
        await state.clear()
