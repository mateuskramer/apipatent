from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.schemas.catalog import RelationItem, RelationTimePoint, TopItem
from app.services.catalog_service import (
    get_relation,
    list_relations,
    get_relation_time_series,
    get_top_relations,
)

router = APIRouter(tags=["relations"])


@router.get("/relations", response_model=List[RelationItem])
def read_relations(limit: int = 100, offset: int = 0) -> List[RelationItem]:
    return list_relations(limit=limit, offset=offset)


@router.get("/relations/top", response_model=List[TopItem])
def read_relations_top(limit: int = 20) -> List[TopItem]:
    return get_top_relations(limit=limit)

@router.get("/relations/{relation_id}", response_model=RelationItem)
def read_relation(relation_id: int) -> RelationItem:
    result = get_relation(relation_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Relation {relation_id} not found")
    return result


@router.get("/relations/{relation_id}/time-series", response_model=List[RelationTimePoint])
def read_relation_time_series(
    relation_id: int,
    from_: Optional[int] = Query(None, alias="from"),
    to: Optional[int] = Query(None),
) -> List[RelationTimePoint]:
    if get_relation(relation_id) is None:
        raise HTTPException(status_code=404, detail=f"Relation {relation_id} not found")
    date_range = (from_, to) if from_ is not None and to is not None else None
    return get_relation_time_series(relation_id, date_range)
