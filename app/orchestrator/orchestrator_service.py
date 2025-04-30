"""
Metacognitive Orchestrator - Main service for pipeline coordination and control.

The Orchestrator is the central component of the Four-Sided Triangle system,
responsible for coordinating pipeline stages, managing working memory,
generating dynamic prompts, monitoring output quality, and adapting the pipeline
based on query complexity and processing requirements.
"""

import logging
import uuid
import time
from typing import Dict, Any, List, Optional, Tuple, Union, Type
import importlib
import inspect

from .interfaces import PipelineStage
from .working_memory import working_memory
from .prompt_generator import prompt_generator
from .process_monitor import process_monitor

logger = logging.getLogger(__name__)

class OrchestratorService:
    """
    The Metacognitive Orchestrator service coordinates the entire knowledge extraction pipeline.
    
    Key responsibilities:
    1. Pipeline initialization and stage registration
    2. Session management
    3. Stage execution coordination
    4. Adaptive processing based on query complexity
    5. Output quality monitoring and refinement
    6. Dynamic prompt generation
    7. Working memory management
    """
    
    def __init__(self):
        """Initialize the orchestrator service."""
        # Dictionary of registered pipeline stages by stage_id
        self.pipeline_stages: Dict[str, Type[PipelineStage]] = {}
        
        # Active instance cache for initialized pipeline stages
        self.stage_instances: Dict[str, PipelineStage] = {}
        
        # Default pipeline execution sequence
        self.default_pipeline_sequence = [
            "query_processor",
            "semantic_atdb",
            "domain_knowledge",
            "reasoning_optimization",
            "solution_generation",
            "response_scoring",
            "response_comparison"
        ]
        
        # Custom pipeline sequences for special query types
        self.specialized_pipelines = {
            "simple_factual": ["query_processor", "semantic_atdb", "solution_generation"],
            "complex_domain": self.default_pipeline_sequence,
            "optimization": ["query_processor", "semantic_atdb", "domain_knowledge", 
                           "reasoning_optimization", "solution_generation"]
        }
        
        # Pipeline execution metrics
        self.execution_metrics = {}
        
        logger.info("Orchestrator service initialized")
    
    def register_pipeline_stage(self, stage_id: str, stage_class: Type[PipelineStage]) -> None:
        """
        Register a pipeline stage with the orchestrator.
        
        Args:
            stage_id: Unique identifier for the stage
            stage_class: The PipelineStage class to register
        """
        if stage_id in self.pipeline_stages:
            logger.warning(f"Overwriting existing pipeline stage: {stage_id}")
        
        # Verify that the class is a subclass of PipelineStage
        if not issubclass(stage_class, PipelineStage):
            raise ValueError(f"Stage class must implement PipelineStage interface: {stage_class.__name__}")
        
        self.pipeline_stages[stage_id] = stage_class
        logger.info(f"Registered pipeline stage: {stage_id} ({stage_class.__name__})")
    
    def discover_pipeline_stages(self, module_paths: List[str]) -> None:
        """
        Automatically discover and register pipeline stages from specified modules.
        
        Args:
            module_paths: List of module paths to search for pipeline stages
        """
        for module_path in module_paths:
            try:
                module = importlib.import_module(module_path)
                
                # Find all classes that implement PipelineStage
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, PipelineStage) and 
                        obj != PipelineStage):
                        
                        # Get stage_id from class
                        stage_id = getattr(obj, "stage_id", None)
                        if stage_id:
                            self.register_pipeline_stage(stage_id, obj)
                
                logger.info(f"Discovered pipeline stages from module: {module_path}")
            
            except (ImportError, AttributeError) as e:
                logger.error(f"Failed to import module {module_path}: {str(e)}")
    
    def get_stage_instance(self, stage_id: str) -> PipelineStage:
        """
        Get an instance of a registered pipeline stage.
        
        Args:
            stage_id: Unique identifier for the stage
            
        Returns:
            Instance of the requested pipeline stage
            
        Raises:
            ValueError: If the stage_id is not registered
        """
        if stage_id not in self.pipeline_stages:
            raise ValueError(f"Unknown pipeline stage: {stage_id}")
        
        # Check if we already have an instance
        if stage_id not in self.stage_instances:
            # Create a new instance
            stage_class = self.pipeline_stages[stage_id]
            self.stage_instances[stage_id] = stage_class()
            logger.debug(f"Created new instance of {stage_id} stage")
        
        return self.stage_instances[stage_id]
    
    def create_session(self, query: str, user_id: Optional[str] = None) -> str:
        """
        Create a new processing session.
        
        Args:
            query: The user's original query
            user_id: Optional user identifier for personalization
            
        Returns:
            Unique session identifier
        """
        # Generate a unique session ID
        session_id = str(uuid.uuid4())
        
        # Initialize session in working memory
        working_memory.create_session(
            session_id=session_id,
            original_query=query,
            user_id=user_id,
            metadata={
                "created_at": time.time(),
                "status": "initialized"
            }
        )
        
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def determine_pipeline_sequence(self, session_id: str) -> List[str]:
        """
        Determine the appropriate pipeline sequence for a query.
        
        Args:
            session_id: The unique session identifier
            
        Returns:
            List of stage_ids in execution order
        """
        # Get query processor output
        query_processor_output = working_memory.get_stage_output(session_id, "query_processor")
        
        # Default to standard pipeline if no query processor output
        if not query_processor_output:
            return self.default_pipeline_sequence
        
        # Extract query type if available
        query_type = query_processor_output.get("query_type", "complex_domain")
        
        # Use specialized pipeline if available, otherwise default
        pipeline_sequence = self.specialized_pipelines.get(query_type, self.default_pipeline_sequence)
        
        logger.info(f"Determined pipeline sequence for {session_id}: {query_type} -> {pipeline_sequence}")
        return pipeline_sequence
    
    def process_query(self, query: str, user_id: Optional[str] = None, custom_pipeline: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Process a query through the pipeline.
        
        Args:
            query: The user's original query
            user_id: Optional user identifier for personalization
            custom_pipeline: Optional custom pipeline sequence
            
        Returns:
            Final result from the pipeline
        """
        # Create a new session
        session_id = self.create_session(query, user_id)
        
        # Process the query in this session
        result = self.process_session(session_id, custom_pipeline)
        
        return result
    
    def process_session(self, session_id: str, custom_pipeline: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Process an existing session through the pipeline.
        
        Args:
            session_id: The unique session identifier
            custom_pipeline: Optional custom pipeline sequence
            
        Returns:
            Final result from the pipeline
        """
        # Update session status
        working_memory.update_session_metadata(session_id, {"status": "processing"})
        
        # Start with query processor stage
        query_processor_stage = self.get_stage_instance("query_processor")
        context = working_memory.get_session_context(session_id)
        
        # Generate prompt for query processor
        prompt = prompt_generator.generate_prompt("query_processor", context)
        
        # Process the query
        query_result = query_processor_stage.process(prompt, context)
        
        # Store the result
        working_memory.store_stage_output(session_id, "query_processor", query_result)
        
        # Add metadata
        working_memory.add_contextual_insight(
            session_id,
            "query_processor",
            {
                "processing_time": query_processor_stage.metrics.get("processing_time", 0),
                "confidence": query_result.get("confidence", 0.7)
            }
        )
        
        # Determine the pipeline sequence
        pipeline_sequence = custom_pipeline
        if not pipeline_sequence:
            pipeline_sequence = self.determine_pipeline_sequence(session_id)
        
        # Execute the pipeline stages (skip query_processor as we've already done it)
        final_result = query_result
        for stage_id in pipeline_sequence:
            if stage_id == "query_processor":
                continue
            
            # Execute this stage
            final_result = self._execute_stage(session_id, stage_id)
            
            # Check if we should stop processing
            if not final_result:
                break
        
        # Update session status
        working_memory.update_session_metadata(session_id, {"status": "completed"})
        
        return final_result
    
    def _execute_stage(self, session_id: str, stage_id: str) -> Dict[str, Any]:
        """
        Execute a single pipeline stage with quality monitoring and refinement.
        
        Args:
            session_id: The unique session identifier
            stage_id: ID of the stage to execute
            
        Returns:
            Stage output after processing and potential refinement
        """
        logger.info(f"Executing stage {stage_id} for session {session_id}")
        
        # Get stage instance
        try:
            stage = self.get_stage_instance(stage_id)
        except ValueError as e:
            logger.error(f"Cannot execute stage {stage_id}: {str(e)}")
            return None
        
        # Get current context from working memory
        context = working_memory.get_session_context(session_id)
        
        # Generate prompt for this stage
        prompt = prompt_generator.generate_prompt(stage_id, context)
        
        # Execute the stage
        start_time = time.time()
        result = stage.process(prompt, context)
        processing_time = time.time() - start_time
        
        # Evaluate output quality
        is_acceptable, quality_scores, feedback = process_monitor.evaluate_output(
            stage_id, result, context
        )
        
        # Record quality metrics as contextual insights
        working_memory.add_contextual_insight(
            session_id,
            stage_id,
            {
                "processing_time": processing_time,
                "quality_scores": quality_scores,
                "quality_feedback": feedback
            }
        )
        
        # If output quality is not acceptable, consider refinement
        if not is_acceptable:
            should_refine, reason = process_monitor.should_refine(
                session_id, stage_id, quality_scores, context
            )
            
            if should_refine:
                logger.info(f"Initiating refinement for {stage_id} in session {session_id}: {reason}")
                
                # Store original result for comparison
                original_result = result
                original_scores = quality_scores
                
                # Generate refinement prompt
                refinement_prompt = prompt_generator.generate_refinement_prompt(
                    stage_id, context, feedback
                )
                
                # Execute refinement
                result = stage.refine(refinement_prompt, context, original_result)
                
                # Re-evaluate output quality
                is_acceptable, quality_scores, feedback = process_monitor.evaluate_output(
                    stage_id, result, context
                )
                
                # Record refinement results
                refinement_record = process_monitor.record_refinement_result(
                    session_id, stage_id, original_scores, quality_scores
                )
                
                # Add refinement insights
                working_memory.add_contextual_insight(
                    session_id,
                    stage_id,
                    {
                        "refinement": refinement_record,
                        "refined_quality_scores": quality_scores,
                        "refined_feedback": feedback
                    }
                )
        
        # Store the final result
        working_memory.store_stage_output(session_id, stage_id, result)
        
        return result
    
    def get_session_results(self, session_id: str) -> Dict[str, Any]:
        """
        Get all results from a session.
        
        Args:
            session_id: The unique session identifier
            
        Returns:
            Dictionary containing all stage outputs and session context
        """
        context = working_memory.get_session_context(session_id)
        stage_outputs = working_memory.get_all_stage_outputs(session_id)
        
        return {
            "session_id": session_id,
            "context": context,
            "stage_outputs": stage_outputs,
            "metadata": working_memory.get_session_metadata(session_id)
        }
    
    def cleanup_session(self, session_id: str) -> None:
        """
        Clean up session data.
        
        Args:
            session_id: The unique session identifier to clean up
        """
        working_memory.cleanup_session(session_id)
        process_monitor.reset_refinement_history(session_id)
        logger.info(f"Cleaned up session {session_id}")

# Singleton instance for application-wide use
orchestrator = OrchestratorService() 