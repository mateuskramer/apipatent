import os
from functools import lru_cache

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    db_host: str
    db_name: str = "postgres"
    db_user: str
    db_pass: str
    db_port: int = 5432
    db_sslmode: str = "require"
    api_key: str | None = None

    class Config:
        env_prefix = ""
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    # Read environment variables with graceful error for missing values
    missing = []
    db_host = os.environ.get("DB_HOST")
    if not db_host:
        missing.append("DB_HOST")
    db_user = os.environ.get("DB_USER")
    if not db_user:
        missing.append("DB_USER")
    db_pass = os.environ.get("DB_PASS")
    if not db_pass:
        missing.append("DB_PASS")

    if missing:
        raise RuntimeError(
            f"Missing required environment variables for database connection: {', '.join(missing)}.\n"
            "Set these in your environment or .env file (DB_HOST, DB_USER, DB_PASS)."
        )

    return Settings(
        db_host=db_host,
        db_name=os.environ.get("DB_NAME", "postgres"),
        db_user=db_user,
        db_pass=db_pass,
        db_port=int(os.environ.get("DB_PORT", 5432)),
        db_sslmode=os.environ.get("DB_SSLMODE", "require"),
        api_key=os.environ.get("API_KEY"),
    )
