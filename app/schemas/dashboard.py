from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional

class DashboardListItem(BaseModel):
    session_id: str
    title: str
    created_at: datetime
    pinned: bool

class DashboardDetail(BaseModel):
    session_id: str
    title: str
    spec: Dict[str, Any]

class DashboardSavePayload(BaseModel):
    session_id: str
    title: str
    spec: Dict[str, Any]

class DashboardRenamePayload(BaseModel):
    title: str
