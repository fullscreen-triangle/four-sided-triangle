"""
Distributed Compute Manager

Handles distributed computing tasks using Ray and Dask for high-performance computing needs.
Acts as an interface between the main application and the distributed computing cluster.
"""

import os
import json
import time
import logging
from typing import Dict, List, Union, Any, Optional, Callable
from enum import Enum

import ray
import dask
from dask.distributed import Client, LocalCluster
import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComputeBackend(str, Enum):
    """Supported compute backends"""
    RAY = "ray"
    DASK = "dask"
    LOCAL = "local"  # For testing/development

class ComputeManager:
    """
    Manages distributed computing tasks across Ray and Dask clusters.
    
    This class handles:
    1. Connection to compute clusters
    2. Dispatching tasks to appropriate backends
    3. Managing compute resources
    4. Load balancing between clusters
    5. Result aggregation and error handling
    """
    
    def __init__(
        self, 
        backend: ComputeBackend = None,
        ray_address: str = None, 
        dask_scheduler: str = None,
        n_local_workers: int = None,
        config_path: str = None
    ):
        """
        Initialize the compute manager with connection to compute clusters.
        
        Args:
            backend: Preferred compute backend (if None, will try in order: Ray, Dask, Local)
            ray_address: Address of Ray cluster (e.g., "ray://ip:port")
            dask_scheduler: Address of Dask scheduler (e.g., "tcp://ip:port")
            n_local_workers: Number of workers for local computation
            config_path: Path to configuration file for connection details
        """
        self.backend = backend
        self.ray_address = ray_address
        self.dask_scheduler = dask_scheduler
        self.n_local_workers = n_local_workers or os.cpu_count()
        self.ray_client = None
        self.dask_client = None
        
        # Load configuration if provided
        if config_path:
            self._load_config(config_path)
        
        # Connect to compute backends based on priority
        self._connect_compute_backends()
        
        # Track active jobs
        self.active_jobs = {}
        
    def _load_config(self, config_path: str):
        """Load configuration from file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            self.backend = config.get('backend') or self.backend
            self.ray_address = config.get('ray_address') or self.ray_address
            self.dask_scheduler = config.get('dask_scheduler') or self.dask_scheduler
            self.n_local_workers = config.get('n_local_workers') or self.n_local_workers
            
            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
    
    def _connect_compute_backends(self):
        """Connect to compute backends based on configuration"""
        # Determine backend priority
        if self.backend:
            backend_priority = [self.backend]
        else:
            backend_priority = [ComputeBackend.RAY, ComputeBackend.DASK, ComputeBackend.LOCAL]
        
        connected = False
        
        for backend in backend_priority:
            try:
                if backend == ComputeBackend.RAY and self._connect_ray():
                    self.backend = ComputeBackend.RAY
                    connected = True
                    break
                elif backend == ComputeBackend.DASK and self._connect_dask():
                    self.backend = ComputeBackend.DASK
                    connected = True
                    break
            except Exception as e:
                logger.warning(f"Failed to connect to {backend} backend: {e}")
        
        # Fall back to local if no distributed backend is available
        if not connected:
            logger.warning("Falling back to local computation mode")
            self.backend = ComputeBackend.LOCAL
            
        logger.info(f"Using compute backend: {self.backend}")
    
    def _connect_ray(self) -> bool:
        """Connect to Ray cluster"""
        try:
            if self.ray_address:
                ray.init(address=self.ray_address)
            else:
                ray.init()
            
            # Test connection by running a simple task
            @ray.remote
            def test_func():
                return "Ray connection successful"
            
            result = ray.get(test_func.remote())
            logger.info(result)
            return True
        except Exception as e:
            logger.error(f"Ray connection failed: {e}")
            return False
    
    def _connect_dask(self) -> bool:
        """Connect to Dask cluster"""
        try:
            if self.dask_scheduler:
                self.dask_client = Client(self.dask_scheduler)
            else:
                cluster = LocalCluster(n_workers=self.n_local_workers)
                self.dask_client = Client(cluster)
            
            # Test connection by running a simple task
            future = self.dask_client.submit(lambda x: f"Dask connection successful with {x} workers", 
                                            self.n_local_workers)
            result = future.result()
            logger.info(result)
            return True
        except Exception as e:
            logger.error(f"Dask connection failed: {e}")
            if self.dask_client:
                self.dask_client.close()
                self.dask_client = None
            return False
    
    def submit_task(
        self, 
        task_func: Callable, 
        *args, 
        task_id: str = None,
        priority: int = 0,
        resources: Dict[str, float] = None,
        **kwargs
    ) -> str:
        """
        Submit a task for distributed execution.
        
        Args:
            task_func: Function to execute
            *args: Positional arguments for the function
            task_id: Unique identifier for the task (generated if None)
            priority: Task priority (higher value = higher priority)
            resources: Resource requirements (e.g., {"GPU": 1})
            **kwargs: Keyword arguments for the function
            
        Returns:
            task_id: Identifier for tracking the task
        """
        task_id = task_id or f"task_{int(time.time())}_{id(task_func)}"
        
        if self.backend == ComputeBackend.RAY:
            future = self._submit_ray_task(task_func, *args, 
                                         priority=priority, 
                                         resources=resources, 
                                         **kwargs)
        elif self.backend == ComputeBackend.DASK:
            future = self._submit_dask_task(task_func, *args, 
                                          priority=priority, 
                                          **kwargs)
        else:  # Local execution
            future = self._submit_local_task(task_func, *args, **kwargs)
        
        self.active_jobs[task_id] = {
            "future": future,
            "status": "SUBMITTED",
            "start_time": time.time(),
            "backend": self.backend
        }
        
        logger.info(f"Submitted task {task_id} to {self.backend} backend")
        return task_id
    
    def _submit_ray_task(self, task_func, *args, priority=0, resources=None, **kwargs):
        """Submit task to Ray cluster"""
        # Create a Ray remote function if not already
        if not hasattr(task_func, 'remote'):
            options = {}
            if priority:
                options["priority"] = priority
            if resources:
                options.update(resources)
                
            task_func = ray.remote(**options)(task_func)
        
        # Submit the task
        return task_func.remote(*args, **kwargs)
    
    def _submit_dask_task(self, task_func, *args, priority=0, **kwargs):
        """Submit task to Dask cluster"""
        return self.dask_client.submit(task_func, *args, **kwargs, priority=priority)
    
    def _submit_local_task(self, task_func, *args, **kwargs):
        """Execute task locally in a separate thread"""
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(task_func, *args, **kwargs)
    
    def get_result(self, task_id: str, timeout: float = None) -> Any:
        """
        Get result of a task.
        
        Args:
            task_id: Task identifier
            timeout: Maximum time to wait (None = wait indefinitely)
            
        Returns:
            Result of the task
        """
        if task_id not in self.active_jobs:
            raise ValueError(f"Unknown task ID: {task_id}")
        
        job = self.active_jobs[task_id]
        future = job["future"]
        backend = job["backend"]
        
        try:
            if backend == ComputeBackend.RAY:
                result = ray.get(future, timeout=timeout)
            elif backend == ComputeBackend.DASK:
                result = future.result(timeout=timeout)
            else:  # Local execution
                result = future.result(timeout=timeout)
            
            job["status"] = "COMPLETED"
            job["end_time"] = time.time()
            job["duration"] = job["end_time"] - job["start_time"]
            
            return result
        except TimeoutError:
            job["status"] = "TIMEOUT"
            raise TimeoutError(f"Task {task_id} timed out after {timeout} seconds")
        except Exception as e:
            job["status"] = "FAILED"
            job["error"] = str(e)
            raise
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get current status of a task"""
        if task_id not in self.active_jobs:
            raise ValueError(f"Unknown task ID: {task_id}")
        
        job = self.active_jobs[task_id]
        
        # Update status for tasks that might be done
        if job["status"] == "SUBMITTED":
            if job["backend"] == ComputeBackend.RAY:
                if ray.wait([job["future"]], timeout=0)[0]:
                    job["status"] = "COMPLETED"
            elif job["backend"] == ComputeBackend.DASK:
                if job["future"].done():
                    if job["future"].exception() is None:
                        job["status"] = "COMPLETED"
                    else:
                        job["status"] = "FAILED"
                        job["error"] = str(job["future"].exception())
        
        return {
            "task_id": task_id,
            "status": job["status"],
            "backend": job["backend"],
            "start_time": job["start_time"],
            "duration": time.time() - job["start_time"]
        }
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id not in self.active_jobs:
            raise ValueError(f"Unknown task ID: {task_id}")
        
        job = self.active_jobs[task_id]
        
        if job["status"] not in ["SUBMITTED", "RUNNING"]:
            return False
        
        try:
            if job["backend"] == ComputeBackend.RAY:
                ray.cancel(job["future"])
            elif job["backend"] == ComputeBackend.DASK:
                self.dask_client.cancel(job["future"])
            else:  # Local execution
                job["future"].cancel()
            
            job["status"] = "CANCELLED"
            return True
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {e}")
            return False
    
    def map(self, func: Callable, items: List[Any], **kwargs) -> List[str]:
        """
        Map a function over a list of items in parallel.
        
        Args:
            func: Function to apply to each item
            items: List of items to process
            **kwargs: Additional arguments to pass to submit_task
            
        Returns:
            List of task IDs
        """
        task_ids = []
        for item in items:
            task_id = self.submit_task(func, item, **kwargs)
            task_ids.append(task_id)
        
        return task_ids
    
    def gather_results(self, task_ids: List[str], timeout: float = None) -> List[Any]:
        """
        Gather results from multiple tasks.
        
        Args:
            task_ids: List of task IDs
            timeout: Maximum time to wait per task
            
        Returns:
            List of results in the same order as task_ids
        """
        results = []
        for task_id in task_ids:
            try:
                result = self.get_result(task_id, timeout=timeout)
                results.append(result)
            except Exception as e:
                logger.error(f"Error getting result for task {task_id}: {e}")
                results.append(None)
        
        return results
    
    def shutdown(self):
        """Shutdown all compute connections"""
        if self.backend == ComputeBackend.RAY:
            ray.shutdown()
        
        if self.dask_client:
            self.dask_client.close()
            self.dask_client = None
        
        logger.info("Compute manager shutdown complete")


# Singleton instance for use throughout the application
_compute_manager_instance = None

def get_compute_manager(config_path: str = None) -> ComputeManager:
    """Get or create the global compute manager instance"""
    global _compute_manager_instance
    
    if _compute_manager_instance is None:
        _compute_manager_instance = ComputeManager(config_path=config_path)
    
    return _compute_manager_instance 