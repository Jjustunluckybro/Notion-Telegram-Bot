import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN")
BACKEND_HOST: str = os.getenv("BACKEND_HOST")
BACKEND_USER_LOGIN: str = os.getenv("BACKEND_USER_LOGIN")
BACKEND_USER_PASSWORD: str = os.getenv("BACKEND_USER_PASSWORD")
