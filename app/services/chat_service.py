from app.repositories.db import fetch_all, execute_write

def list_chat_sessions() -> list[dict]:
    return fetch_all(
        """
        SELECT
            session_id,
            MIN(created_at)  AS started_at,
            COUNT(*)         AS messages,
            MIN(CASE WHEN role = 'user' THEN content END) AS preview
        FROM chat_sessions
        GROUP BY session_id
        ORDER BY MIN(created_at) DESC
        LIMIT 50
        """
    )

def get_chat_history(session_id: str) -> list[dict]:
    return fetch_all(
        """
        SELECT role, content
        FROM chat_sessions
        WHERE session_id = %s
        ORDER BY created_at ASC
        """,
        (session_id,),
    )

def add_chat_message(session_id: str, role: str, content: str) -> bool:
    rows = execute_write(
        """
        INSERT INTO chat_sessions (session_id, role, content)
        VALUES (%s, %s, %s)
        """,
        (session_id, role, content),
    )
    return rows > 0

def delete_chat_session(session_id: str) -> bool:
    rows = execute_write(
        "DELETE FROM chat_sessions WHERE session_id = %s",
        (session_id,),
    )
    return rows > 0
