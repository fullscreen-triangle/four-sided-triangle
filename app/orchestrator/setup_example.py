"""
Example of how to set up and use the Four-Sided Triangle orchestrator.

This module provides an example of registering pipeline stages,
configuring the pipeline, and processing a query.
"""

import logging
import time
from typing import Dict, Any

from app.orchestrator.orchestrator import orchestrator, DefaultOrchestrator
from app.orchestrator.pipeline_stage import QueryProcessorStage, BasePipelineStage
from app.orchestrator.working_memory import working_memory
from app.orchestrator.prompt_generator import prompt_generator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Example pipeline stages
class RetrieverStage(BasePipelineStage):
    """
    Example retriever stage that fetches relevant information.
    """
    
    def _process_implementation(self, inputs: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        # Simplified implementation that would normally retrieve information
        processed_query = inputs.get("query_processor", {}).get("processed_query", inputs.get("query", ""))
        
        # Mock retrieval results
        return {
            "retrieved_information": [
                {
                    "source": "knowledge_base",
                    "content": f"Information related to '{processed_query}'",
                    "relevance_score": 0.85
                }
            ],
            "timestamp": time.time()
        }
    
    def get_stage_id(self) -> str:
        return "retriever"

class SolverStage(BasePipelineStage):
    """
    Example solver stage that generates a solution.
    """
    
    def _process_implementation(self, inputs: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        # Simplified implementation that would normally generate a solution
        processed_query = inputs.get("query_processor", {}).get("processed_query", inputs.get("query", ""))
        retrieved_info = inputs.get("retriever", {}).get("retrieved_information", [])
        
        # Mock solution
        return {
            "solution": f"Answer to '{processed_query}' based on retrieved information",
            "confidence": 0.9,
            "sources": [item.get("source") for item in retrieved_info],
            "timestamp": time.time()
        }
    
    def get_stage_id(self) -> str:
        return "solver"

class InterpreterStage(BasePipelineStage):
    """
    Example interpreter stage that presents the solution to the user.
    """
    
    def _process_implementation(self, inputs: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        # Simplified implementation that would normally format the solution for the user
        original_query = inputs.get("query", "")
        solution = inputs.get("solver", {}).get("solution", "No solution available")
        
        # Mock formatted response
        return {
            "response": f"Based on your question '{original_query}', here's what I found: {solution}",
            "format": "text",
            "timestamp": time.time()
        }
    
    def get_stage_id(self) -> str:
        return "interpreter"

def setup_orchestrator() -> DefaultOrchestrator:
    """
    Set up the orchestrator with pipeline stages and configuration.
    
    Returns:
        Configured orchestrator instance
    """
    # Register pipeline stages
    orchestrator.register_stage("query_processor", QueryProcessorStage())
    orchestrator.register_stage("retriever", RetrieverStage())
    orchestrator.register_stage("solver", SolverStage())
    orchestrator.register_stage("interpreter", InterpreterStage())
    
    # Configure pipeline execution order and dependencies
    pipeline_config = [
        {
            "id": "query_processor",
            "depends_on": []
        },
        {
            "id": "retriever",
            "depends_on": ["query_processor"]
        },
        {
            "id": "solver",
            "depends_on": ["query_processor", "retriever"]
        },
        {
            "id": "interpreter",
            "depends_on": ["solver"]
        }
    ]
    
    orchestrator.configure_pipeline(pipeline_config)
    
    return orchestrator

def process_example_query() -> Dict[str, Any]:
    """
    Process an example query through the orchestrator.
    
    Returns:
        Query processing result
    """
    # Make sure orchestrator is set up
    setup_orchestrator()
    
    # Example query
    query = "What are the key components of the Four-Sided Triangle system?"
    
    # Process the query
    logger.info(f"Processing query: {query}")
    result = orchestrator.process_query(query)
    
    return result

if __name__ == "__main__":
    # Process an example query
    result = process_example_query()
    
    # Print the result
    print("\n===== QUERY PROCESSING RESULT =====")
    print(f"Query ID: {result.get('query_id')}")
    print(f"Success: {result.get('success')}")
    print(f"Execution time: {result.get('execution_time', 0):.3f} seconds")
    
    # Print the final response
    interpreter_output = result.get("stage_outputs", {}).get("interpreter", {})
    if interpreter_output:
        print("\n===== FINAL RESPONSE =====")
        print(interpreter_output.get("response", "No response available")) 