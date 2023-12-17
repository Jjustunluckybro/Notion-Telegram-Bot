from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class AlarmStatus(str, Enum):
    """Possible alarms statuses"""
    READY: str = "READY"
    QUEUE: str = "QUEUE"
    FINISH: str = "FINISH"


class AlarmLinkModel(BaseModel):
    """Models with all relation links that the alarm has"""
    user_id: str
    parent_id: str


class AlarmTimesModel(BaseModel):
    """Models with all date and time info that the alarm has"""
    creation_time: datetime
    next_notion_time: datetime
    end_time: datetime | None
    repeat_interval: int


class AlarmModel(BaseModel):
    """Represent Alarm. Store in the backend db with same model"""
    _id: str
    name: str
    description: str | None
    is_repeatable: bool
    status: AlarmStatus
    links: AlarmLinkModel
    times: AlarmTimesModel


class AlarmModelToCreate(BaseModel):
    """Model to create new Alarm use backend endpoint"""
    name: str
    description: str | None
    is_repeatable: bool
    links: AlarmLinkModel
