from aiogram import Router
from aiogram.filters import CommandStart, Command

from .user_callbacks import open_all_themes, open_all_theme_notes, open_all_note_alarms
from .user_commands import test, start
from src.services.ui.callbacks import Callbacks


def get_main_router() -> Router:
    """Create main user input router"""

    router = Router(name="router_user_command")
    router.message.register(start, CommandStart)
    router.message.register(test, Command("test"))

    callbacks = Callbacks()

    router.callback_query.register(open_all_themes, lambda x: x.data == callbacks.open_all_themes)
    router.callback_query.register(open_all_theme_notes, lambda x: x.data.startswith(Callbacks.open_theme_start_with))
    router.callback_query.register(open_all_note_alarms, lambda x: x.data.startswith(Callbacks.open_note_start_with))

    return router
