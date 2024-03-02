from pydantic import BaseModel


class UserModel(BaseModel):
    """Represent telegram user. Store in the backend db with same model"""
    telegram_id: str
    user_name: str
    lang_code: str  # user language code
    first_name: str | None
    last_name: str | None
