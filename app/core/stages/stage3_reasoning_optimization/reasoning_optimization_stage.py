"""
Reasoning Optimization Stage implementation for the Four-Sided Triangle system.

This module provides the pipeline stage implementation for integrating
the Reasoning Optimization service into the orchestrator.
"""

import logging
from typing import Dict, Any, Optional

from app.orchestrator.interfaces import AbstractPipelineStage
from app.core.stages.stage3_reasoning_optimization.reasoning_optimization_service import ReasoningOptimizationService
from app.llm.llm_service import LLMService

logger = logging.getLogger(__name__)

class ReasoningOptimizationStage(AbstractPipelineStage):
    """
    Pipeline stage for Reasoning Optimization.
    
    This stage applies advanced reasoning strategies, optimizes solution 
    approaches, and reduces cognitive biases in the query processing pipeline.
    """
    
    @property
    def stage_id(self) -> str:
        """Unique identifier for this pipeline stage."""
        return "reasoning_optimization"
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        """
        Initialize the Reasoning Optimization stage.
        
        Args:
            llm_service: Optional LLM service instance. If not provided, 
                         a default instance will be created when needed.
        """
        super().__init__()
        self._llm_service = llm_service
        self._service = None
        logger.info("Reasoning Optimization stage initialized")
    
    def _ensure_service(self):
        """Ensure the service is initialized."""
        if not self._service:
            if not self._llm_service:
                from app.llm.llm_service import get_default_llm_service
                self._llm_service = get_default_llm_service()
            
            self._service = ReasoningOptimizationService(llm_service=self._llm_service)
            logger.debug("Initialized Reasoning Optimization service on first use")
    
    def process(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data to apply reasoning optimization strategies.
        
        Args:
            prompt: The generated prompt for this stage
            context: The current session context
            
        Returns:
            Dictionary containing the optimized reasoning model and metadata
        """
        self._ensure_service()
        
        query_data = context.get('query_data', {})
        semantic_model = context.get('semantic_model', {})
        domain_knowledge = context.get('domain_knowledge', {})
        
        # Update metrics
        start_time = context.get('processing_start_time', {})
        self._metrics['processing_start'] = start_time.get(self.stage_id)
        
        # Process the reasoning optimization
        result = self._service.optimize_reasoning(
            prompt=prompt,
            query_data=query_data,
            semantic_model=semantic_model,
            domain_knowledge=domain_knowledge
        )
        
        # Update metrics
        self._metrics['processing_end'] = self._service.get_last_processing_time()
        self._metrics['optimization_strategies'] = result.get('applied_strategies', [])
        self._metrics['bias_reduction_methods'] = result.get('bias_reduction_methods', [])
        
        # Return the result
        return result
    
    def refine(self, refinement_prompt: str, context: Dict[str, Any], previous_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Refine previous reasoning optimization based on feedback.
        
        Args:
            refinement_prompt: Prompt specifically for refinement
            context: The current session context
            previous_output: The output from the previous processing attempt
            
        Returns:
            The refined reasoning optimization output
        """
        self._ensure_service()
        
        # Update metrics
        self._metrics['refinement_count'] = self._metrics.get('refinement_count', 0) + 1
        
        # Process the refinement
        result = self._service.refine_optimization(
            refinement_prompt=refinement_prompt,
            context=context,
            previous_output=previous_output
        )
        
        # Update metrics
        self._metrics['last_refinement_time'] = self._service.get_last_processing_time()
        
        return result 