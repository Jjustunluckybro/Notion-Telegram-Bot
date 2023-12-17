from abc import ABC, abstractmethod
from logging import getLogger
from typing import Any, Final

from pydantic import BaseModel
from src.utils import statuses
from src.models.user_model import UserModel
from src.services.requests.RequestHandler import get_request_handler, RequestHandler, ResponseModel
from src.utils.exceptions.storage import StorageNotFound, StorageException, UnacceptableResponseStatusCode


class IStorageRequestHandler(ABC):
    request_handler: RequestHandler

    def __init__(self) -> None:
        self.request_handler = get_request_handler()


class UserStorageHandler(IStorageRequestHandler):

    def __init__(self):
        self.logger = getLogger(f"{__name__}.users")
        super().__init__()

    async def get(self, user_id: str) -> UserModel:
        """
        Get user info from storage and convert it to UserModel
        :param user_id:
        :return: UserModel
        :raise StorageNotFound if no user found in storage
        :raise UnacceptableResponseStatusCode if response has Unacceptable status code
        """
        response = await self.request_handler.get(f"users/get_user/{user_id}")

        match response.status:
            case statuses.SUCCESS_200:
                return UserModel.model_validate(response.body)
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found user with id: {user_id}")
                raise StorageNotFound(f"Storage not found user with id: {user_id}")
            case _:
                raise UnacceptableResponseStatusCode(f"Unacceptable response status code: {response.status}")

    async def delete(self, user_id: str) -> None:
        """
        Delete user from storage
        :param user_id:
        :return:
        :raise StorageNotFound if no user found in storage
        :raise UnacceptableResponseStatusCode if response has Unacceptable status code
        """
        response = await self.request_handler.delete(f"users/delete_user/{user_id}")

        match response.status:
            case statuses.SUCCESS_200:
                if not int(response.body):
                    raise StorageException(f"User not deleted with status code 200. user_id: {user_id}")
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found user with id: {user_id}")
                raise StorageNotFound(f"Storage not found user with id: {user_id}")
            case _:
                raise UnacceptableResponseStatusCode(f"Unacceptable response status code: {response.status}")
