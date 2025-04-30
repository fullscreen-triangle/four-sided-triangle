"""
Context Manager Module

Enriches queries with contextual information:
- User history integration
- User preferences application
- Domain-specific context addition
"""

import logging
from typing import Dict, Any, List
import json

logger = logging.getLogger(__name__)

# Context enrichment prompt
CONTEXT_ENRICHMENT_PROMPT = """
You are enhancing a user query with relevant context to improve understanding and processing.

Original Query: "{query}"
Intent Classification: {intent}

User History: {history}
User Preferences: {preferences}

Your task is to enrich the query by:
1. Incorporating relevant user history that provides context
2. Applying user preferences where appropriate
3. Adding domain context that would help in processing the query

Return an enriched version of the query that maintains the original meaning but includes relevant context.
If the original query already has sufficient context, you may return it with minimal changes.

The enriched query should be formatted as:
{{
  "enriched_query": "The enhanced query text incorporating context",
  "context_added": [List of specific context elements you incorporated],
  "reasoning": "Brief explanation of your context enrichment decisions"
}}
"""

async def enrich_with_context(
    query: str, 
    intent_classification: Dict[str, Any],
    user_history: List[Dict[str, Any]],
    user_preferences: Dict[str, Any],
    llm_client
) -> str:
    """
    Enrich a query with contextual information.
    
    Args:
        query: The preprocessed query text
        intent_classification: Intent classification dictionary
        user_history: List of user's previous queries and interactions
        user_preferences: Dict of user preferences
        llm_client: LLM client for making API calls
        
    Returns:
        Enriched query string
    """
    # If no history or preferences, return original query
    if not user_history and not user_preferences:
        logger.info("No context available for enrichment, returning original query")
        return query
    
    # Prepare the context
    intent = intent_classification.get("primary_intent", "informational")
    
    # Format user history for the prompt (limit to last 3 items)
    history_str = "No relevant history available."
    if user_history:
        recent_history = user_history[-3:]
        history_items = [f"- {item.get('query', '')}" for item in recent_history]
        history_str = "\n".join(history_items)
    
    # Format user preferences for the prompt
    preferences_str = "No preferences available."
    if user_preferences:
        pref_items = [f"- {key}: {value}" for key, value in user_preferences.items()]
        preferences_str = "\n".join(pref_items)
    
    # Format the prompt
    prompt = CONTEXT_ENRICHMENT_PROMPT.format(
        query=query,
        intent=intent,
        history=history_str,
        preferences=preferences_str
    )
    
    try:
        # Call LLM for context enrichment
        llm_response = await llm_client.generate_text(
            prompt=prompt,
            model="primary",  # Use the primary general LLM 
            temperature=0.3,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        enriched_data = json.loads(llm_response)
        enriched_query = enriched_data.get("enriched_query", query)
        
        logger.info(f"Query enriched with context. Context added: {enriched_data.get('context_added', [])}")
        return enriched_query
        
    except Exception as e:
        logger.error(f"Error in context enrichment: {str(e)}")
        # Return original query in case of error
        return query 