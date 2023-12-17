from pydantic import BaseModel


class ThemeLinksModel(BaseModel):
    """Models with all relation links that the theme has"""
    user_id: str


class ThemeModel(BaseModel):
    """Represent theme. Store in the backend db with same model"""
    _id: str
    name: str
    description: str
    links: ThemeLinksModel


class ThemeModelToCreate(BaseModel):
    """Model to create new theme use backend endpoint"""
    name: str
    description: str | None
    links: ThemeLinksModel
