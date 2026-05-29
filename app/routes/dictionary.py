from typing import List

from fastapi import APIRouter, Depends

from app.core.security import get_api_key
from app.schemas.dictionary import DictionaryItem
from app.services.dictionary_service import list_dictionary_items

router = APIRouter(tags=["dictionary"])


@router.get("/dictionary", response_model=List[DictionaryItem], dependencies=[Depends(get_api_key)])
def read_dictionary() -> List[DictionaryItem]:
    return list_dictionary_items()
