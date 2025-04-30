"""
Specialized Orchestrator - Implements the 8-stage processing pipeline.

This module extends the metacognitive orchestrator with specialized
model pipeline stages as defined in the Four-Sided Triangle architecture.
"""
from typing import Dict, Any, List, Optional, Tuple, Union
import logging
import time
import json
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.orchestrator.metacognitive_orchestrator import MetacognitiveOrchestrator
from app.orchestrator.working_memory import WorkingMemory
from app.models.factory import (
    get_model,
    get_default_model_for_stage_instance,
    initialize_models
)

logger = logging.getLogger(__name__)

class SpecializedOrchestrator(MetacognitiveOrchestrator):
    """
    Specialized orchestrator implementing the 8-stage pipeline.
    
    This orchestrator extends the metacognitive orchestrator with
    the specialized model stages for the Four-Sided Triangle architecture.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the specialized orchestrator.
        
        Args:
            config: Configuration parameters
        """
        super().__init__(config)
        
        # Initialize the model system
        initialize_models()
        
        # Create executor for parallel processing
        self._executor = ThreadPoolExecutor(
            max_workers=self._config.get("max_workers", 4)
        )
        
        # Stage timeout configuration
        self._stage_timeouts = self._config.get("stage_timeouts", {
            "query_processor": 5,  # seconds
            "semantic_atdb": 5,
            "domain_knowledge": 15,
            "reasoning": 20,
            "solution_generation": 30,
            "response_scoring": 10,
            "ensemble_diversification": 10,
            "threshold_verification": 5
        })
        
        logger.info("Specialized orchestrator initialized")
    
    async def process_query_async(self, query: str, session_id: Optional[str] = None,
                            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a query using the 8-stage pipeline asynchronously.
        
        Args:
            query: User query string
            session_id: Session identifier (generated if not provided)
            context: Additional context information
            
        Returns:
            Processing results
        """
        # Generate session ID if not provided
        if not session_id:
            session_id = f"session_{int(time.time())}"
        
        # Initialize context
        context = context or {}
        
        # Initialize working memory for this session
        self.working_memory.create_session(session_id, query, context.get("user_id"))
        session_context = self.working_memory.get_session_context(session_id)
        
        try:
            # Stage 0: Query Processing
            query_result = await self._process_stage_async(
                "query_processor", query, session_context,
                timeout=self._stage_timeouts.get("query_processor", 5)
            )
            self.working_memory.store_stage_output(session_id, "query_processor", query_result)
            session_context = self.working_memory.get_session_context(session_id)
            
            # Stage 1: Semantic ATDB
            atdb_result = await self._process_stage_async(
                "semantic_atdb", query_result, session_context,
                timeout=self._stage_timeouts.get("semantic_atdb", 5)
            )
            self.working_memory.store_stage_output(session_id, "semantic_atdb", atdb_result)
            session_context = self.working_memory.get_session_context(session_id)
            
            # Stage 2: Domain Knowledge Extraction
            knowledge_result = await self._process_stage_async(
                "domain_knowledge", atdb_result, session_context,
                timeout=self._stage_timeouts.get("domain_knowledge", 15)
            )
            self.working_memory.store_stage_output(session_id, "domain_knowledge", knowledge_result)
            session_context = self.working_memory.get_session_context(session_id)
            
            # Stage 3: Parallel Reasoning
            reasoning_result = await self._process_stage_async(
                "reasoning", atdb_result, session_context,
                timeout=self._stage_timeouts.get("reasoning", 20)
            )
            self.working_memory.store_stage_output(session_id, "reasoning", reasoning_result)
            session_context = self.working_memory.get_session_context(session_id)
            
            # Stage 4: Solution Generation
            # For solution generation, use multiple models with different temperatures
            solution_tasks = []
            models = [
                ("phi3-solution-generator", 0.7),
                ("mixtral-solution-generator", 0.3),
                ("biomedlm-solution-generator", 0.9)
            ]
            
            for model_id, temperature in models:
                task = self._process_with_specific_model_async(
                    "solution_generation", model_id, 
                    atdb_result, reasoning_result, knowledge_result, session_context,
                    temperature=temperature,
                    timeout=self._stage_timeouts.get("solution_generation", 30)
                )
                solution_tasks.append(task)
            
            # Wait for all solution generation tasks to complete
            solutions_results = await asyncio.gather(*solution_tasks, return_exceptions=True)
            
            # Filter out exceptions
            candidates = []
            for i, result in enumerate(solutions_results):
                if isinstance(result, Exception):
                    logger.error(f"Solution generation with {models[i][0]} failed: {str(result)}")
                else:
                    candidates.extend(result)
            
            solution_result = {"candidates": candidates}
            self.working_memory.store_stage_output(session_id, "solution_generation", solution_result)
            session_context = self.working_memory.get_session_context(session_id)
            
            # Stage 5: Response Scoring
            scoring_result = await self._process_stage_async(
                "response_scoring", solution_result, session_context,
                timeout=self._stage_timeouts.get("response_scoring", 10)
            )
            self.working_memory.store_stage_output(session_id, "response_scoring", scoring_result)
            session_context = self.working_memory.get_session_context(session_id)
            
            # Stage 6: Ensemble Diversification
            diversification_result = await self._process_stage_async(
                "ensemble_diversification", solution_result, scoring_result, session_context,
                timeout=self._stage_timeouts.get("ensemble_diversification", 10)
            )
            self.working_memory.store_stage_output(session_id, "ensemble_diversification", diversification_result)
            session_context = self.working_memory.get_session_context(session_id)
            
            # Stage 7: Threshold Verification
            verification_result = await self._process_stage_async(
                "threshold_verification", diversification_result, knowledge_result, session_context,
                timeout=self._stage_timeouts.get("threshold_verification", 5)
            )
            self.working_memory.store_stage_output(session_id, "threshold_verification", verification_result)
            session_context = self.working_memory.get_session_context(session_id)
            
            # Prepare final response
            response = self._prepare_response(session_id, session_context)
            
            return response
        
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            # Record the error
            self.working_memory.update_session_metadata(session_id, {
                "error": str(e),
                "status": "error"
            })
            # Return error response
            return {
                "status": "error",
                "error": str(e),
                "session_id": session_id
            }
    
    def process_query(self, query: str, session_id: Optional[str] = None,
                    context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a query using the 8-stage pipeline.
        
        This is a synchronous wrapper around the async method.
        
        Args:
            query: User query string
            session_id: Session identifier (generated if not provided)
            context: Additional context information
            
        Returns:
            Processing results
        """
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                self.process_query_async(query, session_id, context)
            )
        finally:
            loop.close()
    
    async def _process_stage_async(self, stage_id: str, *args, timeout: Optional[int] = None, **kwargs):
        """
        Process a stage asynchronously with timeout.
        
        Args:
            stage_id: Stage identifier
            *args: Positional arguments for the stage
            timeout: Timeout in seconds
            **kwargs: Keyword arguments for the stage
            
        Returns:
            Stage processing results
            
        Raises:
            TimeoutError: If processing exceeds the timeout
            Exception: Any exception raised during processing
        """
        # Get the default model for this stage
        model = get_default_model_for_stage_instance(stage_id)
        
        # Use the first interface method that matches the stage
        method_name = None
        if stage_id == "query_processor" and hasattr(model, "process_query"):
            method_name = "process_query"
        elif stage_id == "semantic_atdb" and hasattr(model, "transform_query"):
            method_name = "transform_query"
        elif stage_id == "domain_knowledge" and hasattr(model, "extract_knowledge"):
            method_name = "extract_knowledge"
        elif stage_id == "reasoning" and hasattr(model, "reason"):
            method_name = "reason"
        elif stage_id == "solution_generation" and hasattr(model, "generate_candidates"):
            method_name = "generate_candidates"
        elif stage_id == "response_scoring" and hasattr(model, "score_responses"):
            method_name = "score_responses"
        elif stage_id == "ensemble_diversification" and hasattr(model, "diversify"):
            method_name = "diversify"
        elif stage_id == "threshold_verification" and hasattr(model, "verify"):
            method_name = "verify"
        else:
            # Generic fallback
            method_name = "process"
        
        if not hasattr(model, method_name):
            raise ValueError(f"Model {model.model_id} does not have method {method_name}")
        
        # Get the method
        method = getattr(model, method_name)
        
        # Execute with timeout
        if timeout:
            try:
                # Run in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                result = await asyncio.wait_for(
                    loop.run_in_executor(self._executor, method, *args, **kwargs),
                    timeout=timeout
                )
                return result
            except asyncio.TimeoutError:
                logger.warning(f"Timeout ({timeout}s) exceeded for stage {stage_id}")
                raise TimeoutError(f"Processing for stage {stage_id} timed out after {timeout} seconds")
        else:
            # No timeout, just run
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(self._executor, method, *args, **kwargs)
    
    async def _process_with_specific_model_async(self, stage_id: str, model_id: str, 
                                              *args, timeout: Optional[int] = None, **kwargs):
        """
        Process a stage with a specific model asynchronously.
        
        Args:
            stage_id: Stage identifier
            model_id: Model identifier
            *args: Positional arguments for the stage
            timeout: Timeout in seconds
            **kwargs: Keyword arguments for the stage
            
        Returns:
            Stage processing results
            
        Raises:
            TimeoutError: If processing exceeds the timeout
            Exception: Any exception raised during processing
        """
        # Get the specified model
        model = get_model(model_id)
        
        # Use the first interface method that matches the stage (same as _process_stage_async)
        method_name = None
        if stage_id == "query_processor" and hasattr(model, "process_query"):
            method_name = "process_query"
        elif stage_id == "semantic_atdb" and hasattr(model, "transform_query"):
            method_name = "transform_query"
        elif stage_id == "domain_knowledge" and hasattr(model, "extract_knowledge"):
            method_name = "extract_knowledge"
        elif stage_id == "reasoning" and hasattr(model, "reason"):
            method_name = "reason"
        elif stage_id == "solution_generation" and hasattr(model, "generate_candidates"):
            method_name = "generate_candidates"
        elif stage_id == "response_scoring" and hasattr(model, "score_responses"):
            method_name = "score_responses"
        elif stage_id == "ensemble_diversification" and hasattr(model, "diversify"):
            method_name = "diversify"
        elif stage_id == "threshold_verification" and hasattr(model, "verify"):
            method_name = "verify"
        else:
            # Generic fallback
            method_name = "process"
        
        if not hasattr(model, method_name):
            raise ValueError(f"Model {model.model_id} does not have method {method_name}")
        
        # Get the method
        method = getattr(model, method_name)
        
        # Execute with timeout
        if timeout:
            try:
                # Run in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                result = await asyncio.wait_for(
                    loop.run_in_executor(self._executor, method, *args, **kwargs),
                    timeout=timeout
                )
                return result
            except asyncio.TimeoutError:
                logger.warning(f"Timeout ({timeout}s) exceeded for model {model_id} in stage {stage_id}")
                raise TimeoutError(f"Processing for model {model_id} in stage {stage_id} timed out after {timeout} seconds")
        else:
            # No timeout, just run
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(self._executor, method, *args, **kwargs)
    
    def _prepare_response(self, session_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare the final response from the processing results.
        
        Args:
            session_id: Session identifier
            context: Session context
            
        Returns:
            Final response
        """
        # Get all stage outputs
        outputs = self.working_memory.get_all_stage_outputs(session_id)
        
        # Get the verified solutions from the final stage
        verification_result = outputs.get("threshold_verification", {})
        diversification_result = outputs.get("ensemble_diversification", {})
        
        # Get passing solutions
        solutions = []
        if "verified_solutions" in verification_result:
            solutions = verification_result["verified_solutions"]
        elif "diverse_solutions" in diversification_result:
            solutions = diversification_result["diverse_solutions"]
        elif "candidates" in outputs.get("solution_generation", {}):
            # Fallback to raw candidates
            solutions = outputs.get("solution_generation", {}).get("candidates", [])
        
        # Get scores if available
        scores = outputs.get("response_scoring", {}).get("scores", [])
        
        # Get the raw query and processed query
        raw_query = context.get("original_query", "")
        processed_query = outputs.get("query_processor", {})
        
        # Get knowledge context
        knowledge = outputs.get("domain_knowledge", {})
        
        # Prepare the final response
        response = {
            "session_id": session_id,
            "query": raw_query,
            "processed_query": processed_query,
            "solutions": solutions,
            "knowledge_context": knowledge,
            "metadata": {
                "processing_stages": list(outputs.keys()),
                "timestamp": time.time(),
                "model_versions": self._get_model_versions()
            }
        }
        
        # Add scores if available
        if scores:
            response["solution_scores"] = scores
        
        return response
    
    def _get_model_versions(self) -> Dict[str, str]:
        """
        Get version information for all models in the pipeline.
        
        Returns:
            Dictionary of model versions
        """
        versions = {}
        
        # This would be populated with actual version information
        # For now, just return placeholder
        
        return {
            "phi3": "microsoft/Phi-3-mini-4k-instruct",
            "mixtral": "mistralai/Mixtral-8x22B-Instruct-v0.1",
            "biomedlm": "stanford-crfm/BioMedLM-2.7B",
            "bge-reranker": "BAAI/bge-reranker-base"
        } 