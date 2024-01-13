from aiogram import Router

from src.handlers.user_callbacks.fsm.create_theme import router as create_theme_router


def get_fsm_router() -> Router:
    router = Router(name="fsm")

    router.include_router(
        create_theme_router
    )

    return router
