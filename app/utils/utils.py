"""
General utilities for the Four-Sided Triangle system.

This module provides common utility functions used throughout the system.
"""

import logging
import json
import functools
import traceback
from typing import Dict, Any, Callable, Optional
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

def error_handler(func):
    """
    Decorator to standardize error handling in API endpoints.
    
    Catches exceptions and converts them to appropriate HTTPExceptions
    with standardized error response format.
    
    Args:
        func: The function to be decorated
        
    Returns:
        Wrapped function with error handling
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            # Re-raise FastAPI HTTP exceptions without modification
            raise
        except ValueError as e:
            # Convert validation errors to 400 Bad Request
            logger.warning(f"Validation error in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "validation_error",
                    "message": str(e),
                    "location": func.__name__
                }
            )
        except KeyError as e:
            # Missing key errors to 400 Bad Request
            logger.warning(f"Missing key in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "missing_parameter",
                    "message": f"Missing required parameter: {str(e)}",
                    "location": func.__name__
                }
            )
        except TimeoutError as e:
            # Timeout errors to 408 Request Timeout
            logger.error(f"Timeout in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail={
                    "error": "timeout",
                    "message": "Operation timed out",
                    "location": func.__name__
                }
            )
        except Exception as e:
            # All other exceptions become 500 Internal Server Error
            logger.exception(f"Unexpected error in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "internal_server_error",
                    "message": "An unexpected error occurred",
                    "location": func.__name__
                }
            )
    
    return wrapper

def format_response(data: Any, status: str = "success", message: Optional[str] = None) -> Dict[str, Any]:
    """
    Format API response in a standardized structure.
    
    Args:
        data: The response data
        status: Response status (success or error)
        message: Optional status message
        
    Returns:
        Formatted response dictionary
    """
    response = {
        "status": status,
        "data": data
    }
    
    if message:
        response["message"] = message
        
    return response

def parse_json_safely(json_str: str, default: Any = None) -> Any:
    """
    Safely parse a JSON string with error handling.
    
    Args:
        json_str: JSON string to parse
        default: Default value to return if parsing fails
        
    Returns:
        Parsed JSON object or default value
    """
    if not json_str:
        return default
        
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON: {str(e)}")
        return default

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
        
    return text[:max_length].rstrip() + suffix

def get_exception_details(exception: Exception) -> Dict[str, Any]:
    """
    Extract detailed information from an exception.
    
    Args:
        exception: The exception to analyze
        
    Returns:
        Dictionary with exception details
    """
    return {
        "type": exception.__class__.__name__,
        "message": str(exception),
        "traceback": traceback.format_exc(),
        "module": exception.__class__.__module__
    }

def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any], overwrite: bool = True) -> Dict[str, Any]:
    """
    Merge two dictionaries with options for handling conflicts.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        overwrite: Whether to overwrite values from dict1 with dict2
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = merge_dicts(result[key], value, overwrite)
        elif key not in result or overwrite:
            # Add new keys or overwrite existing keys
            result[key] = value
            
    return result 