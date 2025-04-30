"""
Orchestrator implementation for the Four-Sided Triangle system.

This module provides a default implementation of the orchestrator that
coordinates pipeline stages, manages working memory, and processes queries.
"""

import logging
import time
import uuid
from typing import Dict, Any, List, Optional, Type

from app.orchestrator.interfaces import (
    OrchestratorInterface,
    PipelineStageInterface,
    WorkingMemoryInterface
)
from app.orchestrator.working_memory import working_memory
from app.orchestrator.prompt_generator import prompt_generator

logger = logging.getLogger(__name__)

class DefaultOrchestrator(OrchestratorInterface):
    """
    Default implementation of the orchestrator for the Four-Sided Triangle system.
    
    This class coordinates the execution of pipeline stages, manages working memory,
    and processes user queries through the pipeline.
    """
    
    def __init__(self):
        """Initialize the orchestrator."""
        # Registry of pipeline stages
        self._stages: Dict[str, PipelineStageInterface] = {}
        
        # Pipeline configuration (execution order and dependencies)
        self._pipeline_config: List[Dict[str, Any]] = []
        
        # Default maximum refinement iterations
        self.max_refinement_iterations = 2
        
        logger.info("DefaultOrchestrator initialized")
    
    def register_stage(self, stage_id: str, stage: PipelineStageInterface) -> None:
        """
        Register a pipeline stage with the orchestrator.
        
        Args:
            stage_id: Unique identifier for the stage
            stage: Stage implementation object
        """
        if stage_id in self._stages:
            logger.warning("Overwriting existing pipeline stage: %s", stage_id)
        
        self._stages[stage_id] = stage
        logger.info("Registered pipeline stage: %s", stage_id)
    
    def configure_pipeline(self, config: List[Dict[str, Any]]) -> None:
        """
        Configure the pipeline execution order and dependencies.
        
        Args:
            config: List of stage configurations with dependencies and settings
                Each item should contain at least:
                - 'id': Stage identifier
                - 'depends_on': List of stage IDs this stage depends on (optional)
                - 'optional': Whether this stage can be skipped (optional)
        """
        # Validate configuration
        for stage_config in config:
            stage_id = stage_config.get('id')
            if not stage_id:
                raise ValueError("Stage configuration missing 'id' field")
            
            if stage_id not in self._stages:
                raise ValueError(f"Unknown stage ID in pipeline configuration: {stage_id}")
        
        self._pipeline_config = config
        logger.info("Pipeline configured with %d stages", len(config))
    
    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a query through the pipeline.
        
        Args:
            query: The user's query
            context: Additional context to include in working memory
            
        Returns:
            Processing results from the pipeline
        """
        start_time = time.time()
        query_id = self._create_query_id()
        logger.info("Processing query: %s (ID: %s)", query[:50], query_id)
        
        # Initialize working memory
        self._initialize_memory(query_id, query, context)
        
        try:
            # Execute pipeline stages in order
            final_output = self._execute_pipeline(query_id)
            
            # Prepare final result
            result = {
                "success": True,
                "query_id": query_id,
                "final_output": final_output,
                "execution_time": time.time() - start_time
            }
            
            # Add execution metadata
            memory = working_memory.get_memory(query_id)
            result["stage_outputs"] = memory.get("stage_outputs", {})
            result["metadata"] = {
                "execution_time": time.time() - start_time,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error("Error processing query %s: %s", query_id, str(e))
            result = {
                "success": False,
                "query_id": query_id,
                "error": str(e),
                "execution_time": time.time() - start_time
            }
        
        return result
    
    def _create_query_id(self) -> str:
        """
        Create a unique query ID.
        
        Returns:
            Unique query identifier
        """
        return str(uuid.uuid4())
    
    def _initialize_memory(self, query_id: str, query: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize working memory for a query.
        
        Args:
            query_id: Unique identifier for the query
            query: The user's query
            context: Additional context information
        """
        memory_context = {
            "query_id": query_id,
            "original_query": query,
            "timestamp": time.time(),
            "stage_outputs": {},
            "stage_prompts": {}
        }
        
        # Add any additional context
        if context:
            for key, value in context.items():
                if key not in memory_context:
                    memory_context[key] = value
        
        # Initialize working memory
        working_memory.set_memory(query_id, memory_context)
        logger.debug("Initialized working memory for query %s", query_id)
    
    def _execute_pipeline(self, query_id: str) -> Dict[str, Any]:
        """
        Execute the pipeline stages in order.
        
        Args:
            query_id: Unique identifier for the query
            
        Returns:
            Final output from the last stage
        """
        memory = working_memory.get_memory(query_id)
        executed_stages = []
        
        for stage_config in self._pipeline_config:
            stage_id = stage_config['id']
            depends_on = stage_config.get('depends_on', [])
            optional = stage_config.get('optional', False)
            
            # Check if dependencies have been executed
            if not all(dep in executed_stages for dep in depends_on):
                if optional:
                    logger.warning("Skipping optional stage %s due to missing dependencies", stage_id)
                    continue
                else:
                    raise ValueError(f"Cannot execute stage {stage_id} - dependencies not satisfied")
            
            # Execute the stage
            stage_output = self._execute_stage(query_id, stage_id)
            
            if stage_output:
                executed_stages.append(stage_id)
            elif not optional:
                raise RuntimeError(f"Critical stage {stage_id} failed to execute successfully")
            else:
                logger.warning("Optional stage %s failed but pipeline will continue", stage_id)
        
        # Get the final output from the last non-optional stage executed
        memory = working_memory.get_memory(query_id)
        stage_outputs = memory.get("stage_outputs", {})
        
        if not stage_outputs:
            raise RuntimeError("No stage outputs produced during pipeline execution")
        
        # Find the last stage in the pipeline that was executed
        final_stage_id = None
        for stage_config in reversed(self._pipeline_config):
            stage_id = stage_config['id']
            if stage_id in executed_stages:
                final_stage_id = stage_id
                break
        
        if not final_stage_id:
            raise RuntimeError("No pipeline stages were executed successfully")
        
        return stage_outputs.get(final_stage_id, {})
    
    def _execute_stage(self, query_id: str, stage_id: str) -> Dict[str, Any]:
        """
        Execute a single pipeline stage.
        
        Args:
            query_id: Unique identifier for the query
            stage_id: Identifier for the stage to execute
            
        Returns:
            Stage output or None if the stage failed
        """
        logger.info("Executing stage %s for query %s", stage_id, query_id)
        stage = self._stages.get(stage_id)
        
        if not stage:
            raise ValueError(f"Stage {stage_id} not found in registry")
        
        memory = working_memory.get_memory(query_id)
        
        # Generate prompt for this stage
        prompt = prompt_generator.generate_stage_prompt(
            stage_id, 
            memory,
            {"stage_id": stage_id}
        )
        
        # Store the prompt
        if "stage_prompts" not in memory:
            memory["stage_prompts"] = {}
        
        memory["stage_prompts"][stage_id] = prompt
        working_memory.update_memory(query_id, memory)
        
        # Process the stage
        try:
            start_time = time.time()
            stage_input = self._prepare_stage_input(query_id, stage_id)
            stage_output = stage.process(stage_input, prompt)
            processing_time = time.time() - start_time
            
            # Add processing metadata
            if isinstance(stage_output, dict):
                if "metadata" not in stage_output:
                    stage_output["metadata"] = {}
                
                stage_output["metadata"].update({
                    "processing_time": processing_time,
                    "stage_id": stage_id,
                    "timestamp": time.time()
                })
            
            # Store the output
            memory = working_memory.get_memory(query_id)
            if "stage_outputs" not in memory:
                memory["stage_outputs"] = {}
            
            memory["stage_outputs"][stage_id] = stage_output
            working_memory.update_memory(query_id, memory)
            
            logger.info("Stage %s completed in %.2f seconds", stage_id, processing_time)
            return stage_output
            
        except Exception as e:
            logger.error("Error executing stage %s: %s", stage_id, str(e))
            return None
    
    def _prepare_stage_input(self, query_id: str, stage_id: str) -> Dict[str, Any]:
        """
        Prepare input for a stage based on working memory.
        
        Args:
            query_id: Unique identifier for the query
            stage_id: Identifier for the stage
            
        Returns:
            Input data for the stage
        """
        memory = working_memory.get_memory(query_id)
        
        # Find stage dependencies
        stage_config = next((s for s in self._pipeline_config if s['id'] == stage_id), None)
        depends_on = stage_config.get('depends_on', []) if stage_config else []
        
        # Prepare input with original query and outputs from dependencies
        stage_input = {
            "query": memory.get("original_query", ""),
            "query_id": query_id
        }
        
        # Add outputs from dependencies
        stage_outputs = memory.get("stage_outputs", {})
        for dep_stage in depends_on:
            if dep_stage in stage_outputs:
                stage_input[dep_stage] = stage_outputs[dep_stage]
        
        return stage_input
    
    def get_query_result(self, query_id: str) -> Dict[str, Any]:
        """
        Get the processing result for a query.
        
        Args:
            query_id: Unique identifier for the query
            
        Returns:
            Query processing result
        """
        memory = working_memory.get_memory(query_id)
        
        if not memory:
            return {"error": f"No memory found for query ID: {query_id}"}
        
        # Collect outputs from all stages
        stage_outputs = memory.get("stage_outputs", {})
        
        # Find the final stage in the pipeline that was executed
        final_stage_id = None
        for stage_config in reversed(self._pipeline_config):
            stage_id = stage_config['id']
            if stage_id in stage_outputs:
                final_stage_id = stage_id
                break
        
        # Prepare result
        result = {
            "query_id": query_id,
            "original_query": memory.get("original_query", ""),
            "stage_outputs": stage_outputs,
            "timestamp": memory.get("timestamp", time.time())
        }
        
        if final_stage_id:
            result["final_output"] = stage_outputs.get(final_stage_id, {})
        
        return result
    
    def clear_query(self, query_id: str) -> None:
        """
        Clear the working memory for a query.
        
        Args:
            query_id: Unique identifier for the query
        """
        working_memory.clear_memory(query_id)
        logger.info("Cleared working memory for query %s", query_id)

# Global singleton instance
orchestrator = DefaultOrchestrator() 