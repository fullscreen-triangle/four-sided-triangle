"""
LLM Client utility for interfacing with language models.

This module provides a standardized interface for interacting with
various language model providers used throughout the system.
"""

import logging
import os
from typing import Dict, Any, List, Optional, Union
import aiohttp
import json

logger = logging.getLogger(__name__)

class LLMClient:
    """
    Client for making requests to language model APIs.
    
    This client abstracts away the details of specific LLM providers,
    providing a consistent interface for the rest of the application.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "default"):
        """
        Initialize the LLM client.
        
        Args:
            api_key: API key for LLM provider (defaults to env variable)
            model: Name/identifier of the model to use
        """
        self.api_key = api_key or os.environ.get("LLM_API_KEY")
        self.model = model
        self.base_url = os.environ.get("LLM_API_URL", "https://api.example.com/v1")
        logger.info(f"LLMClient initialized with model: {model}")
        
    async def generate_text(
        self, 
        prompt: str, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate text using the configured language model.
        
        Args:
            prompt: The text prompt to send to the model
            parameters: Optional parameters to control generation
            
        Returns:
            Dictionary containing model response and metadata
        """
        parameters = parameters or {}
        default_params = {
            "temperature": 0.7,
            "max_tokens": 1024,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
        }
        
        # Merge default parameters with provided ones
        request_params = {**default_params, **parameters}
        
        # Build the request payload
        payload = {
            "model": self.model,
            "prompt": prompt,
            **request_params
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                async with session.post(
                    f"{self.base_url}/completions", 
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"LLM API error: {response.status} - {error_text}")
                        return {
                            "error": True,
                            "message": f"LLM API returned status {response.status}",
                            "details": error_text
                        }
                    
                    result = await response.json()
                    return {
                        "generated_text": result.get("choices", [{}])[0].get("text", ""),
                        "model": self.model,
                        "usage": result.get("usage", {}),
                        "raw_response": result
                    }
        
        except Exception as e:
            logger.exception(f"Error generating text with LLM: {str(e)}")
            return {
                "error": True,
                "message": f"Failed to generate text: {str(e)}"
            }
            
    async def classify(
        self, 
        text: str, 
        categories: List[str],
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Classify text into one of the provided categories.
        
        Args:
            text: The text to classify
            categories: List of possible categories
            parameters: Optional parameters to control classification
            
        Returns:
            Dictionary with classification results and confidence scores
        """
        parameters = parameters or {}
        
        # Create classification prompt
        prompt = f"""
        Classify the following text into one of these categories:
        {', '.join(categories)}
        
        Text: {text}
        
        Category:
        """
        
        result = await self.generate_text(prompt, parameters)
        
        if result.get("error"):
            return result
            
        # Extract the category from the response
        generated_text = result.get("generated_text", "").strip()
        
        # Find the best matching category
        best_match = None
        best_score = 0.0
        
        for category in categories:
            if category.lower() in generated_text.lower():
                # Simple exact match for now
                best_match = category
                best_score = 1.0
                break
                
        if not best_match and len(generated_text) > 0:
            # Take first line as category if no exact match
            best_match = generated_text.split("\n")[0].strip()
            best_score = 0.7
            
        return {
            "category": best_match or "unknown",
            "confidence": best_score,
            "raw_result": result
        }
    
    async def extract_entities(
        self, 
        text: str,
        entity_types: List[str],
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract entities of specified types from text.
        
        Args:
            text: The text to analyze
            entity_types: Types of entities to extract
            parameters: Optional parameters to control extraction
            
        Returns:
            Dictionary with extracted entities by type
        """
        parameters = parameters or {}
        
        # Create entity extraction prompt
        prompt = f"""
        Extract the following entity types from the text:
        {', '.join(entity_types)}
        
        Text: {text}
        
        Entities (JSON format):
        """
        
        result = await self.generate_text(prompt, parameters)
        
        if result.get("error"):
            return result
            
        # Extract JSON from the response
        generated_text = result.get("generated_text", "").strip()
        
        try:
            # Try to parse as JSON
            json_start = generated_text.find("{")
            json_end = generated_text.rfind("}")
            
            if json_start >= 0 and json_end > json_start:
                json_str = generated_text[json_start:json_end+1]
                entities = json.loads(json_str)
            else:
                # Fallback: parse as simple key-value pairs
                entities = {}
                for entity_type in entity_types:
                    # Simple extraction with a colon pattern
                    pattern = f"{entity_type}:"
                    if pattern in generated_text:
                        value_start = generated_text.find(pattern) + len(pattern)
                        value_end = generated_text.find("\n", value_start)
                        if value_end == -1:
                            value_end = len(generated_text)
                        value = generated_text[value_start:value_end].strip()
                        entities[entity_type] = value
            
            return {
                "entities": entities,
                "raw_result": result
            }
            
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse entities JSON: {generated_text}")
            return {
                "error": True,
                "message": "Failed to parse entity extraction result as JSON",
                "raw_result": result
            } 