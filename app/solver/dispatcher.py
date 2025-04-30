"""
Solver Dispatcher for the Four-Sided Triangle system.

This module provides functionality for analyzing optimization problems,
selecting appropriate solvers, and dispatching computation tasks to them.
"""

from typing import Dict, Any, List, Optional, Tuple
import logging
import importlib
import time

from app.solver.registry import solver_registry

logger = logging.getLogger(__name__)

class SolverDispatcher:
    """
    Dispatcher for mathematical optimization solvers.
    
    This class analyzes optimization problems, selects the most appropriate
    solver from the registry, and handles the solving process including
    fallback mechanisms.
    """
    
    def __init__(self):
        """Initialize the solver dispatcher."""
        self._performance_cache = {}  # Cache of solver performance metrics
        logger.info("Solver Dispatcher initialized")
    
    async def solve(self, 
                   problem_definition: Dict[str, Any],
                   context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Solve an optimization problem using the most appropriate solver.
        
        Args:
            problem_definition: Complete problem definition
            context: Additional context for solver selection
            
        Returns:
            Dictionary containing solution and metadata
        """
        start_time = time.time()
        
        # Extract problem type and characteristics
        problem_type, characteristics = self._analyze_problem(problem_definition)
        
        # Find suitable solvers
        solver_candidates = solver_registry.find_solvers_for_problem(
            problem_type, characteristics
        )
        
        if not solver_candidates:
            logger.warning(f"No suitable solvers found for problem type: {problem_type}")
            return {
                "status": "error",
                "message": f"No suitable solvers found for problem type: {problem_type}",
                "problem_type": problem_type,
                "characteristics": characteristics
            }
        
        # Select primary solver and fallbacks
        primary_solver = solver_candidates[0]
        fallback_solvers = solver_candidates[1:2]  # Take up to 2 fallbacks
        
        # Attempt to solve with primary solver
        solution, status = await self._attempt_solve(
            primary_solver, problem_definition, context
        )
        
        # If primary solver fails, try fallbacks
        if status != "success" and fallback_solvers:
            logger.info(f"Primary solver {primary_solver['solver_id']} failed, trying fallbacks")
            
            for fallback in fallback_solvers:
                logger.info(f"Attempting fallback solver: {fallback['solver_id']}")
                solution, status = await self._attempt_solve(
                    fallback, problem_definition, context
                )
                
                if status == "success":
                    logger.info(f"Fallback solver {fallback['solver_id']} succeeded")
                    # Update solver performance cache
                    self._update_performance_metrics(fallback['solver_id'], problem_type, True)
                    break
        
        # Update performance metrics for primary solver
        self._update_performance_metrics(
            primary_solver['solver_id'], 
            problem_type, 
            status == "success"
        )
        
        # Calculate total solving time
        total_time = time.time() - start_time
        
        # Prepare result
        result = {
            "solution": solution,
            "status": status,
            "solver_id": primary_solver['solver_id'] if status == "success" else None,
            "problem_type": problem_type,
            "total_time_seconds": total_time,
            "fallbacks_attempted": len(fallback_solvers) if status != "success" else 0
        }
        
        return result
    
    async def _attempt_solve(self, 
                            solver_info: Dict[str, Any],
                            problem_definition: Dict[str, Any],
                            context: Optional[Dict[str, Any]]) -> Tuple[Dict[str, Any], str]:
        """
        Attempt to solve using a specific solver.
        
        Args:
            solver_info: Information about the solver to use
            problem_definition: Complete problem definition
            context: Additional context for solving
            
        Returns:
            Tuple of (solution, status)
        """
        solver_id = solver_info["solver_id"]
        solver_class = solver_info["solver_class"]
        
        try:
            # Instantiate the solver
            solver = solver_class()
            
            # Configure the solver with any context
            if hasattr(solver, "configure") and context:
                solver.configure(context)
            
            # Solve the problem
            if hasattr(solver, "solve_async"):
                solution = await solver.solve_async(problem_definition)
            else:
                solution = solver.solve(problem_definition)
            
            logger.info(f"Solver {solver_id} successfully solved the problem")
            return solution, "success"
            
        except Exception as e:
            logger.error(f"Solver {solver_id} failed: {str(e)}")
            return {"error": str(e)}, "error"
    
    def _analyze_problem(self, 
                        problem_definition: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Analyze a problem to determine its type and characteristics.
        
        Args:
            problem_definition: Complete problem definition
            
        Returns:
            Tuple of (problem_type, characteristics)
        """
        # Extract problem metadata if available
        metadata = problem_definition.get("metadata", {})
        
        # Try to get problem type directly from metadata
        problem_type = metadata.get("problem_type")
        
        if not problem_type:
            # Infer problem type based on problem structure
            problem_type = self._infer_problem_type(problem_definition)
        
        # Extract or infer problem characteristics
        characteristics = metadata.get("characteristics", {})
        
        if not characteristics:
            characteristics = self._extract_characteristics(problem_definition)
        
        logger.info(f"Analyzed problem: type={problem_type}, characteristics={characteristics}")
        return problem_type, characteristics
    
    def _infer_problem_type(self, problem_definition: Dict[str, Any]) -> str:
        """
        Infer the problem type based on its structure.
        
        Args:
            problem_definition: Problem definition
            
        Returns:
            Inferred problem type
        """
        # Check for variables and constraints
        variables = problem_definition.get("variables", [])
        constraints = problem_definition.get("constraints", [])
        objective = problem_definition.get("objective", {})
        
        # Check if it's a linear programming problem
        if self._is_linear(objective, constraints):
            if all(var.get("type") == "integer" for var in variables):
                return "integer_linear"
            elif any(var.get("type") == "integer" for var in variables):
                return "mixed_integer"
            else:
                return "linear"
        
        # Check if it's a constraint satisfaction problem
        if not objective and constraints:
            return "constraint_satisfaction"
        
        # Check if it's a nonlinear problem
        if not self._is_linear(objective, constraints):
            return "nonlinear"
        
        # Default to generic optimization
        return "optimization"
    
    def _is_linear(self, 
                  objective: Dict[str, Any], 
                  constraints: List[Dict[str, Any]]) -> bool:
        """
        Check if an optimization problem is linear.
        
        Args:
            objective: Objective function definition
            constraints: List of constraints
            
        Returns:
            True if the problem is linear, False otherwise
        """
        # Check if objective function is linear
        if objective.get("type") != "linear":
            return False
        
        # Check if all constraints are linear
        for constraint in constraints:
            if constraint.get("type") != "linear":
                return False
        
        return True
    
    def _extract_characteristics(self, problem_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract problem characteristics from definition.
        
        Args:
            problem_definition: Problem definition
            
        Returns:
            Dictionary of problem characteristics
        """
        variables = problem_definition.get("variables", [])
        constraints = problem_definition.get("constraints", [])
        objective = problem_definition.get("objective", {})
        
        characteristics = {
            "size": {
                "variables": len(variables),
                "constraints": len(constraints)
            },
            "constraints": {
                "types": list(set(c.get("type", "unknown") for c in constraints))
            },
            "objective": {
                "type": objective.get("type", "unknown") if objective else "none"
            },
            "variable_types": list(set(v.get("type", "continuous") for v in variables))
        }
        
        return characteristics
    
    def _update_performance_metrics(self, 
                                  solver_id: str, 
                                  problem_type: str, 
                                  success: bool) -> None:
        """
        Update solver performance metrics in cache.
        
        Args:
            solver_id: Solver identifier
            problem_type: Type of problem
            success: Whether the solver was successful
        """
        key = f"{solver_id}:{problem_type}"
        
        if key not in self._performance_cache:
            self._performance_cache[key] = {
                "attempts": 0,
                "successes": 0,
                "success_rate": 0.0
            }
        
        metrics = self._performance_cache[key]
        metrics["attempts"] += 1
        
        if success:
            metrics["successes"] += 1
        
        metrics["success_rate"] = metrics["successes"] / metrics["attempts"]

# Global solver dispatcher instance
solver_dispatcher = SolverDispatcher()
