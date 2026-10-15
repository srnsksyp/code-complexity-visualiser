import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Code Complexity Visualizer"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"

    # Supabase PostgreSQL or fallback SQLite
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+pysqlite:///./complexity.db"
    )

    # Allowed CORS Origins
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ]

    # Limits
    MAX_CODE_LENGTH_BYTES: int = 100_000  # ~100KB
    MAX_CODE_LINES: int = 3_000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
