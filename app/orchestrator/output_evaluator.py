"""
Output evaluator for the Four-Sided Triangle orchestration system.

This module provides an implementation of the output evaluator that assesses
the quality and completeness of pipeline stage outputs and determines if 
refinement is needed.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
import json

from app.orchestrator.interfaces import OutputEvaluatorInterface

logger = logging.getLogger(__name__)

class OutputEvaluator(OutputEvaluatorInterface):
    """
    Implementation of the output evaluator for the orchestrator.
    
    The output evaluator assesses the quality of outputs from each stage
    in the pipeline and determines if refinement is needed based on
    quality thresholds and validation rules.
    """
    
    def __init__(self):
        """Initialize the output evaluator."""
        # Evaluation criteria for each stage
        self._criteria = {}
        
        # Default thresholds for pass/fail
        self._default_threshold = 0.7
        
        # Load default evaluation criteria
        self._initialize_default_criteria()
        
        logger.info("Output evaluator initialized")
    
    def _initialize_default_criteria(self) -> None:
        """
        Initialize the default evaluation criteria for pipeline stages.
        """
        # Query processor stage criteria
        self._criteria["query_processor"] = {
            "param_extraction": {
                "weight": 0.4,
                "description": "Extraction of key parameters from the query"
            },
            "intent_clarity": {
                "weight": 0.3,
                "description": "Clarity of identified intent"
            },
            "output_structure": {
                "weight": 0.2,
                "description": "Proper structure of the JSON output"
            },
            "confidence_scoring": {
                "weight": 0.1,
                "description": "Appropriate confidence scoring for extracted elements"
            }
        }
        
        # Domain knowledge stage criteria
        self._criteria["domain_knowledge"] = {
            "relevance": {
                "weight": 0.4,
                "description": "Relevance of retrieved knowledge to the query"
            },
            "completeness": {
                "weight": 0.3,
                "description": "Completeness of domain knowledge coverage"
            },
            "accuracy": {
                "weight": 0.2,
                "description": "Factual accuracy of retrieved information"
            },
            "structure": {
                "weight": 0.1,
                "description": "Proper structure of the output"
            }
        }
        
        # Add more stage-specific criteria as needed
        # ...
    
    def evaluate_output(self, stage_id: str, output: Any, 
                      context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate the output of a pipeline stage.
        
        Args:
            stage_id: Identifier for the pipeline stage
            output: The stage output to evaluate
            context: Additional context from working memory
            
        Returns:
            Evaluation results including scores and pass/fail status
        """
        logger.debug(f"Evaluating output for stage: {stage_id}")
        
        # Get criteria for this stage or use general criteria
        criteria = self._criteria.get(stage_id)
        if not criteria:
            logger.warning(f"No specific criteria for stage {stage_id}, using general evaluation")
            return self._general_evaluation(stage_id, output, context)
        
        # Perform evaluation based on stage-specific criteria
        scores = {}
        feedback = {}
        total_score = 0.0
        total_weight = 0.0
        
        for criterion, config in criteria.items():
            weight = config.get("weight", 1.0)
            total_weight += weight
            
            # Evaluate this criterion
            criterion_score, criterion_feedback = self._evaluate_criterion(
                stage_id, criterion, output, context
            )
            
            scores[criterion] = criterion_score
            feedback[criterion] = criterion_feedback
            total_score += criterion_score * weight
        
        # Normalize the total score
        if total_weight > 0:
            normalized_score = total_score / total_weight
        else:
            normalized_score = 0.0
        
        # Determine if the output passes evaluation
        threshold = context.get("threshold", self._default_threshold)
        passed = normalized_score >= threshold
        
        # Compile evaluation results
        results = {
            "stage_id": stage_id,
            "passed": passed,
            "overall_score": normalized_score,
            "threshold": threshold,
            "scores": scores,
            "feedback": feedback,
            "needs_refinement": not passed
        }
        
        logger.info(f"Stage {stage_id} evaluation: passed={passed}, score={normalized_score:.2f}")
        return results
    
    def _evaluate_criterion(self, stage_id: str, criterion: str, 
                          output: Any, context: Dict[str, Any]) -> Tuple[float, str]:
        """
        Evaluate a specific criterion for a stage output.
        
        Args:
            stage_id: Identifier for the pipeline stage
            criterion: The specific criterion to evaluate
            output: The stage output to evaluate
            context: Additional context from working memory
            
        Returns:
            Tuple of (score, feedback) where score is 0.0-1.0 and feedback is a string
        """
        # This method would contain stage-specific evaluation logic
        # For now, implementing simple generic evaluations
        
        # Query processor stage evaluations
        if stage_id == "query_processor":
            if criterion == "param_extraction":
                return self._evaluate_query_param_extraction(output, context)
            elif criterion == "intent_clarity":
                return self._evaluate_query_intent_clarity(output, context)
            elif criterion == "output_structure":
                return self._evaluate_output_structure(output)
            elif criterion == "confidence_scoring":
                return self._evaluate_confidence_scoring(output)
        
        # Domain knowledge stage evaluations
        elif stage_id == "domain_knowledge":
            if criterion == "relevance":
                return self._evaluate_knowledge_relevance(output, context)
            elif criterion == "completeness":
                return self._evaluate_knowledge_completeness(output, context)
            elif criterion == "accuracy":
                return self._evaluate_knowledge_accuracy(output, context)
            elif criterion == "structure":
                return self._evaluate_output_structure(output)
        
        # Default evaluation
        logger.warning(f"No specific evaluation for {stage_id}.{criterion}, using generic evaluation")
        return self._generic_criterion_evaluation(stage_id, criterion, output, context)
    
    def _evaluate_query_param_extraction(self, output: Any, context: Dict[str, Any]) -> Tuple[float, str]:
        """Evaluate parameter extraction quality in query processor output."""
        try:
            # Check if output contains parameters
            if not isinstance(output, dict) or "parameters" not in output:
                return 0.2, "Output missing 'parameters' field"
            
            parameters = output["parameters"]
            if not parameters or not isinstance(parameters, dict):
                return 0.3, "Parameters field is empty or not a dictionary"
            
            # Check if key parameters are present
            original_query = context.get("original_query", "")
            
            # Simple heuristic: check if parameters seem to cover important query terms
            # This is a simplified approach - in practice, more sophisticated NLP would be used
            query_tokens = set(original_query.lower().split())
            param_coverage = 0
            
            for param in parameters.values():
                if isinstance(param, str):
                    param_tokens = param.lower().split()
                    if any(token in query_tokens for token in param_tokens):
                        param_coverage += 1
            
            if len(parameters) > 0:
                coverage_ratio = min(1.0, param_coverage / len(parameters))
            else:
                coverage_ratio = 0.0
            
            if coverage_ratio >= 0.8:
                return 0.9, "Excellent parameter extraction"
            elif coverage_ratio >= 0.6:
                return 0.8, "Good parameter extraction, but some parameters may be missing"
            elif coverage_ratio >= 0.4:
                return 0.6, "Moderate parameter extraction, missing several parameters"
            else:
                return 0.4, "Poor parameter extraction, many parameters missing or irrelevant"
                
        except Exception as e:
            logger.error(f"Error evaluating query parameter extraction: {str(e)}")
            return 0.0, f"Error evaluating parameter extraction: {str(e)}"
    
    def _evaluate_query_intent_clarity(self, output: Any, context: Dict[str, Any]) -> Tuple[float, str]:
        """Evaluate intent clarity in query processor output."""
        try:
            if not isinstance(output, dict):
                return 0.0, "Output is not a dictionary"
            
            # Check for intent field
            intent = output.get("intent", None)
            if not intent:
                return 0.3, "Missing 'intent' field"
            
            # Check intent completeness
            if isinstance(intent, dict):
                if "primary" not in intent:
                    return 0.5, "Intent missing 'primary' classification"
                
                # Check confidence
                confidence = intent.get("confidence", 0)
                if confidence >= 0.8:
                    return 0.9, "High confidence, clear intent identification"
                elif confidence >= 0.6:
                    return 0.7, "Moderate confidence in intent identification"
                else:
                    return 0.5, "Low confidence in intent identification"
            elif isinstance(intent, str):
                # Simple string intent
                if len(intent) > 5:
                    return 0.7, "Intent specified but lacks confidence scoring"
                else:
                    return 0.5, "Intent is too brief or vague"
            
            return 0.4, "Intent structure is unclear"
            
        except Exception as e:
            logger.error(f"Error evaluating query intent clarity: {str(e)}")
            return 0.0, f"Error evaluating intent clarity: {str(e)}"
    
    def _evaluate_output_structure(self, output: Any) -> Tuple[float, str]:
        """Evaluate the structure of an output."""
        try:
            if not output:
                return 0.0, "Empty output"
            
            if not isinstance(output, dict):
                return 0.3, "Output is not a JSON object"
            
            # Check if the output has a reasonable number of fields
            if len(output) < 2:
                return 0.5, "Output has very few fields"
            
            # Check if values are properly typed (not all None or empty)
            valid_values = 0
            for key, value in output.items():
                if value is not None and (not isinstance(value, str) or value.strip()):
                    valid_values += 1
            
            if valid_values == 0:
                return 0.2, "All output values are empty or None"
            
            ratio = valid_values / len(output)
            
            if ratio >= 0.8:
                return 1.0, "Well-structured output with appropriate fields"
            elif ratio >= 0.6:
                return 0.8, "Mostly well-structured output, some fields may be empty"
            else:
                return 0.5, "Poorly structured output with many empty fields"
                
        except Exception as e:
            logger.error(f"Error evaluating output structure: {str(e)}")
            return 0.0, f"Error evaluating output structure: {str(e)}"
    
    def _evaluate_confidence_scoring(self, output: Any) -> Tuple[float, str]:
        """Evaluate the confidence scoring in an output."""
        try:
            if not isinstance(output, dict):
                return 0.0, "Output is not a dictionary"
            
            # Look for confidence scores in the output
            confidence_fields = []
            
            def find_confidence_fields(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key in ("confidence", "score", "probability", "certainty"):
                            if isinstance(value, (int, float)) and 0 <= value <= 1:
                                confidence_fields.append(f"{path}.{key}" if path else key)
                        elif isinstance(value, (dict, list)):
                            new_path = f"{path}.{key}" if path else key
                            find_confidence_fields(value, new_path)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        if isinstance(item, (dict, list)):
                            new_path = f"{path}[{i}]"
                            find_confidence_fields(item, new_path)
            
            find_confidence_fields(output)
            
            if not confidence_fields:
                return 0.3, "No confidence scores found in output"
            
            # Check if confidence scores are in a reasonable range
            if len(confidence_fields) >= 3:
                return 0.9, "Comprehensive confidence scoring"
            elif len(confidence_fields) >= 1:
                return 0.7, "Basic confidence scoring present"
            else:
                return 0.5, "Minimal confidence scoring"
                
        except Exception as e:
            logger.error(f"Error evaluating confidence scoring: {str(e)}")
            return 0.0, f"Error evaluating confidence scoring: {str(e)}"
    
    def _evaluate_knowledge_relevance(self, output: Any, context: Dict[str, Any]) -> Tuple[float, str]:
        """Evaluate the relevance of domain knowledge output."""
        try:
            if not isinstance(output, dict):
                return 0.0, "Output is not a dictionary"
            
            # Check for essential fields
            if "knowledge" not in output and "facts" not in output and "information" not in output:
                return 0.3, "Missing knowledge content fields"
            
            # Get original query for comparison
            original_query = context.get("original_query", "").lower()
            query_tokens = set(original_query.split())
            
            # Get query processor output if available
            query_params = {}
            if "stage_outputs" in context and "query_processor" in context["stage_outputs"]:
                query_processor_output = context["stage_outputs"]["query_processor"]
                if isinstance(query_processor_output, dict) and "parameters" in query_processor_output:
                    query_params = query_processor_output["parameters"]
            
            # Tokenize knowledge content
            knowledge_content = ""
            if "knowledge" in output:
                knowledge_content += str(output["knowledge"]) + " "
            if "facts" in output:
                knowledge_content += str(output["facts"]) + " "
            if "information" in output:
                knowledge_content += str(output["information"]) + " "
            
            knowledge_tokens = set(knowledge_content.lower().split())
            
            # Calculate overlap between query and knowledge
            if query_tokens:
                token_overlap = len(query_tokens.intersection(knowledge_tokens)) / len(query_tokens)
            else:
                token_overlap = 0.0
            
            # Check parameter coverage
            param_coverage = 0.0
            if query_params:
                param_hits = 0
                for param_value in query_params.values():
                    if isinstance(param_value, str) and param_value.lower() in knowledge_content.lower():
                        param_hits += 1
                
                if len(query_params) > 0:
                    param_coverage = param_hits / len(query_params)
            
            # Calculate overall relevance score
            relevance_score = max(token_overlap, param_coverage)
            
            if relevance_score >= 0.8:
                return 0.9, "Highly relevant knowledge"
            elif relevance_score >= 0.5:
                return 0.7, "Moderately relevant knowledge"
            elif relevance_score >= 0.3:
                return 0.5, "Somewhat relevant knowledge, but missing key elements"
            else:
                return 0.3, "Knowledge appears disconnected from the query"
                
        except Exception as e:
            logger.error(f"Error evaluating knowledge relevance: {str(e)}")
            return 0.0, f"Error evaluating knowledge relevance: {str(e)}"
    
    def _evaluate_knowledge_completeness(self, output: Any, context: Dict[str, Any]) -> Tuple[float, str]:
        """Evaluate the completeness of domain knowledge output."""
        try:
            if not isinstance(output, dict):
                return 0.0, "Output is not a dictionary"
            
            # Check for knowledge fields
            knowledge_fields = 0
            expected_fields = ["facts", "constraints", "formulas", "dependencies", "relationships"]
            
            for field in expected_fields:
                if field in output and output[field]:
                    knowledge_fields += 1
            
            # Check the depth of information
            depth_score = 0.0
            if "knowledge" in output and isinstance(output["knowledge"], dict):
                depth = len(output["knowledge"])
                if depth >= 5:
                    depth_score = 1.0
                elif depth >= 3:
                    depth_score = 0.7
                elif depth >= 1:
                    depth_score = 0.4
            
            # Check for any lists or arrays with facts/knowledge items
            item_count = 0
            for key, value in output.items():
                if isinstance(value, list):
                    item_count += len(value)
            
            if item_count >= 10:
                items_score = 1.0
            elif item_count >= 5:
                items_score = 0.7
            elif item_count >= 2:
                items_score = 0.4
            else:
                items_score = 0.0
            
            # Calculate overall completeness
            field_score = knowledge_fields / len(expected_fields) if expected_fields else 0
            completeness_score = max(field_score, depth_score, items_score)
            
            if completeness_score >= 0.8:
                return 0.9, "Comprehensive knowledge coverage"
            elif completeness_score >= 0.6:
                return 0.7, "Good knowledge coverage, but some details missing"
            elif completeness_score >= 0.4:
                return 0.5, "Basic knowledge coverage with significant gaps"
            else:
                return 0.3, "Incomplete knowledge with major gaps"
                
        except Exception as e:
            logger.error(f"Error evaluating knowledge completeness: {str(e)}")
            return 0.0, f"Error evaluating knowledge completeness: {str(e)}"
    
    def _evaluate_knowledge_accuracy(self, output: Any, context: Dict[str, Any]) -> Tuple[float, str]:
        """
        Evaluate the accuracy of domain knowledge output.
        Note: Full verification would require ground truth data or external validation.
        This implementation uses simpler heuristics.
        """
        try:
            if not isinstance(output, dict):
                return 0.0, "Output is not a dictionary"
            
            # Check for self-contradictions
            # (This is a simple implementation - would need more sophisticated NLP in practice)
            
            # Check if there are explicit confidence scores
            confidence_scores = []
            
            def find_confidence_scores(obj):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key in ("confidence", "accuracy", "certainty") and isinstance(value, (int, float)):
                            confidence_scores.append(value)
                        elif isinstance(value, (dict, list)):
                            find_confidence_scores(value)
                elif isinstance(obj, list):
                    for item in obj:
                        if isinstance(item, (dict, list)):
                            find_confidence_scores(item)
            
            find_confidence_scores(output)
            
            # If we have confidence scores, use their average
            if confidence_scores:
                avg_confidence = sum(confidence_scores) / len(confidence_scores)
                
                if avg_confidence >= 0.8:
                    return 0.9, "High reported accuracy in knowledge"
                elif avg_confidence >= 0.6:
                    return 0.7, "Moderate reported accuracy in knowledge"
                else:
                    return 0.5, "Low reported accuracy in knowledge"
            
            # Check for presence of citations or sources
            has_citations = False
            for key, value in output.items():
                if key in ("sources", "citations", "references"):
                    has_citations = bool(value)
                    break
            
            if has_citations:
                return 0.8, "Knowledge includes citation information"
            
            # Default moderate score when we can't effectively evaluate accuracy
            return 0.6, "Unable to fully verify knowledge accuracy"
                
        except Exception as e:
            logger.error(f"Error evaluating knowledge accuracy: {str(e)}")
            return 0.0, f"Error evaluating knowledge accuracy: {str(e)}"
    
    def _generic_criterion_evaluation(self, stage_id: str, criterion: str, 
                                    output: Any, context: Dict[str, Any]) -> Tuple[float, str]:
        """Generic evaluation for criteria without specific implementations."""
        try:
            # Check if output exists and has content
            if output is None:
                return 0.0, f"No output for {criterion}"
            
            if isinstance(output, dict):
                # Check for common quality indicators
                if len(output) == 0:
                    return 0.3, f"Empty output for {criterion}"
                
                # For structured outputs, check for non-empty values
                valid_values = sum(1 for v in output.values() if v is not None and v != "")
                quality = valid_values / len(output) if len(output) > 0 else 0
                
                if quality >= 0.8:
                    return 0.8, f"Good quality for {criterion}"
                elif quality >= 0.5:
                    return 0.6, f"Moderate quality for {criterion}"
                else:
                    return 0.4, f"Low quality for {criterion}"
            
            elif isinstance(output, list):
                # For list outputs, check length and content
                if len(output) == 0:
                    return 0.3, f"Empty list for {criterion}"
                
                # Check for non-empty items
                valid_items = sum(1 for item in output if item is not None and item != "")
                quality = valid_items / len(output) if len(output) > 0 else 0
                
                if quality >= 0.8 and len(output) >= 3:
                    return 0.8, f"Good quality list for {criterion}"
                elif quality >= 0.5:
                    return 0.6, f"Moderate quality list for {criterion}"
                else:
                    return 0.4, f"Low quality list for {criterion}"
            
            elif isinstance(output, str):
                # For string outputs, check length and content
                if not output.strip():
                    return 0.0, f"Empty string for {criterion}"
                
                # Simple heuristic based on length
                if len(output) >= 100:
                    return 0.7, f"Substantial content for {criterion}"
                elif len(output) >= 30:
                    return 0.5, f"Moderate content for {criterion}"
                else:
                    return 0.3, f"Brief content for {criterion}"
            
            else:
                # For other types, just check if it exists
                return 0.5, f"Output exists for {criterion} but quality uncertain"
                
        except Exception as e:
            logger.error(f"Error in generic evaluation of {criterion}: {str(e)}")
            return 0.0, f"Error evaluating {criterion}: {str(e)}"
    
    def _general_evaluation(self, stage_id: str, output: Any, 
                          context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform general evaluation when no specific criteria exist.
        
        Args:
            stage_id: Identifier for the pipeline stage
            output: The stage output to evaluate
            context: Additional context from working memory
            
        Returns:
            Evaluation results including scores and pass/fail status
        """
        logger.debug(f"Performing general evaluation for stage: {stage_id}")
        
        # Define generic criteria
        generic_criteria = {
            "completeness": {
                "weight": 0.4,
                "description": "Completeness of the output"
            },
            "structure": {
                "weight": 0.3,
                "description": "Structure and format of the output"
            },
            "relevance": {
                "weight": 0.3,
                "description": "Relevance to the original query"
            }
        }
        
        # Evaluate each criterion
        scores = {}
        feedback = {}
        total_score = 0.0
        
        for criterion, config in generic_criteria.items():
            weight = config["weight"]
            
            # Evaluate this criterion
            if criterion == "completeness":
                score, feedback_text = self._evaluate_general_completeness(output)
            elif criterion == "structure":
                score, feedback_text = self._evaluate_output_structure(output)
            elif criterion == "relevance":
                score, feedback_text = self._evaluate_general_relevance(output, context)
            else:
                score, feedback_text = 0.5, "No specific evaluation implemented"
            
            scores[criterion] = score
            feedback[criterion] = feedback_text
            total_score += score * weight
        
        # Determine if the output passes evaluation
        threshold = context.get("threshold", self._default_threshold)
        passed = total_score >= threshold
        
        # Compile evaluation results
        results = {
            "stage_id": stage_id,
            "passed": passed,
            "overall_score": total_score,
            "threshold": threshold,
            "scores": scores,
            "feedback": feedback,
            "needs_refinement": not passed
        }
        
        logger.info(f"General evaluation for stage {stage_id}: passed={passed}, score={total_score:.2f}")
        return results
    
    def _evaluate_general_completeness(self, output: Any) -> Tuple[float, str]:
        """Evaluate the general completeness of an output."""
        try:
            if output is None:
                return 0.0, "No output provided"
            
            if isinstance(output, dict):
                if not output:
                    return 0.2, "Empty dictionary output"
                
                # Check for non-empty values
                non_empty_values = sum(1 for v in output.values() if v is not None and v != "")
                completeness = non_empty_values / len(output) if len(output) > 0 else 0
                
                if completeness >= 0.8:
                    return 0.9, "Very complete output with few empty fields"
                elif completeness >= 0.6:
                    return 0.7, "Mostly complete output"
                elif completeness >= 0.4:
                    return 0.5, "Partially complete output with several empty fields"
                else:
                    return 0.3, "Mostly incomplete output with many empty fields"
            
            elif isinstance(output, list):
                if not output:
                    return 0.2, "Empty list output"
                
                # Consider length of list as a factor
                if len(output) >= 5:
                    return 0.8, "Complete output with multiple items"
                elif len(output) >= 3:
                    return 0.6, "Moderately complete output"
                else:
                    return 0.4, "Minimal list output"
            
            elif isinstance(output, str):
                if not output.strip():
                    return 0.1, "Empty string output"
                
                # Evaluate based on length
                if len(output) >= 200:
                    return 0.8, "Comprehensive text output"
                elif len(output) >= 100:
                    return 0.6, "Moderately detailed text output"
                elif len(output) >= 30:
                    return 0.4, "Brief text output"
                else:
                    return 0.3, "Very brief text output"
            
            else:
                # For other types, just check existence
                return 0.5, "Output exists but completeness uncertain"
                
        except Exception as e:
            logger.error(f"Error evaluating general completeness: {str(e)}")
            return 0.0, f"Error evaluating completeness: {str(e)}"
    
    def _evaluate_general_relevance(self, output: Any, context: Dict[str, Any]) -> Tuple[float, str]:
        """Evaluate the general relevance of an output to the original query."""
        try:
            # Get original query
            original_query = context.get("original_query", "").lower()
            if not original_query:
                return 0.5, "Unable to evaluate relevance without original query"
            
            # Convert output to string for text comparison
            output_text = ""
            if isinstance(output, dict):
                try:
                    output_text = json.dumps(output)
                except:
                    output_text = str(output)
            elif isinstance(output, list):
                try:
                    output_text = json.dumps(output)
                except:
                    output_text = str(output)
            else:
                output_text = str(output)
            
            output_text = output_text.lower()
            
            # Simple keyword matching approach
            # In a production system, this would use more sophisticated semantic relevance
            query_tokens = set(original_query.split())
            
            # Count token matches
            matches = 0
            for token in query_tokens:
                if len(token) > 3 and token in output_text:  # Only count substantive tokens
                    matches += 1
            
            if len(query_tokens) > 0:
                relevance = min(1.0, matches / len(query_tokens))
            else:
                relevance = 0.0
            
            if relevance >= 0.8:
                return 0.9, "Highly relevant to the original query"
            elif relevance >= 0.5:
                return 0.7, "Moderately relevant to the original query"
            elif relevance >= 0.3:
                return 0.5, "Somewhat relevant to the original query"
            else:
                return 0.3, "Low relevance to the original query"
                
        except Exception as e:
            logger.error(f"Error evaluating general relevance: {str(e)}")
            return 0.0, f"Error evaluating relevance: {str(e)}"
    
    def set_evaluation_criteria(self, stage_id: str, criteria: Dict[str, Dict[str, Any]]) -> None:
        """
        Set custom evaluation criteria for a stage.
        
        Args:
            stage_id: Identifier for the pipeline stage
            criteria: Dictionary of criteria configurations with weights and descriptions
        """
        self._criteria[stage_id] = criteria
        logger.info(f"Updated evaluation criteria for stage {stage_id}")
    
    def get_evaluation_criteria(self, stage_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Get the evaluation criteria for a stage.
        
        Args:
            stage_id: Identifier for the pipeline stage
            
        Returns:
            Dictionary of criteria configurations
        """
        return self._criteria.get(stage_id, {})
    
    def set_threshold(self, stage_id: str, threshold: float) -> None:
        """
        Set the evaluation threshold for a specific stage.
        
        Args:
            stage_id: Identifier for the pipeline stage
            threshold: Evaluation threshold (0.0-1.0)
        """
        if 0 <= threshold <= 1:
            stage_criteria = self._criteria.get(stage_id, {})
            if not stage_criteria:
                self._criteria[stage_id] = {}
            
            self._criteria[stage_id]["_threshold"] = threshold
            logger.info(f"Set threshold {threshold} for stage {stage_id}")
        else:
            logger.error(f"Invalid threshold value: {threshold}. Must be between 0 and 1.")
            raise ValueError("Threshold must be between 0 and 1")

# Global singleton instance
output_evaluator = OutputEvaluator() 