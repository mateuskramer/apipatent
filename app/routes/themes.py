from typing import List

from fastapi import APIRouter, HTTPException

from app.schemas.catalog import ThemeItem, ConceptItem, TopItem
from app.services.catalog_service import (
    get_theme,
    list_themes,
    get_concepts_by_theme,
    get_top_themes,
)

router = APIRouter(tags=["themes"])


@router.get("/themes", response_model=List[ThemeItem])
def read_themes(limit: int = 100, offset: int = 0) -> List[ThemeItem]:
    return list_themes(limit=limit, offset=offset)


@router.get("/themes/top", response_model=List[TopItem])
def read_themes_top(limit: int = 20) -> List[TopItem]:
    return get_top_themes(limit=limit)

@router.get("/themes/{theme_id}", response_model=ThemeItem)
def read_theme(theme_id: int) -> ThemeItem:
    result = get_theme(theme_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Theme {theme_id} not found")
    return result


@router.get("/themes/{theme_id}/concepts", response_model=List[ConceptItem])
def read_theme_concepts(theme_id: int) -> List[ConceptItem]:
    if get_theme(theme_id) is None:
        raise HTTPException(status_code=404, detail=f"Theme {theme_id} not found")
    return get_concepts_by_theme(theme_id)
