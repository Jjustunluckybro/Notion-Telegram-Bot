from datetime import datetime

from pydantic import BaseModel, Field


class CheckpointModel(BaseModel):
    """"""
    text: str
    is_finished: bool


class NoteLinksModel(BaseModel):
    """Models with all relation links that the note has"""
    user_id: str
    theme_id: str


class NoteTimesModel(BaseModel):
    """Models with all date and time info that the note has"""
    creation_time: datetime
    end_time: datetime | None


class NoteDataModel(BaseModel):
    """Models with some additional business data that the note has"""
    text: str
    attachments: list[str, ] | None
    checkpoints: list[CheckpointModel, ] | None


class NoteModel(BaseModel):
    """Represent note. Store in the backend db with same model"""
    id: str = Field(alias="_id")
    name: str
    links: NoteLinksModel
    data: NoteDataModel
    times: NoteTimesModel


class NoteModelToCreate(BaseModel):
    """Model to create new Alarm use backend endpoint"""
    name: str
    links: NoteLinksModel
    data: NoteDataModel
