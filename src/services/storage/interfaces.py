from abc import ABC, abstractmethod
from datetime import datetime
from logging import getLogger
from typing import Any

from src.models.alarm_model import AlarmModel, AlarmModelToCreate, AlarmStatus
from src.models.notes_models import NoteModel, NoteModelToCreate
from src.models.themes_modles import ThemeModel, ThemeModelToCreate
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
        """Get user from storage"""
        ...

    @abstractmethod
    async def create(self, user: UserModel) -> str:
        """Create user in storage"""
        ...

    @abstractmethod
    async def update_username(self, user_id: str, new_username: str) -> None:
        """Change username in storage"""
        ...

    @abstractmethod
    async def delete(self, user_id: str) -> None:
        """Delete user from storage"""
        ...


class IThemesStorageHandler(IStorageRequestHandler, ABC):

    def __init__(self) -> None:
        self.logger = getLogger(f"{__name__}.themes")
        super().__init__()

    @abstractmethod
    async def get(self, _id: str) -> ThemeModel:
        """Get Theme from storage by id"""
        ...

    @abstractmethod
    async def get_all_by_user(self, _id: str) -> list[ThemeModel]:
        """
        :param _id: User id
        :return: All themes related to user
        """
        ...

    @abstractmethod
    async def create(self, theme: ThemeModelToCreate) -> str:
        """create user in storage"""
        ...

    @abstractmethod
    async def patch(self, _id: str, new_data: dict[str, Any]):
        """Update theme in storage"""
        ...

    @abstractmethod
    async def delete(self, _id: str) -> None:
        """Delete theme from storage by id"""
        ...

    @abstractmethod
    async def delete_all_by_user(self, _id: str) -> None:
        """
        Delete all themes related to user
        :param _id: User id
        :return: None
        """
        ...


class INotesStorageHandler(IStorageRequestHandler, ABC):

    def __init__(self) -> None:
        self.logger = getLogger(f"{__name__}.notes")
        super().__init__()

    @abstractmethod
    async def get(self, _id: str) -> NoteModel:
        """Get note from storage by it id"""
        ...

    @abstractmethod
    async def get_all_by_theme(self, _id: str) -> list[NoteModel]:
        """
        :param _id: theme id
        :return: All notes related to theme
        """
        ...

    @abstractmethod
    async def get_all_by_user(self, _id: str) -> list[NoteModel]:
        """
        :param _id: user id
        :return: All themes related to user
        """
        ...

    @abstractmethod
    async def create(self, note: NoteModelToCreate) -> str:
        """Create note in storage"""
        ...

    @abstractmethod
    async def patch(self, _id: str, new_data: dict[str, Any]) -> None:
        """Update note in storage by id"""
        ...

    @abstractmethod
    async def delete(self, _id: str) -> None:
        """Delete note from storage by id"""
        ...

    @abstractmethod
    async def delete_by_theme(self, _id: str) -> None:
        """
        Delete all notes related to theme
        :param _id: theme id
        """
        ...


class IAlarmsStoragehandler(IStorageRequestHandler, ABC):

    def __init__(self) -> None:
        self.logger = getLogger(f"{__name__}.alarms")
        super().__init__()

    @abstractmethod
    async def get(self, _id: str) -> AlarmModel:
        """Get alarm from storage by id"""
        ...

    @abstractmethod
    async def get_all_by_parent(self, _id: str) -> list[AlarmModel]:
        """
        :param _id: parent entity id
        :return: All alarms related to entity
        """
        ...

    @abstractmethod
    async def get_all_by_user(self, _id: str) -> list[AlarmModel]:
        """
        :param _id: User id
        :return: All alarms related to user
        """
        ...

    @abstractmethod
    async def get_all_ready(self) -> list[AlarmModel]:
        """Return all alarms with 'READY' status"""
        ...

    @abstractmethod
    async def create(self, alarm: AlarmModelToCreate, next_notion_time: datetime, repeat_interval: int | None) -> str:
        """Create new alarm in storage"""
        ...

    @abstractmethod
    async def postpone_repeatable(self, _id: str) -> datetime:
        """
        :param _id: Alarm id
        :return: New alarm notion time
        """
        ...

    @abstractmethod
    async def path(self, _id: str, new_data: dict[str, Any]) -> None:
        """Update alarm in the storage"""
        ...

    @abstractmethod
    async def update_status(self, _id: str, new_status: AlarmStatus) -> None:
        """Update alarm status"""
        ...

    @abstractmethod
    async def delete(self, _id: str) -> None:
        """Delete alarm from storage by id"""
        ...

    @abstractmethod
    async def delete_by_parent(self, _id: str) -> None:
        """
        Delete all alarms related to entity
        :param _id: entity id
        """
        ...

    @abstractmethod
    async def delete_by_user(self, _id: str) -> None:
        """
        Delete all alarms related to user
        :param _id: user id
        """
        ...
