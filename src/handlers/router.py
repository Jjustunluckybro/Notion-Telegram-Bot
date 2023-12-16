from aiogram import Router
from aiogram.filters import CommandStart, Command
from .ping import ping


def get_main_router() -> Router:
    """Create main user input router"""
    router = Router(name="router_user_command")
    router.message.register(ping, Command("ping"))
    return router
