"""
Compute Helpers

This module provides high-level helper functions for distributed computing tasks,
abstracting away the complexity of directly using the compute manager.
"""

import os
import logging
import json
import uuid
import time
import requests
from typing import Dict, List, Any, Optional, Union, Callable
import numpy as np
import pandas as pd
from datetime import datetime

from app.distributed.compute_manager import get_compute_manager
from app.distributed.ml_tasks import get_ml_tasks

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def distributed_apply(
    func: Callable,
    data: Union[pd.DataFrame, np.ndarray, List],
    partition_size: Optional[int] = None,
    priority: int = 0,
    timeout: Optional[float] = None,
    **kwargs
) -> Any:
    """
    Apply a function to data in a distributed manner.
    
    Args:
        func: Function to apply
        data: Data to process
        partition_size: Size of each partition (if None, auto-determined)
        priority: Priority of the task
        timeout: Maximum time to wait for result
        **kwargs: Additional arguments to pass to the function
        
    Returns:
        Result of the function applied to the data
    """
    # Get compute manager
    compute = get_compute_manager()
    
    # Prepare data for distributed processing
    if isinstance(data, pd.DataFrame):
        # For DataFrames, we can partition by rows
        if partition_size is None:
            # Auto-determine partition size based on size of DataFrame
            total_size = len(data)
            if total_size < 1000:
                partitions = 1
            elif total_size < 10000:
                partitions = 4
            elif total_size < 100000:
                partitions = 8
            else:
                partitions = 16
                
            partition_size = max(1, total_size // partitions)
        
        # Split DataFrame into partitions
        partitioned_data = [
            data.iloc[i:i+partition_size] 
            for i in range(0, len(data), partition_size)
        ]
    elif isinstance(data, np.ndarray):
        # For arrays, partition along the first dimension
        if partition_size is None:
            total_size = data.shape[0]
            partition_size = max(1, total_size // 8)
            
        partitioned_data = np.array_split(data, max(1, data.shape[0] // partition_size))
    elif isinstance(data, list):
        # For lists, simple chunking
        if partition_size is None:
            partition_size = max(1, len(data) // 8)
            
        partitioned_data = [
            data[i:i+partition_size] 
            for i in range(0, len(data), partition_size)
        ]
    else:
        # If can't partition, use as is
        partitioned_data = [data]
    
    # If only one partition, just run directly
    if len(partitioned_data) == 1:
        return func(partitioned_data[0], **kwargs)
    
    # Submit tasks for each partition
    task_ids = []
    for i, partition in enumerate(partitioned_data):
        task_id = compute.submit_task(
            func, 
            partition,
            **kwargs,
            priority=priority,
            task_name=f"distributed_apply_{i}"
        )
        task_ids.append(task_id)
    
    # Gather results
    results = []
    for task_id in task_ids:
        result = compute.get_result(task_id, timeout=timeout)
        results.append(result)
    
    # Combine results based on data type
    if isinstance(data, pd.DataFrame):
        if results and isinstance(results[0], pd.DataFrame):
            return pd.concat(results, ignore_index=True)
        return results
    elif isinstance(data, np.ndarray):
        if results and isinstance(results[0], np.ndarray):
            return np.concatenate(results)
        return results
    elif isinstance(data, list):
        if results and isinstance(results[0], list):
            return [item for sublist in results for item in sublist]
        return results
    else:
        return results


def distributed_map(
    func: Callable,
    items: List,
    max_workers: Optional[int] = None,
    timeout: Optional[float] = None,
    **kwargs
) -> List:
    """
    Apply a function to each item in a list in a distributed manner.
    
    Args:
        func: Function to apply to each item
        items: List of items to process
        max_workers: Maximum number of parallel workers
        timeout: Maximum time to wait for each result
        **kwargs: Additional arguments to pass to the function
        
    Returns:
        List of results
    """
    # Get compute manager
    compute = get_compute_manager()
    
    # If max_workers not specified, determine automatically
    if max_workers is None:
        max_workers = min(len(items), 16)  # Default to max 16 workers
    
    # Process in batches to avoid overwhelming the task system
    batch_size = max(1, len(items) // max_workers)
    batches = [items[i:i+batch_size] for i in range(0, len(items), batch_size)]
    
    # Define function to process a batch
    def process_batch(batch_items):
        return [func(item, **kwargs) for item in batch_items]
    
    # Submit tasks for each batch
    task_ids = []
    for i, batch in enumerate(batches):
        task_id = compute.submit_task(
            process_batch, 
            batch,
            priority=0,
            task_name=f"distributed_map_{i}"
        )
        task_ids.append(task_id)
    
    # Gather results
    batch_results = []
    for task_id in task_ids:
        result = compute.get_result(task_id, timeout=timeout)
        batch_results.append(result)
    
    # Flatten results
    return [item for sublist in batch_results for item in sublist]


def distributed_filter(
    func: Callable,
    items: List,
    max_workers: Optional[int] = None,
    timeout: Optional[float] = None,
    **kwargs
) -> List:
    """
    Filter a list based on a predicate function in a distributed manner.
    
    Args:
        func: Predicate function to apply to each item
        items: List of items to filter
        max_workers: Maximum number of parallel workers
        timeout: Maximum time to wait for each result
        **kwargs: Additional arguments to pass to the function
        
    Returns:
        Filtered list where func(item) is True
    """
    # Define mapping function that returns (item, predicate_result)
    def map_func(item):
        return (item, func(item, **kwargs))
    
    # Apply distributed map
    results = distributed_map(
        map_func,
        items,
        max_workers=max_workers,
        timeout=timeout
    )
    
    # Filter items where predicate is True
    return [item for item, keep in results if keep]


def distributed_reduce(
    func: Callable,
    items: List,
    initial: Optional[Any] = None,
    timeout: Optional[float] = None,
    **kwargs
) -> Any:
    """
    Perform a reduce operation in a distributed manner.
    
    Args:
        func: Binary function to reduce with (takes two arguments and returns one)
        items: List of items to reduce
        initial: Initial value for reduction
        timeout: Maximum time to wait for result
        **kwargs: Additional arguments to pass to the function
        
    Returns:
        Reduced result
    """
    if not items:
        return initial
    
    # Get compute manager
    compute = get_compute_manager()
    
    # If only a few items, don't bother with distribution
    if len(items) <= 4:
        result = items[0] if initial is None else initial
        for item in items if initial is None else [items[0], *items[1:]]:
            result = func(result, item, **kwargs)
        return result
    
    # Divide items into groups
    num_groups = min(16, len(items) // 2)  # At most 16 groups, at least 2 items per group
    group_size = max(2, len(items) // num_groups)
    groups = [items[i:i+group_size] for i in range(0, len(items), group_size)]
    
    # Define function to reduce a group
    def reduce_group(group_items, initial_value=None):
        result = group_items[0] if initial_value is None else initial_value
        for item in group_items if initial_value is None else group_items:
            result = func(result, item, **kwargs)
        return result
    
    # Submit tasks for each group
    task_ids = []
    for i, group in enumerate(groups):
        # Only use initial value for the first group
        group_initial = initial if i == 0 else None
        task_id = compute.submit_task(
            reduce_group, 
            group,
            initial_value=group_initial,
            priority=0,
            task_name=f"distributed_reduce_1_{i}"
        )
        task_ids.append(task_id)
    
    # Get group results
    group_results = []
    for task_id in task_ids:
        result = compute.get_result(task_id, timeout=timeout)
        group_results.append(result)
    
    # If only one group result, return it
    if len(group_results) == 1:
        return group_results[0]
    
    # Recursively reduce group results
    return distributed_reduce(
        func,
        group_results,
        initial=None,
        timeout=timeout,
        **kwargs
    )


def parallel_model_inference(
    model_id: str,
    data: Union[pd.DataFrame, np.ndarray],
    batch_size: int = 10000,
    timeout: Optional[float] = None
) -> np.ndarray:
    """
    Run model inference in parallel across distributed workers.
    
    Args:
        model_id: ID of the model to use
        data: Data to make predictions on
        batch_size: Batch size for prediction
        timeout: Maximum time to wait for results
        
    Returns:
        Array of predictions
    """
    # Get ML tasks handler
    ml_tasks = get_ml_tasks()
    
    # Run prediction with distribution
    return ml_tasks.predict_batch(
        model_id=model_id,
        data=data,
        batch_size=batch_size,
        distributed=True,
        timeout=timeout
    )


def parallel_model_training(
    training_data: pd.DataFrame,
    target_col: str,
    features: Optional[List[str]] = None,
    model_type: str = "xgboost",
    model_params: Optional[Dict[str, Any]] = None,
    validation_fraction: float = 0.2,
    timeout: Optional[float] = None
) -> Dict[str, Any]:
    """
    Train a model in parallel using distributed computing.
    
    Args:
        training_data: Training data as a DataFrame
        target_col: Target column name
        features: List of feature column names (if None, use all columns except target)
        model_type: Type of model to train
        model_params: Parameters for the model
        validation_fraction: Fraction of data to use for validation
        timeout: Maximum time to wait for training
        
    Returns:
        Dictionary with model_id and metrics
    """
    # Get ML tasks handler
    ml_tasks = get_ml_tasks()
    
    # Train model with distribution
    return ml_tasks.train_model(
        data=training_data,
        target_col=target_col,
        features=features,
        model_type=model_type,
        model_params=model_params or {},
        validation_fraction=validation_fraction,
        distribute_data=True,
        timeout=timeout
    )


def process_nlp_model_request(
    system_prompt: str,
    user_prompt: str,
    model_name: str = "gpt-4-turbo",
    temperature: float = 0.3,
    response_format: str = "json",
    max_tokens: int = 4000,
    timeout: int = 120,
    retries: int = 3,
    backoff_factor: float = 2.0
) -> str:
    """
    Process a request to an NLP model and return the response.
    
    Args:
        system_prompt: The system prompt for the LLM
        user_prompt: The user prompt for the LLM
        model_name: Name of the model to use
        temperature: Sampling temperature 
        response_format: Format of the response ("json" or "text")
        max_tokens: Maximum tokens in the response
        timeout: Request timeout in seconds
        retries: Number of retries on failure
        backoff_factor: Backoff factor for retries
        
    Returns:
        String response from the LLM
    """
    # Determine which API to use based on model name
    if model_name.startswith("gpt"):
        return _process_openai_request(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model_name=model_name,
            temperature=temperature,
            response_format=response_format,
            max_tokens=max_tokens,
            timeout=timeout,
            retries=retries,
            backoff_factor=backoff_factor
        )
    elif model_name.startswith("claude"):
        return _process_anthropic_request(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model_name=model_name,
            temperature=temperature,
            response_format=response_format,
            max_tokens=max_tokens,
            timeout=timeout,
            retries=retries,
            backoff_factor=backoff_factor
        )
    else:
        # Default to custom model API
        return _process_custom_model_request(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model_name=model_name,
            temperature=temperature,
            response_format=response_format,
            max_tokens=max_tokens,
            timeout=timeout,
            retries=retries,
            backoff_factor=backoff_factor
        )


def _process_openai_request(
    system_prompt: str,
    user_prompt: str,
    model_name: str = "gpt-4-turbo",
    temperature: float = 0.3,
    response_format: str = "json",
    max_tokens: int = 4000,
    timeout: int = 120,
    retries: int = 3,
    backoff_factor: float = 2.0
) -> str:
    """Process a request using OpenAI API"""
    from openai import OpenAI
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    client = OpenAI(api_key=api_key)
    
    # Set up response format parameter
    response_format_param = None
    if response_format == "json":
        response_format_param = {"type": "json_object"}
    
    # Retry logic
    for retry in range(retries):
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format_param,
                timeout=timeout
            )
            
            # Return the content of the response
            return response.choices[0].message.content
        
        except Exception as e:
            if retry < retries - 1:
                sleep_time = backoff_factor ** retry
                logger.warning(f"OpenAI API request failed: {str(e)}. Retrying in {sleep_time}s")
                time.sleep(sleep_time)
            else:
                logger.error(f"OpenAI API request failed after {retries} retries: {str(e)}")
                raise


def _process_anthropic_request(
    system_prompt: str,
    user_prompt: str,
    model_name: str = "claude-3-opus-20240229",
    temperature: float = 0.3,
    response_format: str = "json",
    max_tokens: int = 4000,
    timeout: int = 120,
    retries: int = 3,
    backoff_factor: float = 2.0
) -> str:
    """Process a request using Anthropic API"""
    import anthropic
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Prepare the system prompt and user prompt
    combined_prompt = f"{system_prompt}\n\n{user_prompt}"
    
    # Define json format instruction for Claude
    if response_format == "json":
        combined_prompt += "\n\nYour response must be valid JSON."
    
    # Retry logic
    for retry in range(retries):
        try:
            response = client.messages.create(
                model=model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": combined_prompt}
                ]
            )
            
            # Return the content of the response
            return response.content[0].text
        
        except Exception as e:
            if retry < retries - 1:
                sleep_time = backoff_factor ** retry
                logger.warning(f"Anthropic API request failed: {str(e)}. Retrying in {sleep_time}s")
                time.sleep(sleep_time)
            else:
                logger.error(f"Anthropic API request failed after {retries} retries: {str(e)}")
                raise


def _process_custom_model_request(
    system_prompt: str,
    user_prompt: str,
    model_name: str,
    temperature: float = 0.3,
    response_format: str = "json",
    max_tokens: int = 4000,
    timeout: int = 120,
    retries: int = 3,
    backoff_factor: float = 2.0
) -> str:
    """Process a request using a custom model API"""
    
    # Get custom model API details from environment
    api_url = os.environ.get("CUSTOM_MODEL_API_URL")
    api_key = os.environ.get("CUSTOM_MODEL_API_KEY")
    
    if not api_url:
        raise ValueError("CUSTOM_MODEL_API_URL environment variable is not set")
    
    # Prepare headers
    headers = {
        "Content-Type": "application/json"
    }
    
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    # Prepare payload
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "response_format": response_format
    }
    
    # Retry logic
    for retry in range(retries):
        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=timeout
            )
            
            response.raise_for_status()  # Raise exception for HTTP errors
            
            # Parse the response
            response_data = response.json()
            
            # Extract content based on the expected response structure
            # Adjust this based on your custom API's response format
            if "choices" in response_data and len(response_data["choices"]) > 0:
                if "message" in response_data["choices"][0]:
                    return response_data["choices"][0]["message"]["content"]
                elif "text" in response_data["choices"][0]:
                    return response_data["choices"][0]["text"]
            
            # Fallback if the expected structure is not found
            return json.dumps(response_data)
        
        except Exception as e:
            if retry < retries - 1:
                sleep_time = backoff_factor ** retry
                logger.warning(f"Custom model API request failed: {str(e)}. Retrying in {sleep_time}s")
                time.sleep(sleep_time)
            else:
                logger.error(f"Custom model API request failed after {retries} retries: {str(e)}")
                raise 