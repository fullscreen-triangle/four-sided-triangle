"""
Metacognitive Orchestrator for the Four-Sided Triangle system.

This module provides the implementation of the metacognitive orchestrator,
which coordinates the execution of the pipeline stages, manages working memory,
and dynamically adjusts the pipeline based on output quality evaluations.
"""

import logging
import time
from typing import Dict, Any, List, Optional, Union, Callable
import json

from app.orchestrator.interfaces import (
    OrchestratorInterface,
    PipelineStageInterface,
    PromptGeneratorInterface,
    OutputEvaluatorInterface
)
from app.orchestrator.working_memory import working_memory
from app.orchestrator.prompt_generator import prompt_generator
from app.orchestrator.output_evaluator import output_evaluator
from app.turbulance import TurbulanceParser, TurbulanceCompiler, TurbulanceOrchestrator

logger = logging.getLogger(__name__)

class MetacognitiveOrchestrator(OrchestratorInterface):
    """
    Implementation of the Metacognitive Orchestrator.
    
    The orchestrator coordinates the execution of pipeline stages,
    manages working memory, evaluates intermediate outputs,
    and dynamically adjusts the pipeline based on quality assessments.
    """
    
    def __init__(self):
        """Initialize the metacognitive orchestrator."""
        # Pipeline stages registry
        self._stages: Dict[str, PipelineStageInterface] = {}
        
        # Pipeline configuration - defines the default execution order
        self._pipeline_config: List[Dict[str, Any]] = []
        
        # Maximum iterations for a stage refinement
        self._max_refinement_iterations = 3
        
        # Callbacks for monitoring pipeline progression
        self._status_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        
        # Evaluation thresholds for stages
        self._thresholds: Dict[str, float] = {}
        
        # Default quality threshold
        self._default_threshold = 0.7
        
        # Turbulance integration
        self._turbulance_orchestrator = TurbulanceOrchestrator(self)
        
        logger.info("Metacognitive orchestrator initialized with Turbulance support")
    
    def register_stage(self, stage_id: str, stage: PipelineStageInterface) -> None:
        """
        Register a pipeline stage with the orchestrator.
        
        Args:
            stage_id: Unique identifier for the stage
            stage: Stage implementation object
        """
        if stage_id in self._stages:
            logger.warning(f"Overwriting existing stage with ID: {stage_id}")
        
        self._stages[stage_id] = stage
        logger.info(f"Registered stage: {stage_id}")
    
    def configure_pipeline(self, config: List[Dict[str, Any]]) -> None:
        """
        Configure the pipeline execution order and dependencies.
        
        Args:
            config: List of stage configurations with dependencies and settings
                Each item should contain at least:
                - 'id': Stage identifier
                - 'depends_on': List of stage IDs this stage depends on (optional)
                - 'optional': Whether this stage can be skipped (optional)
                - 'threshold': Quality threshold for this stage (optional)
        """
        # Validate configuration
        for stage_config in config:
            stage_id = stage_config.get('id')
            if not stage_id:
                raise ValueError("Stage configuration missing 'id' field")
            
            if stage_id not in self._stages:
                raise ValueError(f"Unknown stage ID in pipeline configuration: {stage_id}")
            
            # Store threshold if provided
            threshold = stage_config.get('threshold')
            if threshold is not None:
                if 0 <= threshold <= 1:
                    self._thresholds[stage_id] = threshold
                else:
                    raise ValueError(f"Invalid threshold for stage {stage_id}: {threshold}")
        
        self._pipeline_config = config
        logger.info(f"Pipeline configured with {len(config)} stages")
    
    def register_status_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Register a callback function to be called during pipeline execution.
        
        Args:
            callback: Function to call with status updates
        """
        self._status_callbacks.append(callback)
        logger.debug("Registered status callback")
    
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
        query_id = f"query_{int(start_time)}"
        logger.info(f"Starting query processing: {query_id}")
        
        # Initialize working memory for this query
        self._initialize_memory(query_id, query, context)
        
        # Execute pipeline stages in order
        executed_stages = []
        
        try:
            for stage_config in self._pipeline_config:
                stage_id = stage_config['id']
                stage = self._stages[stage_id]
                depends_on = stage_config.get('depends_on', [])
                optional = stage_config.get('optional', False)
                
                # Check if dependencies have been executed
                if not all(dep in executed_stages for dep in depends_on):
                    if optional:
                        logger.warning(f"Skipping optional stage {stage_id} due to missing dependencies")
                        continue
                    else:
                        raise ValueError(f"Cannot execute stage {stage_id} - dependencies not satisfied")
                
                # Execute the stage with metacognitive monitoring
                success = self._execute_stage_with_monitoring(query_id, stage_id, stage)
                
                if success:
                    executed_stages.append(stage_id)
                elif not optional:
                    raise RuntimeError(f"Critical stage {stage_id} failed to execute successfully")
                else:
                    logger.warning(f"Optional stage {stage_id} failed but pipeline will continue")
            
            # Prepare final result
            result = self._prepare_result(query_id)
            
        except Exception as e:
            logger.error(f"Error processing query {query_id}: {str(e)}")
            result = {
                "success": False,
                "error": str(e),
                "query_id": query_id,
                "partial_results": working_memory.get_memory(query_id)
            }
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Add execution metadata
        result["metadata"] = {
            "query_id": query_id,
            "execution_time": duration,
            "stages_executed": executed_stages,
            "timestamp": end_time
        }
        
        # Notify any registered callbacks
        self._notify_status_callbacks({
            "type": "query_completed",
            "query_id": query_id,
            "success": result.get("success", False),
            "execution_time": duration
        })
        
        return result
    
    def _initialize_memory(self, query_id: str, query: str, context: Optional[Dict[str, Any]]) -> None:
        """
        Initialize working memory for a query.
        
        Args:
            query_id: Unique identifier for this query
            query: The raw query string
            context: Additional context for the query
        """
        memory_context = {
            "query_id": query_id,
            "original_query": query,
            "timestamp": time.time(),
            "stage_outputs": {},
            "stage_prompts": {},
            "stage_evaluations": {},
            "refinement_history": {}
        }
        
        # Add any additional context if provided
        if context:
            for key, value in context.items():
                if key not in memory_context:
                    memory_context[key] = value
        
        # Initialize working memory
        working_memory.set_memory(query_id, memory_context)
        logger.debug(f"Initialized working memory for query {query_id}")
    
    def _execute_stage_with_monitoring(self, query_id: str, stage_id: str, 
                                     stage: PipelineStageInterface) -> bool:
        """
        Execute a pipeline stage with metacognitive monitoring.
        
        This method handles:
        1. Prompt generation for the stage
        2. Stage execution
        3. Output evaluation
        4. Refinement if needed
        
        Args:
            query_id: Unique identifier for this query
            stage_id: Identifier for the stage
            stage: Stage implementation object
            
        Returns:
            Success status of the stage execution
        """
        logger.info(f"Executing stage: {stage_id} for query {query_id}")
        
        # Get current memory context
        context = working_memory.get_memory(query_id)
        
        # Notify any registered callbacks
        self._notify_status_callbacks({
            "type": "stage_started",
            "query_id": query_id,
            "stage_id": stage_id
        })
        
        # Track stage execution metrics
        start_time = time.time()
        refinement_count = 0
        success = False
        
        try:
            # Loop for refinement iterations
            while refinement_count <= self._max_refinement_iterations:
                # Generate appropriate prompt for this stage
                prompt = self._generate_stage_prompt(query_id, stage_id, refinement_count)
                
                # Store prompt in working memory
                if "stage_prompts" not in context:
                    context["stage_prompts"] = {}
                if stage_id not in context["stage_prompts"]:
                    context["stage_prompts"][stage_id] = []
                
                context["stage_prompts"][stage_id].append({
                    "iteration": refinement_count,
                    "prompt": prompt,
                    "timestamp": time.time()
                })
                
                # Update working memory with the new prompt
                working_memory.update_memory(query_id, context)
                
                # Execute the stage
                stage_input = self._prepare_stage_input(query_id, stage_id, context)
                stage_output = stage.process(stage_input, prompt)
                
                # Store the output in working memory
                if "stage_outputs" not in context:
                    context["stage_outputs"] = {}
                
                context["stage_outputs"][stage_id] = stage_output
                working_memory.update_memory(query_id, context)
                
                # Evaluate the output
                evaluation = self._evaluate_stage_output(query_id, stage_id, stage_output, context)
                
                # Store evaluation in working memory
                if "stage_evaluations" not in context:
                    context["stage_evaluations"] = {}
                
                context["stage_evaluations"][stage_id] = evaluation
                working_memory.update_memory(query_id, context)
                
                # Check if output needs refinement
                if not evaluation.get("needs_refinement", False) or refinement_count >= self._max_refinement_iterations:
                    success = evaluation.get("passed", False)
                    break
                
                # Prepare for refinement
                if "refinement_history" not in context:
                    context["refinement_history"] = {}
                if stage_id not in context["refinement_history"]:
                    context["refinement_history"][stage_id] = []
                
                # Record refinement attempt
                context["refinement_history"][stage_id].append({
                    "iteration": refinement_count,
                    "evaluation": evaluation,
                    "timestamp": time.time()
                })
                
                working_memory.update_memory(query_id, context)
                
                # Notify about refinement
                self._notify_status_callbacks({
                    "type": "stage_refinement",
                    "query_id": query_id,
                    "stage_id": stage_id,
                    "iteration": refinement_count,
                    "evaluation": evaluation
                })
                
                # Increment refinement counter
                refinement_count += 1
                
                logger.info(f"Refining stage {stage_id} (iteration {refinement_count})")
            
            # Record execution metrics
            execution_time = time.time() - start_time
            
            # Record final stage status
            stage_status = {
                "success": success,
                "execution_time": execution_time,
                "refinement_count": refinement_count,
                "final_evaluation": context["stage_evaluations"].get(stage_id, {})
            }
            
            if "stage_status" not in context:
                context["stage_status"] = {}
            
            context["stage_status"][stage_id] = stage_status
            working_memory.update_memory(query_id, context)
            
            # Notify completion
            self._notify_status_callbacks({
                "type": "stage_completed",
                "query_id": query_id,
                "stage_id": stage_id,
                "success": success,
                "execution_time": execution_time,
                "refinement_count": refinement_count
            })
            
            logger.info(f"Stage {stage_id} completed with success={success}, refinements={refinement_count}")
            return success
            
        except Exception as e:
            logger.error(f"Error executing stage {stage_id}: {str(e)}")
            
            # Update status in context
            if "stage_status" not in context:
                context["stage_status"] = {}
            
            context["stage_status"][stage_id] = {
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time,
                "refinement_count": refinement_count
            }
            
            working_memory.update_memory(query_id, context)
            
            # Notify error
            self._notify_status_callbacks({
                "type": "stage_error",
                "query_id": query_id,
                "stage_id": stage_id,
                "error": str(e)
            })
            
            return False
    
    def _generate_stage_prompt(self, query_id: str, stage_id: str, iteration: int) -> str:
        """
        Generate a prompt for a pipeline stage.
        
        Args:
            query_id: Unique identifier for this query
            stage_id: Identifier for the stage
            iteration: Current refinement iteration (0 for initial run)
            
        Returns:
            Generated prompt for the stage
        """
        context = working_memory.get_memory(query_id)
        
        if iteration == 0:
            # Initial prompt
            return prompt_generator.generate_stage_prompt(stage_id, context)
        else:
            # Refinement prompt
            evaluation = context.get("stage_evaluations", {}).get(stage_id, {})
            return prompt_generator.generate_refinement_prompt(
                stage_id, 
                context, 
                evaluation, 
                iteration
            )
    
    def _prepare_stage_input(self, query_id: str, stage_id: str, 
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare input for a pipeline stage based on working memory.
        
        Args:
            query_id: Unique identifier for this query
            stage_id: Identifier for the stage
            context: Current working memory context
            
        Returns:
            Stage input dictionary
        """
        # Get stage configuration to determine dependencies
        stage_config = next((s for s in self._pipeline_config if s['id'] == stage_id), None)
        if not stage_config:
            logger.warning(f"No configuration found for stage {stage_id}")
            depends_on = []
        else:
            depends_on = stage_config.get('depends_on', [])
        
        # Build input from original query and outputs of dependent stages
        stage_input = {
            "query": context.get("original_query", ""),
            "query_id": query_id,
            "dependencies": {}
        }
        
        # Add outputs from dependent stages
        stage_outputs = context.get("stage_outputs", {})
        for dep_stage in depends_on:
            if dep_stage in stage_outputs:
                stage_input["dependencies"][dep_stage] = stage_outputs[dep_stage]
        
        # Include any additional context that might be useful
        for key, value in context.items():
            if key not in ["stage_outputs", "stage_prompts", "stage_evaluations", 
                          "refinement_history", "stage_status"]:
                stage_input[key] = value
        
        return stage_input
    
    def _evaluate_stage_output(self, query_id: str, stage_id: str, 
                             output: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate the output of a stage using the output evaluator.
        
        Args:
            query_id: Unique identifier for this query
            stage_id: Identifier for the stage
            output: Stage output to evaluate
            context: Current working memory context
            
        Returns:
            Evaluation results
        """
        # Include threshold in evaluation context
        eval_context = dict(context)
        
        # Get threshold for this stage or use default
        threshold = self._thresholds.get(stage_id, self._default_threshold)
        eval_context["threshold"] = threshold
        
        # Perform evaluation
        evaluation = output_evaluator.evaluate_output(stage_id, output, eval_context)
        
        return evaluation
    
    def _prepare_result(self, query_id: str) -> Dict[str, Any]:
        """
        Prepare the final result from working memory.
        
        Args:
            query_id: Unique identifier for this query
            
        Returns:
            Final processing result
        """
        context = working_memory.get_memory(query_id)
        
        # Get the outputs from the final stages in the pipeline
        stage_outputs = context.get("stage_outputs", {})
        stage_evaluations = context.get("stage_evaluations", {})
        stage_status = context.get("stage_status", {})
        
        # Determine overall success
        success = all(
            status.get("success", False) 
            for stage_id, status in stage_status.items()
            if not next((s for s in self._pipeline_config if s['id'] == stage_id), {}).get('optional', False)
        )
        
        # Find the final stage(s) - those that aren't dependencies for any other stage
        all_deps = set()
        for config in self._pipeline_config:
            all_deps.update(config.get('depends_on', []))
        
        final_stages = [
            config['id'] for config in self._pipeline_config
            if config['id'] not in all_deps
        ]
        
        # Extract outputs from final stages
        final_outputs = {}
        for stage_id in final_stages:
            if stage_id in stage_outputs:
                final_outputs[stage_id] = stage_outputs[stage_id]
        
        # Prepare the result
        result = {
            "success": success,
            "query_id": query_id,
            "final_outputs": final_outputs,
            "all_outputs": stage_outputs,
            "evaluations": stage_evaluations,
            "execution_status": stage_status
        }
        
        return result
    
    def _notify_status_callbacks(self, status: Dict[str, Any]) -> None:
        """
        Notify all registered callbacks with a status update.
        
        Args:
            status: Status information to pass to callbacks
        """
        for callback in self._status_callbacks:
            try:
                callback(status)
            except Exception as e:
                logger.error(f"Error in status callback: {str(e)}")

    async def execute_turbulance_protocol(self, script_content: str, protocol_name: str, 
                                        execution_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a Turbulance protocol through the Four-Sided Triangle pipeline.
        
        Args:
            script_content: The Turbulance script content
            protocol_name: Name of the protocol
            execution_options: Optional execution configuration
            
        Returns:
            Execution result with annotated script and statistics
        """
        start_time = time.time()
        logger.info(f"Executing Turbulance protocol: {protocol_name}")
        
        try:
            # Execute through the Turbulance orchestrator
            result = await self._turbulance_orchestrator.execute_protocol(
                script_content, protocol_name
            )
            
            execution_time = time.time() - start_time
            
            # Prepare response in the standard format
            response = {
                "success": result.success,
                "protocol_name": result.protocol_name,
                "execution_time": result.execution_time,
                "annotated_script": result.annotated_script,
                "step_results": result.step_results,
                "auxiliary_files": result.auxiliary_files,
                "metadata": {
                    "execution_type": "turbulance_protocol",
                    "total_processing_time": execution_time,
                    "timestamp": time.time(),
                    "pipeline_integration": "four_sided_triangle"
                }
            }
            
            # Notify callbacks
            self._notify_status_callbacks({
                "type": "turbulance_protocol_completed",
                "protocol_name": protocol_name,
                "success": result.success,
                "execution_time": execution_time,
                "steps_completed": len([r for r in result.step_results if r.success]),
                "steps_failed": len([r for r in result.step_results if not r.success])
            })
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error executing Turbulance protocol {protocol_name}: {str(e)}", exc_info=True)
            
            error_response = {
                "success": False,
                "protocol_name": protocol_name,
                "error": str(e),
                "execution_time": execution_time,
                "metadata": {
                    "execution_type": "turbulance_protocol",
                    "error_occurred": True,
                    "timestamp": time.time()
                }
            }
            
            # Notify callbacks about the failure
            self._notify_status_callbacks({
                "type": "turbulance_protocol_failed",
                "protocol_name": protocol_name,
                "error": str(e),
                "execution_time": execution_time
            })
            
            return error_response

    def validate_turbulance_script(self, script_content: str, protocol_name: str) -> Dict[str, Any]:
        """
        Validate a Turbulance script for syntax and structural errors.
        
        Args:
            script_content: The Turbulance script content to validate
            protocol_name: Name of the protocol
            
        Returns:
            Validation result with errors and warnings
        """
        try:
            parser = TurbulanceParser()
            parsed_script = parser.parse_script(script_content, protocol_name)
            
            # Perform validation checks
            validation_errors = []
            warnings = []
            
            # Check for basic structure
            if not parsed_script.pipeline_calls:
                warnings.append("No pipeline stage calls found in script")
            
            # Check dependencies
            for var_name, deps in parsed_script.dependencies.items():
                for dep in deps:
                    if dep not in parsed_script.variables and not any(
                        call.parsed_data.get('variable') == dep for call in parsed_script.pipeline_calls
                    ):
                        validation_errors.append(f"Undefined dependency '{dep}' for variable '{var_name}'")
            
            # Check for available stages
            available_stages = list(self._stages.keys())
            for call in parsed_script.pipeline_calls:
                stage_name = call.parsed_data.get('stage')
                if stage_name and stage_name not in available_stages:
                    validation_errors.append(f"Unknown pipeline stage '{stage_name}'")
            
            is_valid = len(validation_errors) == 0
            
            return {
                "is_valid": is_valid,
                "validation_errors": validation_errors,
                "warnings": warnings,
                "script_metrics": {
                    "total_lines": len(script_content.split('\n')),
                    "pipeline_calls": len(parsed_script.pipeline_calls),
                    "variables": len(parsed_script.variables),
                    "dependencies": len(parsed_script.dependencies),
                    "available_stages": available_stages
                },
                "parsed_script": parsed_script
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "validation_errors": [f"Parse error: {str(e)}"],
                "warnings": [],
                "script_metrics": {},
                "error": str(e)
            }

    def get_turbulance_statistics(self) -> Dict[str, Any]:
        """
        Get statistics from the Turbulance orchestrator.
        
        Returns:
            Statistics about Turbulance protocol executions
        """
        try:
            stats = self._turbulance_orchestrator.get_execution_stats()
            return {
                "turbulance_statistics": stats,
                "integration_status": "active",
                "supported_features": [
                    "protocol_parsing",
                    "protocol_compilation", 
                    "protocol_execution",
                    "result_annotation",
                    "auxiliary_file_generation"
                ]
            }
        except Exception as e:
            logger.error(f"Error getting Turbulance statistics: {str(e)}")
            return {
                "turbulance_statistics": {},
                "integration_status": "error",
                "error": str(e)
            }

    def get_pipeline_info(self) -> Dict[str, Any]:
        """
        Get information about the configured pipeline stages.
        
        Returns:
            Information about available stages and configuration
        """
        return {
            "registered_stages": list(self._stages.keys()),
            "pipeline_configuration": self._pipeline_config,
            "stage_thresholds": self._thresholds,
            "default_threshold": self._default_threshold,
            "turbulance_integration": "enabled"
        }

# Global singleton instance
orchestrator = MetacognitiveOrchestrator() 