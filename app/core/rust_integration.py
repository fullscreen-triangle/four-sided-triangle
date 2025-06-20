"""
Rust Integration Module

This module provides Python wrappers for high-performance Rust implementations
of computationally intensive operations in the Four-Sided Triangle system.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

try:
    import four_sided_triangle_core as rust_core
    RUST_AVAILABLE = True
    logging.info("Rust core module loaded successfully")
except ImportError as e:
    RUST_AVAILABLE = False
    logging.warning(f"Rust core module not available: {e}. Falling back to Python implementations.")
    rust_core = None

class RustIntegration:
    """Main integration class for Rust components."""
    
    def __init__(self):
        self.rust_available = RUST_AVAILABLE
        self.logger = logging.getLogger(__name__)
    
    # Bayesian Evaluation Methods
    
    def calculate_posterior_probability(
        self, 
        solution: str, 
        domain_knowledge: Dict[str, Any], 
        query_intent: Dict[str, Any]
    ) -> float:
        """Calculate Bayesian posterior probability with Rust acceleration."""
        if not self.rust_available:
            return self._fallback_posterior_probability(solution, domain_knowledge, query_intent)
        
        try:
            domain_json = json.dumps(domain_knowledge)
            intent_json = json.dumps(query_intent)
            return rust_core.py_calculate_posterior_probability(solution, domain_json, intent_json)
        except Exception as e:
            self.logger.warning(f"Rust posterior calculation failed: {e}. Using fallback.")
            return self._fallback_posterior_probability(solution, domain_knowledge, query_intent)
    
    def calculate_information_gain(
        self, 
        solution: str, 
        domain_knowledge: Dict[str, Any], 
        query_intent: Dict[str, Any]
    ) -> float:
        """Calculate information gain with Rust acceleration."""
        if not self.rust_available:
            return self._fallback_information_gain(solution, domain_knowledge, query_intent)
        
        try:
            domain_json = json.dumps(domain_knowledge)
            intent_json = json.dumps(query_intent)
            return rust_core.py_calculate_information_gain(solution, domain_json, intent_json)
        except Exception as e:
            self.logger.warning(f"Rust information gain calculation failed: {e}. Using fallback.")
            return self._fallback_information_gain(solution, domain_knowledge, query_intent)
    
    def bayesian_evaluate(
        self, 
        solution: str, 
        domain_knowledge: Dict[str, Any], 
        query_intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform complete Bayesian evaluation with Rust acceleration."""
        if not self.rust_available:
            return self._fallback_bayesian_evaluate(solution, domain_knowledge, query_intent)
        
        try:
            domain_json = json.dumps(domain_knowledge)
            intent_json = json.dumps(query_intent)
            result_json = rust_core.py_bayesian_evaluate(solution, domain_json, intent_json)
            return json.loads(result_json)
        except Exception as e:
            self.logger.warning(f"Rust Bayesian evaluation failed: {e}. Using fallback.")
            return self._fallback_bayesian_evaluate(solution, domain_knowledge, query_intent)
    
    # Throttle Detection Methods
    
    def detect_throttling(
        self, 
        response: str, 
        query: str, 
        performance_metrics: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Detect throttling patterns with Rust acceleration."""
        if not self.rust_available:
            return self._fallback_detect_throttling(response, query, performance_metrics)
        
        try:
            metrics_json = json.dumps(performance_metrics) if performance_metrics else None
            result_json = rust_core.py_detect_throttling(response, query, metrics_json)
            return json.loads(result_json)
        except Exception as e:
            self.logger.warning(f"Rust throttle detection failed: {e}. Using fallback.")
            return self._fallback_detect_throttling(response, query, performance_metrics)
    
    def calculate_pattern_score(self, response: str, query: str, pattern_type: str) -> float:
        """Calculate pattern score with Rust acceleration."""
        if not self.rust_available:
            return self._fallback_pattern_score(response, query, pattern_type)
        
        try:
            return rust_core.py_calculate_pattern_score(response, query, pattern_type)
        except Exception as e:
            self.logger.warning(f"Rust pattern score calculation failed: {e}. Using fallback.")
            return self._fallback_pattern_score(response, query, pattern_type)
    
    # Text Processing Methods
    
    def calculate_text_similarity(self, text1: str, text2: str) -> Dict[str, float]:
        """Calculate text similarity with Rust acceleration."""
        if not self.rust_available:
            return self._fallback_text_similarity(text1, text2)
        
        try:
            result_json = rust_core.py_calculate_text_similarity(text1, text2)
            return json.loads(result_json)
        except Exception as e:
            self.logger.warning(f"Rust text similarity calculation failed: {e}. Using fallback.")
            return self._fallback_text_similarity(text1, text2)
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities with Rust acceleration."""
        if not self.rust_available:
            return self._fallback_extract_entities(text)
        
        try:
            result_json = rust_core.py_extract_entities(text)
            return json.loads(result_json)
        except Exception as e:
            self.logger.warning(f"Rust entity extraction failed: {e}. Using fallback.")
            return self._fallback_extract_entities(text)
    
    def calculate_information_density(self, text: str, domain_context: Optional[str] = None) -> float:
        """Calculate information density with Rust acceleration."""
        if not self.rust_available:
            return self._fallback_information_density(text, domain_context)
        
        try:
            return rust_core.py_calculate_information_density(text, domain_context)
        except Exception as e:
            self.logger.warning(f"Rust information density calculation failed: {e}. Using fallback.")
            return self._fallback_information_density(text, domain_context)
    
    # Quality Assessment Methods
    
    def assess_quality_dimensions(
        self, 
        solution: str, 
        domain_knowledge: Dict[str, Any], 
        query_intent: Dict[str, Any], 
        bayesian_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess quality across multiple dimensions with Rust acceleration."""
        if not self.rust_available:
            return self._fallback_quality_assessment(solution, domain_knowledge, query_intent, bayesian_metrics)
        
        try:
            domain_json = json.dumps(domain_knowledge)
            intent_json = json.dumps(query_intent)
            metrics_json = json.dumps(bayesian_metrics)
            result_json = rust_core.py_assess_quality_dimensions(solution, domain_json, intent_json, metrics_json)
            return json.loads(result_json)
        except Exception as e:
            self.logger.warning(f"Rust quality assessment failed: {e}. Using fallback.")
            return self._fallback_quality_assessment(solution, domain_knowledge, query_intent, bayesian_metrics)
    
    # Memory Management Methods
    
    def create_session(
        self, 
        session_id: str, 
        query: str, 
        user_context: Dict[str, Any], 
        query_classification: str
    ) -> None:
        """Create a session with Rust acceleration."""
        if not self.rust_available:
            return self._fallback_create_session(session_id, query, user_context, query_classification)
        
        try:
            context_json = json.dumps(user_context)
            rust_core.py_create_session(session_id, query, context_json, query_classification)
        except Exception as e:
            self.logger.warning(f"Rust session creation failed: {e}. Using fallback.")
            return self._fallback_create_session(session_id, query, user_context, query_classification)
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data with Rust acceleration."""
        if not self.rust_available:
            return self._fallback_get_session(session_id)
        
        try:
            result = rust_core.py_get_session(session_id)
            return json.loads(result) if result else None
        except Exception as e:
            self.logger.warning(f"Rust session retrieval failed: {e}. Using fallback.")
            return self._fallback_get_session(session_id)
    
    # Optimization Methods
    
    def optimize_resource_allocation(
        self, 
        available_resources: float, 
        component_requirements: Dict[str, float], 
        historical_performance: Dict[str, float]
    ) -> Dict[str, Any]:
        """Optimize resource allocation with Rust acceleration."""
        if not self.rust_available:
            return self._fallback_resource_optimization(available_resources, component_requirements, historical_performance)
        
        try:
            requirements_json = json.dumps(component_requirements)
            performance_json = json.dumps(historical_performance)
            result_json = rust_core.py_optimize_resource_allocation(available_resources, requirements_json, performance_json)
            return json.loads(result_json)
        except Exception as e:
            self.logger.warning(f"Rust resource optimization failed: {e}. Using fallback.")
            return self._fallback_resource_optimization(available_resources, component_requirements, historical_performance)
    
    # Fallback Python implementations (simplified versions)
    
    def _fallback_posterior_probability(self, solution: str, domain_knowledge: Dict[str, Any], query_intent: Dict[str, Any]) -> float:
        """Simplified Python fallback for posterior probability calculation."""
        solution_length = len(solution.split())
        complexity = query_intent.get('complexity', 0.5)
        domain_specificity = query_intent.get('domain_specificity', 0.5)
        
        expected_length = 200 * (1 + complexity)
        length_factor = min(solution_length / expected_length, 1.0)
        
        return (length_factor * 0.6 + domain_specificity * 0.4) * 0.8
    
    def _fallback_information_gain(self, solution: str, domain_knowledge: Dict[str, Any], query_intent: Dict[str, Any]) -> float:
        """Simplified Python fallback for information gain calculation."""
        # Basic entropy-like calculation
        words = solution.split()
        unique_words = set(words)
        
        if len(words) == 0:
            return 0.0
        
        uniqueness_ratio = len(unique_words) / len(words)
        complexity = query_intent.get('complexity', 0.5)
        
        return uniqueness_ratio * complexity * 0.7
    
    def _fallback_bayesian_evaluate(self, solution: str, domain_knowledge: Dict[str, Any], query_intent: Dict[str, Any]) -> Dict[str, Any]:
        """Simplified Python fallback for Bayesian evaluation."""
        posterior = self._fallback_posterior_probability(solution, domain_knowledge, query_intent)
        info_gain = self._fallback_information_gain(solution, domain_knowledge, query_intent)
        
        return {
            "posterior_probability": posterior,
            "likelihood": 0.7,
            "prior": 0.5,
            "evidence": 0.6,
            "information_gain": info_gain,
            "mutual_information": info_gain * 0.8,
            "confidence_interval": (max(0.0, posterior - 0.1), min(1.0, posterior + 0.1))
        }
    
    def _fallback_detect_throttling(self, response: str, query: str, performance_metrics: Optional[Dict[str, float]]) -> Dict[str, Any]:
        """Simplified Python fallback for throttle detection."""
        throttle_indicators = ['brief', 'summary', 'concise', 'simplified', 'cannot provide']
        
        indicator_count = sum(1 for indicator in throttle_indicators if indicator in response.lower())
        throttle_score = indicator_count / len(throttle_indicators)
        
        return {
            "throttle_detected": throttle_score > 0.3,
            "pattern_type": "token_limitation" if throttle_score > 0.5 else "",
            "confidence_score": throttle_score,
            "pattern_scores": {"token_limitation": throttle_score},
            "density_score": 0.5,
            "expected_density": 0.7,
            "recommendations": ["Consider breaking query into smaller parts"] if throttle_score > 0.3 else []
        }
    
    def _fallback_pattern_score(self, response: str, query: str, pattern_type: str) -> float:
        """Simplified Python fallback for pattern score calculation."""
        # Basic keyword matching
        if pattern_type == "token_limitation":
            keywords = ['brief', 'summary', 'concise']
        elif pattern_type == "depth_limitation":
            keywords = ['simplified', 'basic', 'general']
        else:
            keywords = ['limitation', 'cannot']
        
        return sum(1 for keyword in keywords if keyword in response.lower()) / len(keywords)
    
    def _fallback_text_similarity(self, text1: str, text2: str) -> Dict[str, float]:
        """Simplified Python fallback for text similarity."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            similarity = 0.0
        else:
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            similarity = intersection / union if union > 0 else 0.0
        
        return {
            "jaccard_similarity": similarity,
            "cosine_similarity": similarity * 0.9,
            "semantic_similarity": similarity * 0.8,
            "overall_similarity": similarity
        }
    
    def _fallback_extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Simplified Python fallback for entity extraction."""
        import re
        entities = []
        
        # Extract numbers with units
        for match in re.finditer(r'(\d+(?:\.\d+)?)\s*([a-zA-Z]+)', text):
            entities.append({
                "text": match.group(0),
                "entity_type": "MEASUREMENT",
                "start_pos": match.start(),
                "end_pos": match.end(),
                "confidence": 0.8
            })
        
        return entities
    
    def _fallback_information_density(self, text: str, domain_context: Optional[str]) -> float:
        """Simplified Python fallback for information density."""
        words = text.split()
        if not words:
            return 0.0
        
        unique_words = set(words)
        technical_terms = ['algorithm', 'optimization', 'analysis', 'methodology']
        technical_count = sum(1 for word in words if any(term in word.lower() for term in technical_terms))
        
        uniqueness = len(unique_words) / len(words)
        technical_density = technical_count / len(words)
        
        return (uniqueness * 0.6 + technical_density * 0.4)
    
    def _fallback_quality_assessment(self, solution: str, domain_knowledge: Dict[str, Any], query_intent: Dict[str, Any], bayesian_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Simplified Python fallback for quality assessment."""
        return {
            "accuracy": 0.7,
            "completeness": 0.6,
            "consistency": 0.8,
            "relevance": 0.7,
            "novelty": 0.5,
            "overall_score": 0.66,
            "uncertainty_metrics": {
                "confidence_bounds": (0.5, 0.8),
                "variance_estimate": 0.1,
                "uncertainty_dimensions": {"solution_length": 0.3}
            }
        }
    
    def _fallback_create_session(self, session_id: str, query: str, user_context: Dict[str, Any], query_classification: str) -> None:
        """Python fallback for session creation (no-op)."""
        pass
    
    def _fallback_get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Python fallback for session retrieval."""
        return None
    
    def _fallback_resource_optimization(self, available_resources: float, component_requirements: Dict[str, float], historical_performance: Dict[str, float]) -> Dict[str, Any]:
        """Simplified Python fallback for resource optimization."""
        total_requirements = sum(component_requirements.values())
        allocations = {}
        
        for component, requirement in component_requirements.items():
            proportion = requirement / total_requirements if total_requirements > 0 else 0
            allocations[component] = available_resources * proportion
        
        return {
            "total_resources": available_resources,
            "allocations": allocations,
            "expected_roi": {k: 0.1 for k in allocations.keys()},
            "risk_factors": {k: 0.3 for k in allocations.keys()}
        }


# Global instance for easy access
rust_integration = RustIntegration()


# Convenience functions for direct access
def calculate_posterior_probability(solution: str, domain_knowledge: Dict[str, Any], query_intent: Dict[str, Any]) -> float:
    """Direct access to Rust-accelerated posterior probability calculation."""
    return rust_integration.calculate_posterior_probability(solution, domain_knowledge, query_intent)


def detect_throttling(response: str, query: str, performance_metrics: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """Direct access to Rust-accelerated throttle detection."""
    return rust_integration.detect_throttling(response, query, performance_metrics)


def assess_quality_dimensions(solution: str, domain_knowledge: Dict[str, Any], query_intent: Dict[str, Any], bayesian_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Direct access to Rust-accelerated quality assessment."""
    return rust_integration.assess_quality_dimensions(solution, domain_knowledge, query_intent, bayesian_metrics)


def calculate_text_similarity(text1: str, text2: str) -> Dict[str, float]:
    """Direct access to Rust-accelerated text similarity calculation."""
    return rust_integration.calculate_text_similarity(text1, text2) 