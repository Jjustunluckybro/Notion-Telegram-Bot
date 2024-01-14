from logging import getLogger

from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from pydantic import ValidationError

from src.models.notes_models import NoteModelToCreate, NoteLinksModel, NoteDataModel, CheckpointModel
from src.services.storage.interfaces import INotesStoragehandler
from src.services.storage.notes_storage_handler import NotesStoragehandler
from src.services.ui.callbacks import Callbacks
from src.services.ui.inline_keyboards import create_cancel_fsm_kb, create_save_kb, create_change_fsm_user_data_kb, \
    create_set_attachments_or_checkpoints_kb, create_cancel_kb, create_done_kb, create_main_menu_kb
from src.utils.exceptions.storage import StorageValidationError
from src.utils.fsm.fsm import CreateNote

logger = getLogger(f"fsm_{__name__}")
router = Router()


@router.callback_query(lambda x: x.data.startswith(Callbacks.CREATE_NOTE), StateFilter(None))
async def create_note(callback: types.CallbackQuery, state: FSMContext) -> None:
    """"""
    parent_id = Callbacks.get_id_from_callback(callback.data)
    await state.update_data(parent_id=parent_id)
    message = await callback.bot.send_message(
        text="Введите название заметки",
        chat_id=callback.from_user.id,
        reply_markup=create_cancel_fsm_kb().as_markup()
    )
    await state.update_data(last_message_id=message.message_id)

    await callback.message.delete()
    await state.set_state(CreateNote.write_name)


@router.message(CreateNote.write_name)
async def create_note_write_name(message: types.Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    previous_message_id = user_data.get("last_message_id")

    # Update user data
    await state.update_data(note_name=message.text)

    # Answer to user
    out_message = await message.answer(
        text=f"Имя заметки: {message.text}, теперь введите текст заметки",
        reply_markup=create_cancel_fsm_kb().as_markup()
    )
    await state.update_data(last_message_id=out_message.message_id)

    # Delete previous messages
    await message.bot.delete_message(
        chat_id=message.from_user.id,
        message_id=previous_message_id
    )
    await message.delete()

    await state.set_state(CreateNote.write_text)


@router.callback_query(lambda x: x.data == Callbacks.DONE, CreateNote.write_attachments)
@router.callback_query(lambda x: x.data == Callbacks.DONE, CreateNote.write_checkpoints)
async def create_note_back_from_attachments_or_checkpoints(
        callback: types.CallbackQuery,
        state: FSMContext
) -> None:
    """"""
    user_data = await state.get_data()
    previous_message_id = user_data.get("last_message_id")

    # Create inline keyboard
    kb = create_save_kb()
    kb.attach(create_set_attachments_or_checkpoints_kb())
    kb.attach(create_change_fsm_user_data_kb())
    kb.attach(create_cancel_fsm_kb())

    out_message = await callback.bot.send_message(
        text=f"Имя заметки: {user_data.get('note_name')}\nТекст заметки: {user_data.get('note_text')}",
        chat_id=callback.from_user.id,
        reply_markup=kb.as_markup()
    )
    await state.update_data(last_message_id=out_message.message_id)

    # Delete previous messages
    await callback.bot.delete_message(
        chat_id=callback.from_user.id,
        message_id=previous_message_id
    )

    await state.set_state(CreateNote.accept)


@router.message(CreateNote.write_text)
async def create_note_write_text(
        message: types.Message,
        state: FSMContext
) -> None:
    """"""
    await state.update_data(note_text=message.text)

    user_data = await state.get_data()
    previous_message_id = user_data.get("last_message_id")

    # Create inline keyboard
    kb = create_save_kb()
    kb.attach(create_set_attachments_or_checkpoints_kb())
    kb.attach(create_change_fsm_user_data_kb())
    kb.attach(create_cancel_fsm_kb())

    out_message = await message.answer(
        text=f"Имя заметки: {user_data.get('note_name')}\nТекст заметки: {user_data.get('note_text')}",
        reply_markup=kb.as_markup()
    )
    await state.update_data(last_message_id=out_message.message_id)

    # Delete previous messages
    await message.bot.delete_message(
        chat_id=message.from_user.id,
        message_id=previous_message_id
    )
    await message.delete()

    await state.set_state(CreateNote.accept)


@router.callback_query(lambda x: x.data == Callbacks.ADD_ATTACHMENTS, CreateNote.accept)
async def create_note_add_attachment(callback: types.CallbackQuery, state: FSMContext) -> None:
    user_data = await state.get_data()
    previous_message_id = user_data.get("last_message_id")
    await callback.bot.delete_message(
        chat_id=callback.from_user.id,
        message_id=previous_message_id
    )

    message_out = await callback.bot.send_message(
        text="Отправьте изображение",
        chat_id=callback.from_user.id,
        reply_markup=create_cancel_kb().as_markup()
    )
    await state.update_data(last_message_id=message_out.message_id)
    await state.set_state(CreateNote.write_attachments)


@router.message(CreateNote.write_attachments)
async def create_note_process_attachment(message: types.Message, state: FSMContext) -> None:  # TODO Not only photo
    """"""
    user_data = await state.get_data()
    previous_message_id = user_data.get("last_message_id")
    await message.bot.delete_message(
        chat_id=message.from_user.id,
        message_id=previous_message_id
    )

    file_id = message.photo[-1].file_id if message.photo[-1] is not None else None
    if file_id is not None:
        attachments = user_data.get("attachments") if user_data.get("attachments") is not None else []
        await state.update_data(attachmets=attachments.append(file_id))
    else:
        await message.answer("Отправьте изображение, пока что другие файлы не поддерживаются")
        return

    message_out = await message.answer(
        f"Файл сохранен, отправьте еще или нажмите 'готово'",
        reply_markup=create_done_kb().as_markup()
    )
    await state.update_data(last_message_id=message_out.message_id)


@router.callback_query(lambda x: x.data == Callbacks.ADD_CHECKPOINT, CreateNote.accept)
async def create_note_add_checkpoint(callback: types.CallbackQuery, state: FSMContext) -> None:
    user_data = await state.get_data()
    previous_message_id = user_data.get("last_message_id")
    await callback.bot.delete_message(
        chat_id=callback.from_user.id,
        message_id=previous_message_id
    )

    message_out = await callback.bot.send_message(
        text="Отправьте текст чеклиста",
        chat_id=callback.from_user.id,
        reply_markup=create_done_kb().as_markup()
    )
    await state.update_data(last_message_id=message_out.message_id)
    await state.set_state(CreateNote.write_checkpoints)


@router.message(CreateNote.write_checkpoints)
async def create_note_process_checkpoint(message: types.Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    previous_message_id = user_data.get("last_message_id")
    await message.bot.delete_message(
        chat_id=message.from_user.id,
        message_id=previous_message_id
    )
    await message.delete()

    checkpoints = user_data.get("checkpoints") if user_data.get("checkpoints") is not None else []
    checkpoints.append(message.text)
    await state.update_data(checkpoints=checkpoints)
    n = "\n"

    message_out = await message.answer(
        text=f"Чекпоинты:\n{n.join(checkpoints)}\nОтправьте еще или нажмите 'готово'",
        reply_markup=create_done_kb().as_markup()
    )
    await state.update_data(last_message_id=message_out.message_id)


@router.callback_query(lambda x: x.data == Callbacks.SAVE, CreateNote.accept)
async def create_note_save(
        callback: types.CallbackQuery,
        state: FSMContext,
        sh: INotesStoragehandler = NotesStoragehandler()
) -> None:
    """"""
    user_data = await state.get_data()
    previous_message_id = user_data.get("last_message_id")
    await callback.bot.delete_message(
        chat_id=callback.from_user.id,
        message_id=previous_message_id
    )

    checkpoints_texts = user_data.get("checkpoints")
    if checkpoints_texts is not None:
        checkpoints = []
        for text in checkpoints_texts:
            checkpoints.append(
                CheckpointModel(text=text, is_finish=False)
            )
    else:
        checkpoints = None

    try:
        note = NoteModelToCreate(
            name=user_data["note_name"],
            links=NoteLinksModel(
                user_id=str(callback.from_user.id),
                theme_id=user_data["parent_id"]
            ),
            data=NoteDataModel(
                text=user_data["note_text"],
                attachments=user_data.get("attachments"),
                check_points=checkpoints
            )
        )
    except KeyError as err:
        logger.error(f"Can't find user fsm data. details: {err}. user_data: {user_data}")
        await callback.bot.send_message(
            text="Что-то пошло не так, попробуйте позже",
            chat_id=callback.from_user.id,
        )
    except ValidationError as err:
        logger.error(f"Model validation error. details: {err}")
        await callback.bot.send_message(
            text="Что-то пошло не так, попробуйте позже",
            chat_id=callback.from_user.id,
        )
    else:
        note_id = await sh.create(note)  # TODO Handel storage exceptions
        logger.info(f"Successfully create theme with id: {note_id}")
        await callback.bot.send_message(
            text=f"Заметка {user_data.get('note_name')} успешно создана",
            chat_id=callback.from_user.id,
            reply_markup=create_main_menu_kb().as_markup()
        )
    finally:
        await state.clear()
