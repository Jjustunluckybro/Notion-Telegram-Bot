from aiogram import Router

from src.handlers.user_callbacks.fsm import get_fsm_router
from src.handlers.user_callbacks.notes_callbacks import router as note_router
from src.handlers.user_callbacks.themes_callbacks import router as themes_router
from src.handlers.user_callbacks.alarms import router as alarms_router


def get_user_callbacks_router() -> Router:
    router = Router(name="user_callbacks")
    router.include_routers(
        get_fsm_router(),
        themes_router,
        note_router,
        alarms_router
    )

    return router
