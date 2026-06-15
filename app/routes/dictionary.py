from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_api_key

from app.schemas.dictionary import DictionaryItem, TermCreate
from app.services.dictionary_service import (
    list_dictionary_items,
    add_term,
    update_term,
    delete_term,
    count_associations,
)

router = APIRouter(tags=["dictionary"])


@router.get("/dictionary", response_model=List[DictionaryItem], dependencies=[Depends(get_api_key)])
def read_dictionary() -> List[DictionaryItem]:
    return list_dictionary_items()


@router.post("/dictionary", dependencies=[Depends(get_api_key)])
def create_dictionary_term(payload: TermCreate) -> dict:
    result = add_term(payload.term)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result.get("message", "Error adding term"))
    return result


@router.put("/dictionary/{term_id}", dependencies=[Depends(get_api_key)])
def update_dictionary_term(term_id: int, payload: TermCreate) -> dict:
    result = update_term(term_id, payload.term)
    if result["status"] == "not_found":
        raise HTTPException(status_code=404, detail="Term not found")
    elif result["status"] == "error":
        raise HTTPException(status_code=400, detail=result.get("message", "Error updating term"))
    return result


@router.delete("/dictionary/{term_id}", dependencies=[Depends(get_api_key)])
def delete_dictionary_term(term_id: int) -> dict:
    result = delete_term(term_id)
    if result["status"] == "not_found":
        raise HTTPException(status_code=404, detail="Term not found")
    elif result["status"] == "error":
        raise HTTPException(status_code=400, detail=result.get("message", "Error deleting term"))
    return result


@router.get("/dictionary/{term_id}/count", dependencies=[Depends(get_api_key)])
def get_term_association_count(term_id: int) -> dict:
    count = count_associations(term_id)
    return {"count": count}

