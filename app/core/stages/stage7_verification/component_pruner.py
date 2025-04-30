"""
Component Pruner

This module contains the ComponentPruner class, which prunes suboptimal components
from the response based on Pareto analysis and quality thresholds.
"""

import logging
from typing import Dict, Any, List, Set, Optional

class ComponentPruner:
    """
    Prunes suboptimal components from the response.
    
    This class implements pruning logic including:
    - Removing dominated components identified by Pareto analysis
    - Pruning low-quality components that don't meet minimum thresholds
    - Applying conservative pruning to maintain content integrity
    - Restructuring the response after pruning
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Component Pruner.
        
        Args:
            config: Configuration dictionary for the component pruner
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Configuration parameters
        self.min_quality_threshold = self.config.get("min_quality_threshold", 0.4)
        self.max_pruning_fraction = self.config.get("max_pruning_fraction", 0.5)
        self.preserve_important_keywords = self.config.get("preserve_important_keywords", True)
        self.content_overlap_threshold = self.config.get("content_overlap_threshold", 0.7)
        self.conservative_pruning = self.config.get("conservative_pruning", True)
        
        # Keywords that should prevent pruning a component
        self.important_keywords = self.config.get("important_keywords", [
            "conclusion", "summary", "recommendation", "diagnosis", "analysis",
            "key finding", "critical", "essential", "vital", "crucial"
        ])
        
        self.logger.info("Component Pruner initialized")
    
    def prune(self, response: Dict[str, Any], pareto_analysis: Dict[str, Any],
            verification_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prune suboptimal components from the response.
        
        Args:
            response: The combined response
            pareto_analysis: Results from Pareto optimization
            verification_results: Results from quality threshold verification
            
        Returns:
            Pruned response with suboptimal components removed
        """
        self.logger.info("Pruning suboptimal components")
        
        # Extract components to prune from Pareto analysis
        dominated_components = set(pareto_analysis.get("dominated_components", []))
        component_scores = pareto_analysis.get("component_scores", {})
        
        # Find additional components to prune based on quality thresholds
        low_quality_components = self._identify_low_quality_components(
            component_scores, verification_results)
        
        # Combine and filter components to prune
        candidates_to_prune = dominated_components.union(low_quality_components)
        components_to_prune = self._filter_pruning_candidates(
            candidates_to_prune, response, component_scores)
        
        if not components_to_prune:
            self.logger.info("No components selected for pruning")
            return response
        
        # Create a deep copy of the response to modify
        pruned_response = self._deep_copy_response(response)
        
        # Perform the actual pruning
        self._remove_components(pruned_response, components_to_prune)
        
        # Restructure the response after pruning
        pruned_response = self._restructure_response(pruned_response, components_to_prune)
        
        # Add pruning metadata
        pruned_response["pruning_metadata"] = {
            "pruned_components": list(components_to_prune),
            "original_component_count": len(component_scores),
            "remaining_component_count": len(component_scores) - len(components_to_prune),
            "pruning_ratio": len(components_to_prune) / max(len(component_scores), 1),
            "pruning_timestamp": self._get_timestamp()
        }
        
        self.logger.info(f"Pruned {len(components_to_prune)} components from response")
        return pruned_response
    
    def _identify_low_quality_components(self, component_scores: Dict[str, Dict[str, float]],
                                       verification_results: Dict[str, Any]) -> Set[str]:
        """
        Identify components with quality scores below the minimum threshold.
        
        Args:
            component_scores: Dictionary mapping component IDs to objective scores
            verification_results: Results from quality threshold verification
            
        Returns:
            Set of component IDs that don't meet minimum quality
        """
        low_quality_components = set()
        
        # Extract dimension weights for calculating overall quality
        dimension_weights = verification_results.get("dimension_weights", {})
        if not dimension_weights:
            # Default to equal weights if not provided
            dimensions = set()
            for scores in component_scores.values():
                dimensions.update(scores.keys())
            dimension_weights = {dim: 1.0 for dim in dimensions}
        
        # Check each component's quality
        for component_id, scores in component_scores.items():
            overall_quality = self._calculate_overall_quality(scores, dimension_weights)
            
            if overall_quality < self.min_quality_threshold:
                low_quality_components.add(component_id)
                self.logger.debug(f"Component {component_id} below quality threshold: {overall_quality:.2f}")
        
        return low_quality_components
    
    def _calculate_overall_quality(self, scores: Dict[str, float], 
                                 dimension_weights: Dict[str, float]) -> float:
        """
        Calculate overall quality score for a component using weighted average.
        
        Args:
            scores: Quality dimension scores for the component
            dimension_weights: Weights for each quality dimension
            
        Returns:
            Overall quality score
        """
        weighted_sum = 0.0
        weight_sum = 0.0
        
        for dimension, score in scores.items():
            weight = dimension_weights.get(dimension, 1.0)
            weighted_sum += score * weight
            weight_sum += weight
        
        if weight_sum == 0:
            return 0.0
            
        return weighted_sum / weight_sum
    
    def _filter_pruning_candidates(self, candidates: Set[str], response: Dict[str, Any],
                                component_scores: Dict[str, Dict[str, float]]) -> Set[str]:
        """
        Filter pruning candidates to avoid excessive pruning or removing important content.
        
        Args:
            candidates: Set of component IDs that are candidates for pruning
            response: The combined response
            component_scores: Dictionary mapping component IDs to objective scores
            
        Returns:
            Filtered set of component IDs to prune
        """
        if not candidates:
            return set()
            
        # Get component map from response
        components = self._extract_components(response)
        
        # Check if pruning would exceed max fraction
        if len(candidates) / max(len(component_scores), 1) > self.max_pruning_fraction:
            self.logger.info("Too many components selected for pruning, limiting pruning")
            # Keep only the lowest quality components
            sorted_candidates = sorted(
                candidates,
                key=lambda c: self._calculate_overall_quality(
                    component_scores.get(c, {}), {}
                )
            )
            max_to_prune = int(len(component_scores) * self.max_pruning_fraction)
            candidates = set(sorted_candidates[:max_to_prune])
        
        if self.conservative_pruning:
            # Conservative mode: further filter candidates
            filtered_candidates = set()
            
            for component_id in candidates:
                component = components.get(component_id, {})
                
                # Skip components with important keywords
                if self.preserve_important_keywords and self._contains_important_keywords(component):
                    self.logger.debug(f"Preserving component {component_id} due to important keywords")
                    continue
                
                # Additional conservative checks
                if self._is_safe_to_prune(component_id, components, component_scores):
                    filtered_candidates.add(component_id)
            
            return filtered_candidates
        
        return candidates
    
    def _contains_important_keywords(self, component: Dict[str, Any]) -> bool:
        """
        Check if component content contains any important keywords.
        
        Args:
            component: Component data
            
        Returns:
            True if important keywords are found, False otherwise
        """
        if not self.important_keywords:
            return False
            
        # Get component content
        content = component.get("content", "")
        if not isinstance(content, str):
            return False
            
        # Check for important keywords (case-insensitive)
        content_lower = content.lower()
        for keyword in self.important_keywords:
            if keyword.lower() in content_lower:
                return True
                
        return False
    
    def _is_safe_to_prune(self, component_id: str, components: Dict[str, Any],
                        component_scores: Dict[str, Dict[str, float]]) -> bool:
        """
        Determine if it's safe to prune a component without losing critical information.
        
        Args:
            component_id: ID of the component to check
            components: Dictionary of all components
            component_scores: Dictionary mapping component IDs to objective scores
            
        Returns:
            True if safe to prune, False otherwise
        """
        component = components.get(component_id, {})
        
        # Prevent pruning if component has a high relevance score
        scores = component_scores.get(component_id, {})
        relevance = scores.get("relevance", 0.0)
        if relevance > 0.8:  # Don't prune highly relevant components
            return False
            
        # Check content overlap with other components
        if self.content_overlap_threshold > 0:
            component_content = component.get("content", "")
            if isinstance(component_content, str) and component_content:
                for other_id, other_component in components.items():
                    if other_id == component_id or other_id in component_scores:
                        continue
                        
                    other_content = other_component.get("content", "")
                    if isinstance(other_content, str) and other_content:
                        overlap = self._calculate_content_overlap(component_content, other_content)
                        if overlap > self.content_overlap_threshold:
                            # Content is redundant, safe to prune
                            return True
        
        # Default to safe if we've come this far
        return True
    
    def _calculate_content_overlap(self, content_a: str, content_b: str) -> float:
        """
        Calculate the content overlap between two text strings.
        
        This is a simple implementation using token overlap. More sophisticated
        methods like semantic similarity could be used in a production environment.
        
        Args:
            content_a: First content string
            content_b: Second content string
            
        Returns:
            Overlap score between 0.0 and 1.0
        """
        if not content_a or not content_b:
            return 0.0
            
        # Simple tokenization by splitting on whitespace
        tokens_a = set(content_a.lower().split())
        tokens_b = set(content_b.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(tokens_a.intersection(tokens_b))
        union = len(tokens_a.union(tokens_b))
        
        if union == 0:
            return 0.0
            
        return intersection / union
    
    def _deep_copy_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a deep copy of the response dictionary.
        
        Args:
            response: The original response
            
        Returns:
            Deep copy of the response
        """
        import copy
        return copy.deepcopy(response)
    
    def _extract_components(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract components from the response.
        
        Args:
            response: The response
            
        Returns:
            Dictionary mapping component IDs to component data
        """
        # Look for components in different possible locations
        content_components = response.get("content_components", {})
        if content_components:
            return content_components
        
        response_components = response.get("components", {})
        if response_components:
            return response_components
        
        info_elements = response.get("information_elements", {})
        if info_elements:
            return info_elements
        
        return {}
    
    def _remove_components(self, response: Dict[str, Any], components_to_prune: Set[str]) -> None:
        """
        Remove the specified components from the response.
        
        Args:
            response: The response to modify
            components_to_prune: Set of component IDs to remove
        """
        # Remove from content_components
        content_components = response.get("content_components", {})
        if content_components:
            for component_id in components_to_prune:
                if component_id in content_components:
                    del content_components[component_id]
        
        # Remove from components
        components = response.get("components", {})
        if components:
            for component_id in components_to_prune:
                if component_id in components:
                    del components[component_id]
        
        # Remove from information_elements
        info_elements = response.get("information_elements", {})
        if info_elements:
            for component_id in components_to_prune:
                if component_id in info_elements:
                    del info_elements[component_id]
    
    def _restructure_response(self, response: Dict[str, Any], pruned_components: Set[str]) -> Dict[str, Any]:
        """
        Restructure the response after pruning to maintain coherence.
        
        Args:
            response: The response after component removal
            pruned_components: Set of component IDs that were pruned
            
        Returns:
            Restructured response
        """
        # Regenerate the main content based on remaining components
        components = self._extract_components(response)
        
        if "content" in response:
            # If there's a full text content field, generate a new version
            # that excludes the pruned components
            new_content = []
            
            for component_id, component in components.items():
                component_content = component.get("content", "")
                if component_content and isinstance(component_content, str):
                    new_content.append(component_content)
            
            # Join with line breaks and set as new content
            if new_content:
                response["content"] = "\n\n".join(new_content)
        
        # Update any component indices or ordering
        if "component_order" in response:
            response["component_order"] = [
                comp_id for comp_id in response["component_order"]
                if comp_id not in pruned_components
            ]
        
        # Update component count
        if "component_count" in response:
            response["component_count"] = len(components)
        
        return response
    
    def _get_timestamp(self) -> str:
        """Get the current timestamp as ISO format string."""
        from datetime import datetime
        return datetime.now().isoformat() 