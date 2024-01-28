from aiogram import types, Router

from src.services.storage.alarms_storage_handler import AlarmsStoragehandler
from src.services.storage.interfaces import IAlarmsStoragehandler
from src.services.ui.callbacks import Callbacks
from src.services.ui.inline_keyboards import create_note_menu_kb
from src.utils.exceptions.decorators import handel_storage_unexpected_response
from src.utils.exceptions.storage import StorageNotFound


@handel_storage_unexpected_response
async def open_note_menu(callback: types.CallbackQuery,
                         sh: IAlarmsStoragehandler = AlarmsStoragehandler()
                         ) -> None:
    """
    :param callback:
    :param sh: Dependency
    """

    note_alarms = None
    note_id = Callbacks.get_id_from_callback(callback.data)

    try:
        note_alarms = await sh.get_all_by_parent(note_id)
    except StorageNotFound:
        ...
    finally:
        kb = create_note_menu_kb(note_id, note_alarms)
        await callback.bot.send_message(
            text="Список ваших напомниний под заметкой ...:",  # TODO Note name and info
            reply_markup=kb.as_markup(),
            chat_id=callback.from_user.id
        )
        await callback.message.delete()


def get_note_router(callbacks: Callbacks = Callbacks()) -> Router:
    """
    """
    router = Router(name=__name__)

    router.callback_query.register(open_note_menu, lambda x: x.data.startswith(callbacks.OPEN_NOTE_START_WITH))

    return router
