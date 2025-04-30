"""
General helper utilities for the Four-Sided Triangle system.

This module contains various helper functions and decorators
used throughout the system.
"""

import time
import logging
import functools
import asyncio
from typing import Callable, Any, Dict, Optional

logger = logging.getLogger(__name__)

def timer_decorator(func):
    """
    Decorator to measure and log the execution time of a function.
    
    Works with both synchronous and asynchronous functions.
    
    Args:
        func: The function to be decorated
        
    Returns:
        Wrapped function that logs execution time
    """
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
            
            # If the result is a dict, add the execution time
            if isinstance(result, dict):
                result["execution_time"] = execution_time
                
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Function {func.__name__} failed after {execution_time:.4f} seconds: {str(e)}")
            raise
            
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
            
            # If the result is a dict, add the execution time
            if isinstance(result, dict):
                result["execution_time"] = execution_time
                
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Function {func.__name__} failed after {execution_time:.4f} seconds: {str(e)}")
            raise
    
    # Determine if the function is async or not
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

def retry_decorator(
    max_attempts: int = 3, 
    delay: float = 1.0, 
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator to retry a function on failure.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier for delay
        exceptions: Tuple of exceptions to catch and retry
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            last_exception = None
            
            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    last_exception = e
                    
                    if attempt >= max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {str(e)}")
                        raise
                        
                    logger.warning(f"Retry {attempt}/{max_attempts} for {func.__name__} after error: {str(e)}")
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
                    
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            last_exception = None
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    last_exception = e
                    
                    if attempt >= max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {str(e)}")
                        raise
                        
                    logger.warning(f"Retry {attempt}/{max_attempts} for {func.__name__} after error: {str(e)}")
                    time.sleep(current_delay)
                    current_delay *= backoff
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator

def memoize(func):
    """
    Decorator to cache function results.
    
    Simple in-memory cache for function results based on arguments.
    Note: This is a simple implementation and doesn't handle complex types.
    
    Args:
        func: The function to be decorated
        
    Returns:
        Wrapped function with caching
    """
    cache = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create a key based on the function arguments
        key_args = str(args)
        key_kwargs = str(sorted(kwargs.items()))
        key = f"{key_args}:{key_kwargs}"
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
            
        return cache[key]
        
    return wrapper

def validate_parameters(required_params: list, optional_params: Optional[list] = None):
    """
    Decorator to validate function parameters.
    
    Args:
        required_params: List of required parameter names
        optional_params: List of optional parameter names
        
    Returns:
        Decorator function
    """
    optional_params = optional_params or []
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get the parameter names in the function signature
            func_args = func.__code__.co_varnames[:func.__code__.co_argcount]
            
            # Skip 'self' or 'cls' for methods
            start_idx = 0
            if func_args and func_args[0] in ('self', 'cls'):
                start_idx = 1
                
            # Check that all required parameters are provided
            for param in required_params:
                if param not in kwargs:
                    arg_idx = func_args.index(param) if param in func_args else -1
                    if arg_idx < 0 or arg_idx >= len(args) + start_idx:
                        raise ValueError(f"Missing required parameter: {param}")
                        
            # Check that all provided parameters are either required or optional
            allowed_params = required_params + optional_params
            for param in kwargs:
                if param not in allowed_params:
                    raise ValueError(f"Unknown parameter: {param}")
                    
            return func(*args, **kwargs)
            
        return wrapper
        
    return decorator 