"""
Intent Classification Module

Determines the primary intent of the query:
- Informational: User is seeking factual information or explanation
- Computational: User is requesting calculations or data processing
- Comparative: User is seeking comparison between concepts or entities
"""

import logging
from typing import Dict, Any, Tuple, List
import json

logger = logging.getLogger(__name__)

# Intent classification constants
INTENT_INFORMATIONAL = "informational"
INTENT_COMPUTATIONAL = "computational" 
INTENT_COMPARATIVE = "comparative"

# LLM Prompt for intent classification
INTENT_CLASSIFICATION_PROMPT = """
You are analyzing a user query to determine its primary intent. Classify the query into one of the following categories:

1. INFORMATIONAL: User is seeking factual information or explanations
   Example: "How does sprint training affect muscle development?"

2. COMPUTATIONAL: User is requesting calculations or data analysis
   Example: "Calculate my ideal body fat percentage based on my age and activity level."

3. COMPARATIVE: User is seeking comparison between concepts, methods, or entities
   Example: "Compare sprint interval training versus continuous cardio for fat loss."

For the query below, determine the PRIMARY intent (choose only one category).
Also provide a confidence score between 0.0 and 1.0 representing your certainty of this classification.

User Query: "{query}"

Reply in JSON format only:
{{
  "intent": "[INFORMATIONAL|COMPUTATIONAL|COMPARATIVE]",
  "confidence": [0.0-1.0],
  "explanation": "Brief explanation of classification"
}}
"""

async def classify_intent(preprocessed_query: str, llm_client) -> Tuple[Dict[str, Any], float]:
    """
    Classify the user query intent using LLM.
    
    Args:
        preprocessed_query: The preprocessed query text
        llm_client: The LLM client for making API calls
        
    Returns:
        Tuple containing:
        - intent_classification: Dict with intent details
        - confidence: Float representing confidence score
    """
    # Format the prompt with the query
    prompt = INTENT_CLASSIFICATION_PROMPT.format(query=preprocessed_query)
    
    try:
        # Call LLM for classification
        llm_response = await llm_client.generate_text(
            prompt=prompt,
            model="primary",  # Use the primary general LLM
            temperature=0.1,  # Low temperature for more deterministic results
            max_tokens=300,
            response_format={"type": "json_object"}
        )
        
        # Parse the JSON response
        classification = json.loads(llm_response)
        
        # Get and normalize the intent
        intent = classification.get("intent", "").lower()
        if intent in [INTENT_INFORMATIONAL, INTENT_COMPUTATIONAL, INTENT_COMPARATIVE]:
            normalized_intent = intent
        else:
            # Default to informational if the response is unexpected
            logger.warning(f"Unexpected intent classification: {intent}. Defaulting to informational.")
            normalized_intent = INTENT_INFORMATIONAL
        
        # Get confidence score
        confidence = min(max(float(classification.get("confidence", 0.7)), 0.0), 1.0)
        
        # Build intent classification object
        intent_classification = {
            "primary_intent": normalized_intent,
            "explanation": classification.get("explanation", ""),
            "raw_classification": classification
        }
        
        logger.info(f"Classified query as {normalized_intent} with confidence {confidence}")
        return intent_classification, confidence
        
    except Exception as e:
        logger.error(f"Error in intent classification: {str(e)}")
        # Default classification in case of error
        return {
            "primary_intent": INTENT_INFORMATIONAL,
            "explanation": "Default classification due to processing error",
            "raw_classification": {}
        }, 0.5 