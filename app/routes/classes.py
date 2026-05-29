from typing import List

from fastapi import APIRouter, HTTPException

from app.schemas.catalog import ClassItem, ConceptItem
from app.services.catalog_service import get_class, list_classes, get_concepts_by_class

router = APIRouter(tags=["classes"])


@router.get("/classes", response_model=List[ClassItem])
def read_classes(limit: int = 100, offset: int = 0) -> List[ClassItem]:
    return list_classes(limit=limit, offset=offset)


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
