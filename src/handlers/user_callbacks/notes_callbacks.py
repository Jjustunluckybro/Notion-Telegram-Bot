from logging import getLogger

from aiogram import types, Router
from pydantic import ValidationError

from src.services.storage.alarms_storage_handler import AlarmsStoragehandler
from src.services.storage.interfaces import IAlarmsStoragehandler, INotesStorageHandler
from src.services.storage.notes_storage_handler import NotesStorageHandler
from src.services.ui.callbacks import Callbacks
from src.services.ui.inline_keyboards import create_note_menu_kb, create_cancel_fsm_kb
from src.utils.exceptions.decorators import handel_storage_unexpected_response
from src.utils.exceptions.storage import StorageNotFound
from src.utils.handlers_utils import send_error_message

logger = getLogger(__name__)


@handel_storage_unexpected_response
async def open_note_menu(callback: types.CallbackQuery,
                         notes_sh: INotesStorageHandler = NotesStorageHandler(),
                         alarms_sh: IAlarmsStoragehandler = AlarmsStoragehandler()
                         ) -> None:
    """
    :param callback:
    :param notes_sh: Dependency
    :param alarms_sh: Dependency
    """

    note_alarms = None
    note_id = Callbacks.get_id_from_callback(callback.data)

    try:
        note = await notes_sh.get(note_id)
    except StorageNotFound:
        logger.error(f"Should found note, but it note found. note_id: {note_id}")
        await send_error_message(callback)
        await callback.message.delete()
        return
    except ValidationError:
        await send_error_message(callback)
        await callback.message.delete()
        return
    else:
        text = f"{note.name}\n\n{note.data.text}"

    try:
        note_alarms = await alarms_sh.get_all_by_parent(note_id)
        text += f"\n\nСписок ваших напомниний:"
    except StorageNotFound:
        text += "\n\nНапоминаний под темой пока нет, создайте их"
    finally:
        kb = create_note_menu_kb(note_id=note_id, note_alarms=note_alarms, parent_theme_id=note.links.theme_id)
        kb.attach(create_cancel_fsm_kb())
        await callback.bot.send_message(
            text=text,
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
