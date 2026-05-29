from typing import List, Optional
import math

from app.repositories.db import fetch_all, fetch_one


def _get_term_id(term: str) -> Optional[int]:
    row = fetch_one(
        """
        SELECT id
        FROM term_dictionary
        WHERE term = %s
        """,
        (term,),
    )
    return int(row["id"]) if row else None


def _cosine_shift(first_vector: dict[str, int], last_vector: dict[str, int]) -> float:
    if not first_vector or not last_vector:
        return 0.0
    dot = sum(first_vector.get(k, 0) * last_vector.get(k, 0) for k in set(first_vector) | set(last_vector))
    norm_first = math.sqrt(sum(v * v for v in first_vector.values()))
    norm_last = math.sqrt(sum(v * v for v in last_vector.values()))
    if norm_first == 0 or norm_last == 0:
        return 0.0
    return (dot / (norm_first * norm_last)) * 100.0


def _get_growth(term_id: int) -> float:
    row = fetch_one(
        """
        WITH monthly AS (
            SELECT p.year_month,
                   count(DISTINCT pt.patent_id::text) AS count
            FROM patent_terms pt
            JOIN patents p ON pt.patent_id::text = p.id::text
            WHERE pt.term_id = %s
              AND p.year_month IS NOT NULL
            GROUP BY p.year_month
        )
        SELECT count, lag(count) OVER (ORDER BY year_month) AS prev_count
        FROM monthly
        ORDER BY year_month DESC
        LIMIT 1
        """,
        (term_id,),
    )
    if not row or row.get("prev_count") is None:
        return 0.0
    current = float(row["count"])
    previous = float(row["prev_count"])
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100.0


def _get_density(term_id: int) -> int:
    row = fetch_one(
        """
        SELECT count(DISTINCT pt.patent_id::text) AS density
        FROM patent_terms pt
        JOIN patents p ON pt.patent_id::text = p.id::text
        WHERE pt.term_id = %s
          AND p.year_month IS NOT NULL
        """,
        (term_id,),
    )
    return int(row["density"]) if row and row["density"] is not None else 0


def _get_fusion(term_id: int) -> int:
    row = fetch_one(
        """
        SELECT count(DISTINCT td2.term) AS fusion
        FROM patent_terms pt
        JOIN patents p ON pt.patent_id::text = p.id::text
        JOIN patent_terms pt2 ON pt2.patent_id::text = pt.patent_id::text
        JOIN term_dictionary td2 ON td2.id = pt2.term_id
        WHERE pt.term_id = %s
          AND td2.id != %s
          AND p.year_month IS NOT NULL
        """,
        (term_id, term_id),
    )
    return int(row["fusion"]) if row and row["fusion"] is not None else 0


def _get_shift(term_id: int) -> float:
    months = fetch_one(
        """
        SELECT min(p.year_month) AS first_month,
               max(p.year_month) AS last_month
        FROM patent_terms pt
        JOIN patents p ON pt.patent_id::text = p.id::text
        WHERE pt.term_id = %s
          AND p.year_month IS NOT NULL
        """,
        (term_id,),
    )
    if not months or months.get("first_month") is None or months["first_month"] == months["last_month"]:
        return 0.0
    first_month = months["first_month"]
    last_month = months["last_month"]
    rows = fetch_all(
        """
        WITH term_patents AS (
            SELECT DISTINCT pt.patent_id::text AS patent_id,
                   p.year_month
            FROM patent_terms pt
            JOIN patents p ON pt.patent_id::text = p.id::text
            WHERE pt.term_id = %s
              AND p.year_month IN (%s, %s)
              AND p.year_month IS NOT NULL
        )
        SELECT tp.year_month,
               td2.term AS other_term,
               count(DISTINCT pt2.patent_id::text) AS count
        FROM term_patents tp
        JOIN patent_terms pt2 ON pt2.patent_id::text = tp.patent_id::text
        JOIN term_dictionary td2 ON td2.id = pt2.term_id
        WHERE td2.id != %s
        GROUP BY tp.year_month, td2.term
        ORDER BY tp.year_month, td2.term
        """,
        (term_id, first_month, last_month, term_id),
    )
    first_vector: dict[str, int] = {}
    last_vector: dict[str, int] = {}
    for row in rows:
        if row["year_month"] == first_month:
            first_vector[row["other_term"]] = int(row["count"])
        elif row["year_month"] == last_month:
            last_vector[row["other_term"]] = int(row["count"])
    return _cosine_shift(first_vector, last_vector)


def _calc_future_score(growth: float, fusion: int, shift: float, density: int) -> float:
    score = 0.35 * min(max(growth, 0.0), 100.0)
    score += 0.25 * min(fusion * 5, 100.0)
    score += 0.20 * min(shift, 100.0)
    score += 0.20 * min(density, 100.0)
    return round(score, 2)


def get_term_correlations(term: str) -> List[dict] | None:
    term_id = _get_term_id(term)
    if term_id is None:
        return None

    total_row = fetch_one(
        """
        SELECT count(DISTINCT pt.patent_id::text) AS total
        FROM patent_terms pt
        JOIN patents p ON pt.patent_id::text = p.id::text
        WHERE p.year_month IS NOT NULL
        """,
        (),
    )
    total = int(total_row["total"]) if total_row and total_row["total"] is not None else 0
    if total == 0:
        return []

    count_a_row = fetch_one(
        """
        SELECT count(DISTINCT pt.patent_id::text) AS count_a
        FROM patent_terms pt
        JOIN patents p ON pt.patent_id::text = p.id::text
        WHERE pt.term_id = %s
          AND p.year_month IS NOT NULL
        """,
        (term_id,),
    )
    count_a = int(count_a_row["count_a"]) if count_a_row and count_a_row["count_a"] is not None else 0
    if count_a == 0:
        return []

    rows = fetch_all(
        """
        WITH term_a_patents AS (
            SELECT DISTINCT pt.patent_id::text AS patent_id
            FROM patent_terms pt
            JOIN patents p ON pt.patent_id::text = p.id::text
            WHERE pt.term_id = %s
              AND p.year_month IS NOT NULL
        )
        SELECT td.term AS term,
               count(DISTINCT ptb.patent_id::text) AS count_b,
               count(DISTINCT CASE WHEN ptb.patent_id::text IN (SELECT patent_id FROM term_a_patents) THEN ptb.patent_id::text END) AS count_ab
        FROM patent_terms ptb
        JOIN term_dictionary td ON td.id = ptb.term_id
        JOIN patents p ON ptb.patent_id::text = p.id::text
        WHERE p.year_month IS NOT NULL
          AND td.id != %s
        GROUP BY td.term
        HAVING count_ab > 0
        """,
        (term_id, term_id),
    )

    results: List[dict] = []
    for row in rows:
        count_b = int(row["count_b"])
        count_ab = int(row["count_ab"])
        pa = count_a / total
        pb = count_b / total
        pab = count_ab / total
        union = count_a + count_b - count_ab
        results.append(
            {
                "term": row["term"],
                "cooc": count_ab,
                "lift": round(pab / (pa * pb), 4) if pa * pb > 0 else 0.0,
                "jaccard": round(count_ab / union, 4) if union > 0 else 0.0,
                "pmi": round(math.log2(pab / (pa * pb)), 4) if pa * pb > 0 and pab > 0 else 0.0,
            }
        )

    return sorted(results, key=lambda item: item["lift"], reverse=True)


def get_term_indicators(term: str) -> dict | None:
    term_id = _get_term_id(term)
    if term_id is None:
        return None

    growth = _get_growth(term_id)
    density = _get_density(term_id)
    fusion = _get_fusion(term_id)
    shift = _get_shift(term_id)
    return {
        "term": term,
        "growth": round(growth, 2),
        "density": density,
        "fusion": fusion,
        "shift": round(shift, 2),
        "future_score": _calc_future_score(growth, fusion, shift, density),
    }


def get_ranking(limit: int = 100) -> List[dict]:
    rows = fetch_all(
        """
        SELECT td.term AS term,
               count(DISTINCT pt.patent_id::text) AS patent_count
        FROM patent_terms pt
        JOIN term_dictionary td ON td.id = pt.term_id
        JOIN patents p ON pt.patent_id::text = p.id::text
        WHERE p.year_month IS NOT NULL
        GROUP BY td.term
        ORDER BY patent_count DESC
        LIMIT %s
        """,
        (limit,),
    )
    ranking: List[dict] = []
    for row in rows:
        indicators = get_term_indicators(row["term"])
        if indicators is not None:
            ranking.append(indicators)
    return sorted(ranking, key=lambda item: item["future_score"], reverse=True)
