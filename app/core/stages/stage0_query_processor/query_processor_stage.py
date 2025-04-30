"""
Query Processor Stage implementation for the Four-Sided Triangle system.

This module provides the pipeline stage implementation for integrating
the Query Processor service into the orchestrator.
"""

import logging
from typing import Dict, Any, Optional

from app.orchestrator.interfaces import AbstractPipelineStage
from app.core.stages.stage0_query_processor.query_processor_service import QueryProcessorService

logger = logging.getLogger(__name__)

class QueryProcessorStage(AbstractPipelineStage):
    """
    Pipeline stage for Query Processing.
    
    This stage handles the initial processing of user queries, including:
    - Query preprocessing and normalization
    - Intent classification
    - Context incorporation
    - Query validation
    - Query packaging
    """
    
    @property
    def stage_id(self) -> str:
        """Unique identifier for this pipeline stage."""
        return "query_processor"
    
    def __init__(self):
        """Initialize the Query Processor stage."""
        super().__init__()
        self._service = None
        logger.info("Query Processor stage initialized")
    
    def _ensure_service(self):
        """Ensure the service is initialized."""
        if not self._service:
            self._service = QueryProcessorService()
            logger.debug("Initialized Query Processor service on first use")
    
    async def process(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data according to the stage's responsibility.
        
        Performs initial query processing including preprocessing, intent classification,
        context incorporation, validation, and packaging.
        
        Args:
            prompt: The generated prompt for this stage
            context: The current session context
            
        Returns:
            The processed query package ready for subsequent stages
        """
        self._ensure_service()
        
        try:
            # Extract query from context
            query_text = context.get("query", "")
            if not query_text:
                logger.warning("Empty query received in Query Processor stage")
                return {"error": "Empty query received"}
            
            # Prepare parameters
            parameters = {
                "prompt": prompt,
                "user_history": context.get("user_history", []),
                "preferences": context.get("preferences", {}),
                "session_id": context.get("session_id", None)
            }
            
            # Process through the service
            structured_query, metadata = await self._service.process_query(query_text, parameters)
            
            # Add service metadata to output metadata
            result = structured_query
            
            if isinstance(result, dict) and "metadata" not in result:
                result["metadata"] = {}
            
            # Add metadata from service processing
            if isinstance(result, dict):
                result["metadata"].update(metadata)
                
                # Add query type for pipeline routing
                if "query_type" not in result:
                    # Extract from intent classification if available
                    if metadata.get("confidence_scores", {}).get("intent") and \
                       metadata.get("intent_classification", {}).get("type"):
                        result["query_type"] = metadata["intent_classification"]["type"]
                    else:
                        # Default to complex domain
                        result["query_type"] = "complex_domain"
            
            # Update metrics
            self._update_metrics({
                "processing_time": metadata.get("total_processing_time", 0),
                "intent_confidence": metadata.get("confidence_scores", {}).get("intent", 0),
                "validation_passed": metadata.get("status") == "success"
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in Query Processor stage processing: {str(e)}")
            self._update_metrics({"errors": str(e)})
            return {"error": str(e)}
    
    async def refine(self, refinement_prompt: str, context: Dict[str, Any], previous_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Refine previous output based on feedback.
        
        Attempts to reprocess the query with additional guidance if the previous
        attempt had issues or was incomplete.
        
        Args:
            refinement_prompt: Prompt specifically for refinement
            context: The current session context
            previous_output: The output from the previous processing attempt
            
        Returns:
            The refined output
        """
        self._ensure_service()
        
        try:
            # Check if there were validation failures
            if previous_output.get("validation_failed"):
                # Extract query from context
                query_text = context.get("query", "")
                
                # Prepare parameters with refinement guidance
                parameters = {
                    "prompt": refinement_prompt,
                    "user_history": context.get("user_history", []),
                    "preferences": context.get("preferences", {}),
                    "session_id": context.get("session_id", None),
                    "refinement": {
                        "previous_validation": previous_output.get("details", {}),
                        "guidance": refinement_prompt
                    }
                }
                
                # Reprocess with refinement data
                structured_query, metadata = await self._service.process_query(query_text, parameters)
                
                # Update metrics
                self._update_metrics({
                    "refinement_count": self._metrics.get("refinement_count", 0) + 1,
                    "refinement_success": metadata.get("status") == "success"
                })
                
                # Add metadata from service processing
                result = structured_query
                if isinstance(result, dict) and "metadata" not in result:
                    result["metadata"] = {}
                    
                if isinstance(result, dict):
                    result["metadata"].update(metadata)
                
                return result
            else:
                # For non-validation failures, use default refinement
                return await super().refine(refinement_prompt, context, previous_output)
                
        except Exception as e:
            logger.error(f"Error in Query Processor stage refinement: {str(e)}")
            return previous_output 