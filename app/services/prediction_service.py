from app.repositories.db import fetch_all
from app.services.term_service import _get_term_timeseries_rows


def get_term_prediction(term: str) -> dict:
    history_rows = _get_term_timeseries_rows(term)
    prediction_rows = fetch_all(
        """
        SELECT target_year_month, predicted_count, pessimistic_count, optimistic_count,
               q25_count, q75_count, trained_at
        FROM patent_predictions
        WHERE term = %s
        ORDER BY target_year_month
        """,
        (term,),
    )
    return {
        "term": term,
        "history": [
            {"yearmonth": row["year_month"], "actual_count": int(row["count"])}
            for row in history_rows
        ],
        "predictions": [
            {
                "target_year_month": row["target_year_month"],
                "predicted_count": float(row["predicted_count"]),
                "pessimistic_count": float(row["pessimistic_count"]) if row.get("pessimistic_count") is not None else None,
                "optimistic_count": float(row["optimistic_count"]) if row.get("optimistic_count") is not None else None,
                "q25_count": float(row["q25_count"]) if row.get("q25_count") is not None else None,
                "q75_count": float(row["q75_count"]) if row.get("q75_count") is not None else None,
                "trained_at": row.get("trained_at"),
            }
            for row in prediction_rows
        ],
    }


def get_term_backtest(term: str) -> list[dict]:
    try:
        rows = fetch_all(
            """
            SELECT target_year_month, predicted_count, real_count
            FROM patent_backtest
            WHERE term = %s
            ORDER BY target_year_month
            """,
            (term,),
        )
        return [
            {
                "target_year_month": row["target_year_month"],
                "predicted_count": float(row["predicted_count"]) if row.get("predicted_count") is not None else None,
                "real_count": float(row["real_count"]) if row.get("real_count") is not None else None,
            }
            for row in rows
        ]
    except Exception:
        # Fallback if the patent_backtest table does not exist
        return []

