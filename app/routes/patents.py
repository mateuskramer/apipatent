from typing import List

from fastapi import APIRouter

from app.schemas.catalog import PatentItem, SimilarPatentItem
from app.services.catalog_service import get_patents_with_embeddings, get_similar_patents

router = APIRouter(tags=["patents"])


@router.get("/patents", response_model=List[PatentItem])
def read_patents(exclude_embeddings: bool = False) -> List[PatentItem]:
    patents = get_patents_with_embeddings()
    if exclude_embeddings:
        for p in patents:
            p["embedding"] = None
    return patents


@router.get("/patents/{patent_id}/similar", response_model=List[SimilarPatentItem])
def read_similar_patents(patent_id: str, limit: int = 10) -> List[SimilarPatentItem]:
    return get_similar_patents(patent_id, top_n=limit)

