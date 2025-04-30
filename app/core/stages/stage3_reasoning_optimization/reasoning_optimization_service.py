"""
Reasoning Optimization Service for the Four-Sided Triangle system.

This module provides the core implementation of the reasoning optimization
stage, which applies advanced reasoning strategies, optimizes solution 
approaches, and reduces cognitive biases.
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple

from app.llm.llm_service import LLMService

logger = logging.getLogger(__name__)

class ReasoningOptimizationService:
    """
    Service implementing reasoning optimization functionality.
    
    This service handles strategy selection, optimization techniques,
    bias reduction, and solution evaluation for the reasoning stage.
    """
    
    def __init__(self, llm_service: LLMService):
        """
        Initialize the reasoning optimization service.
        
        Args:
            llm_service: LLM service to use for reasoning optimization
        """
        self._llm_service = llm_service
        self._last_processing_time = None
        self._available_strategies = self._load_available_strategies()
        self._bias_reduction_methods = self._load_bias_reduction_methods()
        logger.info("Reasoning Optimization service initialized")
    
    def _load_available_strategies(self) -> Dict[str, Dict[str, Any]]:
        """
        Load available reasoning optimization strategies.
        
        Returns:
            Dictionary mapping strategy IDs to their configurations
        """
        # In a real implementation, these could be loaded from configuration
        # or a database of optimization techniques
        return {
            "mathematical_optimization": {
                "name": "Mathematical Optimization",
                "techniques": ["linear_programming", "constraint_satisfaction", "integer_programming"],
                "applicable_problems": ["resource_allocation", "scheduling", "logistics"]
            },
            "heuristic_optimization": {
                "name": "Heuristic Optimization",
                "techniques": ["genetic_algorithms", "simulated_annealing", "particle_swarm"],
                "applicable_problems": ["complex_search", "multi_parameter_optimization", "non_linear"]
            },
            "numerical_methods": {
                "name": "Numerical Methods",
                "techniques": ["gradient_descent", "newton_method", "quasi_newton"],
                "applicable_problems": ["continuous_optimization", "function_minimization"]
            },
            "reinforcement_learning": {
                "name": "Reinforcement Learning",
                "techniques": ["q_learning", "policy_gradients", "deep_q_networks"],
                "applicable_problems": ["sequential_decision", "game_theory", "control_systems"]
            },
            "logical_reasoning": {
                "name": "Logical Reasoning",
                "techniques": ["deduction", "induction", "abduction", "case_based_reasoning"],
                "applicable_problems": ["classification", "diagnosis", "inference"]
            }
        }
    
    def _load_bias_reduction_methods(self) -> Dict[str, Dict[str, Any]]:
        """
        Load available bias reduction methods.
        
        Returns:
            Dictionary mapping method IDs to their configurations
        """
        return {
            "counterfactual_reasoning": {
                "name": "Counterfactual Reasoning",
                "target_biases": ["confirmation_bias", "hindsight_bias"],
                "description": "Generates alternative scenarios to challenge assumptions"
            },
            "perspective_diversification": {
                "name": "Perspective Diversification",
                "target_biases": ["anchoring_bias", "authority_bias", "groupthink"],
                "description": "Incorporates diverse viewpoints to broaden reasoning"
            },
            "probabilistic_reasoning": {
                "name": "Probabilistic Reasoning",
                "target_biases": ["neglect_of_probability", "gambler_fallacy", "base_rate_neglect"],
                "description": "Applies Bayesian reasoning to update beliefs with evidence"
            },
            "debiasing_techniques": {
                "name": "Debiasing Techniques",
                "target_biases": ["availability_bias", "recency_bias", "sunk_cost_fallacy"],
                "description": "Explicit techniques to counter specific cognitive biases"
            },
            "structured_analysis": {
                "name": "Structured Analysis",
                "target_biases": ["framing_effect", "bandwagon_effect", "status_quo_bias"],
                "description": "Uses frameworks to ensure comprehensive analysis"
            }
        }
    
    def optimize_reasoning(self, prompt: str, query_data: Dict[str, Any], 
                          semantic_model: Dict[str, Any], domain_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply reasoning optimization to a problem.
        
        Args:
            prompt: Generated prompt for this stage
            query_data: Data from the query processor stage
            semantic_model: Semantic analysis from the ATDB stage
            domain_knowledge: Knowledge from the domain knowledge stage
            
        Returns:
            Dictionary containing the optimized reasoning approach and metadata
        """
        start_time = time.time()
        
        try:
            # 1. Analyze problem characteristics
            problem_type, complexity = self._analyze_problem(query_data, semantic_model)
            
            # 2. Select appropriate reasoning strategies
            selected_strategies = self._select_strategies(problem_type, complexity, domain_knowledge)
            
            # 3. Apply optimization techniques
            optimization_results = self._apply_optimization(
                prompt, 
                selected_strategies, 
                query_data, 
                semantic_model, 
                domain_knowledge
            )
            
            # 4. Apply bias reduction methods
            bias_reduced_results = self._reduce_biases(optimization_results)
            
            # 5. Evaluate solution quality
            evaluation_results = self._evaluate_solutions(bias_reduced_results)
            
            # 6. Prepare result package
            result = {
                "reasoning_model": {
                    "problem_type": problem_type,
                    "complexity": complexity,
                    "optimized_approach": bias_reduced_results,
                    "evaluation": evaluation_results
                },
                "applied_strategies": [s["name"] for s in selected_strategies],
                "bias_reduction_methods": list(self._get_applied_bias_methods(bias_reduced_results)),
                "confidence_score": self._calculate_confidence(evaluation_results),
                "metadata": {
                    "processing_time": time.time() - start_time,
                    "strategy_selection_confidence": self._calculate_strategy_confidence(selected_strategies),
                    "optimization_iterations": optimization_results.get("iterations", 1)
                }
            }
            
            self._last_processing_time = time.time()
            
            return result
            
        except Exception as e:
            logger.error(f"Error in reasoning optimization: {str(e)}")
            self._last_processing_time = time.time()
            
            # Return an error response
            return {
                "error": str(e),
                "metadata": {
                    "processing_time": time.time() - start_time,
                    "status": "failed"
                }
            }
    
    def refine_optimization(self, refinement_prompt: str, context: Dict[str, Any], 
                           previous_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Refine a previous reasoning optimization based on feedback.
        
        Args:
            refinement_prompt: Prompt for refinement
            context: Current session context
            previous_output: Output from previous processing attempt
            
        Returns:
            Refined reasoning optimization output
        """
        start_time = time.time()
        
        try:
            # Extract previous reasoning model
            prev_model = previous_output.get("reasoning_model", {})
            
            # Parse refinement requirements from prompt
            refinement_focus = self._parse_refinement_focus(refinement_prompt)
            
            # Adjust strategies based on refinement focus
            adjusted_strategies = self._adjust_strategies(
                prev_model.get("problem_type", "unknown"),
                refinement_focus,
                previous_output.get("applied_strategies", [])
            )
            
            # Apply refined optimization
            refined_results = self._apply_refined_optimization(
                refinement_prompt,
                adjusted_strategies,
                context.get("query_data", {}),
                context.get("semantic_model", {}),
                context.get("domain_knowledge", {}),
                prev_model.get("optimized_approach", {})
            )
            
            # Re-evaluate the solution
            evaluation_results = self._evaluate_solutions(refined_results)
            
            # Prepare refined result
            result = {
                "reasoning_model": {
                    "problem_type": prev_model.get("problem_type", "unknown"),
                    "complexity": prev_model.get("complexity", "medium"),
                    "optimized_approach": refined_results,
                    "evaluation": evaluation_results,
                    "refinement_focus": refinement_focus
                },
                "applied_strategies": [s["name"] for s in adjusted_strategies],
                "bias_reduction_methods": list(self._get_applied_bias_methods(refined_results)),
                "confidence_score": self._calculate_confidence(evaluation_results),
                "metadata": {
                    "processing_time": time.time() - start_time,
                    "refinement_iteration": previous_output.get("metadata", {}).get("refinement_iteration", 0) + 1,
                    "improvement_score": self._calculate_improvement(
                        evaluation_results, 
                        prev_model.get("evaluation", {})
                    )
                }
            }
            
            self._last_processing_time = time.time()
            
            return result
            
        except Exception as e:
            logger.error(f"Error in reasoning optimization refinement: {str(e)}")
            self._last_processing_time = time.time()
            
            # Return an error response
            return {
                "error": str(e),
                "metadata": {
                    "processing_time": time.time() - start_time,
                    "status": "refinement_failed"
                }
            }
    
    def get_last_processing_time(self) -> float:
        """
        Get the timestamp of the last processing operation.
        
        Returns:
            Unix timestamp of the last processing operation
        """
        return self._last_processing_time
    
    def _analyze_problem(self, query_data: Dict[str, Any], 
                        semantic_model: Dict[str, Any]) -> Tuple[str, str]:
        """
        Analyze problem characteristics to determine type and complexity.
        
        Args:
            query_data: Data from the query processor stage
            semantic_model: Semantic analysis from the ATDB stage
            
        Returns:
            Tuple of (problem_type, complexity)
        """
        # Extract relevant information from inputs
        query_type = query_data.get("query_type", "unknown")
        entities = query_data.get("entities", [])
        relationships = query_data.get("relationships", [])
        constraints = query_data.get("constraints", [])
        
        # In a real implementation, we would use more sophisticated analysis
        # based on the semantic model, entity relationships, etc.
        
        # Simple logic for demonstration
        if "optimization" in query_type.lower():
            problem_type = "optimization"
        elif any(e.get("type") == "logical_concept" for e in entities):
            problem_type = "logical_reasoning"
        elif any(r.get("type") == "sequence" for r in relationships):
            problem_type = "sequential_decision"
        elif len(constraints) > 3:
            problem_type = "constraint_satisfaction"
        else:
            problem_type = "general_reasoning"
        
        # Determine complexity
        if len(entities) > 10 or len(relationships) > 15 or len(constraints) > 5:
            complexity = "high"
        elif len(entities) > 5 or len(relationships) > 7 or len(constraints) > 2:
            complexity = "medium"
        else:
            complexity = "low"
        
        logger.debug(f"Analyzed problem: type={problem_type}, complexity={complexity}")
        return problem_type, complexity
    
    def _select_strategies(self, problem_type: str, complexity: str, 
                          domain_knowledge: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Select appropriate reasoning strategies based on problem characteristics.
        
        Args:
            problem_type: Type of problem being addressed
            complexity: Problem complexity level
            domain_knowledge: Domain knowledge from previous stage
            
        Returns:
            List of selected strategy configurations
        """
        selected = []
        
        # Simple strategy selection logic based on problem type
        # In a real implementation, this would be more sophisticated
        
        # Map problem types to strategy categories
        type_strategy_map = {
            "optimization": ["mathematical_optimization", "heuristic_optimization"],
            "logical_reasoning": ["logical_reasoning"],
            "sequential_decision": ["reinforcement_learning"],
            "constraint_satisfaction": ["mathematical_optimization"],
            "general_reasoning": ["logical_reasoning", "numerical_methods"]
        }
        
        # Get strategies applicable to this problem type
        applicable_strategies = type_strategy_map.get(problem_type, ["logical_reasoning"])
        
        # For complex problems, add more strategies
        if complexity == "high" and "heuristic_optimization" not in applicable_strategies:
            applicable_strategies.append("heuristic_optimization")
        
        # Convert strategy IDs to full configurations
        for strategy_id in applicable_strategies:
            if strategy_id in self._available_strategies:
                selected.append(self._available_strategies[strategy_id])
        
        logger.debug(f"Selected {len(selected)} strategies for problem type {problem_type}")
        return selected
    
    def _apply_optimization(self, prompt: str, selected_strategies: List[Dict[str, Any]],
                           query_data: Dict[str, Any], semantic_model: Dict[str, Any],
                           domain_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply optimization techniques based on selected strategies.
        
        Args:
            prompt: Generated prompt for this stage
            selected_strategies: Strategy configurations to apply
            query_data: Data from the query processor stage
            semantic_model: Semantic analysis from the ATDB stage
            domain_knowledge: Knowledge from the domain knowledge stage
            
        Returns:
            Dictionary with optimization results
        """
        # In a real implementation, this would invoke specific optimization
        # algorithms based on the selected strategies
        
        strategy_names = [s["name"] for s in selected_strategies]
        techniques = []
        for strategy in selected_strategies:
            techniques.extend(strategy.get("techniques", []))
        
        # Use LLM to generate optimization steps based on the prompt and strategies
        optimization_prompt = self._generate_optimization_prompt(
            prompt, strategy_names, techniques, query_data, domain_knowledge
        )
        
        # Call LLM service
        llm_response = self._llm_service.generate_response(optimization_prompt)
        
        # Process the LLM response to extract structured optimization approach
        optimization_approach = self._process_optimization_response(llm_response)
        
        # Add metadata
        result = {
            "optimization_approach": optimization_approach,
            "applied_techniques": techniques,
            "iterations": 1,  # In a real implementation, this might be higher
            "strategy_application": {s["name"]: 0.8 for s in selected_strategies}  # Placeholder weights
        }
        
        return result
    
    def _reduce_biases(self, optimization_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply bias reduction methods to optimization results.
        
        Args:
            optimization_results: Results from optimization step
            
        Returns:
            Bias-reduced optimization results
        """
        # In a real implementation, this would apply specific bias reduction
        # techniques based on the detected biases in the optimization results
        
        # For demonstration, we'll add some simple bias reduction metadata
        optimization_results["bias_reduction"] = {
            "applied_methods": ["counterfactual_reasoning", "probabilistic_reasoning"],
            "identified_biases": ["confirmation_bias", "availability_bias"],
            "reduction_effectiveness": 0.75
        }
        
        return optimization_results
    
    def _evaluate_solutions(self, optimized_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate the quality and efficiency of generated solutions.
        
        Args:
            optimized_results: Results after optimization and bias reduction
            
        Returns:
            Evaluation metrics and assessments
        """
        # In a real implementation, this would compute specific metrics
        # to assess the quality of the optimized reasoning approach
        
        return {
            "validity_score": 0.92,
            "efficiency_score": 0.85,
            "robustness_score": 0.79,
            "bias_score": 0.15,  # Lower is better
            "overall_quality": 0.88
        }
    
    def _calculate_confidence(self, evaluation: Dict[str, Any]) -> float:
        """
        Calculate overall confidence in the optimization result.
        
        Args:
            evaluation: Result evaluation metrics
            
        Returns:
            Confidence score between 0 and 1
        """
        # Simple weighted average of evaluation metrics
        weights = {
            "validity_score": 0.4,
            "efficiency_score": 0.2,
            "robustness_score": 0.3,
            "bias_score": 0.1  # For bias, lower is better, so we'll invert
        }
        
        confidence = 0.0
        for metric, weight in weights.items():
            if metric in evaluation:
                value = evaluation[metric]
                if metric == "bias_score":
                    value = 1.0 - value  # Invert bias score
                confidence += value * weight
        
        return min(max(confidence, 0.0), 1.0)
    
    def _calculate_strategy_confidence(self, strategies: List[Dict[str, Any]]) -> float:
        """
        Calculate confidence in strategy selection.
        
        Args:
            strategies: Selected strategies
            
        Returns:
            Confidence score between 0 and 1
        """
        # More strategies generally means less confidence in any specific one
        if not strategies:
            return 0.0
        
        base_confidence = 0.9  # Start with high confidence
        strategy_penalty = 0.05 * (len(strategies) - 1)  # Penalty for multiple strategies
        
        return max(base_confidence - strategy_penalty, 0.5)  # Floor at 0.5
    
    def _get_applied_bias_methods(self, results: Dict[str, Any]) -> set:
        """
        Extract applied bias reduction methods from results.
        
        Args:
            results: Results with bias reduction information
            
        Returns:
            Set of bias reduction method names
        """
        bias_reduction = results.get("bias_reduction", {})
        method_ids = bias_reduction.get("applied_methods", [])
        
        return {self._bias_reduction_methods.get(m, {}).get("name", m) for m in method_ids}
    
    def _parse_refinement_focus(self, refinement_prompt: str) -> List[str]:
        """
        Parse refinement focus from refinement prompt.
        
        Args:
            refinement_prompt: Prompt for refinement
            
        Returns:
            List of focus areas for refinement
        """
        # In a real implementation, this would use NLP to understand
        # the specific aspects that need refinement
        
        focus_areas = []
        
        # Simple keyword matching for demonstration
        if "bias" in refinement_prompt.lower():
            focus_areas.append("bias_reduction")
        if "efficien" in refinement_prompt.lower():
            focus_areas.append("efficiency")
        if "optim" in refinement_prompt.lower():
            focus_areas.append("optimization_technique")
        if "strateg" in refinement_prompt.lower():
            focus_areas.append("strategy_selection")
        
        # Default if nothing specific is mentioned
        if not focus_areas:
            focus_areas.append("general_improvement")
        
        return focus_areas
    
    def _adjust_strategies(self, problem_type: str, refinement_focus: List[str],
                         previous_strategies: List[str]) -> List[Dict[str, Any]]:
        """
        Adjust strategies based on refinement focus.
        
        Args:
            problem_type: Type of problem being addressed
            refinement_focus: Focus areas for refinement
            previous_strategies: Previously applied strategies
            
        Returns:
            List of adjusted strategy configurations
        """
        # Convert previous strategy names to IDs
        prev_ids = set()
        for name in previous_strategies:
            for s_id, s_config in self._available_strategies.items():
                if s_config["name"] == name:
                    prev_ids.add(s_id)
        
        # Determine strategy adjustments based on focus
        new_strategy_ids = set(prev_ids)
        
        if "strategy_selection" in refinement_focus:
            # Try a different strategy mix
            if "mathematical_optimization" in prev_ids:
                new_strategy_ids.add("heuristic_optimization")
            elif "heuristic_optimization" in prev_ids:
                new_strategy_ids.add("mathematical_optimization")
            
            if "logical_reasoning" not in prev_ids and problem_type == "general_reasoning":
                new_strategy_ids.add("logical_reasoning")
        
        if "bias_reduction" in refinement_focus:
            # Always include logical reasoning for bias reduction
            new_strategy_ids.add("logical_reasoning")
        
        # Convert strategy IDs to full configurations
        adjusted_strategies = []
        for strategy_id in new_strategy_ids:
            if strategy_id in self._available_strategies:
                adjusted_strategies.append(self._available_strategies[strategy_id])
        
        return adjusted_strategies
    
    def _apply_refined_optimization(self, refinement_prompt: str, 
                                  adjusted_strategies: List[Dict[str, Any]],
                                  query_data: Dict[str, Any], 
                                  semantic_model: Dict[str, Any],
                                  domain_knowledge: Dict[str, Any],
                                  previous_approach: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply refined optimization based on feedback.
        
        Args:
            refinement_prompt: Prompt for refinement
            adjusted_strategies: Adjusted strategy configurations
            query_data: Data from the query processor stage
            semantic_model: Semantic analysis from the ATDB stage
            domain_knowledge: Knowledge from the domain knowledge stage
            previous_approach: Previous optimization approach
            
        Returns:
            Refined optimization results
        """
        # Similar to _apply_optimization but incorporates previous approach
        strategy_names = [s["name"] for s in adjusted_strategies]
        techniques = []
        for strategy in adjusted_strategies:
            techniques.extend(strategy.get("techniques", []))
        
        # Generate a refinement-specific prompt
        refinement_optimization_prompt = self._generate_refinement_prompt(
            refinement_prompt, 
            strategy_names, 
            techniques, 
            previous_approach
        )
        
        # Call LLM service
        llm_response = self._llm_service.generate_response(refinement_optimization_prompt)
        
        # Process the LLM response
        refined_approach = self._process_optimization_response(llm_response)
        
        # Combine with previous approach metadata
        result = {
            "optimization_approach": refined_approach,
            "applied_techniques": techniques,
            "iterations": previous_approach.get("iterations", 1) + 1,
            "strategy_application": {s["name"]: 0.9 for s in adjusted_strategies},  # Higher confidence in refinement
            "bias_reduction": {
                "applied_methods": ["counterfactual_reasoning", "perspective_diversification", 
                                   "probabilistic_reasoning"],
                "identified_biases": previous_approach.get("bias_reduction", {}).get("identified_biases", []),
                "reduction_effectiveness": 0.85  # Higher in refinement
            }
        }
        
        return result
    
    def _calculate_improvement(self, current_eval: Dict[str, Any], 
                             previous_eval: Dict[str, Any]) -> float:
        """
        Calculate improvement score between evaluations.
        
        Args:
            current_eval: Current evaluation metrics
            previous_eval: Previous evaluation metrics
            
        Returns:
            Improvement score (-1 to 1, where positive is improvement)
        """
        if not previous_eval:
            return 0.0
        
        # Compare key metrics
        metrics = ["validity_score", "efficiency_score", "robustness_score", "overall_quality"]
        improvements = []
        
        for metric in metrics:
            if metric in current_eval and metric in previous_eval:
                improvements.append(current_eval[metric] - previous_eval[metric])
        
        # Bias score is inverted (lower is better)
        if "bias_score" in current_eval and "bias_score" in previous_eval:
            improvements.append(previous_eval["bias_score"] - current_eval["bias_score"])
        
        if not improvements:
            return 0.0
            
        # Average improvement across metrics
        return sum(improvements) / len(improvements)
    
    def _generate_optimization_prompt(self, base_prompt: str, strategy_names: List[str], 
                                    techniques: List[str], query_data: Dict[str, Any],
                                    domain_knowledge: Dict[str, Any]) -> str:
        """
        Generate a prompt for optimization processing.
        
        Args:
            base_prompt: Original prompt for this stage
            strategy_names: Names of selected strategies
            techniques: Specific techniques to apply
            query_data: Data from query processor
            domain_knowledge: Domain knowledge from previous stage
            
        Returns:
            Optimization-specific prompt for LLM processing
        """
        # In a real implementation, this would be a more sophisticated prompt
        # template that incorporates all the relevant information
        
        strategies_text = ", ".join(strategy_names)
        techniques_text = ", ".join(techniques)
        
        return f"""
        {base_prompt}
        
        Apply the following reasoning optimization strategies: {strategies_text}
        Specifically utilize these techniques: {techniques_text}
        
        Analyze the problem and provide:
        1. A structured approach to solving it using the specified techniques
        2. Steps for implementing the solution
        3. Considerations for efficiency and robustness
        4. Potential biases in reasoning and how to mitigate them
        
        Return the optimized reasoning approach in a clear, structured format.
        """
    
    def _generate_refinement_prompt(self, refinement_prompt: str, strategy_names: List[str],
                                  techniques: List[str], previous_approach: Dict[str, Any]) -> str:
        """
        Generate a prompt for refinement processing.
        
        Args:
            refinement_prompt: Original refinement prompt
            strategy_names: Names of adjusted strategies
            techniques: Specific techniques to apply
            previous_approach: Previous optimization approach
            
        Returns:
            Refinement-specific prompt for LLM processing
        """
        strategies_text = ", ".join(strategy_names)
        techniques_text = ", ".join(techniques)
        
        # Extract previous approach summary
        prev_approach_text = "N/A"
        if "optimization_approach" in previous_approach:
            prev_approach_text = str(previous_approach["optimization_approach"])
        
        return f"""
        Refinement request: {refinement_prompt}
        
        Previous approach: {prev_approach_text}
        
        Apply these refined reasoning strategies: {strategies_text}
        Specifically utilize these techniques: {techniques_text}
        
        Improve the previous approach by:
        1. Addressing the specific refinement requests
        2. Enhancing the reasoning approach
        3. Reducing potential biases
        4. Increasing efficiency and robustness
        
        Return the refined reasoning approach in a clear, structured format.
        """
    
    def _process_optimization_response(self, llm_response: str) -> Dict[str, Any]:
        """
        Process LLM response into structured optimization approach.
        
        Args:
            llm_response: Raw response from LLM
            
        Returns:
            Structured optimization approach
        """
        # In a real implementation, this would parse the LLM response
        # into a well-structured optimization approach
        
        # For demonstration, we'll just return a simple structure
        return {
            "steps": [
                {"name": "Problem analysis", "description": "Analyze problem structure and constraints"},
                {"name": "Strategy application", "description": "Apply selected optimization techniques"},
                {"name": "Solution validation", "description": "Validate solution against constraints"},
                {"name": "Refinement", "description": "Refine solution for efficiency"}
            ],
            "rationale": "Structured approach based on problem characteristics",
            "implementation_guide": "Step-by-step implementation of the optimization strategy"
        } 