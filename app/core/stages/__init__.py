"""
Four-Sided Triangle Pipeline Stages

This module contains all the stages of the Four-Sided Triangle pipeline,
from initial query processing to final threshold verification.
"""

# Import all stage service classes
from app.core.stages.stage0_query_processor import QueryProcessorService
from app.core.stages.stage1_semantic_atdb import SemanticATDBService
from app.core.stages.stage2_domain_knowledge import DomainKnowledgeService
from app.core.stages.stage3_reasoning_optimization import ReasoningOptimizationService
from app.core.stages.stage4_solution import SolutionGenerationService
from app.core.stages.stage5_scoring import ResponseScoringService
from app.core.stages.stage6_comparison import ResponseComparisonService
from app.core.stages.stage7_verification import ThresholdVerificationService

# Register all stages in the pipeline order
PIPELINE_STAGES = [
    QueryProcessorService,
    SemanticATDBService,
    DomainKnowledgeService,
    ReasoningOptimizationService,
    SolutionGenerationService,
    ResponseScoringService,
    ResponseComparisonService,
    ThresholdVerificationService
]

# Export all stage service classes
__all__ = [
    "QueryProcessorService",
    "SemanticATDBService",
    "DomainKnowledgeService",
    "ReasoningOptimizationService",
    "SolutionGenerationService",
    "ResponseScoringService",
    "ResponseComparisonService",
    "ThresholdVerificationService",
    "PIPELINE_STAGES"
]
