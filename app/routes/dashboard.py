from typing import List
from fastapi import APIRouter, HTTPException

from app.schemas.dashboard import (
    DashboardListItem,
    DashboardDetail,
    DashboardSavePayload,
    DashboardRenamePayload,
)
from app.services.dashboard_service import (
    list_dashboards,
    list_pinned_dashboards,
    get_dashboard,
    save_dashboard,
    rename_dashboard,
    set_dashboard_pinned,
    delete_dashboard,
)

router = APIRouter(tags=["dashboard"])

@router.get("/dashboards", response_model=List[DashboardListItem])
def read_dashboards() -> List[DashboardListItem]:
    return list_dashboards()

@router.get("/dashboards/pinned", response_model=List[DashboardListItem])
def read_pinned_dashboards() -> List[DashboardListItem]:
    return list_pinned_dashboards()

@router.get("/dashboards/{session_id}", response_model=DashboardDetail)
def read_dashboard(session_id: str) -> DashboardDetail:
    res = get_dashboard(session_id)
    if res is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return res

@router.post("/dashboards")
def create_or_update_dashboard(payload: DashboardSavePayload) -> dict:
    success = save_dashboard(payload.session_id, payload.title, payload.spec)
    if not success:
        raise HTTPException(status_code=400, detail="Error saving dashboard")
    return {"status": "ok"}

@router.put("/dashboards/{session_id}/rename")
def rename_dashboard_session(session_id: str, payload: DashboardRenamePayload) -> dict:
    success = rename_dashboard(session_id, payload.title)
    if not success:
        raise HTTPException(status_code=400, detail="Error renaming dashboard")
    return {"status": "ok"}

@router.put("/dashboards/{session_id}/pin")
def pin_dashboard_session(session_id: str) -> dict:
    success = set_dashboard_pinned(session_id, True)
    if not success:
        raise HTTPException(status_code=400, detail="Error pinning dashboard")
    return {"status": "ok"}

@router.put("/dashboards/{session_id}/unpin")
def unpin_dashboard_session(session_id: str) -> dict:
    success = set_dashboard_pinned(session_id, False)
    if not success:
        raise HTTPException(status_code=400, detail="Error unpinning dashboard")
    return {"status": "ok"}

@router.delete("/dashboards/{session_id}")
def remove_dashboard(session_id: str) -> dict:
    success = delete_dashboard(session_id)
    if not success:
        raise HTTPException(status_code=400, detail="Error deleting dashboard")
    return {"status": "ok"}
