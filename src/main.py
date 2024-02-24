import sys
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from src.services.scheduler.scheduler import create_and_start_scheduler
from utils import config
from handlers.router import get_main_router

logger = logging.getLogger('app.main')


async def main():
    bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)

    dp = Dispatcher()
    dp.include_router(get_main_router())

    scheduler = create_and_start_scheduler(bot)
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except(KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
