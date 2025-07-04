"""
Turbulance DSL Orchestrator

This module orchestrates the execution of compiled Turbulance protocols through
the Four-Sided Triangle pipeline system. It handles:
- Protocol execution coordination
- Pipeline stage management
- Result collection and annotation
- Auxiliary file generation
- Error handling and recovery
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from .parser import TurbulanceParser, TurbulanceScript
from .compiler import TurbulanceCompiler, CompiledProtocol, ExecutionStep
from ..orchestrator.metacognitive_orchestrator import MetacognitiveOrchestrator
from ..core.stages.stage0_query_processor.query_processor_service import QueryProcessorService
from ..core.stages.stage1_semantic_atdb.semantic_atdb_service import SemanticAtdbService
from ..core.stages.stage2_domain_knowledge.domain_knowledge_service import DomainKnowledgeService
from ..core.stages.stage3_reasoning_optimization.reasoning_optimization_service import ReasoningOptimizationService
from ..core.stages.stage4_solution.solution_generation_service import SolutionGenerationService
from ..core.stages.stage5_scoring.response_scoring_service import ResponseScoringService
from ..core.stages.stage6_comparison.response_comparison_service import ResponseComparisonService
from ..core.stages.stage7_verification.threshold_verification_service import ThresholdVerificationService

logger = logging.getLogger(__name__)

@dataclass
class ExecutionResult:
    """Result of a single execution step"""
    step_id: str
    success: bool
    result: Dict[str, Any]
    execution_time: float
    error_message: Optional[str] = None

@dataclass
class ProtocolExecutionResult:
    """Result of complete protocol execution"""
    protocol_name: str
    success: bool
    execution_time: float
    step_results: List[ExecutionResult]
    annotated_script: str
    auxiliary_files: Dict[str, str]
    error_message: Optional[str] = None

class TurbulanceOrchestrator:
    """Orchestrates Turbulance protocol execution through Four-Sided Triangle pipeline"""
    
    def __init__(self, orchestrator: Optional[MetacognitiveOrchestrator] = None):
        self.parser = TurbulanceParser()
        self.compiler = TurbulanceCompiler()
        self.orchestrator = orchestrator or MetacognitiveOrchestrator()
        
        # Initialize pipeline services
        self.services = {
            "stage0_query_processor": QueryProcessorService(),
            "stage1_semantic_atdb": SemanticAtdbService(),
            "stage2_domain_knowledge": DomainKnowledgeService(),
            "stage3_reasoning_optimization": ReasoningOptimizationService(),
            "stage4_solution": SolutionGenerationService(),
            "stage5_scoring": ResponseScoringService(),
            "stage6_comparison": ResponseComparisonService(),
            "stage7_verification": ThresholdVerificationService()
        }
        
        # Execution statistics
        self.execution_stats = {
            "total_protocols": 0,
            "successful_protocols": 0,
            "failed_protocols": 0,
            "average_execution_time": 0.0
        }
        
    async def execute_protocol(self, script_content: str, protocol_name: str = "research_protocol") -> ProtocolExecutionResult:
        """Execute a complete Turbulance protocol"""
        start_time = time.time()
        
        try:
            logger.info(f"Starting execution of protocol: {protocol_name}")
            
            # Parse the script
            script = self.parser.parse_script(script_content, protocol_name)
            
            # Compile the protocol
            compiled_protocol = self.compiler.compile_protocol(script)
            
            # Execute the compiled protocol
            step_results = await self._execute_compiled_protocol(compiled_protocol)
            
            # Collect results
            results_dict = {result.step_id: result.result for result in step_results}
            
            # Annotate the script with results
            annotated_script = self.compiler.annotate_script_with_results(
                script_content, results_dict, compiled_protocol.annotation_map
            )
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Check if all steps succeeded
            success = all(result.success for result in step_results)
            
            # Update statistics
            self._update_execution_stats(success, execution_time)
            
            result = ProtocolExecutionResult(
                protocol_name=protocol_name,
                success=success,
                execution_time=execution_time,
                step_results=step_results,
                annotated_script=annotated_script,
                auxiliary_files=compiled_protocol.auxiliary_files
            )
            
            logger.info(f"Protocol execution completed: {protocol_name} (success: {success}, time: {execution_time:.2f}s)")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Protocol execution failed: {protocol_name} - {str(e)}")
            
            self._update_execution_stats(False, execution_time)
            
            return ProtocolExecutionResult(
                protocol_name=protocol_name,
                success=False,
                execution_time=execution_time,
                step_results=[],
                annotated_script=script_content,
                auxiliary_files={},
                error_message=str(e)
            )
    
    async def _execute_compiled_protocol(self, compiled_protocol: CompiledProtocol) -> List[ExecutionResult]:
        """Execute a compiled protocol through the pipeline"""
        results = []
        
        if compiled_protocol.execution_mode.value == "parallel":
            # Execute all steps in parallel
            results = await self._execute_parallel(compiled_protocol.execution_steps)
        elif compiled_protocol.execution_mode.value == "sequential":
            # Execute steps sequentially
            results = await self._execute_sequential(compiled_protocol.execution_steps)
        else:
            # Adaptive execution based on dependencies
            results = await self._execute_adaptive(compiled_protocol.execution_steps, compiled_protocol.dependency_graph)
        
        return results
    
    async def _execute_parallel(self, steps: List[ExecutionStep]) -> List[ExecutionResult]:
        """Execute steps in parallel"""
        tasks = []
        
        for step in steps:
            task = asyncio.create_task(self._execute_step(step))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to failed results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(ExecutionResult(
                    step_id=steps[i].step_id,
                    success=False,
                    result={},
                    execution_time=0.0,
                    error_message=str(result)
                ))
            else:
                final_results.append(result)
        
        return final_results
    
    async def _execute_sequential(self, steps: List[ExecutionStep]) -> List[ExecutionResult]:
        """Execute steps sequentially"""
        results = []
        
        for step in steps:
            result = await self._execute_step(step)
            results.append(result)
            
            # Stop if a step fails (optional - could be configurable)
            if not result.success:
                logger.warning(f"Step {step.step_id} failed, continuing with remaining steps")
        
        return results
    
    async def _execute_adaptive(self, steps: List[ExecutionStep], dependency_graph: Dict[str, List[str]]) -> List[ExecutionResult]:
        """Execute steps adaptively based on dependencies"""
        results = {}
        completed_steps = set()
        
        while len(completed_steps) < len(steps):
            # Find steps that can be executed now
            ready_steps = []
            for step in steps:
                if step.step_id not in completed_steps:
                    dependencies = dependency_graph.get(step.step_id, [])
                    if all(dep in completed_steps for dep in dependencies):
                        ready_steps.append(step)
            
            if not ready_steps:
                # No progress possible - circular dependency or other issue
                remaining_steps = [step for step in steps if step.step_id not in completed_steps]
                for step in remaining_steps:
                    results[step.step_id] = ExecutionResult(
                        step_id=step.step_id,
                        success=False,
                        result={},
                        execution_time=0.0,
                        error_message="Dependency deadlock or circular dependency"
                    )
                    completed_steps.add(step.step_id)
                break
            
            # Execute ready steps in parallel
            tasks = []
            for step in ready_steps:
                task = asyncio.create_task(self._execute_step(step))
                tasks.append(task)
            
            step_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(step_results):
                step = ready_steps[i]
                
                if isinstance(result, Exception):
                    results[step.step_id] = ExecutionResult(
                        step_id=step.step_id,
                        success=False,
                        result={},
                        execution_time=0.0,
                        error_message=str(result)
                    )
                else:
                    results[step.step_id] = result
                
                completed_steps.add(step.step_id)
        
        # Return results in original order
        return [results[step.step_id] for step in steps]
    
    async def _execute_step(self, step: ExecutionStep) -> ExecutionResult:
        """Execute a single pipeline step"""
        start_time = time.time()
        
        try:
            logger.info(f"Executing step: {step.step_id} (stage: {step.stage_name})")
            
            # Get the appropriate service
            service = self.services.get(step.stage_name)
            if not service:
                raise ValueError(f"Unknown stage: {step.stage_name}")
            
            # Prepare the input for the stage
            stage_input = self._prepare_stage_input(step)
            
            # Execute the stage
            if hasattr(service, 'process_async'):
                stage_result = await service.process_async(stage_input)
            else:
                # Fallback to synchronous execution
                stage_result = service.process(stage_input)
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                step_id=step.step_id,
                success=True,
                result=stage_result,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Step execution failed: {step.step_id} - {str(e)}")
            
            return ExecutionResult(
                step_id=step.step_id,
                success=False,
                result={},
                execution_time=execution_time,
                error_message=str(e)
            )
    
    def _prepare_stage_input(self, step: ExecutionStep) -> Dict[str, Any]:
        """Prepare input for a pipeline stage"""
        stage_input = {
            "step_id": step.step_id,
            "variable_name": step.variable_name,
            "parameters": step.parameters,
            "resource_requirements": step.resource_requirements
        }
        
        # Add stage-specific input preparation
        if step.stage_name == "stage0_query_processor":
            stage_input.update({
                "query": step.parameters.get("query", ""),
                "context": step.parameters.get("context", {}),
                "intent": step.parameters.get("intent", "research")
            })
        elif step.stage_name == "stage2_domain_knowledge":
            stage_input.update({
                "domain": step.parameters.get("domain", "general"),
                "expert_models": step.parameters.get("expert_models", []),
                "query_focus": step.parameters.get("query_focus", "")
            })
        elif step.stage_name == "stage3_reasoning_optimization":
            stage_input.update({
                "objective": step.parameters.get("objective", "optimize_quality"),
                "constraints": step.parameters.get("constraints", {}),
                "optimization_method": step.parameters.get("optimization_method", "multi_objective")
            })
        
        return stage_input
    
    def _update_execution_stats(self, success: bool, execution_time: float):
        """Update execution statistics"""
        self.execution_stats["total_protocols"] += 1
        
        if success:
            self.execution_stats["successful_protocols"] += 1
        else:
            self.execution_stats["failed_protocols"] += 1
        
        # Update average execution time
        total = self.execution_stats["total_protocols"]
        current_avg = self.execution_stats["average_execution_time"]
        self.execution_stats["average_execution_time"] = (
            (current_avg * (total - 1) + execution_time) / total
        )
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return self.execution_stats.copy()
    
    def reset_stats(self):
        """Reset execution statistics"""
        self.execution_stats = {
            "total_protocols": 0,
            "successful_protocols": 0,
            "failed_protocols": 0,
            "average_execution_time": 0.0
        } 