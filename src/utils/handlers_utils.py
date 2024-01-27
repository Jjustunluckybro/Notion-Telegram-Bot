from aiogram import types
from aiogram.fsm.context import FSMContext


async def del_prev_message_and_write_current_message_as_prev(
        message: types.Message | types.CallbackQuery,
        state: FSMContext,
        current_message_id: int
) -> None:
    """

    :rtype: object
    """
    user_data = await state.get_data()
    try:
        prev_message_id: int = user_data["last_message_id"]
    except KeyError:
        ...
    else:
        await message.bot.delete_message(
            chat_id=message.from_user.id,
            message_id=prev_message_id
        )
    finally:
        await state.update_data(last_message_id=current_message_id)
