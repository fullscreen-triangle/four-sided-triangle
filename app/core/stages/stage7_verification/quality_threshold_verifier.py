"""
Quality Threshold Verifier

This module contains the QualityThresholdVerifier class, which verifies 
that the response meets all quality thresholds defined in the configuration.
"""

import logging
import math
from typing import Dict, Any, List, Optional

class QualityThresholdVerifier:
    """
    Verifies that the response meets all quality thresholds defined in the configuration.
    
    This class implements quality verification logic including:
    - Dimension-specific quality checks
    - Threshold comparison with configurable strictness
    - Overall quality score calculation using a weighted approach
    - Detection and reporting of quality failures
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Quality Threshold Verifier.
        
        Args:
            config: Configuration dictionary for the quality threshold verifier
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Configuration parameters
        self.dimension_weights = self.config.get("dimension_weights", {
            "accuracy": 1.0,
            "completeness": 0.9,
            "consistency": 0.8,
            "relevance": 1.0,
            "novelty": 0.6
        })
        
        self.default_threshold = self.config.get("default_threshold", 0.7)
        self.threshold_tolerance = self.config.get("threshold_tolerance", 0.05)
        self.use_weighted_scoring = self.config.get("use_weighted_scoring", True)
        
        self.logger.info("Quality Threshold Verifier initialized")
    
    def verify(self, response: Dict[str, Any], quality_thresholds: Dict[str, float],
             required_dimensions: List[str]) -> Dict[str, Any]:
        """
        Verify that the response meets all quality thresholds.
        
        Args:
            response: The combined response to verify
            quality_thresholds: Dictionary mapping dimensions to threshold values
            required_dimensions: List of dimensions that must pass verification
            
        Returns:
            Verification results with dimension scores, failures, and overall assessment
        """
        self.logger.info("Verifying response against quality thresholds")
        
        # Extract quality metrics from response
        scoring_metrics = response.get("scoring_metrics", {})
        dimension_scores = self._extract_dimension_scores(response, scoring_metrics)
        
        # Apply thresholds with tolerance
        dimension_failures = {}
        for dimension in required_dimensions:
            threshold = quality_thresholds.get(dimension, self.default_threshold)
            score = dimension_scores.get(dimension, 0.0)
            
            # Check if dimension falls below threshold (with tolerance)
            if score < threshold - self.threshold_tolerance:
                dimension_failures[dimension] = {
                    "score": score,
                    "threshold": threshold,
                    "gap": threshold - score,
                    "is_required": dimension in required_dimensions
                }
        
        # Calculate overall verification score
        if self.use_weighted_scoring:
            overall_score = self._calculate_weighted_score(dimension_scores)
        else:
            overall_score = sum(dimension_scores.values()) / max(len(dimension_scores), 1)
        
        # Determine if verification passes
        passes_verification = len(dimension_failures) == 0
        
        # Additional verification metrics
        verification_results = {
            "passes_verification": passes_verification,
            "dimension_scores": dimension_scores,
            "dimension_failures": dimension_failures,
            "overall_score": overall_score,
            "metrics_used": list(dimension_scores.keys()),
            "threshold_tolerance_applied": self.threshold_tolerance,
            "verification_timestamp": self._get_timestamp()
        }
        
        self.logger.info(f"Verification complete: {'PASSED' if passes_verification else 'FAILED'}")
        return verification_results
    
    def _extract_dimension_scores(self, response: Dict[str, Any], scoring_metrics: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract quality dimension scores from the response.
        
        Args:
            response: The combined response
            scoring_metrics: Metrics from the scoring stage
            
        Returns:
            Dictionary mapping dimensions to scores
        """
        # Try to extract scores from different possible locations
        dimension_scores = {}
        
        # First check response_scoring output
        bayesian_scores = scoring_metrics.get("bayesian_framework", {})
        if bayesian_scores:
            dimension_scores = {
                "accuracy": bayesian_scores.get("accuracy", 0.0),
                "completeness": bayesian_scores.get("completeness", 0.0),
                "consistency": bayesian_scores.get("consistency", 0.0),
                "relevance": bayesian_scores.get("relevance", 0.0),
                "novelty": bayesian_scores.get("novelty", 0.0)
            }
            return dimension_scores
        
        # If not found, check for direct quality metrics
        quality_metrics = response.get("quality_metrics", scoring_metrics.get("quality_metrics", {}))
        if quality_metrics:
            return {k: float(v) if isinstance(v, (int, float)) else 0.0 
                   for k, v in quality_metrics.items()}
        
        # If still not found, extract from evaluation components if available
        evaluation = response.get("evaluation", {})
        if evaluation:
            component_scores = {}
            for dimension, value in evaluation.items():
                if isinstance(value, dict) and "score" in value:
                    component_scores[dimension] = float(value["score"])
                elif isinstance(value, (int, float)):
                    component_scores[dimension] = float(value)
            
            if component_scores:
                return component_scores
        
        # If no scores found, log warning and return empty dict
        self.logger.warning("Could not extract dimension scores from response")
        return {}
    
    def _calculate_weighted_score(self, dimension_scores: Dict[str, float]) -> float:
        """
        Calculate weighted overall score from dimension scores.
        
        Args:
            dimension_scores: Dictionary mapping dimensions to scores
            
        Returns:
            Weighted overall score
        """
        weighted_sum = 0.0
        weight_sum = 0.0
        
        for dimension, score in dimension_scores.items():
            weight = self.dimension_weights.get(dimension, 1.0)
            weighted_sum += score * weight
            weight_sum += weight
        
        if weight_sum == 0:
            return 0.0
            
        return weighted_sum / weight_sum
    
    def _get_timestamp(self) -> str:
        """Get the current timestamp as ISO format string."""
        from datetime import datetime
        return datetime.now().isoformat()

    def calculate_threshold_distance(self, dimension_scores: Dict[str, float], 
                                   quality_thresholds: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate the distance between each dimension score and its threshold.
        
        Args:
            dimension_scores: Dictionary mapping dimensions to scores
            quality_thresholds: Dictionary mapping dimensions to threshold values
            
        Returns:
            Dictionary mapping dimensions to threshold distances
        """
        threshold_distances = {}
        
        for dimension, score in dimension_scores.items():
            threshold = quality_thresholds.get(dimension, self.default_threshold)
            distance = score - threshold
            threshold_distances[dimension] = distance
        
        return threshold_distances

    def get_verification_summary(self, verification_results: Dict[str, Any]) -> str:
        """
        Get a human-readable summary of the verification results.
        
        Args:
            verification_results: The verification results
            
        Returns:
            Verification summary as a string
        """
        passes = verification_results.get("passes_verification", False)
        overall_score = verification_results.get("overall_score", 0.0)
        failures = verification_results.get("dimension_failures", {})
        
        if passes:
            return f"Verification PASSED with overall score: {overall_score:.2f}"
        else:
            failure_dimensions = list(failures.keys())
            if len(failure_dimensions) == 1:
                return f"Verification FAILED on dimension: {failure_dimensions[0]} with overall score: {overall_score:.2f}"
            else:
                dimensions_str = ", ".join(failure_dimensions)
                return f"Verification FAILED on dimensions: {dimensions_str} with overall score: {overall_score:.2f}" 