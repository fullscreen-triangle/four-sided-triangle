"""
Threshold Verification Service

This module contains the ThresholdVerificationService class, which orchestrates
the process of verifying the combined response against quality thresholds and
applying Pareto optimization techniques.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple

from app.core.stages.stage7_verification.quality_threshold_verifier import QualityThresholdVerifier
from app.core.stages.stage7_verification.pareto_optimizer import ParetoOptimizer 
from app.core.stages.stage7_verification.component_pruner import ComponentPruner
from app.core.stages.stage7_verification.response_finalizer import ResponseFinalizer
from app.orchestrator.interfaces import AbstractPipelineStage

class ThresholdVerificationService(AbstractPipelineStage):
    """
    Orchestrates the threshold verification process by verifying quality thresholds,
    applying Pareto optimization, pruning suboptimal components, and finalizing
    the response for delivery.
    
    This service integrates quality threshold verification, Pareto optimization,
    component pruning, and response finalization to ensure the final response
    meets all quality standards.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Threshold Verification Service.
        
        Args:
            config: Configuration dictionary for the service and its components
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Initialize components with their specific configurations
        threshold_config = self.config.get("quality_threshold_verifier", {})
        pareto_config = self.config.get("pareto_optimizer", {})
        pruner_config = self.config.get("component_pruner", {})
        finalizer_config = self.config.get("response_finalizer", {})
        
        self.threshold_verifier = QualityThresholdVerifier(threshold_config)
        self.pareto_optimizer = ParetoOptimizer(pareto_config)
        self.component_pruner = ComponentPruner(pruner_config)
        self.response_finalizer = ResponseFinalizer(finalizer_config)
        
        # Service-level configuration
        self.strict_verification = self.config.get("strict_verification", True)
        self.enable_pruning = self.config.get("enable_pruning", True)
        self.required_quality_dimensions = self.config.get("required_quality_dimensions", 
                                                      ["accuracy", "completeness", "consistency", "relevance"])
        
        self.logger.info("Threshold Verification Service initialized")
    
    @property
    def stage_id(self) -> str:
        """Get the unique identifier for this pipeline stage."""
        return "threshold_verification"
    
    def process(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and verify the combined response against quality thresholds.
        
        Args:
            prompt: The prompt for threshold verification
            context: The current session context containing combined response and quality thresholds
            
        Returns:
            Verified final response with verification metrics
        """
        self.logger.info("Verifying response against quality thresholds")
        
        # Extract relevant data from context
        combined_response = context.get("stage_outputs", {}).get("response_comparison", {})
        quality_thresholds = self.config.get("quality_thresholds", context.get("config", {}).get("quality_thresholds", {}))
        
        if not combined_response:
            self.logger.warning("No combined response available for verification")
            return {"error": "No response available for verification", "status": "failed"}
        
        # Step 1: Verify that the response meets all quality thresholds
        self.logger.info("Checking response against quality thresholds")
        verification_results = self.threshold_verifier.verify(
            combined_response,
            quality_thresholds,
            self.required_quality_dimensions
        )
        
        if not verification_results.get("passes_verification", True) and self.strict_verification:
            self.logger.warning("Response failed strict verification")
            return self._handle_verification_failure(combined_response, verification_results)
        
        # Step 2: Apply Pareto optimization to identify dominated components
        self.logger.info("Applying Pareto optimization")
        pareto_analysis = self.pareto_optimizer.optimize(
            combined_response,
            verification_results
        )
        
        # Step 3: Prune components that don't meet minimum quality standards (if enabled)
        pruned_response = combined_response
        if self.enable_pruning:
            self.logger.info("Pruning suboptimal components")
            pruned_response = self.component_pruner.prune(
                combined_response,
                pareto_analysis,
                verification_results
            )
        
        # Step 4: Finalize response for delivery
        self.logger.info("Finalizing response for delivery")
        final_response = self.response_finalizer.finalize(
            pruned_response,
            verification_results,
            pareto_analysis
        )
        
        # Add verification metrics to response
        final_response["verification_metrics"] = verification_results
        final_response["pareto_analysis"] = pareto_analysis.get("summary", {})
        
        # Update metrics for monitoring
        self._update_metrics({
            "passed_verification": verification_results.get("passes_verification", False),
            "verification_score": verification_results.get("overall_score", 0.0),
            "pruned_components": len(pareto_analysis.get("dominated_components", [])),
            "final_quality_score": final_response.get("final_quality_score", 0.0)
        })
        
        self.logger.info("Threshold verification completed")
        return final_response
    
    def refine(self, refinement_prompt: str, context: Dict[str, Any], previous_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Refine the final response based on verification feedback.
        
        Args:
            refinement_prompt: Prompt specifically for refinement
            context: The current session context
            previous_output: The previous final response
            
        Returns:
            Refined final response
        """
        self.logger.info("Refining final response")
        
        # Create a new context with verification feedback for upstream refinement
        refinement_context = dict(context)
        refinement_context["verification_feedback"] = previous_output.get("verification_metrics", {}).get("dimension_failures", {})
        
        # Re-process with updated context containing refinement data
        refined_response = self.process(refinement_prompt, refinement_context)
        
        # Add refinement tracking
        refined_response["is_refinement"] = True
        refined_response["refinement_changes"] = self._track_refinement_changes(
            previous_output, refined_response)
        
        self.logger.info("Response refinement completed")
        return refined_response
    
    def _handle_verification_failure(self, combined_response: Dict[str, Any], 
                                   verification_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the case where response fails verification in strict mode.
        
        Args:
            combined_response: The combined response that failed verification
            verification_results: The verification results containing failure details
            
        Returns:
            Response with failure information and improvement recommendations
        """
        failure_response = dict(combined_response)
        
        # Add verification failure information
        failure_response["verification_status"] = "failed"
        failure_response["verification_metrics"] = verification_results
        failure_response["verification_failures"] = verification_results.get("dimension_failures", {})
        
        # Add improvement recommendations
        dimension_failures = verification_results.get("dimension_failures", {})
        failure_response["improvement_recommendations"] = {
            dimension: self._generate_improvement_recommendation(dimension, details)
            for dimension, details in dimension_failures.items()
        }
        
        return failure_response
    
    def _generate_improvement_recommendation(self, dimension: str, failure_details: Dict[str, Any]) -> str:
        """
        Generate a specific improvement recommendation for a failed dimension.
        
        Args:
            dimension: The quality dimension that failed
            failure_details: Details about the failure
            
        Returns:
            Improvement recommendation as a string
        """
        score = failure_details.get("score", 0.0)
        threshold = failure_details.get("threshold", 0.0)
        gap = threshold - score
        
        # Dimension-specific recommendations
        recommendations = {
            "accuracy": f"Increase factual accuracy by validating key statements against domain knowledge. Current gap: {gap:.2f}",
            "completeness": f"Add missing information on key topics identified in the query. Current gap: {gap:.2f}",
            "consistency": f"Resolve logical contradictions between response components. Current gap: {gap:.2f}",
            "relevance": f"Improve alignment with the original query intent. Current gap: {gap:.2f}",
            "novelty": f"Incorporate more unique insights beyond common knowledge. Current gap: {gap:.2f}"
        }
        
        return recommendations.get(dimension, f"Improve {dimension} score by at least {gap:.2f} to meet threshold")
    
    def _track_refinement_changes(self, previous_output: Dict[str, Any], 
                                refined_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track changes made during refinement.
        
        Args:
            previous_output: The output before refinement
            refined_output: The output after refinement
            
        Returns:
            Dictionary of tracked changes
        """
        # Extract verification metrics for comparison
        previous_metrics = previous_output.get("verification_metrics", {})
        refined_metrics = refined_output.get("verification_metrics", {})
        
        # Compare dimension scores
        dimension_changes = {}
        for dimension in self.required_quality_dimensions:
            prev_score = previous_metrics.get("dimension_scores", {}).get(dimension, 0.0)
            new_score = refined_metrics.get("dimension_scores", {}).get(dimension, 0.0)
            dimension_changes[dimension] = {
                "previous": prev_score,
                "current": new_score,
                "change": new_score - prev_score
            }
        
        # Compare overall scores
        previous_overall = previous_metrics.get("overall_score", 0.0)
        refined_overall = refined_metrics.get("overall_score", 0.0)
        
        return {
            "dimension_changes": dimension_changes,
            "overall_score_change": refined_overall - previous_overall,
            "previously_failing_dimensions": list(previous_metrics.get("dimension_failures", {}).keys()),
            "currently_failing_dimensions": list(refined_metrics.get("dimension_failures", {}).keys()),
            "improvement_summary": self._generate_improvement_summary(dimension_changes)
        }
    
    def _generate_improvement_summary(self, dimension_changes: Dict[str, Dict[str, float]]) -> str:
        """
        Generate a summary of improvements made during refinement.
        
        Args:
            dimension_changes: Dictionary of changes in each dimension
            
        Returns:
            Summary of improvements as a string
        """
        # Find dimensions with significant improvement
        improvements = [
            f"{dimension} (+{details['change']:.2f})"
            for dimension, details in dimension_changes.items()
            if details['change'] > 0.05
        ]
        
        # Find dimensions with significant regression
        regressions = [
            f"{dimension} ({details['change']:.2f})"
            for dimension, details in dimension_changes.items()
            if details['change'] < -0.05
        ]
        
        if improvements and not regressions:
            return f"Improved in {', '.join(improvements)}"
        elif regressions and not improvements:
            return f"Regressed in {', '.join(regressions)}"
        elif improvements and regressions:
            return f"Mixed changes: Improved in {', '.join(improvements)}; Regressed in {', '.join(regressions)}"
        else:
            return "No significant changes in quality dimensions" 