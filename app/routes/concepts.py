from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.schemas.analytics import ConceptTimeSeriesPoint
from app.schemas.catalog import ConceptDetail, ConceptItem, ConceptRelationItem, RelationTimePoint, TopItem
from app.services.catalog_service import (
    get_concept,
    get_concept_detail,
    get_concept_neighbors,
    get_concept_relations,
    get_concept_time_series,
    get_concepts_by_ids,
    get_concepts_top,
    get_relation_time_series,
    list_concepts,
)

router = APIRouter(tags=["concepts"])


@router.get("/concepts", response_model=List[ConceptItem])
def read_concepts(limit: int = 100, offset: int = 0) -> List[ConceptItem]:
    return list_concepts(limit=limit, offset=offset)


@router.get("/concepts/top", response_model=List[TopItem])
def read_concepts_top(limit: int = 20) -> List[TopItem]:
    return get_concepts_top(limit=limit)


@router.get("/concepts/{concept_id}", response_model=ConceptDetail)
def read_concept(concept_id: int) -> ConceptDetail:
    result = get_concept_detail(concept_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Concept {concept_id} not found")
    return result


@router.get("/concepts/{concept_id}/neighbors", response_model=List[ConceptItem])
def read_concept_neighbors(concept_id: int, limit: int = 20) -> List[ConceptItem]:
    if get_concept(concept_id) is None:
        raise HTTPException(status_code=404, detail=f"Concept {concept_id} not found")
    neighbors = get_concept_neighbors(concept_id, limit=limit)
    ids = [row["neighbor_id"] for row in neighbors]
    return get_concepts_by_ids(ids) if ids else []


@router.get("/concepts/{concept_id}/relations", response_model=List[ConceptRelationItem])
def read_concept_relations(concept_id: int) -> List[ConceptRelationItem]:
    if get_concept(concept_id) is None:
        raise HTTPException(status_code=404, detail=f"Concept {concept_id} not found")
    raw = get_concept_relations(concept_id)
    return [
        {
            "relation_id": row["relation_id"],
            "source_concept_id": row["source_concept_id"],
            "target_concept_id": row["target_concept_id"],
            "relation_name": row.get("relation_name"),
        }
        for row in raw
    ]


@router.get("/concepts/{concept_id}/time-series", response_model=List[ConceptTimeSeriesPoint])
def read_concept_time_series(
    concept_id: int,
    from_: Optional[int] = Query(None, alias="from"),
    to: Optional[int] = Query(None),
) -> List[ConceptTimeSeriesPoint]:
    if get_concept(concept_id) is None:
        raise HTTPException(status_code=404, detail=f"Concept {concept_id} not found")
    date_range = (from_, to) if from_ is not None and to is not None else None
    return get_concept_time_series(concept_id, date_range)


@router.get("/concepts/{concept_id}/relations/time-series", response_model=List[RelationTimePoint])
def read_concept_relations_time_series(
    concept_id: int,
    from_: Optional[int] = Query(None, alias="from"),
    to: Optional[int] = Query(None),
) -> List[RelationTimePoint]:
    if get_concept(concept_id) is None:
        raise HTTPException(status_code=404, detail=f"Concept {concept_id} not found")
    raw = get_concept_relations(concept_id)
    if not raw:
        return []
    relation_ids = {row["relation_id"] for row in raw}
    results: List[dict] = []
    for relation_id in relation_ids:
        results.extend(get_relation_time_series(relation_id, None if from_ is None or to is None else (from_, to)))
    return results
