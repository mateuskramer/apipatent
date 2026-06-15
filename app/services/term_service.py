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


def get_terms_associations() -> List[dict]:
    return fetch_all(
        """
        SELECT p.id AS patent_id, p.year_month, td.term
        FROM patent_terms pt
        JOIN patents p ON pt.patent_id::text = p.id::text
        JOIN term_dictionary td ON td.id = pt.term_id
        WHERE p.year_month IS NOT NULL
        """
    )


def get_term_network(term: str, depth: int = 3, top_n: int = 5) -> dict:
    import pandas as pd
    associations = get_terms_associations()
    if not associations:
        return {"nodes": [], "edges": []}
    
    df = pd.DataFrame(associations)
    if df.empty or term not in df["term"].values:
        return {"nodes": [], "edges": []}
        
    nodes = {term: {"id": term, "layer": 0}}
    edges = []
    
    frontier = [(term, 0)]
    visited = set()
    
    while frontier:
        curr, level = frontier.pop(0)
        if curr in visited or level >= depth:
            continue
        visited.add(curr)
        
        # Get patent IDs containing the current term
        pats = df[df["term"] == curr]["patent_id"].unique()
        # Get other terms in those patents and count occurrences
        co_counts = (
            df[(df["patent_id"].isin(pats)) & (df["term"] != curr)]["term"]
            .value_counts()
        )
        
        for t, weight in co_counts.head(top_n).items():
            # Add node if not exists, or update if found at a lower layer
            if t not in nodes:
                nodes[t] = {"id": t, "layer": level + 1}
            elif nodes[t]["layer"] > level + 1:
                nodes[t]["layer"] = level + 1
                
            edges.append({
                "source": curr,
                "target": t,
                "weight": int(weight)
            })
            frontier.append((t, level + 1))
            
    return {
        "nodes": list(nodes.values()),
        "edges": edges
    }


def get_sparse_opportunities_for_term(term: str, top_n: int = 20) -> List[dict]:
    import pandas as pd
    import numpy as np
    import scipy.sparse as sp
    
    associations = get_terms_associations()
    if not associations:
        return []
        
    df_terms = pd.DataFrame(associations)
    if df_terms.empty or term not in df_terms["term"].values:
        return []
        
    df_terms = df_terms.copy()
    df_terms["term"] = df_terms["term"].astype("category")
    df_terms["patent_id"] = df_terms["patent_id"].astype("category")
    
    categories = df_terms["term"].cat.categories
    idx_to_term = dict(enumerate(categories))
    t_map = {t: i for i, t in idx_to_term.items()}
    
    if term not in t_map:
        return []
        
    A = sp.csr_matrix((
        np.ones(len(df_terms)),
        (df_terms["patent_id"].cat.codes, df_terms["term"].cat.codes),
    ))
    C = A.T @ A
    C.setdiag(0)
    
    idx = t_map[term]
    direct = C[idx].toarray().flatten()
    indirect = (C @ C[idx].T).toarray().flatten()
    
    mask = (indirect > 0) & (direct == 0)
    mask[idx] = False
    p_idx = np.where(mask)[0]
    if not len(p_idx):
        return []
        
    max_v = C.max() or 1
    
    results = [{
        "term": idx_to_term[i],
        "bridge_strength": int(indirect[i]),
        "common_neighbors_score": round(float(indirect[i] / max_v), 4)
    } for i in p_idx]
    
    results.sort(key=lambda x: x["bridge_strength"], reverse=True)
    return results[:top_n]


