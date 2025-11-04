import os
from enum import Enum
from pydantic_settings import BaseSettings


class DatabaseType(Enum):
    SQLITE = "sqlite"
    MEMORY = "memory"


class Settings(BaseSettings):
    MODE: str | None = None

    # Uvicorn Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    GRACEFUL_SHUTDOWN_TIMEOUT: int = 30

    # Database Configuration
    DATABASE_TYPE: DatabaseType = DatabaseType.SQLITE

    # ollama settings
    OLLAMA_BASE_URL: str | None = "http://localhost:11434"

    @property
    def TEMP_DIR(self) -> str:
        return os.path.join(os.getcwd(), "tmp")

    @property
    def BASE_URL(self) -> str:
        return f"http://{self.HOST}:{self.PORT}"

    def is_dev(self) -> bool:
        return self.MODE == "dev"


settings = Settings()
