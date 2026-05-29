from fastapi import Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

from app.core.config import get_settings

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def get_api_key(api_key_header_value: str | None = Security(api_key_header)) -> str:
    settings = get_settings()
    if settings.api_key is None:
        raise HTTPException(status_code=500, detail="API_KEY is not configured")
    if api_key_header_value != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key_header_value
