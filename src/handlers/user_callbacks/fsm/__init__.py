from aiogram import Router

from src.handlers.user_callbacks.fsm.create_theme import router as create_theme_router
from src.handlers.user_callbacks.fsm.change_theme import router as change_theme_router
from src.handlers.user_callbacks.fsm.create_note import router as create_note_router
from src.handlers.user_callbacks.fsm.create_alarm import router as create_alarm_router
from src.handlers.user_callbacks.fsm.delete_theme import router as delete_theme_router
from src.handlers.user_callbacks.fsm.delete_note import router as delete_note_router
from src.handlers.user_callbacks.fsm.set_alarm_new_repeat_interval import router as set_alarm_new_repeat_interval_router
from src.handlers.user_callbacks.fsm.set_alarm_repeatable import router as set_alarm_repeatable_router
from src.handlers.user_callbacks.fsm.set_new_alarm_time import router as set_new_alarm_time_router
from src.handlers.user_callbacks.fsm.delete_alarm import router as delete_alarm_router


def get_fsm_router() -> Router:
    router = Router(name="fsm")

    router.include_routers(
        create_theme_router,
        create_note_router,
        create_alarm_router,
        delete_theme_router,
        delete_note_router,
        set_alarm_new_repeat_interval_router,
        set_alarm_repeatable_router,
        set_new_alarm_time_router,
        delete_alarm_router,
        change_theme_router
    )

    return router
