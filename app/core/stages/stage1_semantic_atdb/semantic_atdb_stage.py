"""
Semantic ATDB Stage implementation for the Four-Sided Triangle system.

This module provides the pipeline stage implementation for integrating
the Semantic ATDB service into the orchestrator.
"""

import logging
from typing import Dict, Any, Optional

from app.orchestrator.interfaces import AbstractPipelineStage
from app.core.stages.stage1_semantic_atdb.semantic_atdb_service import SemanticATDBService
from app.llm.llm_service import LLMService

logger = logging.getLogger(__name__)

class SemanticATDBStage(AbstractPipelineStage):
    """
    Pipeline stage for Semantic Adversarial Throttle Detection and Bypass (ATDB).
    
    This stage handles semantic analysis of user queries with advanced mechanisms 
    to detect and overcome LLM throttling.
    """
    
    @property
    def stage_id(self) -> str:
        """Unique identifier for this pipeline stage."""
        return "semantic_atdb"
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        """
        Initialize the Semantic ATDB stage.
        
        Args:
            llm_service: Optional LLM service instance. If not provided, 
                         a default instance will be created when needed.
        """
        super().__init__()
        self._llm_service = llm_service
        self._service = None
        logger.info("Semantic ATDB stage initialized")
    
    def _ensure_service(self):
        """Ensure the service is initialized."""
        if not self._service:
            if not self._llm_service:
                from app.llm.llm_service import get_default_llm_service
                self._llm_service = get_default_llm_service()
            
            self._service = SemanticATDBService(llm_service=self._llm_service)
            logger.debug("Initialized Semantic ATDB service on first use")
    
    async def process(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data according to the stage's responsibility.
        
        Performs semantic analysis with throttle detection and bypass on the query.
        
        Args:
            prompt: The generated prompt for this stage
            context: The current session context
            
        Returns:
            The processed semantic model with throttle detection metadata
        """
        self._ensure_service()
        
        start_time = None
        try:
            # Extract query from context
            query_text = context.get("query", "")
            if not query_text:
                logger.warning("Empty query received in Semantic ATDB stage")
                return {"error": "Empty query received"}
            
            # Prepare query data for the service
            query_data = {
                "query": query_text,
                "prompt": prompt,
                "context": context
            }
            
            # Process through the service
            result = await self._service.process_query(query_data)
            
            # Update metrics
            self._update_metrics({
                "throttling_detected": result.get("metadata", {}).get("throttling_detected", False),
                "bypass_strategy_used": result.get("metadata", {}).get("bypass_strategy", "none")
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in Semantic ATDB stage processing: {str(e)}")
            self._update_metrics({"errors": str(e)})
            return {"error": str(e)}
    
    async def refine(self, refinement_prompt: str, context: Dict[str, Any], previous_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Refine previous output based on feedback.
        
        This implementation attempts to improve the analysis if throttling was detected
        or if the previous analysis was incomplete.
        
        Args:
            refinement_prompt: Prompt specifically for refinement
            context: The current session context
            previous_output: The output from the previous processing attempt
            
        Returns:
            The refined output
        """
        self._ensure_service()
        
        try:
            # Check if throttling was detected in the previous output
            if previous_output.get("metadata", {}).get("throttling_detected", False):
                # If throttling was already handled, run a different bypass strategy
                query_text = context.get("query", "")
                
                query_data = {
                    "query": query_text,
                    "prompt": refinement_prompt,
                    "context": context,
                    "refinement": {
                        "previous_output": previous_output,
                        "bypass_strategy_override": "alternate"
                    }
                }
                
                # Process with refinement data
                refined_result = await self._service.process_query(query_data)
                
                # Update metrics
                self._update_metrics({
                    "refinement_count": self._metrics.get("refinement_count", 0) + 1,
                    "refinement_strategy": "alternate_bypass"
                })
                
                return refined_result
            else:
                # For non-throttled content, use default refinement
                return await super().refine(refinement_prompt, context, previous_output)
                
        except Exception as e:
            logger.error(f"Error in Semantic ATDB stage refinement: {str(e)}")
            return previous_output 