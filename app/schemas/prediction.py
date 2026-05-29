from datetime import datetime
from typing import List

from pydantic import BaseModel


class PredictionHistoryPoint(BaseModel):
    yearmonth: str
    actual_count: int


class PredictionPoint(BaseModel):
    target_year_month: str
    predicted_count: float
    pessimistic_count: float | None = None
    optimistic_count: float | None = None
    q25_count: float | None = None
    q75_count: float | None = None
    trained_at: datetime | None = None


class PredictionResponse(BaseModel):
    term: str
    history: List[PredictionHistoryPoint]
    predictions: List[PredictionPoint]
