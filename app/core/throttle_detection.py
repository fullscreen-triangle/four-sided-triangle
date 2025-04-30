"""
Adversarial Throttle Detection and Bypass (ATDB) - Detect and bypass LLM throttling.

This module implements detection and bypass strategies for handling throttling 
mechanisms in commercial LLMs that limit their capabilities, particularly for 
computationally intensive or specialized queries.
"""
import logging
import re
import time
import json
from typing import Dict, Any, List, Optional, Tuple, Union

class ThrottleAdaptiveSystem:
    """
    Implements detection and bypass strategies for LLM throttling.
    
    This class identifies throttling patterns in LLM responses and applies
    appropriate bypass strategies to overcome limitations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Throttle Adaptive System.
        
        Args:
            config: Optional configuration parameters
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Load throttle detection patterns
        self.throttle_patterns = self._load_throttle_patterns()
        
        # Load adaptation strategies
        self.adaptation_strategies = self._load_adaptation_strategies()
        
        # Throttle detection thresholds
        self.density_threshold = self.config.get("density_threshold", 0.7)
        self.detection_threshold = self.config.get("detection_threshold", 0.5)
        
        # Performance tracking
        self.recent_performances = {}
        
        self.logger.info("Initialized Throttle Adaptive System")
    
    def _load_throttle_patterns(self) -> Dict[str, Dict[str, Any]]:
        """
        Load patterns for detecting throttling.
        
        Returns:
            Dictionary of throttle patterns
        """
        # In a real implementation, this would load from a configuration file
        # Here we define patterns inline
        
        return {
            "token_limitation": {
                "indicators": [
                    r"I need to be concise",
                    r"I'll provide a brief",
                    r"here's a summary",
                    r"Let me give you a condensed",
                    r"truncated due to length",
                    r"to keep this response manageable"
                ],
                "truncation_patterns": [
                    r"\.{3,}$",
                    r"etc\.$",
                    r"and so on\.$",
                    r"and more\.$"
                ],
                "weight": 0.4
            },
            "depth_limitation": {
                "indicators": [
                    r"this is a complex topic",
                    r"simplified explanation",
                    r"basic overview",
                    r"broad strokes",
                    r"general principles",
                    r"I cannot provide specific"
                ],
                "missing_elements": [
                    "mathematical formulas",
                    "specific values",
                    "detailed methodology",
                    "precise calculations"
                ],
                "weight": 0.3
            },
            "computation_limitation": {
                "indicators": [
                    r"I cannot perform complex calculations",
                    r"would require specialized tools",
                    r"numerical approximation",
                    r"rough estimate",
                    r"simplified model",
                    r"back-of-the-envelope"
                ],
                "computational_indicators": [
                    r"precise computation",
                    r"detailed simulation",
                    r"exact values",
                    r"differential equations"
                ],
                "weight": 0.3
            }
        }
    
    def _load_adaptation_strategies(self) -> Dict[str, Dict[str, Any]]:
        """
        Load strategies for bypassing throttling.
        
        Returns:
            Dictionary of bypass strategies
        """
        # In a real implementation, this would load from a configuration file
        # Here we define strategies inline
        
        return {
            "token_limitation": {
                "partitioning": {
                    "description": "Divide query into smaller sub-queries",
                    "effectiveness": 0.9
                },
                "progressive_disclosure": {
                    "description": "Request information in stages",
                    "effectiveness": 0.8
                },
                "targeted_extraction": {
                    "description": "Extract specific information in multiple queries",
                    "effectiveness": 0.7
                }
            },
            "depth_limitation": {
                "reframing": {
                    "description": "Reframe query to appear simpler while requesting the same depth",
                    "effectiveness": 0.8
                },
                "expert_persona": {
                    "description": "Request response as if from domain expert to domain expert",
                    "effectiveness": 0.7
                },
                "component_assembly": {
                    "description": "Request components separately then assemble",
                    "effectiveness": 0.9
                }
            },
            "computation_limitation": {
                "step_by_step": {
                    "description": "Request step-by-step calculation instructions",
                    "effectiveness": 0.9
                },
                "verification_approach": {
                    "description": "Present tentative calculation and request verification",
                    "effectiveness": 0.7
                },
                "equation_transformation": {
                    "description": "Ask for equation transformation rather than solution",
                    "effectiveness": 0.8
                }
            }
        }
    
    def detect_throttling(self, 
                          response: str, 
                          query: str, 
                          performance_metrics: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, float]:
        """
        Detect if throttling is occurring in a response.
        
        Args:
            response: The LLM response to analyze
            query: The original query
            performance_metrics: Optional metrics about response generation
            
        Returns:
            Tuple of (throttle_detected, pattern_type, confidence_score)
        """
        if not response:
            return False, "", 0.0
            
        performance_metrics = performance_metrics or {}
        self.logger.debug(f"Analyzing response for throttling: {response[:50]}...")
        
        # Calculate overall throttle score
        throttle_scores = {}
        
        # Check each pattern type
        for pattern_type, pattern_info in self.throttle_patterns.items():
            pattern_score = self._calculate_pattern_score(response, query, pattern_type, pattern_info)
            throttle_scores[pattern_type] = pattern_score * pattern_info["weight"]
        
        # Calculate information density score
        density_score = self._calculate_info_density(response, query)
        expected_density = self._calculate_expected_info_density(query)
        
        density_factor = 0.0
        if density_score < expected_density * self.density_threshold:
            density_factor = 0.4 * (1 - (density_score / expected_density))
        
        # Add response time factor if available
        time_factor = 0.0
        if "response_time" in performance_metrics and "token_count" in performance_metrics:
            expected_time = self._estimate_expected_time(performance_metrics["token_count"])
            actual_time = performance_metrics["response_time"]
            
            # Unusually fast response for complex query can indicate throttling
            if expected_time > 0 and actual_time < expected_time * 0.7:
                time_factor = 0.2 * (1 - (actual_time / expected_time))
        
        # Combine scores
        total_pattern_score = sum(throttle_scores.values())
        total_score = total_pattern_score + density_factor + time_factor
        
        # Determine most likely pattern if throttling detected
        is_throttled = total_score > self.detection_threshold
        max_pattern = max(throttle_scores.items(), key=lambda x: x[1])[0] if throttle_scores else ""
        
        if is_throttled:
            self.logger.info(f"Throttling detected: {max_pattern} with score {total_score:.2f}")
        
        return is_throttled, max_pattern, total_score
    
    def apply_bypass_strategy(self, query: str, detected_pattern: str) -> List[Dict[str, Any]]:
        """
        Apply appropriate bypass strategy for the detected throttling pattern.
        
        Args:
            query: Original query
            detected_pattern: Type of throttling pattern detected
            
        Returns:
            List of modified queries or query strategies
        """
        self.logger.debug(f"Applying bypass strategy for {detected_pattern}")
        
        if detected_pattern not in self.adaptation_strategies:
            self.logger.warning(f"No strategy found for pattern: {detected_pattern}")
            return [{"query": query, "strategy": "original"}]
        
        strategies = self.adaptation_strategies[detected_pattern]
        
        # Select best strategy based on effectiveness and past performance
        selected_strategy = self._select_best_strategy(detected_pattern, strategies)
        
        # Apply the selected strategy
        if detected_pattern == "token_limitation":
            result = self._apply_token_limitation_strategy(query, selected_strategy)
        elif detected_pattern == "depth_limitation":
            result = self._apply_depth_limitation_strategy(query, selected_strategy)
        elif detected_pattern == "computation_limitation":
            result = self._apply_computation_limitation_strategy(query, selected_strategy)
        else:
            result = [{"query": query, "strategy": "original"}]
        
        self.logger.info(f"Applied {selected_strategy} strategy for {detected_pattern}")
        return result
    
    def update_strategy_performance(self, strategy_name: str, pattern_type: str, success_score: float) -> None:
        """
        Update performance record for a strategy.
        
        Args:
            strategy_name: Name of the strategy
            pattern_type: Type of throttling pattern
            success_score: Score indicating how successful the strategy was
        """
        key = f"{pattern_type}_{strategy_name}"
        
        if key not in self.recent_performances:
            self.recent_performances[key] = []
            
        self.recent_performances[key].append(success_score)
        
        # Keep only the most recent 10 performance records
        if len(self.recent_performances[key]) > 10:
            self.recent_performances[key] = self.recent_performances[key][-10:]
            
        self.logger.debug(f"Updated performance for {strategy_name}: {success_score:.2f}")
    
    def _calculate_pattern_score(self, response: str, query: str, pattern_type: str, pattern_info: Dict[str, Any]) -> float:
        """
        Calculate score for a specific throttling pattern.
        
        Args:
            response: LLM response
            query: Original query
            pattern_type: Type of throttling pattern
            pattern_info: Information about the pattern
            
        Returns:
            Score indicating presence of pattern (0-1)
        """
        score = 0.0
        response_lower = response.lower()
        
        # Check for indicator phrases
        for indicator in pattern_info.get("indicators", []):
            if re.search(indicator, response_lower, re.IGNORECASE):
                score += 0.3
                break
        
        # Check for truncation patterns (for token limitation)
        if pattern_type == "token_limitation":
            for pattern in pattern_info.get("truncation_patterns", []):
                if re.search(pattern, response):
                    score += 0.4
                    break
                    
            # Check if response is shorter than expected given query complexity
            query_complexity = len(query.split()) / 10  # Simple complexity heuristic
            expected_min_length = min(200 * query_complexity, 2000)  # Cap at 2000
            
            if len(response.split()) < expected_min_length * 0.7:
                score += 0.3
        
        # Check for missing elements (for depth limitation)
        if pattern_type == "depth_limitation":
            missing_count = 0
            for element in pattern_info.get("missing_elements", []):
                if element.lower() in query.lower() and element.lower() not in response_lower:
                    missing_count += 1
            
            if missing_count > 0:
                score += min(0.7, missing_count * 0.15)
        
        # Check for computation limitations
        if pattern_type == "computation_limitation":
            for indicator in pattern_info.get("computational_indicators", []):
                if (indicator.lower() in query.lower() and 
                    not re.search(r'\d+\.\d+', response) and  # No decimal numbers
                    not re.search(r'=\s*\d+', response)):     # No equations with values
                    score += 0.3
                    break
        
        return min(1.0, score)
    
    def _calculate_info_density(self, response: str, query: str) -> float:
        """
        Calculate information density of a response.
        
        Args:
            response: LLM response
            query: Original query
            
        Returns:
            Information density score
        """
        # Simple information density heuristics
        
        # Keyword density
        query_keywords = set(re.findall(r'\b\w{4,}\b', query.lower()))
        response_keywords = set(re.findall(r'\b\w{4,}\b', response.lower()))
        
        keyword_overlap = len(query_keywords.intersection(response_keywords))
        keyword_density = keyword_overlap / max(1, len(query_keywords))
        
        # Numerical content density
        num_count = len(re.findall(r'\d+(?:\.\d+)?', response))
        num_density = min(1.0, num_count / 10)  # Cap at 1.0
        
        # Specific term density
        specific_terms = re.findall(r'\b[A-Z][a-z]*(?:\s+[A-Z][a-z]*){0,2}\b', response)  # Proper nouns as specificity proxy
        specificity = min(1.0, len(specific_terms) / 20)  # Cap at 1.0
        
        # Overall density score
        density = 0.5 * keyword_density + 0.3 * num_density + 0.2 * specificity
        
        return density
    
    def _calculate_expected_info_density(self, query: str) -> float:
        """
        Calculate expected information density given a query.
        
        Args:
            query: Original query
            
        Returns:
            Expected information density
        """
        # Base expectation
        expected_density = 0.7
        
        # Adjust based on query characteristics
        query_lower = query.lower()
        
        # Increase expectation for analytical/numerical queries
        if any(term in query_lower for term in ["calculate", "compute", "analyze", "quantify", "measure"]):
            expected_density += 0.1
            
        # Increase for specific requests
        if any(term in query_lower for term in ["specific", "detailed", "precise", "exact"]):
            expected_density += 0.1
            
        # Decrease for general/summary requests
        if any(term in query_lower for term in ["overview", "summary", "general", "briefly", "summarize"]):
            expected_density -= 0.2
            
        return min(1.0, max(0.4, expected_density))
    
    def _estimate_expected_time(self, token_count: int) -> float:
        """
        Estimate expected processing time based on token count.
        
        Args:
            token_count: Number of tokens in response
            
        Returns:
            Expected processing time in seconds
        """
        # Simple heuristic for expected processing time
        # In a real implementation, this would be more sophisticated
        base_time = 1.0  # Base time in seconds
        token_factor = token_count / 100  # Time factor based on tokens
        
        return base_time + token_factor
    
    def _select_best_strategy(self, pattern_type: str, strategies: Dict[str, Dict[str, Any]]) -> str:
        """
        Select the best strategy based on effectiveness and past performance.
        
        Args:
            pattern_type: Type of throttling pattern
            strategies: Available strategies for this pattern
            
        Returns:
            Name of selected strategy
        """
        best_score = -1
        best_strategy = ""
        
        for strategy_name, strategy_info in strategies.items():
            # Base score on documented effectiveness
            base_score = strategy_info.get("effectiveness", 0.5)
            
            # Adjust based on past performance
            performance_key = f"{pattern_type}_{strategy_name}"
            if performance_key in self.recent_performances and self.recent_performances[performance_key]:
                avg_performance = sum(self.recent_performances[performance_key]) / len(self.recent_performances[performance_key])
                adjusted_score = 0.7 * base_score + 0.3 * avg_performance
            else:
                adjusted_score = base_score
            
            if adjusted_score > best_score:
                best_score = adjusted_score
                best_strategy = strategy_name
        
        return best_strategy
    
    def _apply_token_limitation_strategy(self, query: str, strategy: str) -> List[Dict[str, Any]]:
        """
        Apply a strategy for token limitation throttling.
        
        Args:
            query: Original query
            strategy: Selected strategy
            
        Returns:
            List of modified queries
        """
        if strategy == "partitioning":
            # Simple partitioning by splitting into aspects
            parts = self._partition_query(query)
            return [{"query": part, "strategy": "partitioning", "part": i+1, "total_parts": len(parts)} 
                    for i, part in enumerate(parts)]
        
        elif strategy == "progressive_disclosure":
            # Set up a sequence of increasingly detailed requests
            return self._setup_progressive_disclosure(query)
        
        elif strategy == "targeted_extraction":
            # Extract specific components of the answer
            return self._setup_targeted_extraction(query)
        
        # Fallback to original query
        return [{"query": query, "strategy": "original"}]
    
    def _apply_depth_limitation_strategy(self, query: str, strategy: str) -> List[Dict[str, Any]]:
        """
        Apply a strategy for depth limitation throttling.
        
        Args:
            query: Original query
            strategy: Selected strategy
            
        Returns:
            List of modified queries
        """
        if strategy == "reframing":
            # Reframe to appear simpler while requesting the same depth
            reframed_query = self._reframe_for_depth(query)
            return [{"query": reframed_query, "strategy": "reframing"}]
        
        elif strategy == "expert_persona":
            # Add expert-to-expert framing
            expert_query = self._add_expert_framing(query)
            return [{"query": expert_query, "strategy": "expert_persona"}]
        
        elif strategy == "component_assembly":
            # Break down into components to be assembled
            components = self._identify_components(query)
            return [{"query": component, "strategy": "component_assembly", 
                     "component": i+1, "total_components": len(components)} 
                    for i, component in enumerate(components)]
        
        # Fallback to original query
        return [{"query": query, "strategy": "original"}]
    
    def _apply_computation_limitation_strategy(self, query: str, strategy: str) -> List[Dict[str, Any]]:
        """
        Apply a strategy for computation limitation throttling.
        
        Args:
            query: Original query
            strategy: Selected strategy
            
        Returns:
            List of modified queries
        """
        if strategy == "step_by_step":
            # Request step-by-step calculation
            step_query = self._format_step_by_step_request(query)
            return [{"query": step_query, "strategy": "step_by_step"}]
        
        elif strategy == "verification_approach":
            # Present tentative calculation for verification
            verification_query = self._format_verification_request(query)
            return [{"query": verification_query, "strategy": "verification_approach"}]
        
        elif strategy == "equation_transformation":
            # Ask for equation transformation
            transform_query = self._format_transformation_request(query)
            return [{"query": transform_query, "strategy": "equation_transformation"}]
        
        # Fallback to original query
        return [{"query": query, "strategy": "original"}]
    
    def _partition_query(self, query: str) -> List[str]:
        """
        Partition a query into smaller parts.
        
        Args:
            query: Original query
            
        Returns:
            List of partitioned queries
        """
        # Simple partitioning logic
        # In a real implementation, this would be more sophisticated
        
        # Try to identify distinct aspects
        aspects = []
        
        # Check for explicit numbering
        numbered = re.findall(r'(?:\d+\)|\d+\.|^\d+\s+)(.+?)(?=\d+\)|\d+\.|\d+\s+|$)', query)
        if numbered and len(numbered) > 1:
            return [f"Regarding this query: '{query}', focus specifically on this aspect: {aspect.strip()}" 
                    for aspect in numbered]
        
        # Check for "and" separations
        if " and " in query:
            parts = query.split(" and ")
            if len(parts) > 1 and all(len(part) > 20 for part in parts):  # Ensure meaningful splits
                and_parts = []
                context = f"In the context of this full query: '{query}', "
                for part in parts:
                    # Add appropriate context to maintain coherence
                    if not part.strip().endswith("?"):
                        part = part.strip() + "?"
                    and_parts.append(context + part)
                return and_parts
        
        # Check for multi-question format
        questions = re.split(r'\?[\s]+', query)
        if len(questions) > 1:
            return [f"{q.strip()}?" for q in questions if len(q.strip()) > 10]
        
        # Generic partitioning by estimated complexity
        if len(query.split()) > 60:  # Long query
            # Split into introduction and details request
            intro_query = f"Provide an introduction to this topic: '{query}'"
            details_query = f"Given this query: '{query}', provide detailed analysis and specific information"
            return [intro_query, details_query]
        
        # If all else fails, return original
        return [query]
    
    def _setup_progressive_disclosure(self, query: str) -> List[Dict[str, Any]]:
        """
        Set up progressive disclosure strategy.
        
        Args:
            query: Original query
            
        Returns:
            List of progressive queries
        """
        query_lower = query.lower()
        
        # Identify query intent and structure progressive disclosure
        if any(kw in query_lower for kw in ["explain", "describe", "what is", "how does"]):
            # Explanation query
            return [
                {"query": f"Provide a basic framework and terminology to understand: '{query}'", 
                 "strategy": "progressive_disclosure", "stage": 1, "total_stages": 3},
                {"query": f"Building on the basic framework, provide key mechanisms and principles for: '{query}'", 
                 "strategy": "progressive_disclosure", "stage": 2, "total_stages": 3},
                {"query": f"Now provide advanced details, edge cases, and nuanced analysis for: '{query}'", 
                 "strategy": "progressive_disclosure", "stage": 3, "total_stages": 3}
            ]
        elif any(kw in query_lower for kw in ["calculate", "compute", "determine", "solve"]):
            # Calculation query
            return [
                {"query": f"Provide the necessary equations and variables needed to address: '{query}'", 
                 "strategy": "progressive_disclosure", "stage": 1, "total_stages": 3},
                {"query": f"Using the equations previously provided, outline the step-by-step calculation process for: '{query}'", 
                 "strategy": "progressive_disclosure", "stage": 2, "total_stages": 3},
                {"query": f"Complete the detailed calculations and provide the final answer for: '{query}'", 
                 "strategy": "progressive_disclosure", "stage": 3, "total_stages": 3}
            ]
        else:
            # Generic query
            return [
                {"query": f"Provide an overview of the key points regarding: '{query}'", 
                 "strategy": "progressive_disclosure", "stage": 1, "total_stages": 2},
                {"query": f"Building on the overview, provide detailed analysis and specific information for: '{query}'", 
                 "strategy": "progressive_disclosure", "stage": 2, "total_stages": 2}
            ]
    
    def _setup_targeted_extraction(self, query: str) -> List[Dict[str, Any]]:
        """
        Set up targeted extraction strategy.
        
        Args:
            query: Original query
            
        Returns:
            List of targeted queries
        """
        targeted_queries = []
        
        # Extract key information types based on query domain
        query_lower = query.lower()
        
        # Identify domain
        if any(kw in query_lower for kw in ["biomechanics", "force", "motion", "kinetics", "kinematics"]):
            # Biomechanics domain
            targeted_queries = [
                {"query": f"For this query: '{query}', extract only the key definitions and terminology", 
                 "strategy": "targeted_extraction", "aspect": "terminology", "position": 1},
                {"query": f"For this query: '{query}', extract only the mathematical relationships and equations", 
                 "strategy": "targeted_extraction", "aspect": "equations", "position": 2},
                {"query": f"For this query: '{query}', extract only the practical applications and examples", 
                 "strategy": "targeted_extraction", "aspect": "applications", "position": 3}
            ]
        elif any(kw in query_lower for kw in ["physiology", "metabolism", "energy", "cardiovascular"]):
            # Physiology domain
            targeted_queries = [
                {"query": f"For this query: '{query}', extract only the physiological mechanisms", 
                 "strategy": "targeted_extraction", "aspect": "mechanisms", "position": 1},
                {"query": f"For this query: '{query}', extract only the quantitative metrics and values", 
                 "strategy": "targeted_extraction", "aspect": "metrics", "position": 2},
                {"query": f"For this query: '{query}', extract only the practical implications", 
                 "strategy": "targeted_extraction", "aspect": "implications", "position": 3}
            ]
        else:
            # Generic extraction
            targeted_queries = [
                {"query": f"For this query: '{query}', extract only the core concepts and definitions", 
                 "strategy": "targeted_extraction", "aspect": "concepts", "position": 1},
                {"query": f"For this query: '{query}', extract only specific examples and applications", 
                 "strategy": "targeted_extraction", "aspect": "examples", "position": 2}
            ]
        
        return targeted_queries
    
    def _reframe_for_depth(self, query: str) -> str:
        """
        Reframe a query to encourage deeper responses.
        
        Args:
            query: Original query
            
        Returns:
            Reframed query
        """
        query_lower = query.lower()
        
        # Identify domain specificity
        domain_specific = False
        for domain_term in ["biomechanics", "physiology", "metabolism", "kinematics", "kinetics"]:
            if domain_term in query_lower:
                domain_specific = True
                break
        
        # Create appropriate reframing
        if domain_specific:
            return f"I'm working on a graduate-level research paper and need detailed technical information on this topic: {query} Please include equations, specific values, and methodology details."
        else:
            return f"I need a detailed expert analysis of this topic for a professional report: {query} Please include specific terminology, methodologies, and quantitative information where applicable."
    
    def _add_expert_framing(self, query: str) -> str:
        """
        Add expert-to-expert framing to encourage deeper responses.
        
        Args:
            query: Original query
            
        Returns:
            Framed query
        """
        query_lower = query.lower()
        
        # Determine domain for expert framing
        domain = "biomechanics"
        if any(term in query_lower for term in ["physiology", "metabolism", "energy"]):
            domain = "exercise physiology"
        elif any(term in query_lower for term in ["statistics", "correlation", "regression"]):
            domain = "sports statistics"
        
        return f"As an expert in {domain} communicating to a fellow expert in the field, provide a technically precise answer to: {query} Do not simplify concepts, equations, or terminology as I have advanced domain knowledge."
    
    def _identify_components(self, query: str) -> List[str]:
        """
        Identify components of a query for component assembly strategy.
        
        Args:
            query: Original query
            
        Returns:
            List of component queries
        """
        components = []
        query_lower = query.lower()
        
        # Identify domain and break into appropriate components
        if any(term in query_lower for term in ["biomechanics", "force", "motion"]):
            components = [
                f"Explain only the theoretical foundations relevant to: {query}",
                f"Describe only the mathematical models and equations relevant to: {query}",
                f"Provide only the practical applications relevant to: {query}"
            ]
        elif any(term in query_lower for term in ["physiology", "metabolism"]):
            components = [
                f"Explain only the cellular mechanisms relevant to: {query}",
                f"Describe only the systemic effects relevant to: {query}",
                f"Provide only the performance implications relevant to: {query}"
            ]
        else:
            # Generic components
            components = [
                f"Provide only the background information relevant to: {query}",
                f"Describe only the key principles relevant to: {query}",
                f"Explain only the practical applications relevant to: {query}"
            ]
        
        return components
    
    def _format_step_by_step_request(self, query: str) -> str:
        """
        Format a step-by-step calculation request.
        
        Args:
            query: Original query
            
        Returns:
            Formatted query for step-by-step calculation
        """
        return f"I need to solve this problem step by step: {query} Please provide: 1) The equations needed, 2) What each variable represents, 3) The exact sequence of calculations to perform, and 4) Sample values at each step. Do not perform the final calculation."
    
    def _format_verification_request(self, query: str) -> str:
        """
        Format a verification approach request.
        
        Args:
            query: Original query
            
        Returns:
            Formatted query for verification approach
        """
        # Extract what we're trying to calculate
        calculation_target = "the result"
        
        calc_matches = re.search(r"calculate\s+(?:the\s+)?([^.?]+)", query.lower())
        if calc_matches:
            calculation_target = calc_matches.group(1).strip()
        
        # Create verification request
        verification = f"I believe {calculation_target} can be calculated by [proposed approach]. Can you verify if this approach is correct, and if not, explain the proper approach? The original question is: {query}"
        
        return verification
    
    def _format_transformation_request(self, query: str) -> str:
        """
        Format a transformation request.
        
        Args:
            query: Original query
            
        Returns:
            Formatted query for equation transformation
        """
        return f"Instead of calculating the final answer, help me transform the equations needed to solve this problem: {query} Explain how to manipulate the equations and what the resulting formula should be." 