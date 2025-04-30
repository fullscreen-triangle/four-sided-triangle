"""
Working memory implementation for the Four-Sided Triangle system.

This module provides a default implementation of working memory
that stores and manages query processing state.
"""

import logging
import time
import uuid
from typing import Dict, Any, Optional, List

from app.orchestrator.interfaces import WorkingMemoryInterface

logger = logging.getLogger(__name__)

class DefaultWorkingMemory(WorkingMemoryInterface):
    """
    Default implementation of working memory for the orchestrator.
    
    This class provides a dictionary-based working memory that stores
    query processing state, including inputs, intermediate outputs,
    evaluations, and metadata.
    """
    
    def __init__(self, memory_ttl: int = 3600):
        """
        Initialize working memory.
        
        Args:
            memory_ttl: Time-to-live for memory entries in seconds (default: 1 hour)
        """
        self._memory_store: Dict[str, Dict[str, Any]] = {}
        self._memory_ttl = memory_ttl
        self._memory_timestamps: Dict[str, float] = {}
        logger.info("DefaultWorkingMemory initialized with TTL of %d seconds", memory_ttl)
    
    def get_memory(self, query_id: str) -> Dict[str, Any]:
        """
        Retrieve working memory for a specific query.
        
        Args:
            query_id: Unique identifier for the query
            
        Returns:
            Current working memory context or empty dict if not found
        """
        self._cleanup_expired_memory()
        
        if query_id not in self._memory_store:
            logger.warning("No memory found for query_id: %s", query_id)
            return {}
        
        self._memory_timestamps[query_id] = time.time()
        return self._memory_store[query_id].copy()
    
    def set_memory(self, query_id: str, context: Dict[str, Any]) -> None:
        """
        Set the entire working memory for a query.
        
        Args:
            query_id: Unique identifier for the query
            context: New working memory context
        """
        self._memory_store[query_id] = context.copy()
        self._memory_timestamps[query_id] = time.time()
        logger.debug("Set complete memory for query_id: %s", query_id)
    
    def update_memory(self, query_id: str, updates: Dict[str, Any]) -> None:
        """
        Update working memory for a query.
        
        Args:
            query_id: Unique identifier for the query
            updates: Dictionary of memory updates to apply
        """
        if query_id not in self._memory_store:
            logger.info("Creating new memory for query_id: %s", query_id)
            self._memory_store[query_id] = {}
        
        # Deep update the memory
        self._deep_update(self._memory_store[query_id], updates)
        self._memory_timestamps[query_id] = time.time()
        logger.debug("Updated memory for query_id: %s", query_id)
    
    def clear_memory(self, query_id: str) -> None:
        """
        Clear working memory for a query.
        
        Args:
            query_id: Unique identifier for the query
        """
        if query_id in self._memory_store:
            del self._memory_store[query_id]
            del self._memory_timestamps[query_id]
            logger.info("Cleared memory for query_id: %s", query_id)
    
    def _cleanup_expired_memory(self) -> None:
        """Remove expired entries from memory based on TTL."""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self._memory_timestamps.items()
            if current_time - timestamp > self._memory_ttl
        ]
        
        for key in expired_keys:
            del self._memory_store[key]
            del self._memory_timestamps[key]
        
        if expired_keys:
            logger.info("Cleaned up %d expired memory entries", len(expired_keys))
    
    def _deep_update(self, target: Dict[str, Any], updates: Dict[str, Any]) -> None:
        """
        Recursively update a nested dictionary.
        
        Args:
            target: Dictionary to update
            updates: Dictionary with updates to apply
        """
        for key, value in updates.items():
            if (
                key in target 
                and isinstance(target[key], dict) 
                and isinstance(value, dict)
            ):
                self._deep_update(target[key], value)
            else:
                target[key] = value
    
    def create_query_id(self) -> str:
        """
        Generate a unique query ID.
        
        Returns:
            New unique query identifier
        """
        return str(uuid.uuid4())
    
    def get_all_query_ids(self) -> List[str]:
        """
        Get all active query IDs.
        
        Returns:
            List of all active query IDs
        """
        self._cleanup_expired_memory()
        return list(self._memory_store.keys())
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current working memory.
        
        Returns:
            Dictionary with memory statistics
        """
        self._cleanup_expired_memory()
        return {
            "active_queries": len(self._memory_store),
            "memory_size_bytes": sum(len(str(memory)) for memory in self._memory_store.values()),
            "ttl_seconds": self._memory_ttl
        }

# Global singleton instance
working_memory = DefaultWorkingMemory()
