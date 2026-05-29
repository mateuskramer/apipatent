from app.repositories.db import fetch_all


def list_dictionary_items() -> list[dict]:
    return fetch_all(
        "SELECT id, term, class, status, created_at FROM term_dictionary ORDER BY term"
    )
