import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
import asyncio
from utils import config
import logging

logger = logging.getLogger('app.main')


async def main():
    bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except(KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
