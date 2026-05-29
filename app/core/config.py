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
    return Settings(
        db_host=os.environ["DB_HOST"],
        db_name=os.environ.get("DB_NAME", "postgres"),
        db_user=os.environ["DB_USER"],
        db_pass=os.environ["DB_PASS"],
        db_port=int(os.environ.get("DB_PORT", 5432)),
        db_sslmode=os.environ.get("DB_SSLMODE", "require"),
        api_key=os.environ.get("API_KEY"),
    )
