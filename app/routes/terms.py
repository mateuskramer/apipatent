from typing import List

from fastapi import APIRouter, HTTPException

from app.schemas.analytics import CorrelationItem, Indicators, TimeSeriesPoint
from app.schemas.catalog import TermItem, ConceptItem, TermOccurrence, TermNetwork, SparseOpportunity
from app.services.analytics_service import get_term_correlations, get_term_indicators
from app.services.catalog_service import get_concepts_by_term, get_term, list_terms
from app.services.term_service import get_term_timeseries, get_terms_associations, get_term_network, get_sparse_opportunities_for_term


router = APIRouter(tags=["terms"])


@router.get("/terms", response_model=List[TermItem])
def read_terms(limit: int = 100, offset: int = 0) -> List[TermItem]:
    return list_terms(limit=limit, offset=offset)


@router.get("/terms/associations", response_model=List[TermOccurrence])
def read_terms_associations() -> List[TermOccurrence]:
    return get_terms_associations()



@router.get("/terms/{term_id}", response_model=TermItem)
def read_term(term_id: int) -> TermItem:
    result = get_term(term_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Term {term_id} not found")
    return result


@router.get("/terms/{term_id}/concepts", response_model=List[ConceptItem])
def read_term_concepts(term_id: int) -> List[ConceptItem]:
    if get_term(term_id) is None:
        raise HTTPException(status_code=404, detail=f"Term {term_id} not found")
    return get_concepts_by_term(term_id)


@router.get("/terms/{term}/timeseries", response_model=List[TimeSeriesPoint])
def read_term_timeseries(term: str) -> List[TimeSeriesPoint]:
    return get_term_timeseries(term)


@router.get("/terms/{term}/correlations", response_model=List[CorrelationItem])
def read_term_correlations(term: str) -> List[CorrelationItem]:
    result = get_term_correlations(term)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Term '{term}' correlations not found")
    return result


@router.get("/terms/{term}/indicators", response_model=Indicators)
def read_term_indicators(term: str) -> Indicators:
    result = get_term_indicators(term)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Term '{term}' indicators not found")
    return result


@router.get("/terms/{term}/network", response_model=TermNetwork)
def read_term_network(term: str, depth: int = 3, limit: int = 5) -> TermNetwork:
    return get_term_network(term, depth=depth, top_n=limit)


@router.get("/terms/{term}/opportunities", response_model=List[SparseOpportunity])
def read_term_opportunities(term: str, limit: int = 20) -> List[SparseOpportunity]:
    return get_sparse_opportunities_for_term(term, top_n=limit)

