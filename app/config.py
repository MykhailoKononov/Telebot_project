import os
from dotenv import load_dotenv
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

load_dotenv()


class Settings(BaseSettings):
    TOKEN: Optional[str] = os.getenv('TOKEN')
    DB_NAME: Optional[str] = os.getenv('DB_NAME')
    USER: Optional[str] = os.getenv('USER')
    HOST: Optional[str] = os.getenv('HOST')
    PASSWORD: Optional[str] = os.getenv('PASSWORD')
    PORT: Optional[int] = os.getenv('PORT')
    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8"
    )


config = Settings()