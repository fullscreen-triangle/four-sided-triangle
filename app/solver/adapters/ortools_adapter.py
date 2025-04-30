"""
Google OR-Tools Adapter for the Four-Sided Triangle system.

This module provides adapters for Google OR-Tools optimization solvers, allowing
the system to leverage OR-Tools for combinatorial optimization problems.
"""

from typing import Dict, Any, List, Optional, Callable, Tuple
import logging
import time

try:
    from ortools.linear_solver import pywraplp
    from ortools.constraint_solver import routing_enums_pb2
    from ortools.constraint_solver import pywrapcp
    from ortools.sat.python import cp_model
except ImportError:
    raise ImportError("Google OR-Tools is required for this adapter. Install with 'pip install ortools'")

from app.solver.registry import solver_registry

logger = logging.getLogger(__name__)

class ORToolsMIPSolver:
    """
    Adapter for Google OR-Tools Mixed Integer Programming (MIP) solver.
    
    This class adapts OR-Tools MIP solver to the Four-Sided Triangle
    solver interface, supporting MIP and LP problems.
    """
    
    def __init__(self):
        """Initialize the OR-Tools MIP solver adapter."""
        self.config = {
            "solver_type": "CBC",  # Default solver
            "time_limit_seconds": 60,
            "verbose": False,
            "num_threads": 4,
            "presolve": True
        }
        logger.info("OR-Tools MIP Solver initialized")
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the solver with specific parameters.
        
        Args:
            config: Configuration parameters
        """
        if config:
            self.config.update(config)
        logger.info(f"OR-Tools MIP Solver configured with {self.config}")
    
    def solve(self, problem_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve a MIP or LP problem using OR-Tools.
        
        Args:
            problem_definition: Complete problem definition
            
        Returns:
            Dictionary containing solution and metadata
        """
        start_time = time.time()
        
        try:
            # Extract problem components
            problem_type = problem_definition.get("metadata", {}).get("problem_type", "mixed_integer")
            
            # Check if we can handle this problem type
            if problem_type not in ["linear", "integer_linear", "mixed_integer"]:
                raise ValueError(f"OR-Tools MIP solver cannot handle problem type: {problem_type}")
            
            # Create the solver
            solver = self._create_solver()
            
            # Build the model
            model, variables = self._build_model(solver, problem_definition)
            
            # Solve the model
            solution, status, stats = self._solve_model(solver, variables)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Prepare solution object
            result = {
                "status": "success" if status == "optimal" else "failed",
                "variables": solution,
                "objective_value": solver.Objective().Value() if status == "optimal" else None,
                "execution_time_seconds": execution_time,
                "message": status,
                "solver_details": {
                    "name": "ortools_mip",
                    "solver_type": self.config["solver_type"],
                    "iterations": stats.get("iterations", 0),
                    "nodes": stats.get("nodes", 0),
                    "best_bound": stats.get("best_bound", None)
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"OR-Tools MIP optimization failed: {str(e)}")
            
            # Return error information
            return {
                "status": "error",
                "message": str(e),
                "solver_details": {
                    "name": "ortools_mip",
                    "error_type": type(e).__name__
                }
            }
    
    def _create_solver(self) -> pywraplp.Solver:
        """
        Create an OR-Tools solver instance.
        
        Returns:
            OR-Tools Solver instance
        """
        solver_type = self.config["solver_type"]
        
        if solver_type == "GLOP":
            # Linear programming solver
            solver = pywraplp.Solver.CreateSolver("GLOP")
        elif solver_type == "CBC":
            # MIP solver - CBC
            solver = pywraplp.Solver.CreateSolver("CBC")
        elif solver_type == "SCIP":
            # MIP solver - SCIP
            solver = pywraplp.Solver.CreateSolver("SCIP")
        elif solver_type == "GUROBI":
            # Gurobi (if available)
            solver = pywraplp.Solver.CreateSolver("GUROBI")
        elif solver_type == "CPLEX":
            # CPLEX (if available)
            solver = pywraplp.Solver.CreateSolver("CPLEX")
        else:
            # Default to CBC
            solver = pywraplp.Solver.CreateSolver("CBC")
        
        if not solver:
            raise ValueError(f"OR-Tools solver {solver_type} is not available")
        
        return solver
    
    def _build_model(self, solver: pywraplp.Solver, problem_definition: Dict[str, Any]) -> Tuple[Any, Dict[str, Any]]:
        """
        Build a MIP/LP model in OR-Tools.
        
        Args:
            solver: OR-Tools solver instance
            problem_definition: Problem definition
            
        Returns:
            Tuple of (model, variables_dict)
        """
        # Extract problem components
        objective_def = problem_definition.get("objective", {})
        constraints_def = problem_definition.get("constraints", [])
        variables_def = problem_definition.get("variables", [])
        
        # Create variables
        variables = {}
        for i, var_def in enumerate(variables_def):
            name = var_def.get("name", f"x{i}")
            lb = var_def.get("lower_bound", 0)
            ub = var_def.get("upper_bound", solver.infinity())
            
            var_type = var_def.get("type", "continuous")
            if var_type == "integer":
                variables[name] = solver.IntVar(lb, ub, name)
            elif var_type == "binary":
                variables[name] = solver.BoolVar(name)
            else:
                variables[name] = solver.NumVar(lb, ub, name)
        
        # Set objective
        objective = solver.Objective()
        
        obj_coeffs = objective_def.get("coefficients", [])
        obj_vars = objective_def.get("variables", [])
        
        if len(obj_coeffs) == len(obj_vars):
            for i, var_name in enumerate(obj_vars):
                if var_name in variables:
                    objective.SetCoefficient(variables[var_name], obj_coeffs[i])
        
        # Set objective sense
        obj_sense = objective_def.get("sense", "minimize")
        if obj_sense.lower() == "minimize":
            objective.SetMinimization()
        else:
            objective.SetMaximization()
        
        # Add constraints
        for i, constraint_def in enumerate(constraints_def):
            name = constraint_def.get("name", f"constraint{i}")
            constraint_type = constraint_def.get("type", "leq")
            rhs = constraint_def.get("rhs", 0)
            
            coeffs = constraint_def.get("coefficients", [])
            var_names = constraint_def.get("variables", [])
            
            if len(coeffs) == len(var_names):
                # Create constraint
                constraint = solver.Constraint(-solver.infinity(), solver.infinity(), name)
                
                # Set coefficients
                for j, var_name in enumerate(var_names):
                    if var_name in variables:
                        constraint.SetCoefficient(variables[var_name], coeffs[j])
                
                # Set bounds based on constraint type
                if constraint_type == "eq" or constraint_type == "equality":
                    constraint.SetBounds(rhs, rhs)
                elif constraint_type == "leq" or constraint_type == "inequality_leq":
                    constraint.SetUb(rhs)
                elif constraint_type == "geq" or constraint_type == "inequality_geq":
                    constraint.SetLb(rhs)
                else:
                    raise ValueError(f"Unsupported constraint type: {constraint_type}")
        
        # Set solver parameters
        solver.SetTimeLimit(int(self.config["time_limit_seconds"] * 1000))  # Convert to milliseconds
        solver.SetNumThreads(self.config["num_threads"])
        
        if self.config["presolve"]:
            solver.EnableOutput()
        
        return solver, variables
    
    def _solve_model(self, solver: pywraplp.Solver, variables: Dict[str, Any]) -> Tuple[Dict[str, Any], str, Dict[str, Any]]:
        """
        Solve the model and extract results.
        
        Args:
            solver: OR-Tools solver instance
            variables: Dictionary of variables
            
        Returns:
            Tuple of (solution_dict, status_string, stats_dict)
        """
        # Solve the model
        status = solver.Solve()
        
        # Process status
        status_str = self._get_status_string(status)
        
        # Extract solution
        solution = {}
        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            for name, var in variables.items():
                solution[name] = var.solution_value()
        
        # Collect statistics
        stats = {
            "iterations": solver.iterations(),
            "nodes": solver.nodes(),
            "best_bound": solver.BestObjectiveBound() if hasattr(solver, "BestObjectiveBound") else None
        }
        
        return solution, status_str, stats
    
    def _get_status_string(self, status: int) -> str:
        """
        Convert OR-Tools status code to string.
        
        Args:
            status: Status code
            
        Returns:
            Status string
        """
        if status == pywraplp.Solver.OPTIMAL:
            return "optimal"
        elif status == pywraplp.Solver.FEASIBLE:
            return "feasible"
        elif status == pywraplp.Solver.INFEASIBLE:
            return "infeasible"
        elif status == pywraplp.Solver.UNBOUNDED:
            return "unbounded"
        elif status == pywraplp.Solver.ABNORMAL:
            return "abnormal"
        elif status == pywraplp.Solver.NOT_SOLVED:
            return "not_solved"
        else:
            return f"unknown_status_{status}"


class ORToolsCPSolver:
    """
    Adapter for Google OR-Tools Constraint Programming solver.
    
    This class adapts OR-Tools CP-SAT solver to the Four-Sided Triangle
    solver interface, supporting constraint satisfaction problems.
    """
    
    def __init__(self):
        """Initialize the OR-Tools CP solver adapter."""
        self.config = {
            "time_limit_seconds": 60,
            "num_search_workers": 8,
            "log_search_progress": False
        }
        logger.info("OR-Tools CP Solver initialized")
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the solver with specific parameters.
        
        Args:
            config: Configuration parameters
        """
        if config:
            self.config.update(config)
        logger.info(f"OR-Tools CP Solver configured with {self.config}")
    
    def solve(self, problem_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve a constraint satisfaction problem using OR-Tools CP-SAT.
        
        Args:
            problem_definition: Complete problem definition
            
        Returns:
            Dictionary containing solution and metadata
        """
        start_time = time.time()
        
        try:
            # Create model and solver
            model = cp_model.CpModel()
            
            # Build the model
            variables = self._build_model(model, problem_definition)
            
            # Create solver
            solver = cp_model.CpSolver()
            self._configure_solver(solver)
            
            # Solve the model
            status = solver.Solve(model)
            
            # Extract solution
            solution, status_str = self._extract_solution(solver, variables, status)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Prepare solution object
            result = {
                "status": "success" if status in [cp_model.OPTIMAL, cp_model.FEASIBLE] else "failed",
                "variables": solution,
                "objective_value": int(solver.ObjectiveValue()) if hasattr(solver, "ObjectiveValue") else None,
                "execution_time_seconds": execution_time,
                "message": status_str,
                "solver_details": {
                    "name": "ortools_cp",
                    "solver_type": "CP-SAT",
                    "branches": solver.NumBranches(),
                    "conflicts": solver.NumConflicts(),
                    "walltime": solver.WallTime()
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"OR-Tools CP optimization failed: {str(e)}")
            
            # Return error information
            return {
                "status": "error",
                "message": str(e),
                "solver_details": {
                    "name": "ortools_cp",
                    "error_type": type(e).__name__
                }
            }
    
    def _build_model(self, model: cp_model.CpModel, problem_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build a CP model in OR-Tools.
        
        Args:
            model: CP model instance
            problem_definition: Problem definition
            
        Returns:
            Dictionary of variables
        """
        # Extract problem components
        objective_def = problem_definition.get("objective", {})
        constraints_def = problem_definition.get("constraints", [])
        variables_def = problem_definition.get("variables", [])
        
        # Create variables
        variables = {}
        for i, var_def in enumerate(variables_def):
            name = var_def.get("name", f"x{i}")
            lb = var_def.get("lower_bound", 0)
            ub = var_def.get("upper_bound", 100)  # Default upper bound for CP
            
            var_type = var_def.get("type", "integer")
            if var_type == "binary":
                variables[name] = model.NewBoolVar(name)
            else:
                # All CP-SAT variables are integers
                variables[name] = model.NewIntVar(lb, ub, name)
        
        # Add constraints
        for i, constraint_def in enumerate(constraints_def):
            constraint_type = constraint_def.get("type", "")
            
            # Process linear constraints
            if constraint_type in ["linear_eq", "linear_leq", "linear_geq"]:
                coeffs = constraint_def.get("coefficients", [])
                var_names = constraint_def.get("variables", [])
                rhs = constraint_def.get("rhs", 0)
                
                if len(coeffs) == len(var_names):
                    terms = [coeffs[j] * variables[var_name] for j, var_name in enumerate(var_names) if var_name in variables]
                    
                    if constraint_type == "linear_eq" or constraint_type == "eq":
                        model.Add(sum(terms) == rhs)
                    elif constraint_type == "linear_leq" or constraint_type == "leq":
                        model.Add(sum(terms) <= rhs)
                    elif constraint_type == "linear_geq" or constraint_type == "geq":
                        model.Add(sum(terms) >= rhs)
            
            # Process all-different constraint
            elif constraint_type == "all_different":
                var_names = constraint_def.get("variables", [])
                model.AddAllDifferent([variables[name] for name in var_names if name in variables])
            
            # Process table constraint
            elif constraint_type == "table":
                var_names = constraint_def.get("variables", [])
                table = constraint_def.get("table", [])
                model.AddAllowedAssignments([variables[name] for name in var_names if name in variables], table)
            
            # Process circuit constraint
            elif constraint_type == "circuit":
                var_names = constraint_def.get("variables", [])
                model.AddCircuit([variables[name] for name in var_names if name in variables])
        
        # Add objective if provided
        if "sense" in objective_def and "expression" in objective_def:
            obj_expr = self._create_objective_expression(model, objective_def, variables)
            
            if objective_def["sense"].lower() == "minimize":
                model.Minimize(obj_expr)
            else:
                model.Maximize(obj_expr)
        
        return variables
    
    def _create_objective_expression(self, model: cp_model.CpModel, objective_def: Dict[str, Any], variables: Dict[str, Any]) -> Any:
        """
        Create an objective expression for the CP model.
        
        Args:
            model: CP model
            objective_def: Objective definition
            variables: Dictionary of variables
            
        Returns:
            CP-SAT linear expression
        """
        expr_type = objective_def.get("expression", {}).get("type", "linear")
        
        if expr_type == "linear":
            # Linear objective: sum(coeff * var)
            coeffs = objective_def["expression"].get("coefficients", [])
            var_names = objective_def["expression"].get("variables", [])
            
            terms = []
            for i, name in enumerate(var_names):
                if name in variables:
                    terms.append(coeffs[i] * variables[name])
            
            return sum(terms)
        
        elif expr_type == "max":
            # Maximum of expressions
            var_names = objective_def["expression"].get("variables", [])
            return model.NewIntVar(0, 1000000, "obj_var")  # This is simplified - real implementation needs more work
        
        else:
            raise ValueError(f"Unsupported objective expression type: {expr_type}")
    
    def _configure_solver(self, solver: cp_model.CpSolver) -> None:
        """
        Configure the CP-SAT solver.
        
        Args:
            solver: CP-SAT solver
        """
        solver.parameters.max_time_in_seconds = self.config["time_limit_seconds"]
        solver.parameters.num_search_workers = self.config["num_search_workers"]
        solver.parameters.log_search_progress = self.config["log_search_progress"]
    
    def _extract_solution(self, solver: cp_model.CpSolver, variables: Dict[str, Any], status: int) -> Tuple[Dict[str, Any], str]:
        """
        Extract solution from the CP solver.
        
        Args:
            solver: CP-SAT solver
            variables: Dictionary of variables
            status: Solution status
            
        Returns:
            Tuple of (solution_dict, status_string)
        """
        solution = {}
        
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            for name, var in variables.items():
                solution[name] = int(solver.Value(var))
        
        status_str = self._get_status_string(status)
        
        return solution, status_str
    
    def _get_status_string(self, status: int) -> str:
        """
        Convert CP-SAT status code to string.
        
        Args:
            status: Status code
            
        Returns:
            Status string
        """
        if status == cp_model.OPTIMAL:
            return "optimal"
        elif status == cp_model.FEASIBLE:
            return "feasible"
        elif status == cp_model.INFEASIBLE:
            return "infeasible"
        elif status == cp_model.MODEL_INVALID:
            return "model_invalid"
        elif status == cp_model.UNKNOWN:
            return "unknown"
        else:
            return f"unknown_status_{status}"


# Register MIP solver with the registry
solver_registry.register_solver(
    solver_id="ortools_mip",
    solver_class=ORToolsMIPSolver,
    capabilities={
        "problem_types": ["linear", "integer_linear", "mixed_integer"],
        "variable_types": ["continuous", "integer", "binary"],
        "max_variables": 1000000,
        "max_constraints": 1000000,
        "algorithms": ["simplex", "branch-and-cut"],
        "performance_profile": {
            "speed": 0.8,
            "robustness": 0.9,
            "memory_efficiency": 0.8
        }
    }
)

# Register CP solver with the registry
solver_registry.register_solver(
    solver_id="ortools_cp",
    solver_class=ORToolsCPSolver,
    capabilities={
        "problem_types": ["constraint_satisfaction", "integer_programming"],
        "variable_types": ["integer", "binary"],
        "max_variables": 100000,
        "max_constraints": 100000,
        "algorithms": ["cp-sat", "constraint_programming"],
        "performance_profile": {
            "speed": 0.9,
            "robustness": 0.8,
            "memory_efficiency": 0.7
        }
    }
)
