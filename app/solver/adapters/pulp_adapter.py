"""
PuLP Optimization Adapter for the Four-Sided Triangle system.

This module provides adapters for PuLP's linear programming solver, allowing
the system to leverage PuLP for various linear optimization problems.
"""

from typing import Dict, Any, List, Optional, Callable, Tuple
import logging
import time

try:
    import pulp
except ImportError:
    raise ImportError("PuLP is required for this adapter. Install with 'pip install pulp'")

from app.solver.registry import solver_registry

logger = logging.getLogger(__name__)

class PuLPOptimizationSolver:
    """
    Adapter for PuLP linear programming solver.
    
    This class adapts PuLP's linear programming functions to the Four-Sided
    Triangle solver interface, supporting various linear problems.
    """
    
    def __init__(self):
        """Initialize the PuLP optimization adapter."""
        self.config = {
            "timeLimit": 120,  # 2 minutes
            "verbose": False,
            "solver": None,  # Default solver
            "mip_gap": 0.01   # 1% optimality gap for MIP
        }
        logger.info("PuLP Optimization Solver initialized")
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the solver with specific parameters.
        
        Args:
            config: Configuration parameters
        """
        if config:
            self.config.update(config)
        logger.info(f"PuLP Optimizer configured with {self.config}")
    
    def solve(self, problem_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve an optimization problem using PuLP.
        
        Args:
            problem_definition: Complete problem definition
            
        Returns:
            Dictionary containing solution and metadata
        """
        start_time = time.time()
        
        try:
            # Extract problem components
            problem_type = problem_definition.get("metadata", {}).get("problem_type", "linear")
            
            # Check if we can handle this problem type
            if problem_type not in ["linear", "integer_linear", "mixed_integer"]:
                raise ValueError(f"PuLP cannot handle problem type: {problem_type}")
            
            # Create the PuLP model
            model = self._create_model(problem_definition)
            
            # Solve the model
            status, solution = self._solve_model(model)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Prepare solution object
            result = {
                "status": "success" if status == pulp.LpStatusOptimal else "failed",
                "variables": solution,
                "objective_value": model.objective.value() if status == pulp.LpStatusOptimal else None,
                "execution_time_seconds": execution_time,
                "message": self._get_status_message(status),
                "solver_details": {
                    "name": "pulp",
                    "status_code": status,
                    "solver_used": str(model.solver)
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"PuLP optimization failed: {str(e)}")
            
            # Return error information
            return {
                "status": "error",
                "message": str(e),
                "solver_details": {
                    "name": "pulp",
                    "error_type": type(e).__name__
                }
            }
    
    def _create_model(self, problem_definition: Dict[str, Any]) -> pulp.LpProblem:
        """
        Create a PuLP model from the problem definition.
        
        Args:
            problem_definition: Problem definition
            
        Returns:
            PuLP model
        """
        # Extract model components
        objective = problem_definition.get("objective", {})
        constraints = problem_definition.get("constraints", [])
        variables_def = problem_definition.get("variables", [])
        
        # Determine objective sense
        sense = objective.get("sense", "minimize")
        if sense.lower() == "minimize":
            prob_sense = pulp.LpMinimize
        else:
            prob_sense = pulp.LpMaximize
        
        # Create problem
        prob = pulp.LpProblem("OptimizationProblem", prob_sense)
        
        # Create variables
        variables = {}
        for i, var_def in enumerate(variables_def):
            name = var_def.get("name", f"x{i}")
            lower_bound = var_def.get("lower_bound", 0)
            upper_bound = var_def.get("upper_bound", None)
            
            var_type = var_def.get("type", "continuous")
            if var_type == "integer":
                var_cat = pulp.LpInteger
            elif var_type == "binary":
                var_cat = pulp.LpBinary
                lower_bound = 0
                upper_bound = 1
            else:
                var_cat = pulp.LpContinuous
            
            variables[name] = pulp.LpVariable(
                name, 
                lowBound=lower_bound, 
                upBound=upper_bound,
                cat=var_cat
            )
        
        # Create objective function
        obj_coeffs = objective.get("coefficients", [])
        obj_vars = objective.get("variables", [])
        
        if len(obj_coeffs) == len(obj_vars):
            # Create expression: sum(coeff * var)
            obj_expr = pulp.lpSum(obj_coeffs[i] * variables[var_name] 
                                  for i, var_name in enumerate(obj_vars))
            prob += obj_expr
        else:
            raise ValueError("Objective coefficients and variables must have the same length")
        
        # Add constraints
        for i, constraint in enumerate(constraints):
            name = constraint.get("name", f"constraint{i}")
            constraint_type = constraint.get("type", "leq")
            rhs = constraint.get("rhs", 0)
            
            coeffs = constraint.get("coefficients", [])
            vars_names = constraint.get("variables", [])
            
            if len(coeffs) == len(vars_names):
                # Create expression: sum(coeff * var)
                expr = pulp.lpSum(coeffs[i] * variables[var_name] 
                                 for i, var_name in enumerate(vars_names))
                
                # Add constraint based on type
                if constraint_type == "eq" or constraint_type == "equality":
                    prob += (expr == rhs, name)
                elif constraint_type == "leq" or constraint_type == "inequality_leq":
                    prob += (expr <= rhs, name)
                elif constraint_type == "geq" or constraint_type == "inequality_geq":
                    prob += (expr >= rhs, name)
                else:
                    raise ValueError(f"Unsupported constraint type: {constraint_type}")
            else:
                raise ValueError("Constraint coefficients and variables must have the same length")
        
        return prob
    
    def _solve_model(self, model: pulp.LpProblem) -> Tuple[int, Dict[str, Any]]:
        """
        Solve the PuLP model.
        
        Args:
            model: PuLP model
            
        Returns:
            Tuple of (status, solution_dict)
        """
        # Select solver
        solver = self.config.get("solver")
        if solver == "GLPK":
            solver = pulp.GLPK(msg=self.config["verbose"], timeLimit=self.config["timeLimit"])
        elif solver == "CPLEX":
            solver = pulp.CPLEX(msg=self.config["verbose"], timeLimit=self.config["timeLimit"])
        elif solver == "GUROBI":
            solver = pulp.GUROBI(msg=self.config["verbose"], timeLimit=self.config["timeLimit"])
        elif solver == "CBC":
            solver = pulp.PULP_CBC_CMD(msg=self.config["verbose"], timeLimit=self.config["timeLimit"])
        else:
            # Default to CBC
            solver = pulp.PULP_CBC_CMD(msg=self.config["verbose"], timeLimit=self.config["timeLimit"])
        
        # Solve the model
        status = model.solve(solver)
        
        # Extract solution
        solution = {}
        if status == pulp.LpStatusOptimal:
            for var in model.variables():
                solution[var.name] = var.value()
        
        return status, solution
    
    def _get_status_message(self, status: int) -> str:
        """
        Convert PuLP status code to human-readable message.
        
        Args:
            status: PuLP status code
            
        Returns:
            Human-readable status message
        """
        status_messages = {
            pulp.LpStatusOptimal: "Optimal solution found",
            pulp.LpStatusNotSolved: "Not solved",
            pulp.LpStatusInfeasible: "Problem is infeasible",
            pulp.LpStatusUnbounded: "Problem is unbounded",
            pulp.LpStatusUndefined: "Status undefined"
        }
        
        return status_messages.get(status, f"Unknown status: {status}")

# Register this solver with the registry
solver_registry.register_solver(
    solver_id="pulp_optimization",
    solver_class=PuLPOptimizationSolver,
    capabilities={
        "problem_types": ["linear", "integer_linear", "mixed_integer"],
        "variable_types": ["continuous", "integer", "binary"],
        "max_variables": 100000,
        "max_constraints": 100000,
        "algorithms": ["simplex", "branch-and-bound", "branch-and-cut"],
        "performance_profile": {
            "speed": 0.7,
            "robustness": 0.8,
            "memory_efficiency": 0.8
        }
    }
)
