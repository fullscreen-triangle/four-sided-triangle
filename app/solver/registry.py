"""
Solver Registry for the Four-Sided Triangle system.

This module provides a registry system for mathematical optimization solvers,
allowing dynamic registration and retrieval of solvers based on problem
characteristics and capabilities.
"""

from typing import Dict, Any, List, Optional, Callable, Type
import logging

logger = logging.getLogger(__name__)

class SolverRegistry:
    """
    Registry for mathematical optimization solvers.
    
    This registry maintains a catalog of available solvers with their
    capabilities, allowing the system to select the most appropriate
    solver for a given problem.
    """
    
    def __init__(self):
        """Initialize the solver registry."""
        self._solvers = {}
        self._capabilities = {}
        logger.info("Solver Registry initialized")
    
    def register_solver(self, 
                         solver_id: str, 
                         solver_class: Type, 
                         capabilities: Dict[str, Any]) -> None:
        """
        Register a solver with the registry.
        
        Args:
            solver_id: Unique identifier for the solver
            solver_class: Class implementing the solver
            capabilities: Dictionary describing solver capabilities
        """
        if solver_id in self._solvers:
            logger.warning(f"Solver {solver_id} already registered, overwriting")
        
        self._solvers[solver_id] = solver_class
        self._capabilities[solver_id] = capabilities
        logger.info(f"Registered solver: {solver_id}")
    
    def unregister_solver(self, solver_id: str) -> bool:
        """
        Remove a solver from the registry.
        
        Args:
            solver_id: Identifier of the solver to remove
            
        Returns:
            True if the solver was removed, False if not found
        """
        if solver_id in self._solvers:
            del self._solvers[solver_id]
            del self._capabilities[solver_id]
            logger.info(f"Unregistered solver: {solver_id}")
            return True
        return False
    
    def get_solver(self, solver_id: str) -> Optional[Type]:
        """
        Retrieve a solver by ID.
        
        Args:
            solver_id: Identifier of the solver to retrieve
            
        Returns:
            Solver class if found, None otherwise
        """
        return self._solvers.get(solver_id)
    
    def get_solver_capabilities(self, solver_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the capabilities of a specific solver.
        
        Args:
            solver_id: Identifier of the solver
            
        Returns:
            Capabilities dictionary if found, None otherwise
        """
        return self._capabilities.get(solver_id)
    
    def find_solvers_by_capability(self, 
                                  capability: str, 
                                  min_value: Any = None) -> List[str]:
        """
        Find solvers that have a specific capability.
        
        Args:
            capability: Capability to search for
            min_value: Minimum value for numerical capabilities
            
        Returns:
            List of solver IDs that have the specified capability
        """
        matching_solvers = []
        
        for solver_id, capabilities in self._capabilities.items():
            if capability in capabilities:
                if min_value is not None:
                    # Handle numerical capability thresholds
                    if capabilities[capability] >= min_value:
                        matching_solvers.append(solver_id)
                else:
                    matching_solvers.append(solver_id)
        
        return matching_solvers
    
    def find_solvers_for_problem(self, 
                                problem_type: str, 
                                problem_characteristics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find suitable solvers for a specific problem.
        
        Args:
            problem_type: Type of problem (e.g., 'linear', 'nonlinear', 'combinatorial')
            problem_characteristics: Dictionary of problem characteristics
            
        Returns:
            List of dictionaries with solver information, sorted by suitability
        """
        suitable_solvers = []
        
        # Determine required capabilities based on problem characteristics
        required_capabilities = self._map_problem_to_capabilities(
            problem_type, problem_characteristics
        )
        
        for solver_id, capabilities in self._capabilities.items():
            compatibility_score = self._calculate_compatibility(
                required_capabilities, capabilities
            )
            
            if compatibility_score > 0:
                suitable_solvers.append({
                    "solver_id": solver_id,
                    "solver_class": self._solvers[solver_id],
                    "compatibility_score": compatibility_score,
                    "capabilities": capabilities
                })
        
        # Sort by compatibility score, highest first
        return sorted(suitable_solvers, 
                      key=lambda s: s["compatibility_score"], 
                      reverse=True)
    
    def list_all_solvers(self) -> List[Dict[str, Any]]:
        """
        List all registered solvers and their capabilities.
        
        Returns:
            List of dictionaries with solver information
        """
        return [
            {
                "solver_id": solver_id,
                "solver_class": self._solvers[solver_id],
                "capabilities": self._capabilities[solver_id]
            }
            for solver_id in self._solvers
        ]
    
    def _map_problem_to_capabilities(self, 
                                    problem_type: str, 
                                    characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map problem characteristics to required solver capabilities.
        
        Args:
            problem_type: Type of problem
            characteristics: Problem characteristics
            
        Returns:
            Dictionary of required capabilities
        """
        required_capabilities = {
            "problem_types": [problem_type],
        }
        
        # Map problem size to capability requirements
        if "size" in characteristics:
            size = characteristics["size"]
            required_capabilities["max_variables"] = size.get("variables", 0)
            required_capabilities["max_constraints"] = size.get("constraints", 0)
        
        # Map other characteristics
        if "constraints" in characteristics:
            constraint_types = characteristics["constraints"].get("types", [])
            required_capabilities["constraint_types"] = constraint_types
        
        if "objective" in characteristics:
            objective_type = characteristics["objective"].get("type")
            if objective_type:
                required_capabilities["objective_types"] = [objective_type]
        
        return required_capabilities
    
    def _calculate_compatibility(self, 
                                required: Dict[str, Any], 
                                available: Dict[str, Any]) -> float:
        """
        Calculate compatibility score between required and available capabilities.
        
        Args:
            required: Dictionary of required capabilities
            available: Dictionary of available capabilities
            
        Returns:
            Compatibility score between 0 and 1
        """
        if "problem_types" in required and "problem_types" in available:
            # If the solver doesn't support any of the required problem types, it's incompatible
            if not any(pt in available["problem_types"] for pt in required["problem_types"]):
                return 0.0
        
        # Count matching capabilities
        matches = 0
        total_requirements = 0
        
        for key, req_value in required.items():
            total_requirements += 1
            
            if key not in available:
                continue
            
            avail_value = available[key]
            
            if isinstance(req_value, list) and isinstance(avail_value, list):
                # For list values, check if any required item is in available
                if any(item in avail_value for item in req_value):
                    matches += 1
            elif isinstance(req_value, (int, float)) and isinstance(avail_value, (int, float)):
                # For numeric values, check if available meets or exceeds required
                if avail_value >= req_value:
                    matches += 1
            elif req_value == avail_value:
                # For exact matches (strings, booleans, etc.)
                matches += 1
        
        # Calculate score based on proportion of matched requirements
        return matches / total_requirements if total_requirements > 0 else 0.0

# Global solver registry instance
solver_registry = SolverRegistry()
