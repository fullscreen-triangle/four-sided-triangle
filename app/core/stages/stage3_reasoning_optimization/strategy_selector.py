"""
Strategy selector for the Reasoning Optimization stage.

This module provides functionality for selecting appropriate reasoning
strategies based on problem characteristics.
"""

import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

class StrategySelector:
    """
    Selects appropriate reasoning strategies based on problem characteristics.
    
    This class analyzes problems and selects the most appropriate reasoning
    strategies and optimization techniques to apply.
    """
    
    def __init__(self, available_strategies: Dict[str, Dict[str, Any]]):
        """
        Initialize the strategy selector.
        
        Args:
            available_strategies: Dictionary of available strategies and their configurations
        """
        self._available_strategies = available_strategies
        logger.info("Strategy selector initialized with %d strategies", len(available_strategies))
    
    def select_strategies(self, problem_type: str, complexity: str, 
                        domain_knowledge: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Select appropriate reasoning strategies based on problem characteristics.
        
        Args:
            problem_type: Type of problem being addressed
            complexity: Problem complexity level (low, medium, high)
            domain_knowledge: Domain knowledge relevant to the problem
            
        Returns:
            List of selected strategy configurations
        """
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
        
        # Apply domain-specific adjustments if available
        self._adjust_for_domain(applicable_strategies, domain_knowledge)
        
        # Convert strategy IDs to full configurations
        selected = []
        for strategy_id in applicable_strategies:
            if strategy_id in self._available_strategies:
                strategy = self._available_strategies[strategy_id].copy()
                strategy["confidence"] = self._calculate_confidence(strategy_id, problem_type, complexity)
                selected.append(strategy)
        
        # Sort strategies by confidence (highest first)
        selected.sort(key=lambda s: s.get("confidence", 0), reverse=True)
        
        logger.debug("Selected %d strategies for problem type %s (complexity: %s)",
                   len(selected), problem_type, complexity)
        return selected
    
    def _adjust_for_domain(self, strategies: List[str], domain_knowledge: Dict[str, Any]) -> None:
        """
        Adjust strategy selection based on domain knowledge.
        
        Args:
            strategies: List of strategy IDs to adjust (modified in place)
            domain_knowledge: Domain knowledge to consider
        """
        domain = domain_knowledge.get("domain", "")
        
        # Simple domain-specific adjustments
        if domain == "finance":
            if "mathematical_optimization" not in strategies:
                strategies.append("mathematical_optimization")
        elif domain == "healthcare":
            if "logical_reasoning" not in strategies:
                strategies.append("logical_reasoning")
        elif domain == "robotics" or domain == "control_systems":
            if "reinforcement_learning" not in strategies:
                strategies.append("reinforcement_learning")
    
    def _calculate_confidence(self, strategy_id: str, problem_type: str, complexity: str) -> float:
        """
        Calculate confidence score for a strategy's applicability.
        
        Args:
            strategy_id: Identifier for the strategy
            problem_type: Type of problem being addressed
            complexity: Problem complexity level
            
        Returns:
            Confidence score between 0 and 1
        """
        # Base confidence based on strategy-problem match
        base_matches = {
            ("mathematical_optimization", "optimization"): 0.9,
            ("mathematical_optimization", "constraint_satisfaction"): 0.85,
            ("heuristic_optimization", "optimization"): 0.8,
            ("heuristic_optimization", "complex_search"): 0.9,
            ("numerical_methods", "continuous_optimization"): 0.9,
            ("reinforcement_learning", "sequential_decision"): 0.95,
            ("logical_reasoning", "logical_reasoning"): 0.9,
            ("logical_reasoning", "general_reasoning"): 0.8
        }
        
        # Default confidence if not specifically defined
        confidence = base_matches.get((strategy_id, problem_type), 0.6)
        
        # Adjust based on complexity
        if strategy_id == "heuristic_optimization" and complexity == "high":
            confidence += 0.1
        elif strategy_id == "mathematical_optimization" and complexity == "low":
            confidence += 0.05
        
        return min(confidence, 1.0)  # Cap at 1.0
    
    def get_strategy_techniques(self, selected_strategies: List[Dict[str, Any]]) -> List[str]:
        """
        Get all techniques from selected strategies.
        
        Args:
            selected_strategies: List of selected strategy configurations
            
        Returns:
            List of all techniques from the selected strategies
        """
        techniques = []
        for strategy in selected_strategies:
            techniques.extend(strategy.get("techniques", []))
        
        return list(set(techniques))  # Remove duplicates
    
    def get_best_techniques_for_problem(self, problem_type: str, 
                                       complexity: str) -> List[Tuple[str, float]]:
        """
        Get the best techniques for a specific problem with confidence scores.
        
        Args:
            problem_type: Type of problem being addressed
            complexity: Problem complexity level
            
        Returns:
            List of (technique_name, confidence) tuples sorted by confidence
        """
        # Map problem types to technique recommendations with confidence
        technique_recommendations = {
            "optimization": [
                ("linear_programming", 0.9),
                ("genetic_algorithms", 0.75),
                ("gradient_descent", 0.7)
            ],
            "logical_reasoning": [
                ("deduction", 0.9),
                ("case_based_reasoning", 0.8),
                ("abduction", 0.7)
            ],
            "sequential_decision": [
                ("q_learning", 0.85),
                ("policy_gradients", 0.8),
                ("monte_carlo_tree_search", 0.75)
            ],
            "constraint_satisfaction": [
                ("constraint_satisfaction", 0.95),
                ("integer_programming", 0.85),
                ("simulated_annealing", 0.7)
            ],
            "general_reasoning": [
                ("deduction", 0.8),
                ("gradient_descent", 0.7),
                ("constraint_satisfaction", 0.65)
            ]
        }
        
        # Get base recommendations
        recommendations = technique_recommendations.get(problem_type, [])
        
        # Adjust for complexity
        if complexity == "high":
            # For high complexity, favor heuristic methods
            for i, (tech, conf) in enumerate(recommendations):
                if "genetic" in tech or "annealing" in tech or "swarm" in tech:
                    recommendations[i] = (tech, min(conf + 0.1, 1.0))
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return recommendations 