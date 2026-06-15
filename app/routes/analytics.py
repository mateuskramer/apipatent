from typing import List

from fastapi import APIRouter, Query

from app.schemas.analytics import RankingItem
from app.schemas.catalog import TermItem, TopItem
from app.services.analytics_service import get_ranking, get_db_stats
from app.services.catalog_service import (
    get_top_classes,
    get_top_relations,
    get_top_themes,
    search_terms,
)

router = APIRouter(tags=["analytics"])


@router.get("/ranking", response_model=List[RankingItem])
def read_ranking(limit: int = Query(100, ge=1, le=500)) -> List[RankingItem]:
    """Retorna ranking de termos ordenados por future_score (maturidade e impacto)."""
    return get_ranking(limit=limit)


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


@router.get("/stats")
def read_db_stats() -> dict:
    return get_db_stats()

