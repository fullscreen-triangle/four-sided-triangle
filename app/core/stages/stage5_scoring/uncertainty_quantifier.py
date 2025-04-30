"""
Uncertainty Quantifier

This module implements uncertainty quantification for quality assessment components,
providing confidence bounds and variance estimates for quality scores.
"""

import logging
import math
from typing import Dict, Any, List, Optional, Tuple

class UncertaintyQuantifier:
    """
    Quantifies uncertainty in quality assessment of generated solutions.
    
    This class analyzes the confidence and variance in quality scores,
    providing uncertainty bounds and confidence intervals for each
    quality dimension.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Uncertainty Quantifier.
        
        Args:
            config: Configuration dictionary for the quantifier
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Configure uncertainty parameters
        self.confidence_level = self.config.get("confidence_level", 0.95)
        self.min_confidence_margin = self.config.get("min_confidence_margin", 0.05)
        self.max_confidence_margin = self.config.get("max_confidence_margin", 0.2)
        self.dimension_variance_priors = self.config.get("dimension_variance_priors", {
            "accuracy": 0.04,
            "completeness": 0.06,
            "consistency": 0.03,
            "relevance": 0.05,
            "novelty": 0.08
        })
        
        self.logger.info("Uncertainty Quantifier initialized")
    
    def quantify(self, solution: Dict[str, Any], quality_scores: Dict[str, float],
               bayesian_metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Quantify uncertainty in quality scores.
        
        Args:
            solution: The generated solution
            quality_scores: Scores for each quality dimension
            bayesian_metrics: Metrics from Bayesian evaluation
            
        Returns:
            Dictionary of uncertainty metrics for each quality dimension
        """
        self.logger.info("Quantifying uncertainty in quality assessment")
        
        uncertainty_metrics = {}
        
        # Calculate overall confidence based on Bayesian posterior
        posterior_probability = bayesian_metrics.get("posterior_probability", 0.5)
        overall_confidence = self._calculate_overall_confidence(posterior_probability)
        
        # Process each quality dimension
        for dimension, score in quality_scores.items():
            uncertainty_metrics[dimension] = self._quantify_dimension_uncertainty(
                dimension, 
                score, 
                solution, 
                bayesian_metrics
            )
        
        # Add aggregate uncertainty metrics
        aggregate_uncertainty = {
            "overall_confidence": overall_confidence,
            "average_confidence_interval": self._calculate_average_interval(uncertainty_metrics),
            "highest_uncertainty_dimension": self._find_highest_uncertainty(uncertainty_metrics),
            "confidence_level": self.confidence_level
        }
        
        # Combine dimension-specific and aggregate metrics
        combined_metrics = {
            "dimensions": uncertainty_metrics,
            "aggregate": aggregate_uncertainty
        }
        
        self.logger.info(f"Uncertainty quantification completed with overall confidence: {overall_confidence:.4f}")
        return combined_metrics
    
    def _quantify_dimension_uncertainty(self, dimension: str, score: float, 
                                     solution: Dict[str, Any],
                                     bayesian_metrics: Dict[str, float]) -> Dict[str, float]:
        """
        Quantify uncertainty for a specific quality dimension.
        
        Args:
            dimension: The quality dimension name
            score: The quality score for this dimension
            solution: The generated solution
            bayesian_metrics: Metrics from Bayesian evaluation
            
        Returns:
            Dictionary of uncertainty metrics for this dimension
        """
        # Get prior variance for this dimension
        prior_variance = self.dimension_variance_priors.get(dimension, 0.05)
        
        # Adjust variance based on solution complexity and available evidence
        solution_complexity = self._estimate_solution_complexity(solution)
        evidence_strength = self._estimate_evidence_strength(dimension, solution, bayesian_metrics)
        
        # Calculate adjusted variance: increases with complexity, decreases with evidence
        adjusted_variance = prior_variance * (solution_complexity / evidence_strength)
        
        # Ensure variance is within reasonable bounds
        adjusted_variance = max(0.01, min(0.25, adjusted_variance))
        
        # Calculate confidence interval
        margin = self._calculate_confidence_margin(adjusted_variance)
        lower_bound = max(0.0, score - margin)
        upper_bound = min(1.0, score + margin)
        
        # Calculate confidence level (inverse relationship with variance)
        confidence = 1.0 - (adjusted_variance * 2)
        confidence = max(0.1, min(0.99, confidence))
        
        # Return uncertainty metrics for this dimension
        return {
            "score": score,
            "variance": adjusted_variance,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "confidence": confidence
        }
    
    def _calculate_confidence_margin(self, variance: float) -> float:
        """
        Calculate confidence margin for a given variance.
        
        Uses a simplified approach based on the normal distribution.
        
        Args:
            variance: Estimated variance for the quality score
            
        Returns:
            Confidence margin (half-width of confidence interval)
        """
        # For 95% confidence on normal distribution, use ~1.96 standard deviations
        # For simplicity, we approximate with 2.0
        z_score = 2.0 if self.confidence_level >= 0.95 else 1.65
        
        # Calculate standard deviation and margin
        std_dev = math.sqrt(variance)
        margin = z_score * std_dev
        
        # Ensure margin is within configured bounds
        margin = max(self.min_confidence_margin, min(self.max_confidence_margin, margin))
        
        return margin
    
    def _calculate_overall_confidence(self, posterior_probability: float) -> float:
        """
        Calculate overall confidence based on Bayesian posterior.
        
        Args:
            posterior_probability: The posterior probability from Bayesian evaluation
            
        Returns:
            Overall confidence score between 0 and 1
        """
        # Posterior closer to 0 or 1 indicates higher confidence
        # Use distance from 0.5 (maximum uncertainty) as confidence measure
        certainty = abs(posterior_probability - 0.5) * 2.0  # Scale to [0, 1]
        
        # Apply non-linear transformation for more intuitive confidence values
        # This favors higher confidence values
        confidence = 0.5 + (certainty * 0.5)
        
        return confidence
    
    def _estimate_solution_complexity(self, solution: Dict[str, Any]) -> float:
        """
        Estimate the complexity of the solution.
        
        Higher complexity leads to higher uncertainty.
        
        Args:
            solution: The generated solution
            
        Returns:
            Complexity factor between 0.5 and 2.0
        """
        # Extract solution elements and structure
        solution_elements = solution.get("content", {}).get("elements", [])
        solution_sections = solution.get("content", {}).get("sections", [])
        
        if not solution_elements:
            return 1.0  # Default complexity
            
        # Factors that increase complexity:
        # 1. Number of elements
        element_count = len(solution_elements)
        element_factor = min(2.0, element_count / 10)  # Normalize to [0, 2]
        
        # 2. Number of sections
        section_count = len(solution_sections) if solution_sections else 0
        section_factor = min(1.5, section_count / 4)  # Normalize to [0, 1.5]
        
        # 3. Types of elements (variety increases complexity)
        element_types = set(elem.get("type", "") for elem in solution_elements)
        type_factor = min(1.5, len(element_types) / 3)  # Normalize to [0, 1.5]
        
        # Combine factors with weights
        complexity = (0.5 * element_factor + 0.3 * section_factor + 0.2 * type_factor)
        
        # Ensure result is within reasonable bounds
        return max(0.5, min(2.0, complexity))
    
    def _estimate_evidence_strength(self, dimension: str, solution: Dict[str, Any],
                                  bayesian_metrics: Dict[str, float]) -> float:
        """
        Estimate the strength of available evidence for a dimension.
        
        Higher evidence strength leads to lower uncertainty.
        
        Args:
            dimension: The quality dimension name
            solution: The generated solution
            bayesian_metrics: Metrics from Bayesian evaluation
            
        Returns:
            Evidence strength factor between 0.5 and 2.0
        """
        # Base evidence strength starts at 1.0
        base_strength = 1.0
        
        # Adjust based on Bayesian metrics
        likelihood = bayesian_metrics.get("likelihood", 0.5)
        evidence_factor = bayesian_metrics.get("evidence_factor", 0.5)
        
        # Different dimensions are affected by different evidence types
        if dimension == "accuracy":
            # Accuracy is strongly affected by likelihood
            strength = base_strength * (0.5 + likelihood)
        elif dimension == "completeness":
            # Completeness is affected by evidence factor
            strength = base_strength * (0.5 + evidence_factor)
        elif dimension == "consistency":
            # Consistency has more inherent uncertainty
            strength = base_strength * 0.8
        elif dimension == "relevance":
            # Relevance is affected by mutual information
            mutual_info = bayesian_metrics.get("mutual_information", 0.0)
            strength = base_strength * (0.7 + (mutual_info * 0.6))
        elif dimension == "novelty":
            # Novelty has high inherent uncertainty
            strength = base_strength * 0.7
        else:
            strength = base_strength
        
        # Ensure result is within reasonable bounds
        return max(0.5, min(2.0, strength))
    
    def _calculate_average_interval(self, uncertainty_metrics: Dict[str, Dict[str, float]]) -> float:
        """
        Calculate the average width of confidence intervals across dimensions.
        
        Args:
            uncertainty_metrics: Uncertainty metrics for each dimension
            
        Returns:
            Average confidence interval width
        """
        if not uncertainty_metrics:
            return 0.0
            
        interval_widths = []
        
        for dimension, metrics in uncertainty_metrics.items():
            upper = metrics.get("upper_bound", 0.0)
            lower = metrics.get("lower_bound", 0.0)
            interval_widths.append(upper - lower)
        
        return sum(interval_widths) / len(interval_widths) if interval_widths else 0.0
    
    def _find_highest_uncertainty(self, uncertainty_metrics: Dict[str, Dict[str, float]]) -> Tuple[str, float]:
        """
        Find the dimension with highest uncertainty.
        
        Args:
            uncertainty_metrics: Uncertainty metrics for each dimension
            
        Returns:
            Tuple of (dimension_name, uncertainty_value)
        """
        if not uncertainty_metrics:
            return ("unknown", 0.0)
            
        highest_dim = None
        highest_uncertainty = -1.0
        
        for dimension, metrics in uncertainty_metrics.items():
            variance = metrics.get("variance", 0.0)
            if variance > highest_uncertainty:
                highest_uncertainty = variance
                highest_dim = dimension
        
        return (highest_dim or "unknown", highest_uncertainty) 