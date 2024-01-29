import functools

from logging import Logger
from typing import Callable, Any

from aiogram import types
from aiogram.fsm.context import FSMContext


def async_method_arguments_logger(logger: Logger) -> Callable:
    def decorator(method: Callable) -> Callable:
        @functools.wraps(method)
        async def wrapper(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Any:
            logger.info(f"Statr handler: {method.__name__} | With arguments: {args}, {kwargs}")

            result = await method(*args, **kwargs)

            logger.info(f"Finish handler: {method.__name__} | With result: {result}")

            return result

        return wrapper

    return decorator


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


async def send_error_message(
        message: types.Message | types.CallbackQuery,
        state: FSMContext | None = None,
        text: str = "Что-то пошло не так, попробуйте позже :("
) -> types.Message:
    """"""

    if state is not None:
        await state.clear()

    if isinstance(message, types.Message):
        message_out = await message.answer(text)
    else:
        message_out = await message.bot.send_message(
            chat_id=message.from_user.id,
            text=text
        )

    return message_out
