"""
Base Solver Adapter for the Four-Sided Triangle system.

This module provides a base adapter class that all specific solver adapters should extend,
eliminating duplicate code and standardizing the interface.
"""

from typing import Dict, Any, List, Optional, Callable, Tuple
import logging
import time
import abc

logger = logging.getLogger(__name__)

class BaseSolverAdapter(abc.ABC):
    """
    Base class for all solver adapters.
    
    This abstract class defines the common interface and shared functionality
    for all solver adapters in the Four-Sided Triangle system.
    """
    
    def __init__(self):
        """Initialize the base solver adapter."""
        self.config = {}
        self.name = "base"
        logger.info(f"{self.__class__.__name__} initialized")
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the solver with specific parameters.
        
        Args:
            config: Configuration parameters
        """
        if config:
            self.config.update(config)
        logger.info(f"{self.__class__.__name__} configured with {self.config}")
    
    def solve(self, problem_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve an optimization problem using the specific solver.
        
        Args:
            problem_definition: Complete problem definition
            
        Returns:
            Dictionary containing solution and metadata
        """
        start_time = time.time()
        
        try:
            # Check if the problem is compatible with this solver
            self._validate_problem(problem_definition)
            
            # Solve the problem using the specific solver implementation
            result = self._solve_implementation(problem_definition)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Add execution time if not already present
            if "execution_time_seconds" not in result:
                result["execution_time_seconds"] = execution_time
                
            # Ensure solver details contains the solver name
            if "solver_details" not in result:
                result["solver_details"] = {"name": self.name}
            elif "name" not in result["solver_details"]:
                result["solver_details"]["name"] = self.name
                
            return result
            
        except Exception as e:
            logger.error(f"{self.__class__.__name__} optimization failed: {str(e)}")
            
            # Return error information
            return {
                "status": "error",
                "message": str(e),
                "solver_details": {
                    "name": self.name,
                    "error_type": type(e).__name__
                }
            }
    
    @abc.abstractmethod
    def _solve_implementation(self, problem_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implement the solver-specific solution logic.
        
        This method must be implemented by all subclasses.
        
        Args:
            problem_definition: Complete problem definition
            
        Returns:
            Dictionary containing solution and metadata
        """
        pass
    
    def _validate_problem(self, problem_definition: Dict[str, Any]) -> None:
        """
        Validate that the problem can be solved by this solver.
        
        Args:
            problem_definition: Problem definition to validate
            
        Raises:
            ValueError: If the problem is incompatible with this solver
        """
        # Check required keys
        required_keys = ["variables", "objective"]
        missing_keys = [key for key in required_keys if key not in problem_definition]
        if missing_keys:
            raise ValueError(f"Problem definition missing required keys: {missing_keys}")
        
        # Subclasses can override this to add additional validation
        pass
    
    def can_solve(self, problem_type: str) -> bool:
        """
        Check if this solver can handle the given problem type.
        
        Args:
            problem_type: Type of problem to check
            
        Returns:
            True if the solver can handle this problem type, False otherwise
        """
        # Base implementation that should be overridden by subclasses
        return False 