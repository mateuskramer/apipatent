from typing import List

from fastapi import APIRouter

from app.schemas.catalog import PatentItem
from app.services.catalog_service import get_patents_with_embeddings

router = APIRouter(tags=["patents"])


@router.get("/patents", response_model=List[PatentItem])
def read_patents() -> List[PatentItem]:
    return get_patents_with_embeddings()
