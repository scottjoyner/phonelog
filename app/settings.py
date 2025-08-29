from pydantic import BaseSettings, Field
from typing import Optional

class Settings(BaseSettings):
    # API
    APP_NAME: str = "phone-log-ingestion"
    ENV: str = "dev"
    LOG_LEVEL: str = "INFO"
    WAL_DIR: str = "/data/wal"
    WAL_ROTATE_BYTES: int = 100_000_000  # ~100MB

    # Neo4j
    NEO4J_URI: str = Field(..., env="NEO4J_URI")
    NEO4J_USER: str = Field(..., env="NEO4J_USER")
    NEO4J_PASSWORD: str = Field(..., env="NEO4J_PASSWORD")
    NEO4J_DATABASE: Optional[str] = Field(default=None, env="NEO4J_DATABASE")

    # Defaults / compatibility
    DEFAULT_USER_ID: str = "kipnerter"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
