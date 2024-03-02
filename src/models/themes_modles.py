from pydantic import BaseModel, Field


class ThemeLinksModel(BaseModel):
    """Models with all relation links that the theme has"""
    user_id: str


class ThemeModel(BaseModel):
    """Represent theme. Store in the backend db with same model"""
    id: str = Field(alias="_id")
    name: str
    description: str
    links: ThemeLinksModel


class ThemeModelToCreate(BaseModel):
    """Model to create new theme use backend endpoint"""
    name: str
    description: str | None
    links: ThemeLinksModel
