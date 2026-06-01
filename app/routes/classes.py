from typing import List

from fastapi import APIRouter, HTTPException

from app.schemas.catalog import ClassItem, ConceptItem, TopItem
from app.services.catalog_service import (
    get_class,
    list_classes,
    get_concepts_by_class,
    get_top_classes,
)

router = APIRouter(tags=["classes"])


@router.get("/classes", response_model=List[ClassItem])
def read_classes(limit: int = 100, offset: int = 0) -> List[ClassItem]:
    return list_classes(limit=limit, offset=offset)


@router.get("/classes/top", response_model=List[TopItem])
def read_classes_top(limit: int = 20) -> List[TopItem]:
    return get_top_classes(limit=limit)

@router.get("/classes/{class_id}", response_model=ClassItem)
def read_class(class_id: int) -> ClassItem:
    result = get_class(class_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Class {class_id} not found")
    return result


@router.get("/classes/{class_id}/concepts", response_model=List[ConceptItem])
def read_class_concepts(class_id: int) -> List[ConceptItem]:
    if get_class(class_id) is None:
        raise HTTPException(status_code=404, detail=f"Class {class_id} not found")
    return get_concepts_by_class(class_id)
