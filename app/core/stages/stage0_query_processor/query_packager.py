"""
Query Packager Module

Prepares a standardized query package for transfer to the modeling component:
- Structures query data
- Adds metadata
- Formats for consumption by next pipeline stage
"""

import logging
import time
from typing import Dict, Any, List
import uuid
import json

logger = logging.getLogger(__name__)

# Query packaging prompt
QUERY_PACKAGING_PROMPT = """
You are preparing a user query for advanced processing by a modeling system.
Your task is to package the query into a structured format with all necessary information.

Enriched Query: "{query}"
Intent Classification: {intent}
Validation Information: {validation}

Create a structured representation of this query that includes:
1. Core query text
2. Identified entities and concepts
3. Key parameters that need to be extracted
4. Relationships between entities
5. Any constraints or conditions specified

Your response should be a JSON object with the following structure:
{{
  "query_text": "The original query text",
  "entities": [
    {{
      "name": "Entity name",
      "type": "Entity type (person, concept, metric, etc.)",
      "relevance": "Relevance score 0-1"
    }}
  ],
  "parameters": [
    {{
      "name": "Parameter name",
      "value": "Parameter value if specified",
      "required": true/false
    }}
  ],
  "relationships": [
    {{
      "source": "Source entity",
      "target": "Target entity", 
      "type": "Relationship type (causes, influences, etc.)"
    }}
  ],
  "constraints": [
    {{
      "type": "Constraint type",
      "value": "Constraint value"
    }}
  ]
}}
"""

async def package_query(
    enriched_query: str,
    intent_classification: Dict[str, Any],
    validation_details: Dict[str, Any],
    parameters: Dict[str, Any],
    llm_client
) -> Dict[str, Any]:
    """
    Package the query into a standardized format for the modeling component.
    
    Args:
        enriched_query: The context-enriched query text
        intent_classification: Intent classification dictionary
        validation_details: Query validation details
        parameters: Additional parameters from the request
        llm_client: LLM client for making API calls
        
    Returns:
        Structured query package dictionary
    """
    # Base query package with metadata
    query_package = {
        "query_id": str(uuid.uuid4()),
        "timestamp": time.time(),
        "raw_query": enriched_query,
        "intent": intent_classification.get("primary_intent", "informational"),
        "metadata": {
            "intent_confidence": intent_classification.get("confidence", 0.0),
            "validation_details": validation_details,
            "process_parameters": parameters.get("process_parameters", {})
        }
    }
    
    # Format the prompt
    prompt = QUERY_PACKAGING_PROMPT.format(
        query=enriched_query,
        intent=intent_classification.get("primary_intent", "informational"),
        validation=json.dumps(validation_details)
    )
    
    try:
        # Call LLM for structured query packaging
        llm_response = await llm_client.generate_text(
            prompt=prompt,
            model="primary",  # Use the primary general LLM
            temperature=0.2,
            max_tokens=800,
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        structured_data = json.loads(llm_response)
        
        # Add structural elements to the query package
        query_package.update({
            "structured_representation": structured_data,
            "entities": structured_data.get("entities", []),
            "parameters": structured_data.get("parameters", []),
            "relationships": structured_data.get("relationships", []),
            "constraints": structured_data.get("constraints", [])
        })
        
        logger.info(f"Query packaged successfully with {len(structured_data.get('entities', []))} entities")
        return query_package
        
    except Exception as e:
        logger.error(f"Error in query packaging: {str(e)}")
        # Return basic package in case of error
        query_package["error"] = str(e)
        query_package["status"] = "packaging_error"
        return query_package 