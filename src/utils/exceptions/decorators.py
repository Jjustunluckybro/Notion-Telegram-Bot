import functools
import traceback
from logging import getLogger
from typing import Callable, Any

from aiogram import types

from src.utils.exceptions.storage import UnexpectedResponse


def handel_storage_unexpected_response(method: Callable) -> Callable:
    """Handle UnexpectedResponse in callback or message handlers"""

    logger = getLogger("UnexpectedResponse")

    @functools.wraps(method)
    async def wrapper(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Any:
        try:
            return await method(*args, **kwargs)

        except UnexpectedResponse as e:
            logger.critical(f"{str(e)} Details: {traceback.format_exc()}")

            text = "Что-то пошло не так, попробуйте позже"
            for i in args:
                if isinstance(i, types.CallbackQuery):
                    await i.bot.send_message(
                        text=text,
                        chat_id=i.from_user.id
                    )
                    await i.message.delete()
                    return wrapper
                if isinstance(i, types.Message):
                    await i.answer(text=text)
                    await i.message.delete()
                    return wrapper

    return wrapper
