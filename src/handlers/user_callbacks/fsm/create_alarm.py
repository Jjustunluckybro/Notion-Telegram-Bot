from logging import getLogger

from aiogram import Router

logger = getLogger(f"fsm_{__name__}")
router = Router(name=__name__)

