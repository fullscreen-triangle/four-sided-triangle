"""
Query Preprocessing Module

Handles standardization of query text:
- Removing noise
- Correcting spelling
- Normalizing terminology
"""

import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def preprocess_query(raw_query: str) -> str:
    """
    Preprocess a raw query to standardize it for further processing.
    
    Args:
        raw_query: The raw query string from user input
        
    Returns:
        Preprocessed query string
    """
    # Initialize with the raw query
    processed_query = raw_query
    
    # 1. Basic cleaning
    processed_query = _clean_text(processed_query)
    
    # 2. Normalize formatting
    processed_query = _normalize_formatting(processed_query)
    
    # 3. Fix common spelling issues (we could use an external spelling library here)
    processed_query = _correct_common_spelling(processed_query)
    
    # 4. Normalize domain terminology
    processed_query = _normalize_terminology(processed_query)
    
    logger.debug(f"Preprocessed query: {processed_query[:50]}...")
    return processed_query

def _clean_text(text: str) -> str:
    """Remove noise from text such as extra whitespace, control characters, etc."""
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Trim whitespace
    text = text.strip()
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)
    
    return text

def _normalize_formatting(text: str) -> str:
    """Normalize text formatting for consistency."""
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
    
    # Normalize dashes
    text = text.replace('—', '-').replace('–', '-')
    
    # Ensure sentence ending punctuation
    if text and not text[-1] in ['.', '?', '!']:
        text += '.'
    
    return text

def _correct_common_spelling(text: str) -> str:
    """Correct common spelling mistakes."""
    # This is a simplified version - in production, use a spell checker library
    common_corrections = {
        # Domain-specific corrections could be added here
        # For example:
        "sprnt": "sprint",
        "anth": "anthro",
        "spint": "sprint",
        "antropo": "anthropo",
    }
    
    for misspelled, correction in common_corrections.items():
        text = re.sub(r'\b' + misspelled + r'\b', correction, text, flags=re.IGNORECASE)
    
    return text

def _normalize_terminology(text: str) -> str:
    """Normalize domain-specific terminology to standard forms."""
    # Standard terminology mapping
    terminology_map = {
        # Domain-specific terminology standardization
        # For example in sports science:
        "max speed": "maximum velocity",
        "top speed": "maximum velocity",
        "vo2 max": "VO2max",
        "body fat": "body fat percentage",
        "sprint time": "sprint duration",
    }
    
    for term, standard_form in terminology_map.items():
        text = re.sub(r'\b' + re.escape(term) + r'\b', standard_form, text, flags=re.IGNORECASE)
    
    return text 