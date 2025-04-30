"""
Bias reduction module for the Reasoning Optimization stage.

This module provides functionality for identifying and mitigating cognitive
biases in reasoning approaches.
"""

import logging
from typing import Dict, Any, List, Tuple, Set

logger = logging.getLogger(__name__)

class BiasReducer:
    """
    Identifies and mitigates cognitive biases in reasoning processes.
    
    This class applies various debiasing techniques to improve the quality
    of reasoning approaches and reduce the impact of common cognitive biases.
    """
    
    def __init__(self, bias_reduction_methods: Dict[str, Dict[str, Any]]):
        """
        Initialize the bias reducer.
        
        Args:
            bias_reduction_methods: Dictionary of available methods and their configurations
        """
        self._bias_reduction_methods = bias_reduction_methods
        logger.info("Bias reducer initialized with %d methods", len(bias_reduction_methods))
    
    def identify_biases(self, approach: Dict[str, Any], problem_type: str) -> List[str]:
        """
        Identify potential cognitive biases in a reasoning approach.
        
        Args:
            approach: The reasoning approach to analyze
            problem_type: Type of problem being addressed
            
        Returns:
            List of identified potential biases
        """
        identified_biases = []
        
        # Common biases for different problem types
        problem_biases = {
            "optimization": ["anchoring_bias", "sunk_cost_fallacy", "availability_bias"],
            "logical_reasoning": ["confirmation_bias", "belief_bias", "framing_effect"],
            "sequential_decision": ["recency_bias", "gambler_fallacy", "hot_hand_fallacy"],
            "constraint_satisfaction": ["anchoring_bias", "base_rate_neglect"],
            "general_reasoning": ["confirmation_bias", "availability_bias", "authority_bias"]
        }
        
        # Add problem-specific biases
        identified_biases.extend(problem_biases.get(problem_type, ["confirmation_bias"]))
        
        # Check for additional biases based on approach characteristics
        # This would be much more sophisticated in a real implementation
        steps = approach.get("steps", [])
        step_names = [s.get("name", "").lower() for s in steps]
        
        if len(steps) < 3:
            identified_biases.append("neglect_of_probability")
        
        if not any("alternative" in s for s in step_names):
            identified_biases.append("confirmation_bias")
            
        if not any("probability" in s or "uncertain" in s for s in step_names):
            identified_biases.append("overconfidence_bias")
        
        return list(set(identified_biases))  # Remove duplicates
    
    def select_reduction_methods(self, identified_biases: List[str]) -> List[str]:
        """
        Select appropriate bias reduction methods for identified biases.
        
        Args:
            identified_biases: List of identified biases to address
            
        Returns:
            List of method IDs to apply
        """
        selected_methods = set()
        
        # Map biases to appropriate reduction methods
        for bias in identified_biases:
            for method_id, method_config in self._bias_reduction_methods.items():
                if bias in method_config.get("target_biases", []):
                    selected_methods.add(method_id)
        
        # Ensure we have at least one method
        if not selected_methods:
            selected_methods.add("structured_analysis")  # Default method
        
        logger.debug("Selected %d bias reduction methods for %d identified biases",
                   len(selected_methods), len(identified_biases))
        return list(selected_methods)
    
    def apply_bias_reduction(self, approach: Dict[str, Any], 
                            identified_biases: List[str]) -> Dict[str, Any]:
        """
        Apply bias reduction methods to the reasoning approach.
        
        Args:
            approach: The reasoning approach to improve
            identified_biases: List of identified biases to address
            
        Returns:
            Improved approach with reduced cognitive biases
        """
        # Select appropriate methods
        selected_methods = self.select_reduction_methods(identified_biases)
        
        # Create a copy of the approach to modify
        improved_approach = approach.copy()
        
        # Apply each selected method
        reduction_details = []
        for method_id in selected_methods:
            if method_id in self._bias_reduction_methods:
                method_name = self._bias_reduction_methods[method_id]["name"]
                method_description = self._bias_reduction_methods[method_id]["description"]
                
                # Record the application of this method
                reduction_details.append({
                    "method": method_name,
                    "targeted_biases": [b for b in identified_biases 
                                       if b in self._bias_reduction_methods[method_id].get("target_biases", [])],
                    "description": method_description
                })
                
                # Apply method-specific improvements
                # In a real implementation, this would make actual modifications
                # to the approach based on the specific method
                self._apply_specific_method(improved_approach, method_id)
        
        # Add bias reduction information to the approach
        improved_approach["bias_reduction"] = {
            "applied_methods": selected_methods,
            "identified_biases": identified_biases,
            "reduction_details": reduction_details,
            "reduction_effectiveness": self._estimate_effectiveness(selected_methods, identified_biases)
        }
        
        return improved_approach
    
    def _apply_specific_method(self, approach: Dict[str, Any], method_id: str) -> None:
        """
        Apply a specific bias reduction method to the approach.
        
        Args:
            approach: The approach to modify (modified in place)
            method_id: Identifier for the method to apply
        """
        # In a real implementation, this would apply specific modifications
        # based on the method. Here we'll just add placeholder improvements.
        
        steps = approach.get("steps", [])
        
        if method_id == "counterfactual_reasoning":
            # Add a counterfactual reasoning step
            steps.append({
                "name": "Consider alternative scenarios",
                "description": "Generate and evaluate counterfactual scenarios to challenge assumptions"
            })
        
        elif method_id == "perspective_diversification":
            # Add a perspective diversification step
            steps.append({
                "name": "Incorporate diverse perspectives",
                "description": "Consider the problem from multiple stakeholder viewpoints"
            })
        
        elif method_id == "probabilistic_reasoning":
            # Add a probabilistic reasoning step
            steps.append({
                "name": "Apply probabilistic analysis",
                "description": "Quantify uncertainty and update beliefs based on evidence"
            })
        
        elif method_id == "debiasing_techniques":
            # Add explicit debiasing
            steps.append({
                "name": "Apply debiasing techniques",
                "description": "Explicitly counter cognitive biases in the reasoning process"
            })
        
        elif method_id == "structured_analysis":
            # Add structured analysis
            steps.append({
                "name": "Apply structured analytical framework",
                "description": "Use a comprehensive framework to ensure thorough analysis"
            })
        
        # Update the steps in the approach
        approach["steps"] = steps
    
    def _estimate_effectiveness(self, methods: List[str], biases: List[str]) -> float:
        """
        Estimate the effectiveness of bias reduction methods.
        
        Args:
            methods: List of applied method IDs
            biases: List of identified biases
            
        Returns:
            Estimated effectiveness score between 0 and 1
        """
        if not biases:
            return 1.0  # No biases to reduce
        
        if not methods:
            return 0.0  # No methods applied
        
        # Count how many biases are targeted by the selected methods
        targeted_biases = set()
        for method_id in methods:
            if method_id in self._bias_reduction_methods:
                targeted_biases.update(
                    set(self._bias_reduction_methods[method_id].get("target_biases", [])) & set(biases)
                )
        
        # Calculate coverage ratio
        coverage_ratio = len(targeted_biases) / len(biases)
        
        # Method effectiveness factor (more methods generally means better coverage)
        method_factor = min(len(methods) / 3, 1.0)  # Cap at 1.0 after 3 methods
        
        # Combine factors with diminishing returns
        effectiveness = 0.5 + (coverage_ratio * 0.3) + (method_factor * 0.2)
        
        return min(effectiveness, 1.0)  # Cap at 1.0
    
    def get_bias_descriptions(self) -> Dict[str, str]:
        """
        Get descriptions of common cognitive biases.
        
        Returns:
            Dictionary mapping bias names to descriptions
        """
        return {
            "confirmation_bias": "The tendency to search for, interpret, and recall information that confirms existing beliefs",
            "availability_bias": "Overestimating the likelihood of events based on how easily examples come to mind",
            "anchoring_bias": "Relying too heavily on the first piece of information encountered (the anchor)",
            "authority_bias": "The tendency to attribute greater accuracy to the opinion of an authority figure",
            "sunk_cost_fallacy": "Continuing a behavior based on previously invested resources",
            "framing_effect": "Drawing different conclusions from the same information presented differently",
            "recency_bias": "Placing greater importance on recent events than those in the past",
            "gambler_fallacy": "Believing that past events affect the probability of future events in random processes",
            "hindsight_bias": "The tendency to perceive past events as having been predictable",
            "overconfidence_bias": "Excessive confidence in one's own answers to questions",
            "base_rate_neglect": "Ignoring general information in favor of specific information",
            "belief_bias": "Evaluating logical strength based on whether the conclusion is believable",
            "neglect_of_probability": "The tendency to disregard probability when making decisions",
            "bandwagon_effect": "The tendency to do or believe things because others do or believe them",
            "status_quo_bias": "Preference for the current state of affairs",
            "hot_hand_fallacy": "Believing that a person who has experienced success has a higher chance of success in further attempts"
        } 