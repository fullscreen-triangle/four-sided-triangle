"""
Four-Sided Triangle Orchestrator Package.

This package provides orchestration components for the Four-Sided Triangle system,
including the 8-stage pipeline specialized orchestrator.
"""

from app.orchestrator.interfaces import (
    PipelineStage, AbstractPipelineStage, WorkingMemoryInterface,
    PromptGeneratorInterface, ProcessMonitorInterface
)

from app.orchestrator.working_memory import WorkingMemory
from app.orchestrator.pipeline_stage import PipelineStageManager
from app.orchestrator.prompt_generator import PromptGenerator
from app.orchestrator.output_evaluator import OutputEvaluator
from app.orchestrator.process_monitor import ProcessMonitor
from app.orchestrator.orchestrator import Orchestrator
from app.orchestrator.metacognitive_orchestrator import MetacognitiveOrchestrator
from app.orchestrator.specialized_orchestrator import SpecializedOrchestrator

__all__ = [
    # Interfaces
    'PipelineStage', 'AbstractPipelineStage', 'WorkingMemoryInterface',
    'PromptGeneratorInterface', 'ProcessMonitorInterface',
    
    # Core components
    'WorkingMemory', 'PipelineStageManager', 'PromptGenerator',
    'OutputEvaluator', 'ProcessMonitor',
    
    # Orchestrators
    'Orchestrator', 'MetacognitiveOrchestrator', 'SpecializedOrchestrator'
]
