import os

from typing import Final
from dotenv import load_dotenv

from .exceptions.configurate_exceptions import EnvDependNotFound

load_dotenv()


def get_env_var(var_name: str) -> str:
    """
    :raise EnvDependNotFound if value in None
    :param var_name: Env var name
    :return: Var value by name
    """
    value: str | None = os.getenv(var_name)
    if value is None:
        raise EnvDependNotFound(var_name)
    else:
        return value


BOT_TOKEN: Final[str] = get_env_var("BOT_TOKEN")
BACKEND_HOST: Final[str] = get_env_var("BACKEND_HOST")
BACKEND_USER_LOGIN: Final[str] = get_env_var("BACKEND_USER_LOGIN")
BACKEND_USER_PASSWORD: Final[str] = get_env_var("BACKEND_USER_PASSWORD")
