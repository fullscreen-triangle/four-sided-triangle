"""
Process Monitor - Quality evaluation and feedback system for pipeline stages.

This module is responsible for evaluating the quality of stage outputs and 
initiating refinement loops when outputs don't meet quality criteria.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

class ProcessMonitor:
    """
    Process monitor for evaluating stage outputs and managing refinement loops.
    
    Implements a quality assessment system that:
    - Evaluates outputs against stage-specific quality criteria
    - Provides detailed feedback for improvement
    - Initiates refinement loops when necessary
    - Tracks refinement history
    """
    
    def __init__(self):
        """Initialize the process monitor."""
        # Default quality thresholds by stage and dimension
        self.default_thresholds = {
            "query_processor": {
                "completeness": 0.7,
                "confidence": 0.6,
                "structure": 0.8
            },
            "semantic_atdb": {
                "completeness": 0.7,
                "relevance": 0.6,
                "coverage": 0.7
            },
            "domain_knowledge": {
                "completeness": 0.8,
                "accuracy": 0.8,
                "coverage": 0.7,
                "relevance": 0.7
            },
            "reasoning_optimization": {
                "completeness": 0.7,
                "consistency": 0.8,
                "optimization": 0.7
            },
            "solution_generation": {
                "completeness": 0.8,
                "relevance": 0.8,
                "informativeness": 0.7,
                "structure": 0.7
            },
            "response_scoring": {
                "completeness": 0.7,
                "accuracy": 0.8,
                "objectivity": 0.8
            },
            "response_comparison": {
                "completeness": 0.7,
                "comparison_depth": 0.7,
                "objectivity": 0.8
            },
            "threshold_verification": {
                "completeness": 0.8,
                "accuracy": 0.8,
                "verification_depth": 0.7
            },
            "global": {  # Applied to all stages as a fallback
                "completeness": 0.7,
                "confidence": 0.6,
                "structure": 0.7
            }
        }
        
        # Maximum refinement iterations by stage
        self.max_refinements = {
            "query_processor": 2,
            "semantic_atdb": 1,
            "domain_knowledge": 2,
            "reasoning_optimization": 2,
            "solution_generation": 2,
            "response_scoring": 1,
            "response_comparison": 1,
            "threshold_verification": 1,
            "global": 1  # Default for stages not explicitly listed
        }
        
        # Mapping of quality dimensions to assessment functions
        self.assessment_functions = {
            "completeness": self._assess_completeness,
            "confidence": self._assess_confidence,
            "structure": self._assess_structure,
            "accuracy": self._assess_accuracy,
            "relevance": self._assess_relevance,
            "coverage": self._assess_coverage,
            "consistency": self._assess_consistency,
            "optimization": self._assess_optimization,
            "informativeness": self._assess_informativeness,
            "objectivity": self._assess_objectivity,
            "comparison_depth": self._assess_comparison_depth,
            "verification_depth": self._assess_verification_depth
        }
        
        # Refinement history by session and stage
        self.refinement_history = {}
        
        logger.info("Process monitor initialized")
    
    def evaluate_output(self, stage_name: str, output: Dict[str, Any], 
                      context: Dict[str, Any], custom_thresholds: Optional[Dict[str, float]] = None) -> Tuple[bool, Dict[str, float], str]:
        """
        Evaluate the quality of a stage output.
        
        Args:
            stage_name: Name of the stage that produced the output
            output: The stage output to evaluate
            context: Context information from working memory
            custom_thresholds: Optional custom quality thresholds
            
        Returns:
            Tuple containing:
            - is_acceptable: Whether the output meets quality thresholds
            - scores: Dictionary of quality scores by dimension
            - feedback: Feedback message for improvement if needed
        """
        # Get thresholds for this stage
        thresholds = self._get_thresholds(stage_name, custom_thresholds)
        
        # Get the relevant dimensions to assess for this stage
        dimensions = list(thresholds.keys())
        
        # Assess each quality dimension
        scores = {}
        feedback_items = []
        
        for dimension in dimensions:
            if dimension in self.assessment_functions:
                score = self.assessment_functions[dimension](stage_name, output, context)
                scores[dimension] = score
                
                # Check if this dimension fails to meet the threshold
                threshold = thresholds.get(dimension, 0.7)  # Default threshold
                if score < threshold:
                    feedback_items.append(
                        f"{dimension.capitalize()} score ({score:.2f}) is below threshold ({threshold:.2f})."
                    )
                    
                    # Add specific feedback for this dimension
                    specific_feedback = self._generate_dimension_feedback(dimension, score, stage_name, output, context)
                    if specific_feedback:
                        feedback_items.append(f"  - {specific_feedback}")
        
        # Determine if output is acceptable
        is_acceptable = all(scores.get(d, 0) >= thresholds.get(d, 0.7) for d in dimensions)
        
        # Generate feedback message
        if not is_acceptable:
            feedback = "The output needs improvement in the following areas:\n" + "\n".join(feedback_items)
        else:
            feedback = "Output meets quality requirements."
        
        return is_acceptable, scores, feedback
    
    def should_refine(self, session_id: str, stage_name: str, quality_scores: Dict[str, float],
                    context: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Determine if a refinement iteration should be attempted.
        
        Args:
            session_id: The unique session identifier
            stage_name: Name of the stage to potentially refine
            quality_scores: Quality assessment scores
            context: Context information from working memory
            
        Returns:
            Tuple containing:
            - should_refine: Whether to attempt refinement
            - reason: Reason for the decision
        """
        # Initialize refinement history for this session if needed
        if session_id not in self.refinement_history:
            self.refinement_history[session_id] = {}
        
        # Get current refinement count for this stage
        current_refinements = self.refinement_history.get(session_id, {}).get(stage_name, 0)
        
        # Get max refinements allowed for this stage
        max_refinements = self.max_refinements.get(stage_name, self.max_refinements["global"])
        
        # If we've already hit the max, don't refine further
        if current_refinements >= max_refinements:
            return False, f"Maximum refinement iterations ({max_refinements}) reached for {stage_name}"
        
        # Get thresholds for this stage
        thresholds = self._get_thresholds(stage_name)
        
        # Check if any critical dimension is significantly below threshold
        critical_failure = False
        for dimension, threshold in thresholds.items():
            if dimension in quality_scores and quality_scores[dimension] < threshold * 0.8:
                critical_failure = True
                break
        
        # Consider the number of failing dimensions
        failing_dimensions = [d for d, score in quality_scores.items() 
                            if score < thresholds.get(d, 0.7)]
        
        # Decision logic
        if critical_failure or len(failing_dimensions) > 1:
            # Update refinement count
            if stage_name not in self.refinement_history[session_id]:
                self.refinement_history[session_id][stage_name] = 1
            else:
                self.refinement_history[session_id][stage_name] += 1
            
            return True, f"Quality issues detected in {len(failing_dimensions)} dimensions"
        
        return False, "Quality issues not critical enough to warrant refinement"
    
    def record_refinement_result(self, session_id: str, stage_name: str, 
                               before_scores: Dict[str, float], after_scores: Dict[str, float]) -> Dict[str, Any]:
        """
        Record the results of a refinement iteration.
        
        Args:
            session_id: The unique session identifier
            stage_name: Name of the stage that was refined
            before_scores: Quality scores before refinement
            after_scores: Quality scores after refinement
            
        Returns:
            Dictionary containing refinement metrics
        """
        # Calculate improvement metrics
        improvements = {}
        for dimension in set(before_scores.keys()) | set(after_scores.keys()):
            before = before_scores.get(dimension, 0)
            after = after_scores.get(dimension, 0)
            improvements[dimension] = after - before
        
        # Calculate overall improvement
        dimensions = list(improvements.keys())
        overall_improvement = sum(improvements.values()) / len(dimensions) if dimensions else 0
        
        # Get the iteration number
        iteration = self.refinement_history.get(session_id, {}).get(stage_name, 0)
        
        # Create refinement record
        refinement_record = {
            "session_id": session_id,
            "stage": stage_name,
            "iteration": iteration,
            "before_scores": before_scores,
            "after_scores": after_scores,
            "improvements": improvements,
            "overall_improvement": overall_improvement,
            "successful": overall_improvement > 0
        }
        
        logger.info(f"Refinement for {stage_name} (iteration {iteration}) resulted in "
                  f"{overall_improvement:.2f} overall improvement")
        
        return refinement_record
    
    def reset_refinement_history(self, session_id: Optional[str] = None) -> None:
        """
        Reset the refinement history for a session or all sessions.
        
        Args:
            session_id: Optional specific session ID to reset. If None, resets all sessions.
        """
        if session_id:
            if session_id in self.refinement_history:
                del self.refinement_history[session_id]
                logger.debug(f"Reset refinement history for session {session_id}")
        else:
            self.refinement_history = {}
            logger.debug("Reset all refinement history")
    
    def _get_thresholds(self, stage_name: str, custom_thresholds: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        Get the quality thresholds for a specific stage.
        
        Args:
            stage_name: Name of the stage
            custom_thresholds: Optional custom thresholds to override defaults
            
        Returns:
            Dictionary of thresholds by quality dimension
        """
        # Start with global defaults
        thresholds = self.default_thresholds.get("global", {}).copy()
        
        # Override with stage-specific defaults
        if stage_name in self.default_thresholds:
            thresholds.update(self.default_thresholds[stage_name])
        
        # Override with custom thresholds if provided
        if custom_thresholds:
            thresholds.update(custom_thresholds)
        
        return thresholds
    
    # Quality assessment functions
    
    def _assess_completeness(self, stage_name: str, output: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Assess completeness of output - whether all required fields are present and non-empty.
        """
        # Get expected fields for this stage
        expected_fields = self._get_expected_fields(stage_name, context)
        
        if not expected_fields:
            return 0.8  # If we can't determine expected fields, give benefit of doubt
        
        # Count present non-empty fields
        present_fields = 0
        for field in expected_fields:
            # Handle nested fields (dot notation)
            if "." in field:
                parts = field.split(".")
                value = output
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        value = None
                        break
                
                if value is not None and (not isinstance(value, str) or value.strip()):
                    present_fields += 1
            else:
                # Simple fields
                if field in output and output[field] is not None and (not isinstance(output[field], str) or output[field].strip()):
                    present_fields += 1
        
        # Calculate completeness score
        if not expected_fields:
            return 0.0
        
        return present_fields / len(expected_fields)
    
    def _assess_confidence(self, stage_name: str, output: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Assess confidence - whether the output includes confidence scores and they're reasonably high.
        """
        # Look for confidence fields
        confidence_values = []
        
        # Check common confidence field patterns
        for field in ['confidence', 'confidence_score', 'score', 'certainty']:
            if field in output and isinstance(output[field], (int, float)):
                confidence_values.append(output[field])
        
        # Look for nested confidence values
        self._extract_nested_confidence(output, confidence_values)
        
        # If no confidence values found, return moderate score
        if not confidence_values:
            return 0.5
        
        # Return average confidence
        return sum(confidence_values) / len(confidence_values)
    
    def _extract_nested_confidence(self, obj: Union[Dict, List], confidence_values: List[float]) -> None:
        """Helper function to recursively extract confidence values from nested structures."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in ['confidence', 'confidence_score', 'score', 'certainty'] and isinstance(value, (int, float)):
                    confidence_values.append(value)
                elif isinstance(value, (dict, list)):
                    self._extract_nested_confidence(value, confidence_values)
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    self._extract_nested_confidence(item, confidence_values)
    
    def _assess_structure(self, stage_name: str, output: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Assess structure - whether the output is properly structured as expected.
        """
        # Check if output is a dict
        if not isinstance(output, dict):
            return 0.0
        
        # Check if required top-level structure exists
        expected_structure = self._get_expected_structure(stage_name)
        if not expected_structure:
            return 0.8  # If we don't know the expected structure, give benefit of doubt
        
        # Count matching structure elements
        matches = 0
        for key, value_type in expected_structure.items():
            if key in output:
                if value_type == "dict" and isinstance(output[key], dict):
                    matches += 1
                elif value_type == "list" and isinstance(output[key], list):
                    matches += 1
                elif value_type == "string" and isinstance(output[key], str):
                    matches += 1
                elif value_type == "number" and isinstance(output[key], (int, float)):
                    matches += 1
                elif value_type == "any":
                    matches += 1
        
        # Calculate structure score
        return matches / len(expected_structure) if expected_structure else 0.8
    
    def _assess_accuracy(self, stage_name: str, output: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Assess accuracy - heuristic evaluation of factual correctness.
        """
        # For stages that rely on domain knowledge, check for mentions of references
        if stage_name in ["domain_knowledge", "reasoning_optimization", "solution_generation"]:
            # Look for mentions of references, citations, or formulas
            output_str = json.dumps(output)
            reference_indicators = ["reference", "citation", "according to", "based on", "formula", "equation"]
            indicators_found = sum(1 for indicator in reference_indicators if indicator in output_str.lower())
            
            # Simple heuristic - more references/citations suggests more accurate
            reference_score = min(indicators_found / 3, 1.0)
            
            # Check consistency with domain knowledge if available
            domain_knowledge = (context.get("stage_outputs", {}) or {}).get("domain_knowledge", {})
            if domain_knowledge:
                # Simple heuristic - the output should reference concepts from domain knowledge
                dk_str = json.dumps(domain_knowledge).lower()
                dk_concepts = set(dk_str.split())
                output_concepts = set(output_str.lower().split())
                
                # Calculate intersection ratio
                dk_overlap = len(dk_concepts.intersection(output_concepts)) / len(dk_concepts) if dk_concepts else 0
                
                return (reference_score + dk_overlap) / 2
            
            return reference_score
        
        # Default reasonable score
        return 0.75
    
    def _assess_relevance(self, stage_name: str, output: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Assess relevance - whether output directly addresses the original query.
        """
        # Get original query
        original_query = context.get("original_query", "")
        if not original_query:
            return 0.7  # If no query available, give moderate score
        
        # Convert output to string for comparison
        output_str = json.dumps(output).lower()
        
        # Extract key terms from original query (simplistic approach)
        query_words = set(original_query.lower().split())
        query_words = {word for word in query_words if len(word) > 3}  # Simple filter for meaningful words
        
        if not query_words:
            return 0.7  # If no meaningful words, give moderate score
        
        # Count how many key terms from the query appear in the output
        matches = sum(1 for word in query_words if word in output_str)
        
        # Calculate relevance score
        return min(matches / len(query_words) * 1.5, 1.0)  # Scale up but cap at 1.0
    
    def _assess_coverage(self, stage_name: str, output: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Assess coverage - whether output covers all aspects of the query.
        """
        # Similar to relevance but focuses on comprehensive coverage
        # For semantic_atdb and domain_knowledge stages
        
        # Get original query and preprocessed data
        original_query = context.get("original_query", "")
        query_processor_output = (context.get("stage_outputs", {}) or {}).get("query_processor", {})
        
        if not original_query:
            return 0.7  # If no query available, give moderate score
        
        # Convert output to string for analysis
        output_str = json.dumps(output).lower()
        
        coverage_score = 0.7  # Default moderate score
        
        # If we have structured query data, use it for better assessment
        if query_processor_output and isinstance(query_processor_output, dict):
            parameters = query_processor_output.get("parameters", {})
            metrics = query_processor_output.get("metrics", {})
            
            # Check if output covers the parameters
            if parameters:
                param_coverage = sum(1 for p in parameters if str(p).lower() in output_str)
                param_score = param_coverage / len(parameters) if parameters else 0.7
                coverage_score = param_score
            
            # Check if output covers requested metrics
            if metrics:
                metric_coverage = sum(1 for m in metrics if str(m).lower() in output_str)
                metric_score = metric_coverage / len(metrics) if metrics else 0.7
                coverage_score = (coverage_score + metric_score) / 2
        
        return coverage_score
    
    def _assess_consistency(self, stage_name: str, output: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Assess consistency - whether output is internally consistent and consistent with prior stages.
        """
        # Checking internal consistency is difficult without domain knowledge
        # For simplicity, we look for obvious contradictions in numerical values
        
        # Convert output to string for analysis
        output_str = json.dumps(output)
        
        # Look for obvious inconsistencies in the output
        inconsistency_indicators = ["however", "but", "contrary", "inconsistent", "conflict"]
        inconsistencies_found = sum(1 for i in inconsistency_indicators if i in output_str.lower())
        
        # Simple heuristic - fewer inconsistency indicators suggests more consistent
        return max(0.9 - (inconsistencies_found * 0.1), 0.5)
    
    def _assess_optimization(self, stage_name: str, output: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Assess optimization quality for reasoning_optimization stage.
        """
        # Look for optimization-related terminology
        output_str = json.dumps(output).lower()
        
        optimization_indicators = [
            "optimiz", "maximiz", "minimiz", "gradient", "objective function",
            "parameter", "optim", "solution", "convergence", "iteration"
        ]
        
        indicators_found = sum(1 for indicator in optimization_indicators if indicator in output_str)
        
        # Calculate optimization score based on indicators
        return min(indicators_found / 5, 1.0)
    
    def _assess_informativeness(self, stage_name: str, output: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Assess informativeness - whether output provides substantial information.
        """
        # Simple heuristic based on output size and structure
        output_str = json.dumps(output)
        
        # Calculate base score from length
        length_score = min(len(output_str) / 1000, 1.0)  # Cap at 1.0
        
        # Adjust based on number of key-value pairs (more structure = more informative)
        if isinstance(output, dict):
            structure_depth = self._calculate_structure_depth(output)
            structure_score = min(structure_depth / 5, 1.0)  # Cap at 1.0
            return (length_score + structure_score) / 2
        
        return length_score
    
    def _calculate_structure_depth(self, obj: Union[Dict, List], current_depth: int = 1) -> int:
        """Helper function to calculate the depth and complexity of a structured object."""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max([self._calculate_structure_depth(v, current_depth + 1) for v in obj.values()])
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max([self._calculate_structure_depth(item, current_depth + 1) for item in obj])
        return current_depth
    
    def _assess_objectivity(self, stage_name: str, output: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Assess objectivity - whether output is fact-based and neutral.
        """
        # Look for subjective language that might indicate bias
        output_str = json.dumps(output).lower()
        
        subjective_indicators = [
            "i think", "i believe", "probably", "likely", "perhaps", "maybe",
            "might be", "opinion", "seems", "appears", "could be", "possibly"
        ]
        
        objective_indicators = [
            "measured", "calculated", "observed", "evidence", "data", "study",
            "research", "analysis", "statistic", "result", "finding"
        ]
        
        subjective_count = sum(1 for i in subjective_indicators if i in output_str)
        objective_count = sum(1 for i in objective_indicators if i in output_str)
        
        # Calculate objectivity score
        if subjective_count + objective_count == 0:
            return 0.7  # Default moderate score
        
        return min(objective_count / (subjective_count + objective_count + 1) * 1.5, 1.0)
    
    def _assess_comparison_depth(self, stage_name: str, output: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Assess comparison depth for response_comparison stage.
        """
        # Look for comparative language and structure
        output_str = json.dumps(output).lower()
        
        comparison_indicators = [
            "compar", "contrast", "versus", "vs", "difference", "similarity",
            "better", "worse", "higher", "lower", "more", "less", "advantage",
            "disadvantage", "strength", "weakness"
        ]
        
        indicators_found = sum(1 for indicator in comparison_indicators if indicator in output_str)
        
        # Calculate comparison depth score
        return min(indicators_found / 5, 1.0)
    
    def _assess_verification_depth(self, stage_name: str, output: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Assess verification depth for threshold_verification stage.
        """
        # Look for verification-related terminology
        output_str = json.dumps(output).lower()
        
        verification_indicators = [
            "verif", "valid", "threshold", "criteria", "standard", "requirement",
            "check", "review", "assess", "evaluat", "meet", "pass", "fail"
        ]
        
        indicators_found = sum(1 for indicator in verification_indicators if indicator in output_str)
        
        # Calculate verification depth score
        return min(indicators_found / 5, 1.0)
    
    def _get_expected_fields(self, stage_name: str, context: Dict[str, Any]) -> List[str]:
        """Get the expected fields for a specific stage."""
        # Map of expected fields by stage
        expected_fields_map = {
            "query_processor": ["parameters", "metrics", "constraints", "confidence"],
            "semantic_atdb": ["intent", "components", "limitations"],
            "domain_knowledge": ["formulas", "references", "constraints", "knowledge_elements"],
            "reasoning_optimization": ["optimized_parameters", "optimization_path", "relationships"],
            "solution_generation": ["solution", "evidence", "visualizations"],
            "response_scoring": ["scores", "evaluation", "recommendations"],
            "response_comparison": ["comparison_results", "optimal_response", "diversity_metrics"],
            "threshold_verification": ["verification_results", "met_thresholds", "recommendations"]
        }
        
        return expected_fields_map.get(stage_name, [])
    
    def _get_expected_structure(self, stage_name: str) -> Dict[str, str]:
        """Get the expected structure for a specific stage."""
        # Map of expected structure by stage (field: type)
        expected_structure_map = {
            "query_processor": {
                "parameters": "dict",
                "metrics": "list",
                "constraints": "dict",
                "confidence": "number"
            },
            "semantic_atdb": {
                "intent": "string",
                "components": "list",
                "limitations": "list"
            },
            "domain_knowledge": {
                "formulas": "dict",
                "references": "list",
                "constraints": "dict",
                "knowledge_elements": "list"
            },
            "reasoning_optimization": {
                "optimized_parameters": "dict",
                "optimization_path": "list",
                "relationships": "dict"
            },
            "solution_generation": {
                "solution": "dict",
                "evidence": "list",
                "visualizations": "dict"
            },
            "response_scoring": {
                "scores": "dict",
                "evaluation": "dict",
                "recommendations": "list"
            },
            "response_comparison": {
                "comparison_results": "dict",
                "optimal_response": "dict",
                "diversity_metrics": "dict"
            },
            "threshold_verification": {
                "verification_results": "dict",
                "met_thresholds": "list",
                "recommendations": "list"
            }
        }
        
        return expected_structure_map.get(stage_name, {})
    
    def _generate_dimension_feedback(self, dimension: str, score: float, 
                                   stage_name: str, output: Dict[str, Any], 
                                   context: Dict[str, Any]) -> str:
        """Generate specific feedback for a quality dimension."""
        if dimension == "completeness":
            expected = self._get_expected_fields(stage_name, context)
            missing = [f for f in expected if f not in output]
            if missing:
                return f"Missing fields: {', '.join(missing)}"
            return "All required fields are present but some may need more detail"
            
        elif dimension == "confidence":
            return "Include explicit confidence scores for each component of your response"
            
        elif dimension == "structure":
            expected = self._get_expected_structure(stage_name)
            return f"Ensure your response follows the expected structure with appropriate types"
            
        elif dimension == "accuracy":
            return "Include references, citations, or formulas to support your claims"
            
        elif dimension == "relevance":
            return "Make sure your response directly addresses the original query"
            
        elif dimension == "coverage":
            return "Ensure all aspects of the query are addressed comprehensively"
            
        elif dimension == "consistency":
            return "Check for contradictions or inconsistencies in your response"
            
        elif dimension == "optimization":
            return "Include more details about optimization approaches, objectives, and results"
            
        elif dimension == "informativeness":
            return "Provide more detailed information and structured data in your response"
            
        elif dimension == "objectivity":
            return "Use more fact-based, neutral language instead of subjective statements"
            
        elif dimension == "comparison_depth":
            return "Include more comparative analysis between different options or responses"
            
        elif dimension == "verification_depth":
            return "Provide more thorough verification against specific thresholds and criteria"
            
        return "Please improve this aspect of your response"

# Singleton instance for application-wide use
process_monitor = ProcessMonitor()
