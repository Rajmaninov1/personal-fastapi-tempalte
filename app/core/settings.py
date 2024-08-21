from enum import Enum
from pathlib import Path

from pydantic_settings import SettingsConfigDict, BaseSettings


class Environment(str, Enum):
    PROD = 'PROD'
    TEST = 'TEST'
    DEV = 'DEV'


class Settings(BaseSettings):
    # API metadata
    WEB_APP_TITLE: str = 'FastAPI Project Template'
    WEB_APP_DESCRIPTION: str = 'Description about what the microservice does'
    WEB_APP_VERSION: str = '1.0.0'
    OPENAPI_SERVER: str = ''

    # To know the development where is executed
    ENVIRONMENT: Environment = Environment.DEV
    LOCAL: bool = False
    DEBUG: bool = False

    # Path to the place main.py is
    BASE_PATH: Path = Path.cwd()

    # Background tasks limit
    BACKGROUND_TASK_LIMIT: int = 0
    # Resolution of 30 seconds
    BACKGROUND_TASK_GARBAGE_RESOLUTION: int = 30
    # In seconds, default to six hours
    BACKGROUND_TASK_PERSISTENCE_LIMIT: int = 6 * 60 * 60

    # Only for selenium projects
    REMOTE_BROWSER: bool = False

    # DB vars
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: str
    DATABASE_DB: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
