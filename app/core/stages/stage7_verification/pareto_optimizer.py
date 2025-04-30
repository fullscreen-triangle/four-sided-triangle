"""
Pareto Optimizer

This module contains the ParetoOptimizer class, which implements Pareto optimization
to identify dominated response components and ensure optimal trade-offs.
"""

import logging
import numpy as np
from typing import Dict, Any, List, Tuple, Set, Optional

class ParetoOptimizer:
    """
    Applies Pareto optimization to identify dominated components in the response.
    
    This class implements Pareto efficiency analysis to:
    - Identify the Pareto frontier of response components
    - Determine dominated components that can be pruned
    - Calculate dominance relationships between components
    - Optimize for multi-objective trade-offs
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Pareto Optimizer.
        
        Args:
            config: Configuration dictionary for the Pareto optimizer
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Configuration parameters
        self.objectives = self.config.get("objectives", ["accuracy", "completeness", "consistency", "relevance"])
        self.min_component_quality = self.config.get("min_component_quality", 0.5)
        self.dominance_threshold = self.config.get("dominance_threshold", 0.1)
        self.include_diversity = self.config.get("include_diversity", True)
        
        self.logger.info("Pareto Optimizer initialized")
    
    def optimize(self, response: Dict[str, Any], verification_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply Pareto optimization to response components.
        
        Args:
            response: The combined response
            verification_results: Results from quality threshold verification
            
        Returns:
            Pareto analysis results including dominated components and Pareto frontier
        """
        self.logger.info("Applying Pareto optimization")
        
        # Extract response components 
        components = self._extract_components(response)
        component_scores = self._extract_component_scores(components, verification_results)
        
        if not component_scores:
            self.logger.warning("No valid component scores found for Pareto analysis")
            return {"error": "No valid component scores", "dominated_components": []}
        
        # Identify Pareto frontier and dominated components
        pareto_frontier, dominated_components = self._find_pareto_frontier(component_scores)
        
        # Calculate dominance relationships
        dominance_relationships = self._calculate_dominance_relationships(component_scores)
        
        # Prepare analysis results
        analysis_results = {
            "pareto_frontier": list(pareto_frontier),
            "dominated_components": list(dominated_components),
            "dominance_relationships": dominance_relationships,
            "component_scores": component_scores,
            "objectives_used": self.objectives,
            "summary": self._generate_summary(pareto_frontier, dominated_components, component_scores)
        }
        
        self.logger.info(f"Pareto analysis complete: {len(pareto_frontier)} components in frontier, "
                       f"{len(dominated_components)} dominated components")
        return analysis_results
    
    def _extract_components(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract individual components from the response.
        
        Args:
            response: The combined response
            
        Returns:
            Dictionary mapping component IDs to component data
        """
        # Look for components in different possible locations
        components = {}
        
        # Try content components
        content_components = response.get("content_components", {})
        if content_components:
            return content_components
        
        # Try response components
        response_components = response.get("components", {})
        if response_components:
            return response_components
        
        # Try information elements
        info_elements = response.get("information_elements", {})
        if info_elements:
            return info_elements
        
        # If no structured components, create artificial components from the response content
        response_content = response.get("content", response.get("response", ""))
        if isinstance(response_content, str) and response_content:
            # Create a single component for the whole response
            components["full_response"] = {
                "content": response_content,
                "type": "text",
                "weight": 1.0
            }
            return components
        
        # If still no components found, return an empty dict
        self.logger.warning("Could not extract components from response")
        return {}
    
    def _extract_component_scores(self, components: Dict[str, Any], 
                                verification_results: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """
        Extract quality scores for each component.
        
        Args:
            components: Dictionary of response components
            verification_results: Results from quality threshold verification
            
        Returns:
            Dictionary mapping component IDs to quality dimension scores
        """
        component_scores = {}
        
        # Look for component-specific scores
        for component_id, component_data in components.items():
            # Try to get scores directly from component data
            quality_scores = component_data.get("quality_scores", component_data.get("metrics", {}))
            
            if quality_scores:
                # Filter to only include our objectives
                filtered_scores = {obj: float(quality_scores.get(obj, 0.0)) 
                                 for obj in self.objectives 
                                 if obj in quality_scores}
                
                # Only include components with scores for all objectives
                if len(filtered_scores) == len(self.objectives):
                    component_scores[component_id] = filtered_scores
                    continue
            
            # If no component-specific scores, use response-level scores for all components
            dimension_scores = verification_results.get("dimension_scores", {})
            if dimension_scores:
                component_scores[component_id] = {
                    obj: dimension_scores.get(obj, 0.0) for obj in self.objectives
                }
        
        return component_scores
    
    def _find_pareto_frontier(self, component_scores: Dict[str, Dict[str, float]]) -> Tuple[Set[str], Set[str]]:
        """
        Find the Pareto frontier and dominated components.
        
        Args:
            component_scores: Dictionary mapping component IDs to objective scores
            
        Returns:
            Tuple of (Pareto frontier components, dominated components)
        """
        component_ids = list(component_scores.keys())
        n_components = len(component_ids)
        
        if n_components <= 1:
            # With 0 or 1 components, everything is on the frontier
            return set(component_ids), set()
        
        # Initialize sets for Pareto frontier and dominated components
        pareto_frontier = set(component_ids)
        dominated = set()
        
        # Perform pairwise comparisons to identify dominated components
        for i in range(n_components):
            component_i = component_ids[i]
            scores_i = component_scores[component_i]
            
            if component_i in dominated:
                continue
                
            for j in range(n_components):
                if i == j:
                    continue
                    
                component_j = component_ids[j]
                scores_j = component_scores[component_j]
                
                if self._dominates(scores_j, scores_i):
                    # Component j dominates component i
                    dominated.add(component_i)
                    if component_i in pareto_frontier:
                        pareto_frontier.remove(component_i)
                    break
        
        # Ensure every component is either in frontier or dominated
        all_components = set(component_ids)
        missing = all_components - (pareto_frontier | dominated)
        pareto_frontier.update(missing)
        
        return pareto_frontier, dominated
    
    def _dominates(self, scores_a: Dict[str, float], scores_b: Dict[str, float]) -> bool:
        """
        Check if scores_a dominates scores_b in the Pareto sense.
        
        For dominance, scores_a must be at least as good as scores_b in all objectives,
        and strictly better in at least one objective.
        
        Args:
            scores_a: Objective scores for component A
            scores_b: Objective scores for component B
            
        Returns:
            True if scores_a dominates scores_b, False otherwise
        """
        # Initialize flags
        at_least_as_good = True
        strictly_better = False
        
        # Check each objective
        for obj in self.objectives:
            score_a = scores_a.get(obj, 0.0)
            score_b = scores_b.get(obj, 0.0)
            
            # A must be at least as good as B in all objectives
            if score_a < score_b - self.dominance_threshold:
                at_least_as_good = False
                break
                
            # A must be strictly better than B in at least one objective
            if score_a > score_b + self.dominance_threshold:
                strictly_better = True
        
        return at_least_as_good and strictly_better
    
    def _calculate_dominance_relationships(self, component_scores: Dict[str, Dict[str, float]]) -> List[Dict[str, Any]]:
        """
        Calculate dominance relationships between all components.
        
        Args:
            component_scores: Dictionary mapping component IDs to objective scores
            
        Returns:
            List of dominance relationships
        """
        component_ids = list(component_scores.keys())
        relationships = []
        
        for i, component_i in enumerate(component_ids):
            scores_i = component_scores[component_i]
            
            for j, component_j in enumerate(component_ids):
                if i == j:
                    continue
                    
                scores_j = component_scores[component_j]
                
                if self._dominates(scores_i, scores_j):
                    # Calculate dominance strength
                    dominance_strength = self._calculate_dominance_strength(scores_i, scores_j)
                    
                    relationships.append({
                        "dominant": component_i,
                        "dominated": component_j,
                        "strength": dominance_strength,
                        "objectives": self._get_dominating_objectives(scores_i, scores_j)
                    })
        
        # Sort relationships by strength (descending)
        return sorted(relationships, key=lambda x: x["strength"], reverse=True)
    
    def _calculate_dominance_strength(self, scores_a: Dict[str, float], scores_b: Dict[str, float]) -> float:
        """
        Calculate the strength of dominance of scores_a over scores_b.
        
        Args:
            scores_a: Objective scores for component A
            scores_b: Objective scores for component B
            
        Returns:
            Dominance strength as a float
        """
        total_advantage = 0.0
        
        for obj in self.objectives:
            score_a = scores_a.get(obj, 0.0)
            score_b = scores_b.get(obj, 0.0)
            
            # Sum the advantages across all objectives
            advantage = max(0.0, score_a - score_b)
            total_advantage += advantage
        
        return total_advantage / max(len(self.objectives), 1)
    
    def _get_dominating_objectives(self, scores_a: Dict[str, float], scores_b: Dict[str, float]) -> List[str]:
        """
        Get the list of objectives where scores_a dominates scores_b.
        
        Args:
            scores_a: Objective scores for component A
            scores_b: Objective scores for component B
            
        Returns:
            List of dominating objectives
        """
        dominating_objectives = []
        
        for obj in self.objectives:
            score_a = scores_a.get(obj, 0.0)
            score_b = scores_b.get(obj, 0.0)
            
            if score_a > score_b + self.dominance_threshold:
                dominating_objectives.append(obj)
        
        return dominating_objectives
    
    def _generate_summary(self, pareto_frontier: Set[str], dominated_components: Set[str],
                        component_scores: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        Generate a summary of the Pareto analysis.
        
        Args:
            pareto_frontier: Set of component IDs in the Pareto frontier
            dominated_components: Set of dominated component IDs
            component_scores: Dictionary mapping component IDs to objective scores
            
        Returns:
            Summary dictionary
        """
        # Calculate average scores for frontier vs dominated components
        frontier_scores = {obj: 0.0 for obj in self.objectives}
        dominated_scores = {obj: 0.0 for obj in self.objectives}
        
        # Sum scores for frontier components
        for component_id in pareto_frontier:
            scores = component_scores.get(component_id, {})
            for obj in self.objectives:
                frontier_scores[obj] += scores.get(obj, 0.0)
        
        # Calculate averages for frontier components
        if pareto_frontier:
            for obj in self.objectives:
                frontier_scores[obj] /= len(pareto_frontier)
        
        # Sum scores for dominated components
        for component_id in dominated_components:
            scores = component_scores.get(component_id, {})
            for obj in self.objectives:
                dominated_scores[obj] += scores.get(obj, 0.0)
        
        # Calculate averages for dominated components
        if dominated_components:
            for obj in self.objectives:
                dominated_scores[obj] /= len(dominated_components)
        
        return {
            "frontier_size": len(pareto_frontier),
            "dominated_size": len(dominated_components),
            "frontier_avg_scores": frontier_scores,
            "dominated_avg_scores": dominated_scores,
            "efficiency_gain": self._calculate_efficiency_gain(frontier_scores, dominated_scores)
        }
    
    def _calculate_efficiency_gain(self, frontier_scores: Dict[str, float], 
                                 dominated_scores: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate the efficiency gain from using only frontier components.
        
        Args:
            frontier_scores: Average scores for frontier components
            dominated_scores: Average scores for dominated components
            
        Returns:
            Dictionary mapping objectives to efficiency gains
        """
        efficiency_gain = {}
        
        for obj in self.objectives:
            frontier_score = frontier_scores.get(obj, 0.0)
            dominated_score = dominated_scores.get(obj, 0.0)
            
            if dominated_score > 0:
                gain = (frontier_score / dominated_score) - 1.0
            else:
                gain = 0.0 if frontier_score == 0 else float('inf')
                
            efficiency_gain[obj] = gain
        
        # Add overall gain (average across objectives)
        valid_gains = [g for g in efficiency_gain.values() if not np.isinf(g)]
        efficiency_gain["overall"] = sum(valid_gains) / max(len(valid_gains), 1)
        
        return efficiency_gain 