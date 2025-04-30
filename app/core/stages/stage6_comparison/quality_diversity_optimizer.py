"""
Quality-Diversity Optimizer

This module implements optimization of the quality-diversity trade-off
in the response ensemble, balancing between response quality and diversity.
"""

import logging
import math
from typing import Dict, Any, List, Optional, Set, Tuple

class QualityDiversityOptimizer:
    """
    Optimizes the balance between quality and diversity in the response ensemble.
    
    This class applies Pareto optimization techniques to find the optimal
    trade-off between response quality and diversity, identifying components
    that maximize both objectives.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Quality-Diversity Optimizer.
        
        Args:
            config: Configuration dictionary for the optimizer
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Configure optimization parameters
        self.quality_weight = self.config.get("quality_weight", 0.7)
        self.diversity_weight = self.config.get("diversity_weight", 0.3)
        self.pareto_threshold = self.config.get("pareto_threshold", 0.05)
        self.min_quality_threshold = self.config.get("min_quality_threshold", 0.3)
        
        # Store trade-off metrics for reference
        self.trade_off_metrics = {}
        
        self.logger.info("Quality-Diversity Optimizer initialized")
    
    def optimize(self, ensemble: List[Dict[str, Any]], 
               evaluation_metrics: Dict[str, Any],
               diversity_scores: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize the quality-diversity trade-off in the response ensemble.
        
        Args:
            ensemble: List of response candidates in the ensemble
            evaluation_metrics: Evaluation metrics from response scoring
            diversity_scores: Diversity scores between responses
            
        Returns:
            Dictionary of optimized components for response combination
        """
        self.logger.info("Optimizing quality-diversity trade-off")
        
        # Reset trade-off metrics
        self.trade_off_metrics = {
            "pareto_optimal_components": 0,
            "quality_range": (0.0, 0.0),
            "diversity_range": (0.0, 0.0),
            "trade_off_balance": self.quality_weight / self.diversity_weight
        }
        
        # If ensemble is empty or has only one response, return that response
        if not ensemble:
            return {}
        
        if len(ensemble) == 1:
            return {
                "primary_response": ensemble[0],
                "component_weights": {0: 1.0},
                "optimized_elements": self._extract_elements(ensemble[0]),
                "optimization_metrics": {
                    "quality_score": 1.0,
                    "diversity_score": 0.0,
                    "combined_score": self.quality_weight
                }
            }
        
        # Extract quality scores for each candidate
        candidate_quality = self._extract_quality_scores(ensemble, evaluation_metrics)
        
        # Extract pairwise diversity scores
        pairwise_diversity = diversity_scores.get("pairwise_scores", {})
        
        # Calculate average diversity for each candidate
        candidate_diversity = self._calculate_candidate_diversity(ensemble, pairwise_diversity)
        
        # Apply Pareto optimization to identify non-dominated components
        pareto_optimal = self._identify_pareto_optimal(ensemble, candidate_quality, candidate_diversity)
        
        # Select optimal elements from across the ensemble
        optimized_elements = self._select_optimal_elements(ensemble, pareto_optimal, 
                                                       candidate_quality, candidate_diversity)
        
        # Calculate component weights for response combination
        component_weights = self._calculate_component_weights(ensemble, candidate_quality, 
                                                          candidate_diversity, pareto_optimal)
        
        # Store trade-off metrics
        if candidate_quality:
            self.trade_off_metrics["quality_range"] = (min(candidate_quality.values()), 
                                                   max(candidate_quality.values()))
        if candidate_diversity:
            self.trade_off_metrics["diversity_range"] = (min(candidate_diversity.values()), 
                                                     max(candidate_diversity.values()))
        
        self.trade_off_metrics["pareto_optimal_components"] = len(pareto_optimal)
        
        # Construct optimization result
        optimization_result = {
            "primary_response": ensemble[0] if ensemble else {},
            "component_weights": component_weights,
            "optimized_elements": optimized_elements,
            "pareto_optimal_indices": pareto_optimal,
            "optimization_metrics": {
                "quality_scores": candidate_quality,
                "diversity_scores": candidate_diversity,
                "pareto_optimal_count": len(pareto_optimal)
            }
        }
        
        self.logger.info(f"Quality-diversity optimization completed with {len(pareto_optimal)} Pareto optimal components")
        return optimization_result
    
    def get_trade_off_metrics(self) -> Dict[str, Any]:
        """
        Get the trade-off metrics from the last optimization.
        
        Returns:
            Dictionary of trade-off metrics
        """
        return self.trade_off_metrics
    
    def _extract_quality_scores(self, ensemble: List[Dict[str, Any]],
                              evaluation_metrics: Dict[str, Any]) -> Dict[int, float]:
        """
        Extract quality scores for each candidate in the ensemble.
        
        Args:
            ensemble: List of response candidates
            evaluation_metrics: Evaluation metrics from response scoring
            
        Returns:
            Dictionary mapping candidate indices to quality scores
        """
        quality_scores = {}
        
        # Primary response (index 0) quality is based on evaluation metrics
        overall_score = evaluation_metrics.get("overall_score", 0.8)
        quality_scores[0] = overall_score
        
        # For alternatives, use their quality_score if available, or scale down from primary
        for i in range(1, len(ensemble)):
            if "quality_score" in ensemble[i]:
                quality_scores[i] = ensemble[i]["quality_score"]
            else:
                # Scale quality based on position in ensemble
                decay_factor = 0.15 * i
                quality_scores[i] = max(self.min_quality_threshold, 
                                     overall_score - decay_factor)
        
        # Normalize quality scores to [0, 1] range
        max_quality = max(quality_scores.values()) if quality_scores else 1.0
        if max_quality > 0:
            for i in quality_scores:
                quality_scores[i] = quality_scores[i] / max_quality
        
        return quality_scores
    
    def _calculate_candidate_diversity(self, ensemble: List[Dict[str, Any]],
                                    pairwise_diversity: Dict[str, float]) -> Dict[int, float]:
        """
        Calculate average diversity score for each candidate.
        
        Args:
            ensemble: List of response candidates
            pairwise_diversity: Pairwise diversity scores between candidates
            
        Returns:
            Dictionary mapping candidate indices to diversity scores
        """
        diversity_scores = {}
        n_candidates = len(ensemble)
        
        # For each candidate, calculate average diversity to all others
        for i in range(n_candidates):
            diversity_sum = 0.0
            comparisons = 0
            
            # Sum diversity scores with all other candidates
            for j in range(n_candidates):
                if i != j:
                    pair_key = f"{min(i, j)}-{max(i, j)}"
                    if pair_key in pairwise_diversity:
                        diversity_sum += pairwise_diversity[pair_key]
                        comparisons += 1
            
            # Calculate average diversity
            if comparisons > 0:
                diversity_scores[i] = diversity_sum / comparisons
            else:
                diversity_scores[i] = 0.0
        
        # Normalize diversity scores to [0, 1] range
        max_diversity = max(diversity_scores.values()) if diversity_scores else 1.0
        if max_diversity > 0:
            for i in diversity_scores:
                diversity_scores[i] = diversity_scores[i] / max_diversity
        
        return diversity_scores
    
    def _identify_pareto_optimal(self, ensemble: List[Dict[str, Any]],
                              quality_scores: Dict[int, float],
                              diversity_scores: Dict[int, float]) -> List[int]:
        """
        Identify Pareto-optimal components in the quality-diversity space.
        
        Args:
            ensemble: List of response candidates
            quality_scores: Quality score for each candidate
            diversity_scores: Diversity score for each candidate
            
        Returns:
            List of indices of Pareto-optimal candidates
        """
        candidates = list(range(len(ensemble)))
        pareto_optimal = []
        
        # Check each candidate for Pareto optimality
        for i in candidates:
            is_dominated = False
            
            # A candidate is dominated if there exists another candidate
            # that is better in at least one dimension and not worse in any dimension
            for j in candidates:
                if i == j:
                    continue
                
                quality_i = quality_scores.get(i, 0.0)
                quality_j = quality_scores.get(j, 0.0)
                
                diversity_i = diversity_scores.get(i, 0.0)
                diversity_j = diversity_scores.get(j, 0.0)
                
                # Check if j dominates i
                if ((quality_j > quality_i + self.pareto_threshold or 
                    abs(quality_j - quality_i) <= self.pareto_threshold) and
                    (diversity_j > diversity_i + self.pareto_threshold or 
                    abs(diversity_j - diversity_i) <= self.pareto_threshold) and
                    (quality_j > quality_i + self.pareto_threshold or 
                    diversity_j > diversity_i + self.pareto_threshold)):
                    is_dominated = True
                    break
            
            # If not dominated, add to Pareto-optimal set
            if not is_dominated:
                pareto_optimal.append(i)
        
        # Always include primary response (index 0) if not already included
        if 0 not in pareto_optimal:
            pareto_optimal.insert(0, 0)
        
        return pareto_optimal
    
    def _select_optimal_elements(self, ensemble: List[Dict[str, Any]],
                              pareto_optimal: List[int],
                              quality_scores: Dict[int, float],
                              diversity_scores: Dict[int, float]) -> List[Dict[str, Any]]:
        """
        Select optimal elements from across the ensemble.
        
        Args:
            ensemble: List of response candidates
            pareto_optimal: List of indices of Pareto-optimal candidates
            quality_scores: Quality score for each candidate
            diversity_scores: Diversity score for each candidate
            
        Returns:
            List of optimized elements
        """
        optimized_elements = []
        element_ids = set()
        
        # First, extract elements from the primary response
        primary_elements = self._extract_elements(ensemble[0])
        for elem in primary_elements:
            elem_id = elem.get("id")
            if elem_id and elem_id not in element_ids:
                elem["source_response"] = 0
                elem["quality_score"] = quality_scores.get(0, 1.0)
                optimized_elements.append(elem)
                element_ids.add(elem_id)
        
        # Then, extract elements from other Pareto-optimal candidates
        for i in pareto_optimal:
            if i == 0:  # Skip primary (already processed)
                continue
                
            # Get elements from this candidate
            candidate_elements = self._extract_elements(ensemble[i])
            
            # Add elements not already included
            for elem in candidate_elements:
                elem_id = elem.get("id")
                # Only add elements with unique IDs
                if elem_id and elem_id not in element_ids:
                    elem["source_response"] = i
                    elem["quality_score"] = quality_scores.get(i, 0.5)
                    elem["diversity_value"] = diversity_scores.get(i, 0.5)
                    optimized_elements.append(elem)
                    element_ids.add(elem_id)
        
        # Calculate weighted scores and sort elements by it
        for elem in optimized_elements:
            quality = elem.get("quality_score", 0.5)
            diversity = elem.get("diversity_value", 0.5)
            relevance = elem.get("relevance", 0.5)
            
            weighted_score = (
                quality * self.quality_weight + 
                diversity * self.diversity_weight + 
                relevance * 0.3
            )
            
            elem["weighted_score"] = weighted_score
        
        # Sort elements by weighted score (descending)
        optimized_elements.sort(key=lambda x: x.get("weighted_score", 0), reverse=True)
        
        return optimized_elements
    
    def _calculate_component_weights(self, ensemble: List[Dict[str, Any]],
                                  quality_scores: Dict[int, float],
                                  diversity_scores: Dict[int, float],
                                  pareto_optimal: List[int]) -> Dict[int, float]:
        """
        Calculate weights for each component in the ensemble.
        
        Args:
            ensemble: List of response candidates
            quality_scores: Quality score for each candidate
            diversity_scores: Diversity score for each candidate
            pareto_optimal: List of indices of Pareto-optimal candidates
            
        Returns:
            Dictionary mapping candidate indices to weights
        """
        component_weights = {}
        
        # Calculate weight based on weighted sum of quality and diversity
        for i in pareto_optimal:
            quality = quality_scores.get(i, 0.5)
            diversity = diversity_scores.get(i, 0.5)
            
            # Weighted sum
            weight = quality * self.quality_weight + diversity * self.diversity_weight
            component_weights[i] = weight
        
        # Ensure primary response has significant weight
        if 0 in component_weights:
            # Boost primary response weight to ensure it has at least 40% weight
            primary_weight = component_weights[0]
            total_weight = sum(component_weights.values())
            
            if total_weight > 0 and primary_weight / total_weight < 0.4:
                boost_factor = (0.4 * total_weight) / primary_weight
                component_weights[0] = primary_weight * boost_factor
        
        # Normalize weights
        total_weight = sum(component_weights.values())
        if total_weight > 0:
            for i in component_weights:
                component_weights[i] = component_weights[i] / total_weight
        elif component_weights:
            # If weights are all zero, distribute evenly
            equal_weight = 1.0 / len(component_weights)
            for i in component_weights:
                component_weights[i] = equal_weight
        
        return component_weights
    
    def _extract_elements(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract elements from a response.
        
        Args:
            response: Response dictionary
            
        Returns:
            List of elements from the response
        """
        content = response.get("content", {})
        elements = content.get("elements", [])
        
        # Make a deep copy to avoid modifying the original
        copied_elements = []
        for elem in elements:
            elem_copy = dict(elem)
            copied_elements.append(elem_copy)
        
        return copied_elements 