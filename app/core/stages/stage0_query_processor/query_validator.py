"""
Query Validator Module

Verifies that a query meets minimum information requirements for further processing:
- Checks for information completeness
- Verifies domain relevance
- Validates required parameters for the query intent
"""

import logging
from typing import Dict, Any, Tuple, List

logger = logging.getLogger(__name__)

# Minimum word counts by intent type
MIN_WORDS_INFORMATIONAL = 3
MIN_WORDS_COMPUTATIONAL = 5
MIN_WORDS_COMPARATIVE = 5

# Required information by intent type
REQUIRED_INFO = {
    "informational": ["subject"],
    "computational": ["subject", "metric"],
    "comparative": ["subject", "comparison_target"]
}

def validate_query_requirements(query: str, intent_classification: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """
    Validate that the query meets minimum information requirements.
    
    Args:
        query: The processed query text
        intent_classification: Intent classification dictionary
        
    Returns:
        Tuple containing:
        - is_valid: Boolean indicating if query is valid
        - validation_details: Dict with validation details
    """
    validation_details = {
        "length_check": False,
        "domain_relevance": False,
        "required_parameters": False,
        "overall_valid": False,
        "missing_information": [],
        "suggestions": []
    }
    
    # Get the intent
    intent = intent_classification.get("primary_intent", "informational")
    
    # 1. Check query length
    words = query.split()
    word_count = len(words)
    
    min_required_words = {
        "informational": MIN_WORDS_INFORMATIONAL,
        "computational": MIN_WORDS_COMPUTATIONAL,
        "comparative": MIN_WORDS_COMPARATIVE
    }.get(intent, MIN_WORDS_INFORMATIONAL)
    
    validation_details["length_check"] = word_count >= min_required_words
    if not validation_details["length_check"]:
        validation_details["missing_information"].append("query_too_short")
        validation_details["suggestions"].append(
            f"Please provide more details. For {intent} queries, we need at least {min_required_words} words."
        )
    
    # 2. Check domain relevance (simplified implementation)
    # In a real system, this might use more sophisticated techniques like
    # embedding similarity or keyword matching against a domain ontology
    domain_keywords = [
        "sprint", "athletic", "biomechanics", "performance", "training",
        "technique", "anthropomorphic", "measurement", "velocity", "power",
        "strength", "athlete", "sport", "exercise", "fitness", "body", "muscle",
        "metabolism", "physiology", "vo2", "cardio", "endurance", "agility"
    ]
    
    query_lower = query.lower()
    has_domain_terms = any(keyword in query_lower for keyword in domain_keywords)
    
    validation_details["domain_relevance"] = has_domain_terms
    if not validation_details["domain_relevance"]:
        validation_details["missing_information"].append("domain_relevance")
        validation_details["suggestions"].append(
            "Your query doesn't appear to be related to sports science or athletic performance. "
            "Please include specific terms related to these domains."
        )
    
    # 3. Check for required parameters based on intent
    required_params = REQUIRED_INFO.get(intent, [])
    missing_params = []
    
    # This is a simplified implementation
    # In a real system, we might use NER or structured entity extraction
    # to identify presence of required parameters
    for param in required_params:
        # Simplified check - would be more sophisticated in production
        if not _has_parameter(query, param):
            missing_params.append(param)
    
    validation_details["required_parameters"] = len(missing_params) == 0
    if not validation_details["required_parameters"]:
        validation_details["missing_information"].extend(missing_params)
        
        suggestions = []
        for param in missing_params:
            suggestions.append(f"Please specify the {param.replace('_', ' ')}.")
        
        validation_details["suggestions"].extend(suggestions)
    
    # Overall validation result
    validation_details["overall_valid"] = (
        validation_details["length_check"] and
        validation_details["domain_relevance"] and
        validation_details["required_parameters"]
    )
    
    logger.info(f"Query validation result: {validation_details['overall_valid']}")
    if not validation_details["overall_valid"]:
        logger.info(f"Validation details: {validation_details}")
    
    return validation_details["overall_valid"], validation_details

def _has_parameter(query: str, param: str) -> bool:
    """
    Simplified check if the query contains a specific parameter.
    
    In a real system, this would use more sophisticated NLP techniques.
    """
    # Sample parameter detection logic based on simple keyword matching
    # This is just for demonstration - would be much more sophisticated in practice
    param_indicators = {
        "subject": ["about", "regarding", "on", "for", "concerning"],
        "metric": ["measure", "calculate", "compute", "determine", "value"],
        "comparison_target": ["compare", "versus", "vs", "against", "between", "than"]
    }
    
    query_lower = query.lower()
    
    # Check if parameter indicators are present
    indicators = param_indicators.get(param, [])
    return any(indicator in query_lower for indicator in indicators) 