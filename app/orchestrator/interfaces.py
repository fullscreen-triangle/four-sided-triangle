"""
Interface definitions for the Four-Sided Triangle orchestration system.

This module provides interface classes that define the contracts between 
the metacognitive orchestrator and the various components of the system,
including pipeline stages, prompt generators, and output evaluators.
"""

from typing import Dict, Any, List, Optional, Protocol, runtime_checkable
from abc import ABC, abstractmethod

@runtime_checkable
class PipelineStage(Protocol):
    """Protocol defining the interface for pipeline stages."""
    
    stage_id: str
    
    def process(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data according to the stage's responsibility.
        
        Args:
            prompt: The generated prompt for this stage
            context: The current session context
            
        Returns:
            The processed output
        """
        ...
    
    def refine(self, refinement_prompt: str, context: Dict[str, Any], previous_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Refine previous output based on feedback.
        
        Args:
            refinement_prompt: Prompt specifically for refinement
            context: The current session context
            previous_output: The output from the previous processing attempt
            
        Returns:
            The refined output
        """
        ...
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """
        Return metrics about the stage's processing.
        
        Returns:
            Dictionary of metrics
        """
        ...

class AbstractPipelineStage(ABC):
    """
    Abstract base class implementing the PipelineStage protocol.
    
    Pipeline stages can inherit from this class to get a default implementation
    of the protocol with proper abstract method definitions.
    """
    
    def __init__(self):
        """Initialize the pipeline stage."""
        self._metrics = {}
    
    @property
    @abstractmethod
    def stage_id(self) -> str:
        """Unique identifier for this pipeline stage."""
        pass
    
    @abstractmethod
    def process(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data according to the stage's responsibility.
        
        Args:
            prompt: The generated prompt for this stage
            context: The current session context
            
        Returns:
            The processed output
        """
        pass
    
    def refine(self, refinement_prompt: str, context: Dict[str, Any], previous_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Refine previous output based on feedback.
        
        Default implementation simply calls process with the refinement prompt.
        Subclasses should override this for more sophisticated refinement.
        
        Args:
            refinement_prompt: Prompt specifically for refinement
            context: The current session context
            previous_output: The output from the previous processing attempt
            
        Returns:
            The refined output
        """
        return self.process(refinement_prompt, context)
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """
        Return metrics about the stage's processing.
        
        Returns:
            Dictionary of metrics
        """
        return self._metrics
    
    def _update_metrics(self, metrics_update: Dict[str, Any]) -> None:
        """
        Update the stage's metrics.
        
        Args:
            metrics_update: Metrics to update or add
        """
        self._metrics.update(metrics_update)

class WorkingMemoryInterface(Protocol):
    """Protocol defining the working memory interface."""
    
    def create_session(self, session_id: str, original_query: str, user_id: Optional[str] = None, 
                       metadata: Optional[Dict[str, Any]] = None) -> None:
        """Create a new session in working memory."""
        ...
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get the full context for a session."""
        ...
    
    def store_stage_output(self, session_id: str, stage_id: str, output: Dict[str, Any]) -> None:
        """Store output from a pipeline stage."""
        ...
    
    def get_stage_output(self, session_id: str, stage_id: str) -> Optional[Dict[str, Any]]:
        """Get output from a specific pipeline stage."""
        ...
    
    def get_all_stage_outputs(self, session_id: str) -> Dict[str, Dict[str, Any]]:
        """Get all stage outputs for a session."""
        ...
    
    def add_contextual_insight(self, session_id: str, source: str, insight: Dict[str, Any]) -> None:
        """Add contextual insights to the session."""
        ...
    
    def get_session_metadata(self, session_id: str) -> Dict[str, Any]:
        """Get metadata for a session."""
        ...
    
    def update_session_metadata(self, session_id: str, metadata_update: Dict[str, Any]) -> None:
        """Update metadata for a session."""
        ...
    
    def cleanup_session(self, session_id: str) -> None:
        """Clean up session data."""
        ...

class PromptGeneratorInterface(Protocol):
    """Protocol defining the prompt generator interface."""
    
    def generate_prompt(self, stage_id: str, context: Dict[str, Any]) -> str:
        """Generate a prompt for a pipeline stage."""
        ...
    
    def generate_refinement_prompt(self, stage_id: str, context: Dict[str, Any], 
                                  feedback: Dict[str, Any]) -> str:
        """Generate a refinement prompt for a pipeline stage."""
        ...

class ProcessMonitorInterface(Protocol):
    """Protocol defining the process monitor interface."""
    
    def evaluate_output(self, stage_id: str, output: Dict[str, Any], 
                        context: Dict[str, Any]) -> tuple[bool, Dict[str, float], Dict[str, Any]]:
        """Evaluate the quality of a stage's output."""
        ...
    
    def should_refine(self, session_id: str, stage_id: str, quality_scores: Dict[str, float], 
                     context: Dict[str, Any]) -> tuple[bool, str]:
        """Determine if refinement is necessary."""
        ...
    
    def record_refinement_result(self, session_id: str, stage_id: str, 
                                original_scores: Dict[str, float], 
                                refined_scores: Dict[str, float]) -> Dict[str, Any]:
        """Record the results of a refinement iteration."""
        ...
    
    def reset_refinement_history(self, session_id: Optional[str] = None) -> None:
        """Reset refinement history for a session."""
        ...

class PipelineStageInterface(ABC):
    """
    Interface for pipeline stages that process inputs and produce outputs.
    
    Each stage takes inputs from previous stages along with a generated prompt,
    and produces an output that can be evaluated and potentially refined.
    """
    
    @abstractmethod
    def process(self, inputs: Dict[str, Any], prompt: str) -> Any:
        """
        Process inputs using the provided prompt.
        
        Args:
            inputs: Dictionary containing input data and context
            prompt: Generated prompt for this stage processing
            
        Returns:
            Processing result in a format appropriate for the stage
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Report capabilities of this pipeline stage.
        
        Returns:
            Dictionary of capability information
        """
        pass

class PromptGeneratorInterface(ABC):
    """
    Interface for prompt generators that create tailored prompts for pipeline stages.
    
    Prompt generators create context-aware prompts for each stage, including
    refinement prompts when a stage's output needs improvement.
    """
    
    @abstractmethod
    def generate_stage_prompt(self, stage_id: str, context: Dict[str, Any]) -> str:
        """
        Generate an initial prompt for a pipeline stage.
        
        Args:
            stage_id: Identifier for the stage
            context: Current working memory context
            
        Returns:
            Generated prompt string
        """
        pass
    
    @abstractmethod
    def generate_refinement_prompt(self, stage_id: str, context: Dict[str, Any], 
                                  evaluation: Dict[str, Any], iteration: int) -> str:
        """
        Generate a refinement prompt for a pipeline stage.
        
        Args:
            stage_id: Identifier for the stage
            context: Current working memory context
            evaluation: Evaluation results from previous iteration
            iteration: Current refinement iteration number
            
        Returns:
            Generated refinement prompt string
        """
        pass

class OutputEvaluatorInterface(ABC):
    """
    Interface for output evaluators that assess stage outputs.
    
    Output evaluators determine if a stage's output meets quality criteria
    and whether it needs refinement.
    """
    
    @abstractmethod
    def evaluate_output(self, stage_id: str, output: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate the output of a pipeline stage.
        
        Args:
            stage_id: Identifier for the stage
            output: Stage output to evaluate
            context: Current working memory context
            
        Returns:
            Evaluation results including at least:
            - passed: Whether the output passed evaluation
            - score: Overall quality score (0-1)
            - needs_refinement: Whether the output needs refinement
            - issues: List of identified issues
            - strengths: List of identified strengths
        """
        pass

class WorkingMemoryInterface(ABC):
    """
    Interface for working memory that stores query processing state.
    
    Working memory maintains the state of query processing across stages,
    including intermediate outputs, evaluations, and other context.
    """
    
    @abstractmethod
    def get_memory(self, query_id: str) -> Dict[str, Any]:
        """
        Retrieve working memory for a specific query.
        
        Args:
            query_id: Unique identifier for the query
            
        Returns:
            Current working memory context
        """
        pass
    
    @abstractmethod
    def set_memory(self, query_id: str, context: Dict[str, Any]) -> None:
        """
        Set the entire working memory for a query.
        
        Args:
            query_id: Unique identifier for the query
            context: New working memory context
        """
        pass
    
    @abstractmethod
    def update_memory(self, query_id: str, context: Dict[str, Any]) -> None:
        """
        Update working memory for a query.
        
        Args:
            query_id: Unique identifier for the query
            context: Updated working memory context
        """
        pass
    
    @abstractmethod
    def clear_memory(self, query_id: str) -> None:
        """
        Clear working memory for a query.
        
        Args:
            query_id: Unique identifier for the query
        """
        pass

class OrchestratorInterface(ABC):
    """
    Interface for the metacognitive orchestrator.
    
    The orchestrator coordinates pipeline stages, manages working memory,
    evaluates outputs, and dynamically adjusts the pipeline.
    """
    
    @abstractmethod
    def register_stage(self, stage_id: str, stage: PipelineStageInterface) -> None:
        """
        Register a pipeline stage with the orchestrator.
        
        Args:
            stage_id: Unique identifier for the stage
            stage: Stage implementation object
        """
        pass
    
    @abstractmethod
    def configure_pipeline(self, config: List[Dict[str, Any]]) -> None:
        """
        Configure the pipeline execution order and dependencies.
        
        Args:
            config: List of stage configurations with dependencies and settings
        """
        pass
    
    @abstractmethod
    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a query through the pipeline.
        
        Args:
            query: The user's query
            context: Additional context to include in working memory
            
        Returns:
            Processing results from the pipeline
        """
        pass
