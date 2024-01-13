from aiogram import Router

from src.handlers.user_callbacks.notes_callbacks import get_note_router
from src.handlers.user_callbacks.themes_callbacks import get_themes_router


def get_user_callbacks_router() -> Router:
    router = Router(name="user_callbacks")
    router.include_routers(
        get_themes_router(),
        get_note_router()
    )

    return router
