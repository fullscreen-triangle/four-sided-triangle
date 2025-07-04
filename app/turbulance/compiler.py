"""
Turbulance DSL Compiler

This module compiles parsed Turbulance scripts into executable Four-Sided Triangle
pipeline sequences. It handles:
- Pipeline stage sequencing
- Dependency resolution
- Resource allocation
- Execution plan generation
- Result annotation preparation
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

from .parser import TurbulanceScript, TurbulanceNode, TurbulanceNodeType

logger = logging.getLogger(__name__)

class ExecutionMode(Enum):
    """Execution modes for compiled protocols"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ADAPTIVE = "adaptive"

class ResourcePriority(Enum):
    """Resource priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ExecutionStep:
    """Represents a single execution step in the compiled pipeline"""
    step_id: str
    stage_name: str
    variable_name: str
    parameters: Dict[str, Any]
    dependencies: List[str]
    resource_requirements: Dict[str, Any]
    line_number: int
    annotation_target: str  # Where to inject results in the script

@dataclass
class CompiledProtocol:
    """Represents a compiled Turbulance protocol ready for execution"""
    protocol_name: str
    execution_steps: List[ExecutionStep]
    execution_mode: ExecutionMode
    resource_allocation: Dict[str, Any]
    dependency_graph: Dict[str, List[str]]
    annotation_map: Dict[str, str]  # Maps execution results to script locations
    auxiliary_files: Dict[str, str]  # .fs, .ghd, .hre file contents

class TurbulanceCompiler:
    """Compiles Turbulance scripts into executable Four-Sided Triangle pipelines"""
    
    def __init__(self):
        self.stage_mappings = {
            "query_processor": "stage0_query_processor",
            "semantic_atdb": "stage1_semantic_atdb", 
            "domain_knowledge": "stage2_domain_knowledge",
            "reasoning_optimization": "stage3_reasoning_optimization",
            "solution_generation": "stage4_solution",
            "response_scoring": "stage5_scoring",
            "response_comparison": "stage6_comparison",
            "threshold_verification": "stage7_verification"
        }
        
        self.default_resource_estimates = {
            "stage0_query_processor": {"cpu": 1, "memory": 2, "gpu": 0, "time": 10},
            "stage1_semantic_atdb": {"cpu": 2, "memory": 4, "gpu": 0, "time": 15},
            "stage2_domain_knowledge": {"cpu": 4, "memory": 8, "gpu": 1, "time": 30},
            "stage3_reasoning_optimization": {"cpu": 3, "memory": 6, "gpu": 0, "time": 25},
            "stage4_solution": {"cpu": 2, "memory": 4, "gpu": 0, "time": 20},
            "stage5_scoring": {"cpu": 1, "memory": 2, "gpu": 0, "time": 15},
            "stage6_comparison": {"cpu": 2, "memory": 4, "gpu": 0, "time": 10},
            "stage7_verification": {"cpu": 1, "memory": 2, "gpu": 0, "time": 5}
        }
        
    def compile_protocol(self, script: TurbulanceScript) -> CompiledProtocol:
        """Compile a parsed Turbulance script into executable protocol"""
        logger.info(f"Compiling Turbulance protocol: {script.protocol_name}")
        
        # Create execution steps from pipeline calls
        execution_steps = self._create_execution_steps(script)
        
        # Resolve dependencies
        dependency_graph = self._resolve_dependencies(execution_steps)
        
        # Determine execution mode
        execution_mode = self._determine_execution_mode(execution_steps, dependency_graph)
        
        # Allocate resources
        resource_allocation = self._allocate_resources(execution_steps, execution_mode)
        
        # Create annotation map for result injection
        annotation_map = self._create_annotation_map(script, execution_steps)
        
        # Generate auxiliary files
        from .parser import TurbulanceParser
        parser = TurbulanceParser()
        auxiliary_files = parser.generate_auxiliary_files(script)
        
        compiled_protocol = CompiledProtocol(
            protocol_name=script.protocol_name,
            execution_steps=execution_steps,
            execution_mode=execution_mode,
            resource_allocation=resource_allocation,
            dependency_graph=dependency_graph,
            annotation_map=annotation_map,
            auxiliary_files=auxiliary_files
        )
        
        logger.info(f"Compiled protocol with {len(execution_steps)} steps")
        return compiled_protocol
    
    def _create_execution_steps(self, script: TurbulanceScript) -> List[ExecutionStep]:
        """Create execution steps from pipeline calls"""
        steps = []
        
        for call in script.pipeline_calls:
            stage_name = call.parsed_data.get('stage', 'unknown')
            variable_name = call.parsed_data.get('variable', f'step_{call.line_number}')
            parameters = call.parsed_data.get('parameters', {})
            
            # Map to actual stage names
            actual_stage = self.stage_mappings.get(stage_name, stage_name)
            
            # Get resource requirements
            resource_requirements = self.default_resource_estimates.get(
                actual_stage, 
                {"cpu": 1, "memory": 2, "gpu": 0, "time": 10}
            )
            
            # Create execution step
            step = ExecutionStep(
                step_id=f"{script.protocol_name}_{variable_name}",
                stage_name=actual_stage,
                variable_name=variable_name,
                parameters=parameters,
                dependencies=call.dependencies,
                resource_requirements=resource_requirements,
                line_number=call.line_number,
                annotation_target=f"// RESULT: {variable_name} = "
            )
            
            steps.append(step)
        
        return steps
    
    def _resolve_dependencies(self, steps: List[ExecutionStep]) -> Dict[str, List[str]]:
        """Resolve dependencies between execution steps"""
        dependency_graph = {}
        
        # Create a map of variable names to step IDs
        variable_to_step = {step.variable_name: step.step_id for step in steps}
        
        for step in steps:
            dependencies = []
            
            # Resolve each dependency
            for dep in step.dependencies:
                if dep in variable_to_step:
                    dependencies.append(variable_to_step[dep])
            
            dependency_graph[step.step_id] = dependencies
        
        return dependency_graph
    
    def _determine_execution_mode(self, steps: List[ExecutionStep], dependency_graph: Dict[str, List[str]]) -> ExecutionMode:
        """Determine the best execution mode for the protocol"""
        
        # If all steps have dependencies, we need sequential execution
        independent_steps = [step for step in steps if not dependency_graph.get(step.step_id, [])]
        
        if len(independent_steps) == 0:
            return ExecutionMode.SEQUENTIAL
        elif len(independent_steps) == len(steps):
            return ExecutionMode.PARALLEL
        else:
            # Mixed - some parallel, some sequential
            return ExecutionMode.ADAPTIVE
    
    def _allocate_resources(self, steps: List[ExecutionStep], execution_mode: ExecutionMode) -> Dict[str, Any]:
        """Allocate resources for execution"""
        total_cpu = sum(step.resource_requirements.get('cpu', 1) for step in steps)
        total_memory = sum(step.resource_requirements.get('memory', 2) for step in steps)
        total_gpu = sum(step.resource_requirements.get('gpu', 0) for step in steps)
        
        # Adjust for execution mode
        if execution_mode == ExecutionMode.PARALLEL:
            # All steps run simultaneously
            max_cpu = max(step.resource_requirements.get('cpu', 1) for step in steps)
            max_memory = max(step.resource_requirements.get('memory', 2) for step in steps)
            max_gpu = max(step.resource_requirements.get('gpu', 0) for step in steps)
            
            allocation = {
                "cpu_cores": max_cpu,
                "memory_gb": max_memory,
                "gpu_units": max_gpu
            }
        else:
            # Sequential or adaptive - use average resource requirements
            allocation = {
                "cpu_cores": min(total_cpu, 8),  # Cap at 8 cores
                "memory_gb": min(total_memory, 32),  # Cap at 32GB
                "gpu_units": min(total_gpu, 2)  # Cap at 2 GPUs
            }
        
        allocation.update({
            "execution_mode": execution_mode.value,
            "estimated_time_seconds": sum(step.resource_requirements.get('time', 10) for step in steps),
            "step_count": len(steps)
        })
        
        return allocation
    
    def _create_annotation_map(self, script: TurbulanceScript, steps: List[ExecutionStep]) -> Dict[str, str]:
        """Create mapping for result annotation back to script"""
        annotation_map = {}
        
        for step in steps:
            # Find the original line in the script
            original_line = None
            for node in script.nodes:
                if (node.node_type == TurbulanceNodeType.PIPELINE_CALL and 
                    node.line_number == step.line_number):
                    original_line = node.content
                    break
            
            if original_line:
                annotation_map[step.step_id] = {
                    "original_line": original_line,
                    "line_number": step.line_number,
                    "variable_name": step.variable_name,
                    "annotation_pattern": f"// RESULT: {step.variable_name} = {{result}}"
                }
        
        return annotation_map
    
    def annotate_script_with_results(self, script_content: str, results: Dict[str, Any], annotation_map: Dict[str, str]) -> str:
        """Annotate the original script with execution results"""
        lines = script_content.split('\n')
        annotated_lines = []
        
        for i, line in enumerate(lines):
            annotated_lines.append(line)
            
            # Check if this line needs annotation
            line_number = i + 1
            for step_id, annotation_info in annotation_map.items():
                if annotation_info["line_number"] == line_number:
                    # Get the result for this step
                    result = results.get(step_id, {})
                    
                    # Format the result annotation
                    if result:
                        result_summary = self._format_result_for_annotation(result)
                        annotation = annotation_info["annotation_pattern"].format(result=result_summary)
                        annotated_lines.append(f"    {annotation}")
                    
                    break
        
        return '\n'.join(annotated_lines)
    
    def _format_result_for_annotation(self, result: Dict[str, Any]) -> str:
        """Format a result for script annotation"""
        if not result:
            return "No result"
        
        # Extract key information for annotation
        summary_parts = []
        
        if "confidence" in result:
            summary_parts.append(f"confidence: {result['confidence']:.3f}")
        
        if "result_type" in result:
            summary_parts.append(f"type: {result['result_type']}")
        
        if "key_findings" in result:
            findings = result["key_findings"]
            if isinstance(findings, list):
                summary_parts.append(f"findings: {', '.join(findings[:3])}")
            else:
                summary_parts.append(f"findings: {str(findings)[:100]}")
        
        if "processing_time" in result:
            summary_parts.append(f"time: {result['processing_time']:.2f}s")
        
        return "{" + ", ".join(summary_parts) + "}"
    
    def create_execution_plan(self, compiled_protocol: CompiledProtocol) -> Dict[str, Any]:
        """Create detailed execution plan for the orchestrator"""
        plan = {
            "protocol_name": compiled_protocol.protocol_name,
            "execution_mode": compiled_protocol.execution_mode.value,
            "resource_allocation": compiled_protocol.resource_allocation,
            "steps": [],
            "dependencies": compiled_protocol.dependency_graph,
            "auxiliary_files": compiled_protocol.auxiliary_files
        }
        
        for step in compiled_protocol.execution_steps:
            plan["steps"].append({
                "step_id": step.step_id,
                "stage_name": step.stage_name,
                "variable_name": step.variable_name,
                "parameters": step.parameters,
                "dependencies": step.dependencies,
                "resource_requirements": step.resource_requirements,
                "annotation_target": step.annotation_target
            })
        
        return plan 