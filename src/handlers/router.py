from aiogram import Router
from aiogram.filters import CommandStart, Command

from .user_callbacks import get_user_callbacks_router
from .user_commands import test, start, register_user_command_router


def get_main_router() -> Router:
    """Create main user input router"""

    router = Router(name="main")
    router.message.register(start, CommandStart)
    router.message.register(test, Command("test"))

    user_commands_router = register_user_command_router()
    user_callbacks_router = get_user_callbacks_router()

    router.include_routers(
        user_callbacks_router,
        user_commands_router
    )

    return router
