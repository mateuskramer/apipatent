from typing import List, Optional

from pydantic import BaseModel
from app.schemas.analytics import ConceptTimeSeriesPoint


class TermItem(BaseModel):
    term_id: int
    description: str
    normalized_desc: Optional[str] = None


class ClassItem(BaseModel):
    class_id: int
    name: Optional[str] = None


class ThemeItem(BaseModel):
    theme_id: int
    name: Optional[str] = None


class RelationItem(BaseModel):
    relation_id: int
    name: Optional[str] = None


class ConceptItem(BaseModel):
    concept_id: int
    term_id: int
    class_id: Optional[int] = None
    theme_id: Optional[int] = None


class ConceptDetail(BaseModel):
    concept_id: int
    term: TermItem
    class_: Optional[ClassItem] = None
    theme: Optional[ThemeItem] = None


class RelationTimePoint(BaseModel):
    time_id: int
    source_concept_id: int
    target_concept_id: int
    relation_id: int
    joint_frequency: int


class ConceptRelationItem(BaseModel):
    relation_id: int
    source_concept_id: int
    target_concept_id: int
    relation_name: Optional[str] = None


class TopItem(BaseModel):
    id: int
    name: str
    score: int
