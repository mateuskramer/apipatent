from app.repositories.db import fetch_all, fetch_one, execute_write


def list_dictionary_items() -> list[dict]:
    return fetch_all(
        "SELECT id, term, class, status, created_at FROM term_dictionary ORDER BY term"
    )


def count_associations(term_id: int) -> int:
    row = fetch_one(
        "SELECT COUNT(*) AS count FROM patent_terms WHERE term_id = %s",
        (term_id,),
    )
    return int(row["count"]) if row and row.get("count") is not None else 0


def add_term(term: str) -> dict:
    term_clean = term.strip().lower()
    try:
        row = fetch_one(
            """
            INSERT INTO term_dictionary (term, class, status)
            VALUES (%s, 'technology', 'approved')
            ON CONFLICT (term) DO NOTHING
            RETURNING id
            """,
            (term_clean,),
        )
        if row and row.get("id"):
            return {"status": "ok", "id": int(row["id"])}
        return {"status": "duplicate"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def update_term(term_id: int, new_term: str) -> dict:
    new_term_clean = new_term.strip()
    try:
        rows_affected = execute_write(
            "UPDATE term_dictionary SET term = %s WHERE id = %s",
            (new_term_clean, term_id),
        )
        if rows_affected > 0:
            return {"status": "ok"}
        return {"status": "not_found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def delete_term(term_id: int) -> dict:
    try:
        execute_write("DELETE FROM patent_terms WHERE term_id = %s", (term_id,))
        rows_affected = execute_write("DELETE FROM term_dictionary WHERE id = %s", (term_id,))
        if rows_affected > 0:
            return {"status": "ok"}
        return {"status": "not_found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

