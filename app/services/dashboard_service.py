import json
import logging
from typing import List, Optional
from app.repositories.db import fetch_all, fetch_one, execute_write

logger = logging.getLogger(__name__)

def list_dashboards() -> List[dict]:
    try:
        return fetch_all(
            "SELECT session_id, title, created_at, COALESCE(pinned, FALSE) AS pinned FROM dashboard_sessions ORDER BY created_at DESC LIMIT 40"
        )
    except Exception as e:
        logger.error("Error listing dashboards: %s", e, exc_info=True)
        return []

def list_pinned_dashboards() -> List[dict]:
    try:
        return fetch_all(
            "SELECT session_id, title, created_at, COALESCE(pinned, FALSE) AS pinned FROM dashboard_sessions WHERE pinned = TRUE ORDER BY created_at DESC"
        )
    except Exception as e:
        logger.error("Error listing pinned dashboards: %s", e, exc_info=True)
        return []

def get_dashboard(session_id: str) -> Optional[dict]:
    try:
        row = fetch_one(
            "SELECT session_id, title, spec_json FROM dashboard_sessions WHERE session_id = %s",
            (session_id,)
        )
        if not row:
            return None
        try:
            spec = json.loads(row["spec_json"])
        except Exception:
            spec = {}
        return {
            "session_id": row["session_id"],
            "title": row["title"],
            "spec": spec
        }
    except Exception as e:
        logger.error("Error getting dashboard %s: %s", session_id, e, exc_info=True)
        return None

def save_dashboard(session_id: str, title: str, spec: dict) -> bool:
    try:
        spec_str = json.dumps(spec, ensure_ascii=False)
        rows = execute_write(
            """
            INSERT INTO dashboard_sessions (session_id, title, spec_json)
            VALUES (%s, %s, %s)
            ON CONFLICT (session_id)
            DO UPDATE SET title = EXCLUDED.title, spec_json = EXCLUDED.spec_json, created_at = NOW()
            """,
            (session_id, title, spec_str)
        )
        return rows > 0
    except Exception as e:
        logger.error("Error saving dashboard %s: %s", session_id, e, exc_info=True)
        return False

def rename_dashboard(session_id: str, title: str) -> bool:
    try:
        rows = execute_write(
            "UPDATE dashboard_sessions SET title = %s WHERE session_id = %s",
            (title, session_id)
        )
        return rows > 0
    except Exception as e:
        logger.error("Error renaming dashboard %s: %s", session_id, e, exc_info=True)
        return False

def set_dashboard_pinned(session_id: str, pinned: bool) -> bool:
    try:
        rows = execute_write(
            "UPDATE dashboard_sessions SET pinned = %s WHERE session_id = %s",
            (pinned, session_id)
        )
        return rows > 0
    except Exception as e:
        logger.error("Error pinning dashboard %s: %s", session_id, e, exc_info=True)
        return False

def delete_dashboard(session_id: str) -> bool:
    try:
        rows = execute_write(
            "DELETE FROM dashboard_sessions WHERE session_id = %s",
            (session_id,)
        )
        return rows > 0
    except Exception as e:
        logger.error("Error deleting dashboard %s: %s", session_id, e, exc_info=True)
        return False
