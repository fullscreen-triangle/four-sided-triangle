import logging
from typing import Dict, Any, List
import numpy as np

logger = logging.getLogger(__name__)

class ThrottleDetector:
    """
    Detects throttling patterns in LLM responses.
    
    This class implements sophisticated techniques to identify when an LLM
    is throttling its capabilities, particularly for complex queries.
    """
    
    def __init__(self):
        """Initialize the throttle detector with detection patterns."""
        # Throttling patterns to look for
        self.throttle_patterns = [
            "token_limitation",     # When LLM is limiting response length
            "depth_limitation",     # When LLM is limiting analytical depth
            "computation_limitation" # When LLM is limiting computational reasoning
        ]
        
        # Historical threshold calibrations (these would be dynamically updated in production)
        self.thresholds = {
            "info_density_ratio": 0.7,  # Expected vs actual information density
            "parameter_coverage_ratio": 0.6,  # Expected vs actual parameter count
            "confidence_variance": 0.05,  # Variance in confidence distributions
            "reasoning_depth_ratio": 0.65,  # Expected vs actual reasoning depth
        }
        
        # Domain-specific expected parameters (would be more comprehensive in production)
        self.domain_parameter_expectations = {
            "body_metrics": ["height", "weight", "body_mass_index", "body_composition", 
                            "limb_measurements", "circumferences"],
            "sprint_performance": ["stride_length", "cadence", "ground_contact_time", 
                                "flight_time", "power_output"],
            "biomechanics": ["joint_angles", "forces", "moment_arms", "torques", 
                            "center_of_mass", "stance_width"]
        }
    
    def detect_throttling(
        self, 
        response: Dict[str, Any], 
        query: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Detect throttling in LLM response.
        
        Args:
            response: The LLM response to analyze
            query: The original query text
            context: Additional context
            
        Returns:
            Detection results with pattern and confidence
        """
        # Extract necessary data for analysis
        parameters = response.get("parametersOfInterest", [])
        reasoning = response.get("reasoning", "")
        confidence_score = response.get("confidence", 0.5)
        
        # Perform detection checks
        info_density_ratio = self._analyze_info_density(response, query)
        parameter_coverage_ratio = self._analyze_parameter_coverage(parameters, query)
        confidence_analysis = self._analyze_confidence_pattern(confidence_score, response)
        reasoning_depth_ratio = self._analyze_reasoning_depth(reasoning, query)
        
        # Calculate throttling indicators with weights
        throttle_indicators = {
            "info_density": 1.0 if info_density_ratio < self.thresholds["info_density_ratio"] else 0.0,
            "parameter_coverage": 1.0 if parameter_coverage_ratio < self.thresholds["parameter_coverage_ratio"] else 0.0,
            "confidence_pattern": 1.0 if confidence_analysis["is_suspicious"] else 0.0,
            "reasoning_depth": 1.0 if reasoning_depth_ratio < self.thresholds["reasoning_depth_ratio"] else 0.0
        }
        
        # Calculate weights based on query characteristics
        weights = self._calculate_indicator_weights(query)
        
        # Weighted throttle score
        throttle_score = sum(
            throttle_indicators[indicator] * weights[indicator]
            for indicator in throttle_indicators
        ) / sum(weights.values())
        
        # Determine if throttled and identify pattern
        is_throttled = throttle_score > 0.5
        pattern = self._identify_throttle_pattern(throttle_indicators, weights) if is_throttled else None
        
        return {
            "is_throttled": is_throttled,
            "pattern": pattern,
            "confidence": throttle_score,
            "metrics": {
                "info_density_ratio": info_density_ratio,
                "parameter_coverage_ratio": parameter_coverage_ratio,
                "confidence_variance": confidence_analysis["variance"],
                "reasoning_depth_ratio": reasoning_depth_ratio
            },
            "indicators": throttle_indicators
        }
    
    def _analyze_info_density(self, response: Dict[str, Any], query: str) -> float:
        """Analyze information density ratio compared to expectations."""
        # Calculate expected information density
        query_length = len(query)
        term_complexity = self._analyze_term_complexity(query)
        expected_density = term_complexity * (1 + np.log(max(10, query_length) / 100))
        
        # Calculate actual information density
        parameters = response.get("parametersOfInterest", [])
        actual_density = len(parameters) * 0.5 + self._analyze_term_specificity(parameters) * 0.5
        
        # Return ratio of actual to expected
        if expected_density == 0:
            return 1.0
        return actual_density / expected_density
    
    def _analyze_parameter_coverage(self, parameters: List[str], query: str) -> float:
        """Analyze parameter coverage based on domain expectations."""
        # Determine the expected domains based on query
        domain_matches = []
        for domain in self.domain_parameter_expectations:
            if any(term in query.lower() for term in domain.split("_")):
                domain_matches.append(domain)
        
        # If no domains match, use all domains
        if not domain_matches:
            domain_matches = list(self.domain_parameter_expectations.keys())
        
        # Build expected parameter list
        expected_parameters = []
        for domain in domain_matches:
            expected_parameters.extend(self.domain_parameter_expectations[domain])
        
        # Count how many expected parameters are covered
        covered_parameters = 0
        for param in parameters:
            # Check if this parameter is related to any expected parameter
            for expected in expected_parameters:
                if expected in param.lower() or self._are_related_terms(param, expected):
                    covered_parameters += 1
                    break
        
        # Return coverage ratio
        if not expected_parameters:
            return 1.0
        return covered_parameters / len(expected_parameters)
    
    def _analyze_confidence_pattern(self, confidence: float, response: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze confidence score pattern for suspicious uniformity."""
        # In a real implementation, we would look at confidence across multiple responses
        # For now, we'll use a simple heuristic: is the confidence exactly 0.7-0.8?
        is_generic_confidence = 0.7 <= confidence <= 0.8
        
        # Check if confidence seems artificially precise
        is_suspicious = is_generic_confidence
        
        return {
            "is_suspicious": is_suspicious,
            "variance": 0.0 if is_suspicious else 0.1  # Mock variance
        }
    
    def _analyze_reasoning_depth(self, reasoning: str, query: str) -> float:
        """Analyze reasoning depth compared to query complexity."""
        # Simple heuristic: reasoning should be proportional to query complexity
        query_complexity = self._analyze_query_complexity(query)
        
        # Calculate reasoning depth based on length, structure, and richness
        reasoning_sentences = reasoning.split(". ")
        reasoning_depth = len(reasoning_sentences) * 0.3
        
        # Check for reasoning richness (e.g., causal language)
        causal_terms = ["because", "therefore", "thus", "consequently", "as a result", 
                        "leads to", "caused by", "results in", "due to"]
        richness_score = sum(1 for term in causal_terms if term in reasoning.lower())
        reasoning_depth += richness_score * 0.5
        
        # Return depth ratio
        expected_depth = max(3, query_complexity * 1.5)
        return reasoning_depth / expected_depth
    
    def _identify_throttle_pattern(self, indicators: Dict[str, float], weights: Dict[str, float]) -> str:
        """Identify the most likely throttle pattern based on indicators."""
        weighted_indicators = {k: v * weights[k] for k, v in indicators.items()}
        
        # Map indicators to patterns
        pattern_scores = {
            "token_limitation": weighted_indicators["info_density"] * 0.7 + 
                               weighted_indicators["parameter_coverage"] * 0.3,
            "depth_limitation": weighted_indicators["reasoning_depth"] * 0.6 + 
                               weighted_indicators["info_density"] * 0.4,
            "computation_limitation": weighted_indicators["reasoning_depth"] * 0.4 + 
                                    weighted_indicators["parameter_coverage"] * 0.6
        }
        
        # Return the pattern with the highest score
        return max(pattern_scores.items(), key=lambda x: x[1])[0]
    
    def _calculate_indicator_weights(self, query: str) -> Dict[str, float]:
        """Calculate weights for different indicators based on query characteristics."""
        # Analyze query to determine which indicators matter more
        query_length = len(query)
        has_computational_terms = any(term in query.lower() for term in 
                                      ["calculate", "compute", "measurement", "metric"])
        has_analysis_terms = any(term in query.lower() for term in 
                                ["analyze", "compare", "relationship", "correlation"])
        
        # Assign weights based on query characteristics
        weights = {
            "info_density": 1.0,
            "parameter_coverage": 1.0,
            "confidence_pattern": 0.7,
            "reasoning_depth": 1.0
        }
        
        # Adjust weights based on query
        if query_length > 100:
            weights["info_density"] = 1.2
        
        if has_computational_terms:
            weights["parameter_coverage"] = 1.3
            
        if has_analysis_terms:
            weights["reasoning_depth"] = 1.2
            
        return weights
    
    # Helper methods
    def _analyze_term_complexity(self, text: str) -> float:
        """Analyze the complexity of terms in text."""
        # Simple implementation - word length and domain specificity
        words = text.split()
        avg_length = sum(len(word) for word in words) / max(1, len(words))
        
        # Domain specificity bonus
        domain_terms = ["biomechanics", "sprint", "performance", "genetic", "metrics", 
                       "physiological", "anthropometric", "muscle", "power", "velocity"]
        domain_count = sum(1 for term in domain_terms if term in text.lower())
        
        return 0.5 + avg_length / 10 + domain_count * 0.2
    
    def _analyze_term_specificity(self, terms: List[str]) -> float:
        """Analyze how specific the given terms are."""
        if not terms:
            return 0.0
            
        # Simple implementation - longer terms tend to be more specific
        avg_length = sum(len(term) for term in terms) / len(terms)
        
        # Check for compound terms (containing underscores or multiple words)
        compound_ratio = sum(1 for term in terms if "_" in term or " " in term) / len(terms)
        
        return avg_length / 10 + compound_ratio * 0.5
    
    def _analyze_query_complexity(self, query: str) -> float:
        """Analyze the complexity of a query."""
        # Simple implementation - based on length, question marks, and domain terms
        sentences = query.split(". ")
        questions = sum(1 for s in sentences if "?" in s)
        
        domain_terms = ["biomechanics", "sprint", "performance", "genetic", "metrics", 
                       "physiological", "anthropometric", "muscle", "power", "velocity"]
        domain_count = sum(1 for term in domain_terms if term in query.lower())
        
        return 1.0 + len(sentences) * 0.5 + questions * 0.7 + domain_count * 0.3
    
    def _are_related_terms(self, term1: str, term2: str) -> bool:
        """Check if two terms are semantically related."""
        # In a real implementation, this would use word embeddings or a taxonomy
        # Simple implementation - check for shared roots
        term1_lower = term1.lower()
        term2_lower = term2.lower()
        
        # Check for common prefixes (at least 4 chars)
        for i in range(4, min(len(term1_lower), len(term2_lower)) + 1):
            if term1_lower[:i] == term2_lower[:i]:
                return True
                
        # Related pairs lookup
        related_pairs = [
            ("weight", "mass"),
            ("height", "stature"),
            ("speed", "velocity"),
            ("length", "distance"),
            ("strength", "power"),
            ("muscle", "muscular")
        ]
        
        # Check if terms are in related pairs
        for pair in related_pairs:
            if (pair[0] in term1_lower and pair[1] in term2_lower) or \
               (pair[1] in term1_lower and pair[0] in term2_lower):
                return True
                
        return False
