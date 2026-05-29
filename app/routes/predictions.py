from fastapi import APIRouter, HTTPException

from app.schemas.prediction import PredictionResponse
from app.services.prediction_service import get_term_prediction

router = APIRouter(tags=["predictions"])


@router.get("/predictions/{term}", response_model=PredictionResponse)
def read_term_predictions(term: str) -> PredictionResponse:
    result = get_term_prediction(term)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Predictions not found for term '{term}'")
    return result
