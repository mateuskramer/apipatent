from typing import List

from fastapi import APIRouter, Query

from app.schemas.catalog import TermItem, TopItem
from app.services.catalog_service import (
    get_top_classes,
    get_top_relations,
    get_top_themes,
    search_terms,
)

router = APIRouter(tags=["analytics"])


@router.get("/classes/top", response_model=List[TopItem])
def read_classes_top(limit: int = 20) -> List[TopItem]:
    return get_top_classes(limit=limit)


@router.get("/themes/top", response_model=List[TopItem])
def read_themes_top(limit: int = 20) -> List[TopItem]:
    return get_top_themes(limit=limit)


@router.get("/relations/top", response_model=List[TopItem])
def read_relations_top(limit: int = 20) -> List[TopItem]:
    return get_top_relations(limit=limit)


@router.get("/search", response_model=List[TermItem])
def search(q: str, limit: int = 20, offset: int = 0) -> List[TermItem]:
    return search_terms(q=q, limit=limit, offset=offset)
