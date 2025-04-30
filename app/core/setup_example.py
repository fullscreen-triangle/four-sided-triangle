"""
Example setup for the Four-Sided Triangle orchestrator with all pipeline stages.

This module demonstrates how to set up the orchestrator with all seven
pipeline stages in the correct order.
"""

import logging
from typing import Dict, Any, Optional

from app.orchestrator.orchestrator import DefaultOrchestrator
from app.core.stages.stage0_query_processor.query_processor_stage import QueryProcessorStage
from app.core.stages.stage1_semantic_atdb.semantic_atdb_stage import SemanticATDBStage
# Import other stages as they are implemented
# from app.core.stages.stage2_domain_knowledge.domain_knowledge_stage import DomainKnowledgeStage
# from app.core.stages.stage3_reasoning_optimization.reasoning_optimization_stage import ReasoningOptimizationStage
# from app.core.stages.stage4_solution_generation.solution_generation_stage import SolutionGenerationStage
# from app.core.stages.stage5_response_scoring.response_scoring_stage import ResponseScoringStage
# from app.core.stages.stage6_response_comparison.response_comparison_stage import ResponseComparisonStage

logger = logging.getLogger(__name__)

def setup_orchestrator() -> DefaultOrchestrator:
    """
    Set up the orchestrator with all pipeline stages.
    
    Returns:
        Configured orchestrator instance
    """
    # Create orchestrator instance
    orchestrator = DefaultOrchestrator()
    
    # Register all pipeline stages
    orchestrator.register_stage("query_processor", QueryProcessorStage())
    orchestrator.register_stage("semantic_atdb", SemanticATDBStage())
    
    # Add other stages as they are implemented
    # orchestrator.register_stage("domain_knowledge", DomainKnowledgeStage())
    # orchestrator.register_stage("reasoning_optimization", ReasoningOptimizationStage())
    # orchestrator.register_stage("solution_generation", SolutionGenerationStage())
    # orchestrator.register_stage("response_scoring", ResponseScoringStage())
    # orchestrator.register_stage("response_comparison", ResponseComparisonStage())
    
    # Configure pipeline execution order and dependencies
    pipeline_config = [
        {
            "id": "query_processor",
            "depends_on": []
        },
        {
            "id": "semantic_atdb",
            "depends_on": ["query_processor"]
        }
        # Add other stages as they are implemented
        # {
        #     "id": "domain_knowledge",
        #     "depends_on": ["query_processor", "semantic_atdb"]
        # },
        # {
        #     "id": "reasoning_optimization",
        #     "depends_on": ["domain_knowledge"]
        # },
        # {
        #     "id": "solution_generation",
        #     "depends_on": ["reasoning_optimization"]
        # },
        # {
        #     "id": "response_scoring",
        #     "depends_on": ["solution_generation"]
        # },
        # {
        #     "id": "response_comparison",
        #     "depends_on": ["response_scoring"]
        # }
    ]
    
    orchestrator.configure_pipeline(pipeline_config)
    
    logger.info("Orchestrator setup complete with stages: %s", 
                ", ".join(stage["id"] for stage in pipeline_config))
    
    return orchestrator

def main():
    """Example usage of the orchestrator setup."""
    orchestrator = setup_orchestrator()
    
    # Process a sample query
    result = orchestrator.process_query(
        "What is the impact of quantum computing on cryptography?",
        {"user_id": "test_user"}
    )
    
    print(f"Query processing complete with result: {result}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    main() 