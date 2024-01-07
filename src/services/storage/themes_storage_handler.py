from typing import Any, List

from pydantic import ValidationError, TypeAdapter

from src.models.themes_modles import ThemeModelToCreate, ThemeModel
from src.services.storage.interfaces import IThemesStorageHandler
from src.utils import statuses
from src.utils.exceptions.storage import StorageValidationError, UnexpectedResponse, StorageNotFound


class ThemesStorageHandler(IThemesStorageHandler):

    async def get(self, _id: str) -> ThemeModel:
        """
        Че у тебя функция, забирает айди, отдает какую то твою модель,
        а дальше просто проверка на успешность отправки/приема, код 200,
        возвращает какое то тело, если 400 то сасай, все остальное тоже сосай
        :param _id: Theme id
        :return: ThemeModel
        :raise: ValidationError - Can't validate response answer to ThemeModel
        :raise: StorageNotFound -Theme with this id not found
        :raise: UnexpectedResponse
        """
        response = await self.request_handler.get(f"themes/get_theme/{_id}")

        match response.status:
            case statuses.SUCCESS_200:
                try:
                    return ThemeModel.model_validate_json(response.body)
                except ValidationError as err:
                    self.logger.error(f"StorageValidationError: {str(err)}")
                    raise StorageValidationError(str(err))
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found theme with id: {_id}")
                raise StorageNotFound(f"Storage not found theme with id: {_id}")
            case _:
                raise UnexpectedResponse(f"Unacceptable response status code: {response.status}")

    async def get_all_by_user(self, _id: str) -> list[ThemeModel]:
        """
        Get all themes related to user from storage by request and validate it to list of ThemesModel
        :param _id:
        :return:
        """

        response = await self.request_handler.get(f"themes/get_all_user_themes/{_id}")

        match response.status:
            case statuses.SUCCESS_200:
                ta = TypeAdapter(List[ThemeModel])  # Need to validate list of pydantic models
                try:
                    return ta.validate_python(response.status)
                except ValidationError as err:
                    self.logger.error(f"StorageValidationError: {str(err)}")
                    raise StorageValidationError(str(err))
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found theme relates to user with id: {_id}")
                raise StorageNotFound(f"Storage not found theme relates to user with id: {_id}")
            case _:
                self.logger.error(f"Unacceptable response status code: {response.status}")
                raise UnexpectedResponse(f"Unacceptable response status code: {response.status}")

    async def create(self, theme: ThemeModelToCreate) -> str:
        """"""
        response = await self.request_handler.post("themes/create_theme", body=theme.model_dump())

        match response.status:
            case statuses.CREATED_201:
                self.logger.info(f"Theme was successful created with id: {response.body}")
                return response.body
            case statuses.VALIDATION_ERROR_422:
                self.logger.error(f"Request body doesn't match validation: {response.body}")
                raise StorageValidationError(f"Request body doesn't match validation: {response.body}")
            case _:
                self.logger.error(f"Unacceptable response status code: {response.status}")
                raise UnexpectedResponse(f"Unacceptable response status code: {response.status}")

    async def patch(self, _id: str, new_data: dict[str, Any]) -> None:
        """"""

        response = await self.request_handler.patch(f"themes/update_theme/{_id}", body=new_data)

        match response.status:
            case statuses.SUCCESS_200:
                self.logger.info("Theme was successful updated")
                return
            case statuses.VALIDATION_ERROR_422:
                self.logger.error(f"Request body doesn't match validation: {response.body}")
                raise StorageValidationError(f"Request body doesn't match validation: {response.body}")
            case statuses.BAD_REQUEST_400:
                self.logger.error(f"{response.body} with id: {_id}")
                raise StorageValidationError(f"{response.body} with id: {_id}")
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found theme with id: {_id}")
                raise StorageNotFound(f"Storage not found theme with id: {_id}")
            case _:
                self.logger.error(f"Unacceptable response status code: {response.status}")
                raise UnexpectedResponse(f"Unacceptable response status code: {response.status}")

    async def delete(self, _id: str) -> None:
        """"""
        response = await self.request_handler.delete(f"themes/delete_theme/{_id}")

        match response.status:
            case statuses.SUCCESS_200:
                self.logger.info("Theme was successful delete")
                return
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found theme with id: {_id}")
                raise StorageNotFound(f"Storage not found theme with id: {_id}")
            case statuses.BAD_REQUEST_400:
                self.logger.error(f"{response.body} with id: {_id}")
                raise StorageValidationError(f"{response.body} with id: {_id}")
            case _:
                self.logger.error(f"Unacceptable response status code: {response.status}")
                raise UnexpectedResponse(f"Unacceptable response status code: {response.status}")

    async def delete_all_by_user(self, _id: str) -> None:
        """"""
        response = await self.request_handler.delete(f"themes/delete_all_user_themes/{_id}")

        match response.status:
            case statuses.SUCCESS_200:
                self.logger.info(f"{response.body} themes was successful delete")
                return
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found themes or user with id: {_id}")
                raise StorageNotFound(f"Storage not found themes or user with id: {_id}")
            case _:
                self.logger.error(f"Unacceptable response status code: {response.status}")
                raise UnexpectedResponse(f"Unacceptable response status code: {response.status}")
