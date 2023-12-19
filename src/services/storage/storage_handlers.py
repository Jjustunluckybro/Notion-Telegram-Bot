from abc import ABC
from logging import getLogger

from src.utils import statuses
from src.models.user_model import UserModel
from src.services.requests.RequestHandler import get_request_handler, RequestHandler, ResponseModel
from src.utils.exceptions.storage import StorageNotFound, StorageException, UnacceptableResponseStatusCode, \
    StorageValidationError, StorageDuplicate


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
                return UserModel.model_validate_json(response.body)
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found user with id: {user_id}")
                raise StorageNotFound(f"Storage not found user with id: {user_id}")
            case _:
                raise UnacceptableResponseStatusCode(f"Unacceptable response status code: {response.status}")

    async def create(self, user: UserModel) -> str:
        """
        Create user in storage
        :param user:
        :return: User id
        :raise StorageDuplicate if user already exist
        :raise StorageValidationError if some endpoint model validation error
        """
        response = await self.request_handler.post(
            f"users/create_user",
            body=user.model_dump()
        )

        match response.status:
            case statuses.SUCCESS_200:
                self.logger.info(f"Create user in storage with id: {response.body}")
                return response.body
            case statuses.CONFLICT_409:
                self.logger.info(f"User with id: {user.telegram_id} already exist")
                raise StorageDuplicate(f"User with id: {user.telegram_id} already exist")
            case statuses.VALIDATION_ERROR_422:
                self.logger.error(f"Storage not supported model - {response.body}")
                raise StorageValidationError()
            case _:
                raise UnacceptableResponseStatusCode(f"Unacceptable response status code: {response.status}")

    async def update_username(self, user_id: str, new_username: str) -> None:
        """

        :param user_id: user telegram id
        :param new_username:
        :return: None
        :raise StorageNotFound if no user found in storage
        """
        response = await self.request_handler.patch(f"users/update_username/{user_id}?new_name={new_username}")

        match response.status:
            case statuses.SUCCESS_200:
                self.logger.info(f"Username in storage successful changed - user_id: {user_id}")
                return
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found user with id: {user_id}")
                raise StorageNotFound(f"Storage not found user with id: {user_id}")

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


def get_user_storage_handler() -> UserStorageHandler:
    return UserStorageHandler()
