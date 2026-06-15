import json
from typing import List, Optional, Tuple

from app.repositories.db import fetch_all



def _fetch_one(query: str, params: tuple) -> Optional[dict]:
    rows = fetch_all(query, params)
    return rows[0] if rows else None


def list_terms(limit: int = 100, offset: int = 0) -> List[dict]:
    return fetch_all(
        "SELECT term_id, description, normalized_desc FROM di_term ORDER BY term_id LIMIT %s OFFSET %s",
        (limit, offset),
    )


def get_term(term_id: int) -> Optional[dict]:
    return _fetch_one(
        "SELECT term_id, description, normalized_desc FROM di_term WHERE term_id = %s",
        (term_id,),
    )


def list_classes(limit: int = 100, offset: int = 0) -> List[dict]:
    return fetch_all(
        "SELECT class_id, name FROM di_class ORDER BY class_id LIMIT %s OFFSET %s",
        (limit, offset),
    )


def get_class(class_id: int) -> Optional[dict]:
    return _fetch_one(
        "SELECT class_id, name FROM di_class WHERE class_id = %s",
        (class_id,),
    )


def list_themes(limit: int = 100, offset: int = 0) -> List[dict]:
    return fetch_all(
        "SELECT theme_id, name FROM di_theme ORDER BY theme_id LIMIT %s OFFSET %s",
        (limit, offset),
    )


def get_theme(theme_id: int) -> Optional[dict]:
    return _fetch_one(
        "SELECT theme_id, name FROM di_theme WHERE theme_id = %s",
        (theme_id,),
    )


def list_relations(limit: int = 100, offset: int = 0) -> List[dict]:
    return fetch_all(
        "SELECT relation_id, name FROM di_relation ORDER BY relation_id LIMIT %s OFFSET %s",
        (limit, offset),
    )


def get_relation(relation_id: int) -> Optional[dict]:
    return _fetch_one(
        "SELECT relation_id, name FROM di_relation WHERE relation_id = %s",
        (relation_id,),
    )


def list_concepts(limit: int = 100, offset: int = 0) -> List[dict]:
    return fetch_all(
        "SELECT concept_id, term_id, class_id, theme_id FROM di_concept ORDER BY concept_id LIMIT %s OFFSET %s",
        (limit, offset),
    )


def get_concepts_by_ids(concept_ids: List[int]) -> List[dict]:
    return fetch_all(
        "SELECT concept_id, term_id, class_id, theme_id FROM di_concept WHERE concept_id = ANY(%s) ORDER BY concept_id",
        (concept_ids,),
    )


def get_concept(concept_id: int) -> Optional[dict]:
    return _fetch_one(
        "SELECT concept_id, term_id, class_id, theme_id FROM di_concept WHERE concept_id = %s",
        (concept_id,),
    )


def get_concept_detail(concept_id: int) -> Optional[dict]:
    row = _fetch_one(
        """
        SELECT c.concept_id,
               t.term_id AS term_id,
               t.description AS term_description,
               t.normalized_desc AS term_normalized_desc,
               cl.class_id AS class_id,
               cl.name AS class_name,
               th.theme_id AS theme_id,
               th.name AS theme_name
        FROM di_concept c
        LEFT JOIN di_term t ON c.term_id = t.term_id
        LEFT JOIN di_class cl ON c.class_id = cl.class_id
        LEFT JOIN di_theme th ON c.theme_id = th.theme_id
        WHERE c.concept_id = %s
        """,
        (concept_id,),
    )
    if row is None:
        return None
    return {
        "concept_id": row["concept_id"],
        "term": {
            "term_id": row["term_id"],
            "description": row["term_description"],
            "normalized_desc": row["term_normalized_desc"],
        },
        "class_": {
            "class_id": row["class_id"],
            "name": row["class_name"],
        }
        if row["class_id"] is not None
        else None,
        "theme": {
            "theme_id": row["theme_id"],
            "name": row["theme_name"],
        }
        if row["theme_id"] is not None
        else None,
    }


def get_concepts_by_term(term_id: int) -> List[dict]:
    return fetch_all(
        "SELECT concept_id, term_id, class_id, theme_id FROM di_concept WHERE term_id = %s ORDER BY concept_id",
        (term_id,),
    )


def get_concepts_by_class(class_id: int) -> List[dict]:
    return fetch_all(
        "SELECT concept_id, term_id, class_id, theme_id FROM di_concept WHERE class_id = %s ORDER BY concept_id",
        (class_id,),
    )


def get_concepts_by_theme(theme_id: int) -> List[dict]:
    return fetch_all(
        "SELECT concept_id, term_id, class_id, theme_id FROM di_concept WHERE theme_id = %s ORDER BY concept_id",
        (theme_id,),
    )


def get_concept_time_series(concept_id: int, date_range: Optional[Tuple[int, int]] = None) -> List[dict]:
    sql = "SELECT time_id, concept_id, frequency FROM ft_concept_time WHERE concept_id = %s"
    params: tuple = (concept_id,)
    if date_range is not None:
        sql += " AND time_id BETWEEN %s AND %s"
        params = (concept_id, date_range[0], date_range[1])
    sql += " ORDER BY time_id"
    return fetch_all(sql, params)


def get_relation_time_series(relation_id: int, date_range: Optional[Tuple[int, int]] = None) -> List[dict]:
    sql = "SELECT time_id, source_concept_id, target_concept_id, relation_id, joint_frequency FROM ft_relation_time WHERE relation_id = %s"
    params: tuple = (relation_id,)
    if date_range is not None:
        sql += " AND time_id BETWEEN %s AND %s"
        params = (relation_id, date_range[0], date_range[1])
    sql += " ORDER BY time_id"
    return fetch_all(sql, params)


def get_concept_relations(concept_id: int) -> List[dict]:
    return fetch_all(
        "SELECT source_concept_id, target_concept_id, relation_id FROM ft_relation_time WHERE source_concept_id = %s OR target_concept_id = %s GROUP BY source_concept_id, target_concept_id, relation_id ORDER BY relation_id",
        (concept_id, concept_id),
    )


def get_concept_neighbors(concept_id: int, limit: int = 20) -> List[dict]:
    return fetch_all(
        """
        SELECT DISTINCT other.concept_id AS neighbor_id
        FROM ft_relation_time rel
        JOIN di_concept other ON (rel.source_concept_id = other.concept_id OR rel.target_concept_id = other.concept_id)
        WHERE (rel.source_concept_id = %s OR rel.target_concept_id = %s)
          AND other.concept_id != %s
        ORDER BY neighbor_id
        LIMIT %s
        """,
        (concept_id, concept_id, concept_id, limit),
    )


def get_concepts_top(limit: int = 20) -> List[dict]:
    return fetch_all(
        """
        SELECT c.concept_id AS id, t.description AS name, SUM(ft.frequency) AS score
        FROM di_concept c
        LEFT JOIN di_term t ON c.term_id = t.term_id
        LEFT JOIN ft_concept_time ft ON c.concept_id = ft.concept_id
        GROUP BY c.concept_id, t.description
        ORDER BY score DESC
        LIMIT %s
        """,
        (limit,),
    )


def get_top_classes(limit: int = 20) -> List[dict]:
    return fetch_all(
        """
        SELECT cl.class_id AS id, cl.name AS name, COUNT(c.concept_id) AS score
        FROM di_class cl
        LEFT JOIN di_concept c ON cl.class_id = c.class_id
        GROUP BY cl.class_id, cl.name
        ORDER BY score DESC
        LIMIT %s
        """,
        (limit,),
    )


def get_top_themes(limit: int = 20) -> List[dict]:
    return fetch_all(
        """
        SELECT th.theme_id AS id, th.name AS name, COUNT(c.concept_id) AS score
        FROM di_theme th
        LEFT JOIN di_concept c ON th.theme_id = c.theme_id
        GROUP BY th.theme_id, th.name
        ORDER BY score DESC
        LIMIT %s
        """,
        (limit,),
    )


def get_top_relations(limit: int = 20) -> List[dict]:
    return fetch_all(
        """
        SELECT r.relation_id AS id, r.name AS name, COUNT(*) AS score
        FROM di_relation r
        LEFT JOIN ft_relation_time ft ON r.relation_id = ft.relation_id
        GROUP BY r.relation_id, r.name
        ORDER BY score DESC
        LIMIT %s
        """,
        (limit,),
    )


def search_terms(q: str, limit: int = 20, offset: int = 0) -> List[dict]:
    return fetch_all(
        "SELECT term_id, description, normalized_desc FROM di_term WHERE description ILIKE %s OR normalized_desc ILIKE %s ORDER BY term_id LIMIT %s OFFSET %s",
        (f"%{q}%", f"%{q}%", limit, offset),
    )


def get_patents_with_embeddings() -> List[dict]:
    rows = fetch_all(
        "SELECT id, title, abstract, year_month, embedding FROM patents WHERE embedding IS NOT NULL AND embedding <> ''"
    )
    for r in rows:
        if isinstance(r["embedding"], str):
            try:
                r["embedding"] = json.loads(r["embedding"])
            except Exception:
                r["embedding"] = []
    return rows


def get_similar_patents(patent_id: str, top_n: int = 10) -> List[dict]:
    import numpy as np
    patents = get_patents_with_embeddings()
    if not patents:
        return []
    
    # Find the target patent index
    target_idx = None
    for idx, p in enumerate(patents):
        if p["id"] == patent_id:
            target_idx = idx
            break
            
    if target_idx is None:
        return []
        
    # Stack embeddings
    try:
        emb_list = [np.array(p["embedding"], dtype=np.float32) for p in patents]
        EMB = np.vstack(emb_list)
    except Exception as e:
        # In case shapes are mismatching
        if not emb_list:
            return []
        first_shape = emb_list[0].shape
        valid_indices = [i for i, emb in enumerate(emb_list) if emb.shape == first_shape]
        patents = [patents[i] for i in valid_indices]
        EMB = np.vstack([emb_list[i] for i in valid_indices])
        # Find new target index
        target_idx = None
        for idx, p in enumerate(patents):
            if p["id"] == patent_id:
                target_idx = idx
                break
        if target_idx is None:
            return []

    target_vec = EMB[target_idx]
    
    # Cosine similarity using numpy: dot_product / (norm_a * norm_b)
    dot = np.dot(EMB, target_vec)
    norm_target = np.linalg.norm(target_vec)
    norm_all = np.linalg.norm(EMB, axis=1)
    
    # Avoid division by zero
    norm_all[norm_all == 0] = 1.0
    if norm_target == 0:
        norm_target = 1.0
        
    sims = dot / (norm_target * norm_all)
    
    # Construct results
    results = []
    for idx, p in enumerate(patents):
        if idx == target_idx:
            continue
        results.append({
            "id": p["id"],
            "title": p["title"],
            "year_month": p["year_month"],
            "similarity": float(sims[idx])
        })
        
    # Sort and return top_n
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_n]


