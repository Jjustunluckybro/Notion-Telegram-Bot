from aiogram import types


async def ping(msg: types.message) -> None:
    await msg.answer("Ping AlarmBot")
