from pydantic import BaseModel


class TimeSeriesPoint(BaseModel):
    yearmonth: str
    count: int


class ConceptTimeSeriesPoint(BaseModel):
    time_id: int
    concept_id: int
    frequency: int


class CorrelationItem(BaseModel):
    term: str
    cooc: int
    lift: float
    jaccard: float
    pmi: float


class Indicators(BaseModel):
    term: str
    growth: float
    density: int
    fusion: int
    shift: float
    future_score: float


class RankingItem(BaseModel):
    term: str
    growth: float
    density: int
    fusion: int
    shift: float
    future_score: float
