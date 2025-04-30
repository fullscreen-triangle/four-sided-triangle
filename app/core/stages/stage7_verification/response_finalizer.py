"""
Response Finalizer

This module contains the ResponseFinalizer class, which finalizes the response
for delivery after verification and pruning.
"""

import logging
from typing import Dict, Any, List, Optional

class ResponseFinalizer:
    """
    Finalizes the response for delivery after verification and pruning.
    
    This class ensures the final response is properly formatted and contains:
    - Optimal trade-offs between objectives
    - Complete metadata for tracking
    - Properly formatted content structure
    - Summary of verification and optimization results
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Response Finalizer.
        
        Args:
            config: Configuration dictionary for the response finalizer
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Configuration parameters
        self.include_verification_metadata = self.config.get("include_verification_metadata", True)
        self.include_optimization_metrics = self.config.get("include_optimization_metrics", True)
        self.format_as_json = self.config.get("format_as_json", False)
        self.include_summary = self.config.get("include_summary", True)
        self.standardize_output_format = self.config.get("standardize_output_format", True)
        
        self.logger.info("Response Finalizer initialized")
    
    def finalize(self, response: Dict[str, Any], verification_results: Dict[str, Any],
               pareto_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Finalize the response for delivery.
        
        Args:
            response: The pruned response
            verification_results: Results from quality threshold verification
            pareto_analysis: Results from Pareto optimization
            
        Returns:
            Finalized response ready for delivery
        """
        self.logger.info("Finalizing response for delivery")
        
        # Start with a deep copy of the response
        final_response = self._deep_copy_response(response)
        
        # Apply consistent structure
        if self.standardize_output_format:
            final_response = self._standardize_structure(final_response)
        
        # Add verification and optimization summaries
        if self.include_summary:
            final_response = self._add_summary(final_response, verification_results, pareto_analysis)
        
        # Add quality metrics
        final_response = self._add_quality_metrics(final_response, verification_results)
        
        # Add optimization metrics if requested
        if self.include_optimization_metrics:
            final_response = self._add_optimization_metrics(final_response, pareto_analysis)
        
        # Handle verification metadata
        if self.include_verification_metadata:
            final_response = self._add_verification_metadata(final_response, verification_results)
        else:
            # Remove intermediate verification data if not wanted
            final_response = self._remove_intermediate_metadata(final_response)
        
        # Format as JSON if requested
        if self.format_as_json:
            final_response = self._format_as_json(final_response)
        
        # Calculate final quality score
        final_response["final_quality_score"] = self._calculate_final_quality_score(verification_results)
        
        # Add completion timestamp
        final_response["completion_timestamp"] = self._get_timestamp()
        final_response["status"] = "completed"
        
        self.logger.info("Response finalization completed")
        return final_response
    
    def _standardize_structure(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize the response structure to ensure consistent format.
        
        Args:
            response: The response to standardize
            
        Returns:
            Standardized response
        """
        standardized = {}
        
        # Ensure core fields are present and properly ordered
        core_fields = ["content", "metadata", "components", "quality_metrics", "verification_status"]
        
        # Transfer content first if it exists
        if "content" in response:
            standardized["content"] = response["content"]
        elif "response" in response:
            standardized["content"] = response["response"]
        
        # Create or transfer metadata
        metadata = response.get("metadata", {})
        if not metadata:
            # Collect metadata from various fields
            metadata = {
                "generated_at": self._get_timestamp(),
                "verification_status": response.get("verification_status", "verified")
            }
            
            # Add any existing metadata-like fields
            for field in ["source", "model", "processing_time", "query_id"]:
                if field in response:
                    metadata[field] = response[field]
        
        standardized["metadata"] = metadata
        
        # Transfer components
        components = self._extract_components(response)
        if components:
            standardized["components"] = components
        
        # Transfer quality metrics
        quality_metrics = response.get("quality_metrics", {})
        if not quality_metrics and "dimension_scores" in response:
            quality_metrics = response["dimension_scores"]
            
        if quality_metrics:
            standardized["quality_metrics"] = quality_metrics
        
        # Transfer any remaining fields not specifically handled
        for key, value in response.items():
            if key not in standardized and key not in ["content_components", "information_elements"]:
                standardized[key] = value
        
        return standardized
    
    def _add_summary(self, response: Dict[str, Any], verification_results: Dict[str, Any],
                   pareto_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a summary of verification and optimization results to the response.
        
        Args:
            response: The response to modify
            verification_results: Results from quality threshold verification
            pareto_analysis: Results from Pareto optimization
            
        Returns:
            Response with added summary
        """
        # Create summary section
        summary = {
            "verification_result": verification_results.get("passes_verification", False),
            "overall_quality_score": verification_results.get("overall_score", 0.0),
            "quality_dimensions": verification_results.get("dimension_scores", {}),
            "pareto_efficiency": {
                "frontier_size": pareto_analysis.get("summary", {}).get("frontier_size", 0),
                "efficiency_gain": pareto_analysis.get("summary", {}).get("efficiency_gain", {}).get("overall", 0.0)
            }
        }
        
        # Add failing dimensions if any
        failing_dimensions = verification_results.get("dimension_failures", {})
        if failing_dimensions:
            summary["failing_dimensions"] = list(failing_dimensions.keys())
        
        # Add summary to response
        response["summary"] = summary
        
        return response
    
    def _add_quality_metrics(self, response: Dict[str, Any], verification_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add quality metrics to the response.
        
        Args:
            response: The response to modify
            verification_results: Results from quality threshold verification
            
        Returns:
            Response with added quality metrics
        """
        dimension_scores = verification_results.get("dimension_scores", {})
        
        if dimension_scores and "quality_metrics" not in response:
            response["quality_metrics"] = dimension_scores
            
        # Add overall score if not present
        if "overall_score" not in response.get("quality_metrics", {}):
            response.setdefault("quality_metrics", {})["overall"] = verification_results.get("overall_score", 0.0)
            
        return response
    
    def _add_optimization_metrics(self, response: Dict[str, Any], pareto_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add optimization metrics to the response.
        
        Args:
            response: The response to modify
            pareto_analysis: Results from Pareto optimization
            
        Returns:
            Response with added optimization metrics
        """
        # Extract key optimization metrics
        summary = pareto_analysis.get("summary", {})
        
        optimization_metrics = {
            "pareto_frontier_size": summary.get("frontier_size", 0),
            "dominated_components_count": summary.get("dominated_size", 0),
            "efficiency_gain": summary.get("efficiency_gain", {}).get("overall", 0.0),
            "frontier_quality": summary.get("frontier_avg_scores", {})
        }
        
        # Add optimization metrics to response
        response["optimization_metrics"] = optimization_metrics
        
        return response
    
    def _add_verification_metadata(self, response: Dict[str, Any], verification_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add verification metadata to the response.
        
        Args:
            response: The response to modify
            verification_results: Results from quality threshold verification
            
        Returns:
            Response with added verification metadata
        """
        # Simplify verification results to include only essential fields
        verification_metadata = {
            "verification_status": "passed" if verification_results.get("passes_verification", False) else "failed",
            "verification_timestamp": verification_results.get("verification_timestamp", self._get_timestamp()),
            "overall_score": verification_results.get("overall_score", 0.0),
            "dimension_scores": verification_results.get("dimension_scores", {}),
            "threshold_tolerance": verification_results.get("threshold_tolerance_applied", 0.05)
        }
        
        # Add failing dimensions if any
        failures = verification_results.get("dimension_failures", {})
        if failures:
            verification_metadata["failures"] = {
                dimension: {
                    "score": details.get("score", 0.0),
                    "threshold": details.get("threshold", 0.0),
                    "gap": details.get("gap", 0.0)
                } for dimension, details in failures.items()
            }
        
        # Add verification metadata to response
        response["verification_metadata"] = verification_metadata
        
        return response
    
    def _remove_intermediate_metadata(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove intermediate processing metadata to clean up the response.
        
        Args:
            response: The response to clean
            
        Returns:
            Cleaned response
        """
        # Fields to remove
        fields_to_remove = [
            "verification_metrics", 
            "pareto_analysis",
            "dominance_relationships",
            "component_scores",
            "pruning_details",
            "threshold_calculations"
        ]
        
        # Remove fields if present
        for field in fields_to_remove:
            if field in response:
                del response[field]
                
        return response
    
    def _format_as_json(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the response for JSON serialization.
        
        Args:
            response: The response to format
            
        Returns:
            JSON-formatted response
        """
        # Ensure all values are JSON serializable
        serializable_response = {}
        
        for key, value in response.items():
            if isinstance(value, (str, int, float, bool, list, dict)):
                # Already serializable
                serializable_response[key] = value
            elif value is None:
                # None can be represented as null in JSON
                serializable_response[key] = None
            else:
                # Convert non-serializable types to strings
                serializable_response[key] = str(value)
                
        return serializable_response
    
    def _calculate_final_quality_score(self, verification_results: Dict[str, Any]) -> float:
        """
        Calculate the final quality score for the response.
        
        Args:
            verification_results: Results from quality threshold verification
            
        Returns:
            Final quality score
        """
        # Use the overall score from verification results
        overall_score = verification_results.get("overall_score", 0.0)
        
        # Apply penalty for failing verification
        if not verification_results.get("passes_verification", True):
            # Calculate penalty based on number of failing dimensions
            failures = verification_results.get("dimension_failures", {})
            penalty = min(0.2, len(failures) * 0.05)
            overall_score = max(0.0, overall_score - penalty)
            
        return overall_score
    
    def _extract_components(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract components from the response.
        
        Args:
            response: The response
            
        Returns:
            Dictionary of components
        """
        # Try different potential component locations
        for field in ["components", "content_components", "information_elements"]:
            if field in response and response[field]:
                return response[field]
                
        return {}
    
    def _deep_copy_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a deep copy of the response.
        
        Args:
            response: The response to copy
            
        Returns:
            Deep copy of the response
        """
        import copy
        return copy.deepcopy(response)
    
    def _get_timestamp(self) -> str:
        """Get the current timestamp as ISO format string."""
        from datetime import datetime
        return datetime.now().isoformat() 