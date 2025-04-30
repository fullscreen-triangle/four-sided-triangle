"""
Solution evaluator for the Reasoning Optimization stage.

This module provides functionality for evaluating the quality and efficiency
of generated solutions.
"""

import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

class SolutionEvaluator:
    """
    Evaluates the quality and efficiency of generated solutions.
    
    This class provides methods for assessing solution validity, efficiency,
    robustness, and overall quality.
    """
    
    def __init__(self):
        """Initialize the solution evaluator."""
        logger.info("Solution evaluator initialized")
    
    def evaluate_solution(self, solution: Dict[str, Any], problem_type: str, 
                         complexity: str) -> Dict[str, Any]:
        """
        Evaluate a solution for overall quality.
        
        Args:
            solution: The solution to evaluate
            problem_type: Type of problem being addressed
            complexity: Problem complexity level
            
        Returns:
            Dictionary of evaluation metrics
        """
        # Calculate individual metrics
        validity_score = self.evaluate_validity(solution, problem_type)
        efficiency_score = self.evaluate_efficiency(solution, complexity)
        robustness_score = self.evaluate_robustness(solution)
        bias_score = self.evaluate_bias(solution)
        
        # Calculate overall quality from the individual metrics
        overall_quality = self._calculate_overall_quality(
            validity_score, efficiency_score, robustness_score, bias_score
        )
        
        # Compile and return evaluation metrics
        evaluation = {
            "validity_score": validity_score,
            "efficiency_score": efficiency_score,
            "robustness_score": robustness_score,
            "bias_score": bias_score,  # Lower is better
            "overall_quality": overall_quality
        }
        
        logger.debug("Evaluated solution: overall_quality=%.2f", overall_quality)
        return evaluation
    
    def evaluate_validity(self, solution: Dict[str, Any], problem_type: str) -> float:
        """
        Evaluate solution validity (correctness and completeness).
        
        Args:
            solution: The solution to evaluate
            problem_type: Type of problem being addressed
            
        Returns:
            Validity score between 0 and 1
        """
        # In a real implementation, this would perform detailed analysis based
        # on the problem type and solution characteristics
        
        # Basic validity checks
        steps = solution.get("steps", [])
        
        # More steps generally indicates better completeness
        completeness = min(len(steps) / 5, 1.0)  # Cap at 1.0 after 5 steps
        
        # Check for key elements in solution based on problem type
        correctness = 0.7  # Default baseline
        
        if problem_type == "optimization":
            if any("constraint" in str(s).lower() for s in steps):
                correctness += 0.1
            if any("objective" in str(s).lower() for s in steps):
                correctness += 0.1
        
        elif problem_type == "logical_reasoning":
            if any("premise" in str(s).lower() for s in steps):
                correctness += 0.1
            if any("conclusion" in str(s).lower() for s in steps):
                correctness += 0.1
        
        elif problem_type == "sequential_decision":
            if any("sequence" in str(s).lower() for s in steps):
                correctness += 0.1
            if any("outcome" in str(s).lower() for s in steps):
                correctness += 0.1
        
        # Combine completeness and correctness
        validity = (0.6 * correctness) + (0.4 * completeness)
        
        return min(validity, 1.0)  # Cap at 1.0
    
    def evaluate_efficiency(self, solution: Dict[str, Any], complexity: str) -> float:
        """
        Evaluate solution efficiency (computational and implementational).
        
        Args:
            solution: The solution to evaluate
            complexity: Problem complexity level
            
        Returns:
            Efficiency score between 0 and 1
        """
        # In a real implementation, this would analyze algorithm complexity,
        # resource usage, etc.
        
        # Basic efficiency estimation
        steps = solution.get("steps", [])
        
        # Baseline efficiency based on complexity
        if complexity == "high":
            base_efficiency = 0.7  # High complexity problems tend to have less efficient solutions
        elif complexity == "medium":
            base_efficiency = 0.8
        else:
            base_efficiency = 0.9  # Low complexity problems can be solved efficiently
        
        # Check for efficiency indicators in the solution
        efficiency_bonus = 0.0
        
        efficiency_keywords = ["efficient", "optimize", "streamline", "simplify", "reduce"]
        for keyword in efficiency_keywords:
            if any(keyword in str(s).lower() for s in steps):
                efficiency_bonus += 0.02  # Small bonus for each efficiency indicator
        
        # Excessive steps may indicate inefficiency
        if len(steps) > 7:
            efficiency_penalty = 0.05 * ((len(steps) - 7) / 3)  # Penalty for too many steps
        else:
            efficiency_penalty = 0.0
        
        efficiency = base_efficiency + efficiency_bonus - efficiency_penalty
        
        return min(max(efficiency, 0.0), 1.0)  # Clamp between 0 and 1
    
    def evaluate_robustness(self, solution: Dict[str, Any]) -> float:
        """
        Evaluate solution robustness (stability and error handling).
        
        Args:
            solution: The solution to evaluate
            
        Returns:
            Robustness score between 0 and 1
        """
        # In a real implementation, this would analyze how well the solution
        # handles edge cases, errors, and unexpected inputs
        
        # Basic robustness checks
        steps = solution.get("steps", [])
        
        # Baseline robustness
        base_robustness = 0.6
        
        # Check for robustness indicators
        robustness_bonus = 0.0
        
        robustness_keywords = ["validate", "verify", "check", "handle", "robust", 
                             "error", "exception", "edge case"]
        for keyword in robustness_keywords:
            if any(keyword in str(s).lower() for s in steps):
                robustness_bonus += 0.025  # Small bonus for each robustness indicator
        
        # Check for validation step
        if any("validat" in str(s).lower() for s in steps):
            robustness_bonus += 0.1  # Significant bonus for explicit validation
        
        robustness = base_robustness + robustness_bonus
        
        return min(robustness, 1.0)  # Cap at 1.0
    
    def evaluate_bias(self, solution: Dict[str, Any]) -> float:
        """
        Evaluate cognitive bias in the solution.
        
        Args:
            solution: The solution to evaluate
            
        Returns:
            Bias score between 0 and 1 (lower is better)
        """
        # Check if bias reduction has been applied
        bias_reduction = solution.get("bias_reduction", {})
        applied_methods = bias_reduction.get("applied_methods", [])
        identified_biases = bias_reduction.get("identified_biases", [])
        
        # Default bias score
        if not identified_biases:
            return 0.05  # Low bias score if no biases identified
        
        # Calculate bias score based on reduction effectiveness
        reduction_effectiveness = bias_reduction.get("reduction_effectiveness", 0.0)
        
        # More identified biases means higher potential bias
        base_bias = min(0.2 + (len(identified_biases) * 0.05), 0.5)
        
        # Apply reduction effectiveness
        reduced_bias = base_bias * (1.0 - reduction_effectiveness)
        
        return min(max(reduced_bias, 0.05), 0.5)  # Clamp between 0.05 and 0.5
    
    def _calculate_overall_quality(self, validity: float, efficiency: float, 
                                 robustness: float, bias: float) -> float:
        """
        Calculate overall quality from individual metrics.
        
        Args:
            validity: Validity score
            efficiency: Efficiency score
            robustness: Robustness score
            bias: Bias score (lower is better)
            
        Returns:
            Overall quality score between 0 and 1
        """
        # Weights for different aspects
        weights = {
            "validity": 0.4,    # Correctness is most important
            "efficiency": 0.25,  # Efficiency is quite important
            "robustness": 0.25,  # Robustness is equally important
            "bias": 0.1         # Bias is less weighted but still counts
        }
        
        # For bias, lower is better, so we invert it
        bias_factor = 1.0 - bias
        
        # Weighted average
        overall = (weights["validity"] * validity +
                  weights["efficiency"] * efficiency +
                  weights["robustness"] * robustness +
                  weights["bias"] * bias_factor)
        
        return overall
    
    def get_improvement_recommendations(self, evaluation: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations for improving a solution based on evaluation.
        
        Args:
            evaluation: Evaluation metrics for a solution
            
        Returns:
            List of improvement recommendations
        """
        recommendations = []
        
        # Check validity score
        validity = evaluation.get("validity_score", 0.0)
        if validity < 0.7:
            recommendations.append("Improve solution completeness by addressing all aspects of the problem")
        
        # Check efficiency score
        efficiency = evaluation.get("efficiency_score", 0.0)
        if efficiency < 0.7:
            recommendations.append("Enhance solution efficiency by reducing unnecessary steps")
        
        # Check robustness score
        robustness = evaluation.get("robustness_score", 0.0)
        if robustness < 0.7:
            recommendations.append("Increase solution robustness by adding validation and error handling")
        
        # Check bias score
        bias = evaluation.get("bias_score", 0.0)
        if bias > 0.2:
            recommendations.append("Reduce cognitive bias by applying additional debiasing techniques")
        
        # If all metrics are good but overall is still not excellent
        overall = evaluation.get("overall_quality", 0.0)
        if overall < 0.85 and len(recommendations) == 0:
            recommendations.append("Fine-tune the balance between validity, efficiency, and robustness")
        
        return recommendations 