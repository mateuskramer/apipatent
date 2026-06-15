from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from app.services.chat_service import (
    list_chat_sessions,
    get_chat_history,
    add_chat_message,
    delete_chat_session,
)

router = APIRouter(tags=["chat"])


class ChatMessageSchema(BaseModel):
    role: str
    content: str


@router.get("/chat/sessions")
def read_chat_sessions() -> List[dict]:
    return list_chat_sessions()


@router.get("/chat/sessions/{session_id}")
def read_chat_history(session_id: str) -> List[dict]:
    return get_chat_history(session_id)


@router.post("/chat/sessions/{session_id}/messages")
def save_chat_message(session_id: str, payload: ChatMessageSchema) -> dict:
    success = add_chat_message(session_id, payload.role, payload.content)
    if not success:
        raise HTTPException(status_code=400, detail="Error saving message")
    return {"status": "ok"}


@router.delete("/chat/sessions/{session_id}")
def remove_chat_session(session_id: str) -> dict:
    success = delete_chat_session(session_id)
    if not success:
        raise HTTPException(status_code=400, detail="Error deleting session")
    return {"status": "ok"}
