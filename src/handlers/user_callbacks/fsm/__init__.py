from aiogram import Router

from src.handlers.user_callbacks.fsm.create_theme import router as create_theme_router
from src.handlers.user_callbacks.fsm.delete_theme import router as delete_theme_router
from src.handlers.user_callbacks.fsm.create_note import router as create_note_router
from src.handlers.user_callbacks.fsm.create_alarm import router as create_alarm_router


def get_fsm_router() -> Router:
    router = Router(name="fsm")

    router.include_routers(
        create_theme_router,
        create_note_router,
        create_alarm_router,
        delete_theme_router
    )

    return router
