from aiogram import Router

from .general_callbacks import router as general_callbacks_router
from .user_callbacks import get_user_callbacks_router
from .user_commands import register_user_command_router


def get_main_router() -> Router:
    """Create main user input router"""

    router = Router(name="main")

    user_commands_router = register_user_command_router()
    user_callbacks_router = get_user_callbacks_router()

    router.include_routers(
        user_callbacks_router,
        user_commands_router,
        general_callbacks_router
    )

    return router
