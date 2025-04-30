"""
SciPy Optimization Adapter for the Four-Sided Triangle system.

This module provides adapters for SciPy's optimization functions, allowing
the system to leverage SciPy's solvers for various optimization problems.
"""

from typing import Dict, Any, List, Optional, Callable, Tuple
import logging
import numpy as np

try:
    from scipy import optimize
except ImportError:
    raise ImportError("SciPy is required for this adapter. Install with 'pip install scipy'")

from app.solver.registry import solver_registry

logger = logging.getLogger(__name__)

class ScipyOptimizationSolver:
    """
    Adapter for SciPy optimization solvers.
    
    This class adapts SciPy's optimization functions to the Four-Sided
    Triangle solver interface, supporting various optimization algorithms.
    """
    
    def __init__(self):
        """Initialize the SciPy optimization adapter."""
        self.config = {
            "max_iterations": 1000,
            "tolerance": 1e-6,
            "verbose": False
        }
        logger.info("SciPy Optimization Solver initialized")
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the solver with specific parameters.
        
        Args:
            config: Configuration parameters
        """
        if config:
            self.config.update(config)
        logger.info(f"SciPy Optimizer configured with {self.config}")
    
    def solve(self, problem_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve an optimization problem using SciPy.
        
        Args:
            problem_definition: Complete problem definition
            
        Returns:
            Dictionary containing solution and metadata
        """
        start_time = np.datetime64('now')
        
        try:
            # Extract problem components
            problem_type = problem_definition.get("metadata", {}).get("problem_type", "unknown")
            
            # Select appropriate solver method based on problem type
            if problem_type == "linear":
                result = self._solve_linear(problem_definition)
            elif problem_type == "nonlinear":
                result = self._solve_nonlinear(problem_definition)
            elif problem_type == "constrained":
                result = self._solve_constrained(problem_definition)
            elif problem_type == "least_squares":
                result = self._solve_least_squares(problem_definition)
            else:
                # Default to general minimize method
                result = self._solve_general(problem_definition)
            
            # Calculate execution time
            end_time = np.datetime64('now')
            execution_time = (end_time - start_time) / np.timedelta64(1, 's')
            
            # Prepare solution object
            solution = {
                "status": "success",
                "variables": result.get("variables", {}),
                "objective_value": result.get("objective_value"),
                "iterations": result.get("iterations", 0),
                "execution_time_seconds": float(execution_time),
                "message": result.get("message", "Optimization successful"),
                "solver_details": {
                    "name": "scipy",
                    "method": result.get("method", "minimize"),
                    "success": result.get("success", True)
                }
            }
            
            return solution
            
        except Exception as e:
            logger.error(f"SciPy optimization failed: {str(e)}")
            
            # Return error information
            return {
                "status": "error",
                "message": str(e),
                "solver_details": {
                    "name": "scipy",
                    "error_type": type(e).__name__
                }
            }
    
    def _solve_linear(self, problem_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve a linear programming problem using SciPy's linprog.
        
        Args:
            problem_definition: Problem definition
            
        Returns:
            Dictionary with solution details
        """
        # Extract objective and constraints
        objective = problem_definition.get("objective", {})
        constraints = problem_definition.get("constraints", [])
        bounds = problem_definition.get("bounds", [])
        
        # Get coefficients from objective
        c = np.array(objective.get("coefficients", []))
        
        # Process inequality constraints (Ax <= b)
        A_ub = []
        b_ub = []
        
        # Process equality constraints (Aeq x = beq)
        A_eq = []
        b_eq = []
        
        for constraint in constraints:
            coeffs = np.array(constraint.get("coefficients", []))
            rhs = constraint.get("rhs", 0)
            
            if constraint.get("type") == "equality":
                A_eq.append(coeffs)
                b_eq.append(rhs)
            else:  # Inequality
                A_ub.append(coeffs)
                b_ub.append(rhs)
        
        # Convert lists to numpy arrays
        if A_ub:
            A_ub = np.array(A_ub)
            b_ub = np.array(b_ub)
        else:
            A_ub = None
            b_ub = None
            
        if A_eq:
            A_eq = np.array(A_eq)
            b_eq = np.array(b_eq)
        else:
            A_eq = None
            b_eq = None
        
        # Process bounds
        var_bounds = None
        if bounds:
            var_bounds = [(b.get("lower", 0), b.get("upper", None)) for b in bounds]
        
        # Set options
        options = {
            "maxiter": self.config["max_iterations"],
            "tol": self.config["tolerance"],
            "disp": self.config["verbose"]
        }
        
        # Solve using linprog
        result = optimize.linprog(
            c=c,
            A_ub=A_ub, 
            b_ub=b_ub,
            A_eq=A_eq, 
            b_eq=b_eq,
            bounds=var_bounds,
            method='interior-point',
            options=options
        )
        
        # Extract and return results
        return {
            "variables": result.x.tolist() if hasattr(result, 'x') else [],
            "objective_value": float(result.fun) if hasattr(result, 'fun') else None,
            "iterations": int(result.nit) if hasattr(result, 'nit') else 0,
            "message": result.message if hasattr(result, 'message') else "",
            "success": result.success if hasattr(result, 'success') else False,
            "method": "linprog"
        }
    
    def _solve_nonlinear(self, problem_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve a nonlinear optimization problem using SciPy's minimize.
        
        Args:
            problem_definition: Problem definition
            
        Returns:
            Dictionary with solution details
        """
        # Extract objective function components
        objective = problem_definition.get("objective", {})
        initial_guess = np.array(problem_definition.get("initial_guess", [0.0, 0.0]))
        
        # Get objective function
        objective_type = objective.get("type", "custom")
        
        if objective_type == "custom" and "function" in objective:
            # Use provided function
            func = objective["function"]
        else:
            # Create default quadratic function as fallback
            func = lambda x: np.sum(x**2)
        
        # Process constraints
        constraints = []
        for constraint in problem_definition.get("constraints", []):
            if "function" in constraint:
                # Add constraint using SciPy's NonlinearConstraint
                constraint_func = constraint["function"]
                lb = constraint.get("lower_bound", -np.inf)
                ub = constraint.get("upper_bound", np.inf)
                
                constraints.append(
                    optimize.NonlinearConstraint(constraint_func, lb, ub)
                )
        
        # Process bounds
        bounds = None
        if "bounds" in problem_definition:
            bounds_list = problem_definition["bounds"]
            bounds = optimize.Bounds(
                lb=np.array([b.get("lower", -np.inf) for b in bounds_list]),
                ub=np.array([b.get("upper", np.inf) for b in bounds_list])
            )
        
        # Set options
        options = {
            "maxiter": self.config["max_iterations"],
            "disp": self.config["verbose"]
        }
        
        # Determine method based on problem characteristics
        method = problem_definition.get("metadata", {}).get("preferred_method", "SLSQP")
        
        # Solve using minimize
        result = optimize.minimize(
            fun=func,
            x0=initial_guess,
            method=method,
            bounds=bounds,
            constraints=constraints,
            options=options
        )
        
        # Extract and return results
        return {
            "variables": result.x.tolist() if hasattr(result, 'x') else [],
            "objective_value": float(result.fun) if hasattr(result, 'fun') else None,
            "iterations": int(result.nit) if hasattr(result, 'nit') else 0,
            "message": result.message if hasattr(result, 'message') else "",
            "success": result.success if hasattr(result, 'success') else False,
            "method": method
        }
    
    def _solve_constrained(self, problem_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve a constrained optimization problem using SciPy's optimize.minimize.
        
        Args:
            problem_definition: Problem definition
            
        Returns:
            Dictionary with solution details
        """
        # This is actually handled by _solve_nonlinear, but kept as a separate method
        # for potential future specialization
        return self._solve_nonlinear(problem_definition)
    
    def _solve_least_squares(self, problem_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve a least squares problem using SciPy's least_squares.
        
        Args:
            problem_definition: Problem definition
            
        Returns:
            Dictionary with solution details
        """
        # Extract problem components
        residual_function = problem_definition.get("residual_function")
        initial_guess = np.array(problem_definition.get("initial_guess", [0.0, 0.0]))
        
        if not residual_function:
            # Create a simple default residual function
            def default_residual(x):
                return np.array([x[0]**2 + x[1]**2 - 1, x[0] - x[1]])
            
            residual_function = default_residual
        
        # Process bounds if available
        bounds = None
        if "bounds" in problem_definition:
            bounds_list = problem_definition["bounds"]
            lower_bounds = np.array([b.get("lower", -np.inf) for b in bounds_list])
            upper_bounds = np.array([b.get("upper", np.inf) for b in bounds_list])
            bounds = (lower_bounds, upper_bounds)
        
        # Set options
        options = {}
        if "max_iterations" in self.config:
            options["maxiter"] = self.config["max_iterations"]
        if "verbose" in self.config:
            options["verbose"] = 2 if self.config["verbose"] else 0
        
        # Solve using least_squares
        result = optimize.least_squares(
            residual_function,
            initial_guess,
            bounds=bounds,
            method="trf",
            **options
        )
        
        # Extract and return results
        return {
            "variables": result.x.tolist() if hasattr(result, 'x') else [],
            "objective_value": float(result.cost) if hasattr(result, 'cost') else None,
            "iterations": int(result.nfev) if hasattr(result, 'nfev') else 0,
            "message": result.message if hasattr(result, 'message') else "",
            "success": result.success if hasattr(result, 'success') else False,
            "method": "least_squares"
        }
    
    def _solve_general(self, problem_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        General optimization using SciPy's minimize.
        
        Args:
            problem_definition: Problem definition
            
        Returns:
            Dictionary with solution details
        """
        # This is a fallback that handles general optimization problems
        return self._solve_nonlinear(problem_definition)


# Register this solver with the registry
solver_registry.register_solver(
    solver_id="scipy_optimization",
    solver_class=ScipyOptimizationSolver,
    capabilities={
        "problem_types": ["linear", "nonlinear", "constrained", "least_squares", "general"],
        "variable_types": ["continuous"],
        "max_variables": 10000,
        "max_constraints": 10000,
        "algorithms": ["SLSQP", "Nelder-Mead", "Powell", "BFGS", "L-BFGS-B", "TNC", "CG", "trust-constr"],
        "performance_profile": {
            "speed": 0.8,
            "robustness": 0.9,
            "memory_efficiency": 0.7
        }
    }
)
