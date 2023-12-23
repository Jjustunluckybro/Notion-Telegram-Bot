from typing import Any, List

from pydantic import ValidationError, TypeAdapter

from src.models.notes_models import NoteModelToCreate, NoteModel
from src.services.storage.interfaces import INotesStoragehandler
from src.utils import statuses
from src.utils.exceptions.storage import StorageValidationError, StorageNotFound, UnacceptableResponseStatusCode


class NotesStoragehandler(INotesStoragehandler):
    async def get(self, _id: str) -> NoteModel:
        """"""

        response = await self.request_handler.get(f"notes/get_note/{_id}")

        match response.status:
            case statuses.SUCCESS_200:
                try:
                    return NoteModel.model_validate_json(response.body)
                except ValidationError as err:
                    self.logger.error(f"StorageValidationError: {str(err)}")
                    raise StorageValidationError(str(err))
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found note with id: {_id}")
                raise StorageNotFound(f"Storage not found note with id: {_id}")
            case _:
                raise UnacceptableResponseStatusCode(f"Unacceptable response status code: {response.status}")

    async def get_all_by_theme(self, _id: str) -> list[NoteModel]:
        """"""

        response = await self.request_handler.get(f"notes/get_all_notes_by_theme_id/{_id}")

        match response.status:
            case statuses.SUCCESS_200:
                ta = TypeAdapter(List[NoteModel])  # Need to validate list of pydantic models
                try:
                    return ta.validate_python(response.status)
                except ValidationError as err:
                    self.logger.error(f"StorageValidationError: {str(err)}")
                    raise StorageValidationError(str(err))
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found note relates to theme with id: {_id}")
                raise StorageNotFound(f"Storage not found note relates to theme with id: {_id}")
            case _:
                self.logger.error(f"Unacceptable response status code: {response.status}")
                raise UnacceptableResponseStatusCode(f"Unacceptable response status code: {response.status}")

    async def get_all_by_user(self, _id: str) -> list[NoteModel]:
        """"""

        response = await self.request_handler.get(f"notes/get_all_notes_by_user_id/{_id}")

        match response.status:
            case statuses.SUCCESS_200:
                ta = TypeAdapter(List[NoteModel])  # Need to validate list of pydantic models
                try:
                    return ta.validate_python(response.status)
                except ValidationError as err:
                    self.logger.error(f"StorageValidationError: {str(err)}")
                    raise StorageValidationError(str(err))
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found note relates to user with id: {_id}")
                raise StorageNotFound(f"Storage not found note relates to user with id: {_id}")
            case _:
                self.logger.error(f"Unacceptable response status code: {response.status}")
                raise UnacceptableResponseStatusCode(f"Unacceptable response status code: {response.status}")

    async def create(self, note: NoteModelToCreate) -> str:
        """"""

        response = await self.request_handler.post("notes/create_note", body=note.model_dump())

        match response.status:
            case statuses.CREATED_201:
                self.logger.info(f"Note was successful created with id: {response.body}")
                return response.body
            case statuses.VALIDATION_ERROR_422:
                self.logger.error(f"Request body doesn't match validation: {response.body}")
                raise StorageValidationError(f"Request body doesn't match validation: {response.body}")
            case _:
                self.logger.error(f"Unacceptable response status code: {response.status}")
                raise UnacceptableResponseStatusCode(f"Unacceptable response status code: {response.status}")

    async def patch(self, _id: str, new_data: dict[str, Any]) -> None:
        """"""

        response = await self.request_handler.patch(f"notes/update_note/{_id}", body=new_data)

        match response.status:
            case statuses.SUCCESS_200:
                self.logger.info("Note was successful updated")
                return
            case statuses.VALIDATION_ERROR_422:
                self.logger.error(f"Request body doesn't match validation: {response.body}")
                raise StorageValidationError(f"Request body doesn't match validation: {response.body}")
            case statuses.BAD_REQUEST_400:
                self.logger.error(f"{response.body} with id: {_id}")
                raise StorageValidationError(f"{response.body} with id: {_id}")
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found note with id: {_id}")
                raise StorageNotFound(f"Storage not found note with id: {_id}")
            case _:
                self.logger.error(f"Unacceptable response status code: {response.status}")
                raise UnacceptableResponseStatusCode(f"Unacceptable response status code: {response.status}")

    async def delete(self, _id: str) -> None:
        """"""
        response = await self.request_handler.delete(f"notes/delete_note/{_id}")

        match response.status:
            case statuses.SUCCESS_200:
                self.logger.info("Note was successful delete")
                return
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found note with id: {_id}")
                raise StorageNotFound(f"Storage not found note with id: {_id}")
            case statuses.BAD_REQUEST_400:
                self.logger.error(f"{response.body} with id: {_id}")
                raise StorageValidationError(f"{response.body} with id: {_id}")
            case _:
                self.logger.error(f"Unacceptable response status code: {response.status}")
                raise UnacceptableResponseStatusCode(f"Unacceptable response status code: {response.status}")

    async def delete_by_theme(self, _id: str) -> None:
        """"""
        response = await self.request_handler.delete(f"notes/delete_all_user_notes/{_id}")

        match response.status:
            case statuses.SUCCESS_200:
                self.logger.info(f"{response.body} notes was successful deleted")
                return
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found notes related to theme or theme with id: {_id}")
                raise StorageNotFound(f"Storage not found notes related to theme or theme with id: {_id}")
            case _:
                self.logger.error(f"Unacceptable response status code: {response.status}")
                raise UnacceptableResponseStatusCode(f"Unacceptable response status code: {response.status}")
