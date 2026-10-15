from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HistoryItemResponse(BaseModel):
    id: str
    submission_id: str
    title: str
    code_snippet: str
    time_complexity: str
    space_complexity: str
    confidence: str
    created_at: datetime

    model_config = {"from_attributes": True}


class HistoryDetailResponse(BaseModel):
    id: str
    submission_id: str
    title: str
    code: str
    time_complexity: str
    space_complexity: str
    confidence: str
    complexity_reasoning: str
    statistics: Dict[str, Any]
    structure: Dict[str, Any]
    graph_data: Dict[str, Any]
    detected_patterns: List[str]
    optimization_suggestions: List[str]
    created_at: datetime

    model_config = {"from_attributes": True}
