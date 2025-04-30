"""
Refinement Analyzer

This module analyzes quality scores and uncertainty metrics to determine if refinement
is needed and to prioritize specific areas for improvement.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple

class RefinementAnalyzer:
    """
    Analyzes quality scores and uncertainty metrics to determine refinement needs.
    
    This class evaluates whether a solution requires refinement based on quality
    thresholds and uncertainty levels, and prioritizes specific dimensions
    and components for improvement.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Refinement Analyzer.
        
        Args:
            config: Configuration dictionary for the analyzer
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Configure refinement parameters
        self.dimension_thresholds = self.config.get("dimension_thresholds", {
            "accuracy": 0.80,
            "completeness": 0.75,
            "consistency": 0.85,
            "relevance": 0.75,
            "novelty": 0.30
        })
        
        self.dimension_weights = self.config.get("dimension_weights", {
            "accuracy": 0.30,
            "completeness": 0.25,
            "consistency": 0.15,
            "relevance": 0.25,
            "novelty": 0.05
        })
        
        self.uncertainty_penalty = self.config.get("uncertainty_penalty", 0.1)
        self.max_refinement_items = self.config.get("max_refinement_items", 3)
        
        self.logger.info("Refinement Analyzer initialized")
    
    def analyze(self, quality_scores: Dict[str, float], 
              uncertainty_metrics: Dict[str, Any],
              threshold: float = 0.75) -> Dict[str, Any]:
        """
        Analyze quality scores and uncertainty metrics to determine refinement needs.
        
        Args:
            quality_scores: Scores for each quality dimension
            uncertainty_metrics: Uncertainty metrics for each dimension
            threshold: Overall quality threshold for refinement decision
            
        Returns:
            Dictionary with refinement analysis results
        """
        self.logger.info("Analyzing refinement needs")
        
        # Calculate dimension-specific refinement needs
        dimension_analysis = self._analyze_dimensions(quality_scores, uncertainty_metrics)
        
        # Calculate weighted quality score
        weighted_score = self._calculate_weighted_score(quality_scores)
        
        # Determine if refinement is needed based on:
        # 1. Overall weighted score vs threshold
        # 2. Critical dimension failures
        critical_dimensions = [dim for dim, analysis in dimension_analysis.items() 
                             if analysis["is_critical"] and analysis["needs_refinement"]]
        
        needs_refinement = (weighted_score < threshold) or bool(critical_dimensions)
        
        # Prioritize dimensions for refinement
        refinement_priority = self._prioritize_refinement(
            dimension_analysis, quality_scores, uncertainty_metrics)
        
        # Generate specific refinement suggestions
        refinement_suggestions = self._generate_suggestions(
            dimension_analysis, refinement_priority, quality_scores)
        
        # Construct refinement analysis result
        analysis_result = {
            "needs_refinement": needs_refinement,
            "weighted_score": weighted_score,
            "threshold": threshold,
            "dimension_analysis": dimension_analysis,
            "critical_failures": critical_dimensions,
            "refinement_priority": refinement_priority,
            "refinement_suggestions": refinement_suggestions
        }
        
        self.logger.info(f"Refinement analysis completed, needs refinement: {needs_refinement}")
        return analysis_result
    
    def _analyze_dimensions(self, quality_scores: Dict[str, float],
                         uncertainty_metrics: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze each quality dimension against its threshold.
        
        Args:
            quality_scores: Scores for each quality dimension
            uncertainty_metrics: Uncertainty metrics for each dimension
            
        Returns:
            Dictionary with analysis for each dimension
        """
        dimension_analysis = {}
        
        for dimension, score in quality_scores.items():
            threshold = self.dimension_thresholds.get(dimension, 0.7)
            weight = self.dimension_weights.get(dimension, 0.2)
            
            # Extract uncertainty metrics for this dimension
            dimension_uncertainty = uncertainty_metrics.get("dimensions", {}).get(dimension, {})
            confidence = dimension_uncertainty.get("confidence", 0.8)
            
            # Adjust effective score by applying uncertainty penalty
            uncertainty_adjustment = self.uncertainty_penalty * (1.0 - confidence)
            effective_score = max(0.0, score - uncertainty_adjustment)
            
            # Determine if this dimension needs refinement
            needs_refinement = effective_score < threshold
            
            # Determine if this is a critical dimension (high weight and below threshold)
            is_critical = weight >= 0.25 and needs_refinement
            
            # Calculate gap to threshold
            threshold_gap = threshold - effective_score if needs_refinement else 0.0
            
            # Store analysis for this dimension
            dimension_analysis[dimension] = {
                "score": score,
                "effective_score": effective_score,
                "threshold": threshold,
                "weight": weight,
                "confidence": confidence,
                "needs_refinement": needs_refinement,
                "is_critical": is_critical,
                "threshold_gap": threshold_gap,
                "uncertainty_adjustment": uncertainty_adjustment
            }
        
        return dimension_analysis
    
    def _calculate_weighted_score(self, quality_scores: Dict[str, float]) -> float:
        """
        Calculate weighted quality score across all dimensions.
        
        Args:
            quality_scores: Scores for each quality dimension
            
        Returns:
            Weighted quality score between 0 and 1
        """
        weighted_sum = 0.0
        weight_sum = 0.0
        
        for dimension, score in quality_scores.items():
            weight = self.dimension_weights.get(dimension, 0.0)
            weighted_sum += score * weight
            weight_sum += weight
        
        # Normalize by the sum of weights used
        return weighted_sum / weight_sum if weight_sum > 0 else 0.0
    
    def _prioritize_refinement(self, dimension_analysis: Dict[str, Dict[str, Any]],
                            quality_scores: Dict[str, float],
                            uncertainty_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Prioritize dimensions for refinement based on impact and feasibility.
        
        Args:
            dimension_analysis: Analysis for each dimension
            quality_scores: Scores for each quality dimension
            uncertainty_metrics: Uncertainty metrics for each dimension
            
        Returns:
            List of prioritized dimensions with refinement metrics
        """
        # Filter dimensions that need refinement
        needs_refinement = [
            (dimension, analysis) for dimension, analysis in dimension_analysis.items()
            if analysis["needs_refinement"]
        ]
        
        if not needs_refinement:
            return []
        
        # Calculate prioritization score for each dimension
        # This combines:
        # 1. Impact (weight × threshold gap)
        # 2. Feasibility (confidence in assessment)
        prioritized = []
        
        for dimension, analysis in needs_refinement:
            weight = analysis["weight"]
            threshold_gap = analysis["threshold_gap"]
            confidence = analysis["confidence"]
            
            # Higher score = higher priority for refinement
            impact = weight * threshold_gap
            feasibility = confidence * 0.5 + 0.5  # Scale to [0.5, 1.0] so low confidence doesn't eliminate possibility
            priority_score = impact * feasibility
            
            prioritized.append({
                "dimension": dimension,
                "priority_score": priority_score,
                "impact": impact,
                "feasibility": feasibility,
                "threshold_gap": threshold_gap
            })
        
        # Sort by priority score (highest first)
        prioritized.sort(key=lambda x: x["priority_score"], reverse=True)
        
        # Limit to max items
        return prioritized[:self.max_refinement_items]
    
    def _generate_suggestions(self, dimension_analysis: Dict[str, Dict[str, Any]],
                           refinement_priority: List[Dict[str, Any]],
                           quality_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Generate specific refinement suggestions for prioritized dimensions.
        
        Args:
            dimension_analysis: Analysis for each dimension
            refinement_priority: Prioritized list of dimensions for refinement
            quality_scores: Scores for each quality dimension
            
        Returns:
            List of specific refinement suggestions
        """
        suggestions = []
        
        # Generate dimension-specific suggestions
        for priority_item in refinement_priority:
            dimension = priority_item["dimension"]
            threshold_gap = priority_item["threshold_gap"]
            
            # Generate suggestion based on dimension type
            if dimension == "accuracy":
                suggestions.append({
                    "dimension": dimension,
                    "severity": "high" if threshold_gap > 0.2 else "medium",
                    "suggestion": "Verify factual correctness and align statements with domain knowledge",
                    "expected_improvement": min(0.3, threshold_gap * 1.5)
                })
            
            elif dimension == "completeness":
                suggestions.append({
                    "dimension": dimension,
                    "severity": "high" if threshold_gap > 0.15 else "medium",
                    "suggestion": "Include missing information elements and address all aspects of the query",
                    "expected_improvement": min(0.25, threshold_gap * 1.3)
                })
            
            elif dimension == "consistency":
                suggestions.append({
                    "dimension": dimension,
                    "severity": "medium",
                    "suggestion": "Resolve logical contradictions and improve structural coherence",
                    "expected_improvement": min(0.2, threshold_gap * 1.2)
                })
            
            elif dimension == "relevance":
                suggestions.append({
                    "dimension": dimension,
                    "severity": "high" if threshold_gap > 0.15 else "medium",
                    "suggestion": "Focus more directly on the specific query intent and user needs",
                    "expected_improvement": min(0.3, threshold_gap * 1.4)
                })
            
            elif dimension == "novelty":
                suggestions.append({
                    "dimension": dimension,
                    "severity": "low",
                    "suggestion": "Add non-obvious insights and connections between domain concepts",
                    "expected_improvement": min(0.15, threshold_gap * 1.1)
                })
        
        # Check for overall balance issues (if no specific dimensions are prioritized)
        if not suggestions and sum(quality_scores.values()) / len(quality_scores) < 0.7:
            suggestions.append({
                "dimension": "overall",
                "severity": "medium",
                "suggestion": "Improve overall quality by restructuring and enriching the response",
                "expected_improvement": 0.15
            })
        
        return suggestions 