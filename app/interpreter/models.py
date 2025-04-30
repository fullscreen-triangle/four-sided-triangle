from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ResponseQualityMetrics(BaseModel):
    accuracy: float
    completeness: float
    clarity: float
    relevance: float
    bias_assessment: float
    overall_quality: float

class VisualizationElement(BaseModel):
    id: str
    type: str  # chart, diagram, etc.
    title: str
    description: str
    data: Dict[str, Any]
    config: Dict[str, Any]

class InterpretedSolution(BaseModel):
    technical_explanation: str
    user_friendly_explanation: str
    key_insights: List[str]
    visual_elements: Optional[List[VisualizationElement]] = None
    sources: Optional[List[Dict[str, Any]]] = None
    follow_up_suggestions: Optional[List[str]] = None

class InterpretationRequest(BaseModel):
    solution_package: Dict[str, Any]  # Contains reasoning steps, conclusions, results
    user_context: Dict[str, Any]  # User expertise level, preferences
    presentation_requirements: Optional[Dict[str, Any]] = None  # Format, detail level

class InterpretationResponse(BaseModel):
    interpreted_solution: InterpretedSolution
    quality_metrics: ResponseQualityMetrics
    metadata: Dict[str, Any] 