from abc import ABC, abstractmethod
from logging import getLogger

from src.models.user_model import UserModel
from src.services.requests.RequestHandler import RequestHandler, get_request_handler


class IStorageRequestHandler(ABC):
    request_handler: RequestHandler

    def __init__(self) -> None:
        self.request_handler = get_request_handler()


class IUserStorageHandler(IStorageRequestHandler, ABC):

    def __init__(self):
        self.logger = getLogger(f"{__name__}.users")
        super().__init__()

    @abstractmethod
    async def get(self, user_id: str) -> UserModel:
        ...

    @abstractmethod
    async def create(self, user: UserModel) -> str:
        ...

    @abstractmethod
    async def update_username(self, user_id: str, new_username: str) -> None:
        ...

    @abstractmethod
    async def delete(self, user_id: str) -> None:
        ...
