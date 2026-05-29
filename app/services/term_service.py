from typing import List

from app.repositories.db import fetch_all


def list_terms() -> List[str]:
    rows = fetch_all("SELECT DISTINCT term FROM term_dictionary ORDER BY term")
    return [row["term"] for row in rows]


def _get_term_timeseries_rows(term: str) -> List[dict]:
    return fetch_all(
        """
        SELECT p.year_month, COUNT(*) AS count
        FROM patent_terms pt
        JOIN patents p ON pt.patent_id::text = p.id::text
        JOIN term_dictionary td ON td.id = pt.term_id
        WHERE td.term = %s AND p.year_month IS NOT NULL
        GROUP BY p.year_month
        ORDER BY p.year_month
        """,
        (term,),
    )


def get_term_timeseries(term: str) -> List[dict]:
    rows = _get_term_timeseries_rows(term)
    return [{"yearmonth": row["year_month"], "count": int(row["count"])} for row in rows]
