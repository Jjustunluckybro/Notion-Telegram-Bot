from aiogram import types


async def ping(msg: types.Message) -> None:
    await msg.answer("Ping AlarmBot")
