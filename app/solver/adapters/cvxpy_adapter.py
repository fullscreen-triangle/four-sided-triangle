"""
CVXPY Optimization Adapter for the Four-Sided Triangle system.

This module provides adapters for CVXPY's convex optimization solvers, allowing
the system to leverage CVXPY for various convex optimization problems.
"""

from typing import Dict, Any, List, Optional, Callable, Tuple
import logging
import time
import numpy as np

try:
    import cvxpy as cp
except ImportError:
    raise ImportError("CVXPY is required for this adapter. Install with 'pip install cvxpy'")

from app.solver.registry import solver_registry
from app.solver.adapters.base_adapter import BaseSolverAdapter

logger = logging.getLogger(__name__)

class CVXPYOptimizationSolver(BaseSolverAdapter):
    """
    Adapter for CVXPY convex optimization solvers.
    
    This class adapts CVXPY's convex optimization functions to the Four-Sided
    Triangle solver interface, supporting various convex problems.
    """
    
    def __init__(self):
        """Initialize the CVXPY optimization adapter."""
        super().__init__()
        self.name = "cvxpy"
        self.config = {
            "solver": None,  # Default solver (CVXPY will choose best available)
            "verbose": False,
            "max_iters": 1000,
            "abstol": 1e-8,
            "reltol": 1e-8
        }
        logger.info("CVXPY Optimization Solver initialized")
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the solver with specific parameters.
        
        Args:
            config: Configuration parameters
        """
        if config:
            self.config.update(config)
        logger.info(f"CVXPY Optimizer configured with {self.config}")
    
    def _solve_implementation(self, problem_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve an optimization problem using CVXPY.
        
        Args:
            problem_definition: Complete problem definition
            
        Returns:
            Dictionary containing solution and metadata
        """
        start_time = time.time()
        
        try:
            # Create the CVXPY model
            problem, variables = self._create_problem(problem_definition)
            
            # Solve the problem
            result = self._solve_problem(problem)
            
            # Extract the solution
            solution = self._extract_solution(variables, problem)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Prepare solution object
            return {
                "status": "success" if problem.status in ["optimal", "optimal_inaccurate"] else "failed",
                "variables": solution,
                "objective_value": float(problem.value) if problem.value is not None else None,
                "execution_time_seconds": execution_time,
                "message": problem.status,
                "solver_details": {
                    "name": "cvxpy",
                    "solver_used": str(problem.solver_stats.solver_name) if problem.solver_stats else "unknown",
                    "solve_time": problem.solver_stats.solve_time if problem.solver_stats else None,
                    "setup_time": problem.solver_stats.setup_time if problem.solver_stats else None,
                    "num_iters": problem.solver_stats.num_iters if problem.solver_stats else None
                }
            }
            
        except Exception as e:
            logger.error(f"CVXPY optimization failed: {str(e)}")
            
            # Return error information
            return {
                "status": "error",
                "message": str(e),
                "solver_details": {
                    "name": "cvxpy",
                    "error_type": type(e).__name__
                }
            }
    
    def _validate_problem(self, problem_definition: Dict[str, Any]) -> None:
        """
        Validate that the problem can be solved by CVXPY.
        
        Args:
            problem_definition: Problem definition to validate
            
        Raises:
            ValueError: If the problem is incompatible with CVXPY
        """
        # Call the base validation first
        super()._validate_problem(problem_definition)
        
        # Check if the problem type is supported by CVXPY
        problem_type = problem_definition.get("metadata", {}).get("problem_type", "convex")
        if problem_type not in ["convex", "linear", "quadratic", "mixed_integer"]:
            raise ValueError(f"CVXPY adapter does not support problem type: {problem_type}")
    
    def can_solve(self, problem_type: str) -> bool:
        """
        Check if CVXPY can handle the given problem type.
        
        Args:
            problem_type: Type of problem to check
            
        Returns:
            True if CVXPY can handle this problem type, False otherwise
        """
        return problem_type in ["convex", "linear", "quadratic", "mixed_integer"]
    
    def _create_problem(self, problem_definition: Dict[str, Any]) -> Tuple[cp.Problem, Dict[str, cp.Variable]]:
        """
        Create a CVXPY problem from the problem definition.
        
        Args:
            problem_definition: Problem definition
            
        Returns:
            Tuple of (cvxpy_problem, variables_dict)
        """
        # Extract problem components
        objective_def = problem_definition.get("objective", {})
        constraints_def = problem_definition.get("constraints", [])
        variables_def = problem_definition.get("variables", [])
        
        # Create variables
        variables = {}
        for i, var_def in enumerate(variables_def):
            name = var_def.get("name", f"x{i}")
            shape = var_def.get("shape", (1,))
            
            # Handle different variable types
            var_type = var_def.get("type", "continuous")
            if var_type == "integer":
                variables[name] = cp.Variable(shape, integer=True, name=name)
            elif var_type == "binary":
                variables[name] = cp.Variable(shape, boolean=True, name=name)
            elif var_type == "positive":
                variables[name] = cp.Variable(shape, nonneg=True, name=name)
            elif var_type == "complex":
                variables[name] = cp.Variable(shape, complex=True, name=name)
            else:
                variables[name] = cp.Variable(shape, name=name)
            
            # Add bounds if specified
            if "lower_bound" in var_def:
                constraints_def.append({
                    "type": "inequality_geq",
                    "expression": {"variable": name},
                    "bound": var_def["lower_bound"]
                })
            
            if "upper_bound" in var_def:
                constraints_def.append({
                    "type": "inequality_leq",
                    "expression": {"variable": name},
                    "bound": var_def["upper_bound"]
                })
        
        # Create objective
        obj_type = objective_def.get("type", "minimize")
        obj_expr = self._create_expression(objective_def.get("expression", {}), variables)
        
        if obj_type.lower() == "minimize":
            objective = cp.Minimize(obj_expr)
        else:
            objective = cp.Maximize(obj_expr)
        
        # Create constraints
        constraints = []
        for constraint_def in constraints_def:
            constraint = self._create_constraint(constraint_def, variables)
            if constraint is not None:
                constraints.append(constraint)
        
        # Create problem
        problem = cp.Problem(objective, constraints)
        
        return problem, variables
    
    def _create_expression(self, expr_def: Dict[str, Any], variables: Dict[str, cp.Variable]) -> cp.Expression:
        """
        Create a CVXPY expression from a definition.
        
        Args:
            expr_def: Expression definition
            variables: Dictionary of variables
            
        Returns:
            CVXPY expression
        """
        # Handle different expression types
        expr_type = expr_def.get("type", "variable")
        
        if expr_type == "variable":
            # Direct variable reference
            var_name = expr_def.get("variable", None)
            if var_name in variables:
                return variables[var_name]
            else:
                raise ValueError(f"Variable not found: {var_name}")
        
        elif expr_type == "constant":
            # Constant value
            return expr_def.get("value", 0)
        
        elif expr_type == "linear":
            # Linear combination: sum(coeff * var)
            coeffs = expr_def.get("coefficients", [])
            var_names = expr_def.get("variables", [])
            
            if len(coeffs) != len(var_names):
                raise ValueError("Coefficients and variables must have the same length")
            
            terms = [coeffs[i] * variables[name] for i, name in enumerate(var_names)]
            return sum(terms)
        
        elif expr_type == "quadratic":
            # Quadratic form
            terms = []
            
            for term in expr_def.get("terms", []):
                coeff = term.get("coefficient", 1.0)
                var1_name = term.get("var1")
                var2_name = term.get("var2")
                
                if var1_name in variables and var2_name in variables:
                    terms.append(coeff * variables[var1_name] * variables[var2_name])
            
            return sum(terms)
        
        elif expr_type == "sum":
            # Sum of expressions
            exprs = [self._create_expression(e, variables) for e in expr_def.get("expressions", [])]
            return sum(exprs)
        
        elif expr_type == "norm":
            # Vector norm
            var_name = expr_def.get("variable")
            p = expr_def.get("p", 2)  # Default to L2 norm
            if var_name in variables:
                return cp.norm(variables[var_name], p)
            else:
                raise ValueError(f"Variable not found: {var_name}")
        
        else:
            raise ValueError(f"Unsupported expression type: {expr_type}")
    
    def _create_constraint(self, constraint_def: Dict[str, Any], variables: Dict[str, cp.Variable]) -> Optional[cp.constraints.Constraint]:
        """
        Create a CVXPY constraint from a definition.
        
        Args:
            constraint_def: Constraint definition
            variables: Dictionary of variables
            
        Returns:
            CVXPY constraint or None if invalid
        """
        constraint_type = constraint_def.get("type", "equality")
        
        # Handle expressions in different formats
        if "expression" in constraint_def:
            # Expression object format
            expr = self._create_expression(constraint_def["expression"], variables)
            bound = constraint_def.get("bound", 0)
            
            if constraint_type == "equality" or constraint_type == "eq":
                return expr == bound
            elif constraint_type == "inequality_leq" or constraint_type == "leq":
                return expr <= bound
            elif constraint_type == "inequality_geq" or constraint_type == "geq":
                return expr >= bound
        
        elif "left_expression" in constraint_def and "right_expression" in constraint_def:
            # Two-sided expression format
            left_expr = self._create_expression(constraint_def["left_expression"], variables)
            right_expr = self._create_expression(constraint_def["right_expression"], variables)
            
            if constraint_type == "equality" or constraint_type == "eq":
                return left_expr == right_expr
            elif constraint_type == "inequality_leq" or constraint_type == "leq":
                return left_expr <= right_expr
            elif constraint_type == "inequality_geq" or constraint_type == "geq":
                return left_expr >= right_expr
        
        logger.warning(f"Invalid constraint definition: {constraint_def}")
        return None
    
    def _solve_problem(self, problem: cp.Problem) -> Any:
        """
        Solve a CVXPY problem.
        
        Args:
            problem: CVXPY problem
            
        Returns:
            Solver result
        """
        # Configure solver options
        solver = self.config.get("solver")
        verbose = self.config.get("verbose", False)
        
        # Set solver-specific parameters
        solver_opts = {
            "max_iters": self.config.get("max_iters"),
            "abstol": self.config.get("abstol"),
            "reltol": self.config.get("reltol"),
            "verbose": verbose
        }
        
        # Solve the problem
        return problem.solve(solver=solver, verbose=verbose, **solver_opts)
    
    def _extract_solution(self, variables: Dict[str, cp.Variable], problem: cp.Problem) -> Dict[str, Any]:
        """
        Extract solution values from solved problem.
        
        Args:
            variables: Dictionary of variables
            problem: Solved CVXPY problem
            
        Returns:
            Dictionary of variable values
        """
        solution = {}
        
        if problem.status in ["optimal", "optimal_inaccurate"]:
            for name, var in variables.items():
                if var.value is not None:
                    # Convert numpy arrays to lists for JSON serialization
                    if isinstance(var.value, np.ndarray):
                        if var.value.size == 1:
                            # For scalars, extract the value
                            solution[name] = float(var.value.item())
                        else:
                            # For arrays, convert to nested lists
                            solution[name] = var.value.tolist()
                    else:
                        # For other types
                        solution[name] = var.value
        
        return solution

# Register this solver with the registry
solver_registry.register_solver(
    solver_id="cvxpy_optimization",
    solver_class=CVXPYOptimizationSolver,
    capabilities={
        "problem_types": ["convex", "linear", "quadratic", "semidefinite", "geometric"],
        "variable_types": ["continuous", "integer", "binary", "complex"],
        "max_variables": 50000,
        "max_constraints": 50000,
        "algorithms": ["interior-point", "SOCP", "SDP", "ADMM", "SCS"],
        "performance_profile": {
            "speed": 0.8,
            "robustness": 0.9,
            "memory_efficiency": 0.7
        }
    }
)
