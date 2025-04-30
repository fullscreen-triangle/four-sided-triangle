"""
Custom Optimization Adapter for the Four-Sided Triangle system.

This module provides a framework for custom optimization algorithms and
heuristic methods that aren't available in standard libraries.
"""

from typing import Dict, Any, List, Optional, Callable, Tuple
import logging
import time
import random
import math

from app.solver.registry import solver_registry

logger = logging.getLogger(__name__)

class CustomOptimizationSolver:
    """
    Adapter for custom optimization algorithms.
    
    This class provides implementations of specialized algorithms
    like simulated annealing, genetic algorithms, and other heuristic
    methods not available in standard optimization libraries.
    """
    
    def __init__(self):
        """Initialize the custom optimization adapter."""
        self.config = {
            "algorithm": "simulated_annealing",  # Default algorithm
            "max_iterations": 1000,
            "timeout_seconds": 60,
            "random_seed": None
        }
        logger.info("Custom Optimization Solver initialized")
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the solver with specific parameters.
        
        Args:
            config: Configuration parameters
        """
        if config:
            self.config.update(config)
            
            # Set random seed if provided
            if self.config["random_seed"] is not None:
                random.seed(self.config["random_seed"])
                
        logger.info(f"Custom Optimizer configured with {self.config}")
    
    def solve(self, problem_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve an optimization problem using custom algorithms.
        
        Args:
            problem_definition: Complete problem definition
            
        Returns:
            Dictionary containing solution and metadata
        """
        start_time = time.time()
        
        try:
            # Select algorithm based on configuration
            algorithm = self.config["algorithm"].lower()
            
            # Route to appropriate algorithm implementation
            if algorithm == "simulated_annealing":
                solution, objective_value, iterations = self._simulated_annealing(problem_definition)
            elif algorithm == "genetic_algorithm":
                solution, objective_value, iterations = self._genetic_algorithm(problem_definition)
            elif algorithm == "particle_swarm":
                solution, objective_value, iterations = self._particle_swarm(problem_definition)
            elif algorithm == "tabu_search":
                solution, objective_value, iterations = self._tabu_search(problem_definition)
            else:
                raise ValueError(f"Unknown algorithm: {algorithm}")
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Prepare solution object
            result = {
                "status": "success",
                "variables": solution,
                "objective_value": objective_value,
                "execution_time_seconds": execution_time,
                "message": f"Solution found using {algorithm}",
                "solver_details": {
                    "name": "custom_optimization",
                    "algorithm": algorithm,
                    "iterations": iterations
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Custom optimization failed: {str(e)}")
            
            # Return error information
            return {
                "status": "error",
                "message": str(e),
                "solver_details": {
                    "name": "custom_optimization",
                    "error_type": type(e).__name__
                }
            }
    
    def _simulated_annealing(self, problem_definition: Dict[str, Any]) -> Tuple[Dict[str, Any], float, int]:
        """
        Simulated annealing optimization algorithm.
        
        Args:
            problem_definition: Problem definition
            
        Returns:
            Tuple of (solution_dict, objective_value, iterations)
        """
        # Extract problem components
        initial_solution = self._create_initial_solution(problem_definition)
        objective_function = self._create_objective_function(problem_definition)
        
        # Algorithm parameters
        max_iterations = self.config["max_iterations"]
        initial_temperature = 100.0
        cooling_rate = 0.95
        
        # Initialize
        current_solution = initial_solution.copy()
        current_objective = objective_function(current_solution)
        best_solution = current_solution.copy()
        best_objective = current_objective
        
        temperature = initial_temperature
        iteration = 0
        
        start_time = time.time()
        timeout = self.config["timeout_seconds"]
        
        # Main loop
        while iteration < max_iterations and time.time() - start_time < timeout:
            # Generate neighboring solution
            neighbor = self._generate_neighbor(current_solution, problem_definition)
            
            # Evaluate neighbor
            neighbor_objective = objective_function(neighbor)
            
            # Determine if we should accept the neighbor
            delta = neighbor_objective - current_objective
            accept_probability = 1.0 if delta < 0 else math.exp(-delta / temperature)
            
            if random.random() < accept_probability:
                current_solution = neighbor
                current_objective = neighbor_objective
                
                # Update best solution if needed
                if current_objective < best_objective:
                    best_solution = current_solution.copy()
                    best_objective = current_objective
            
            # Cool down
            temperature *= cooling_rate
            iteration += 1
            
            # Early stopping if temperature is very low
            if temperature < 0.01:
                break
        
        logger.info(f"Simulated annealing completed after {iteration} iterations")
        return best_solution, best_objective, iteration
    
    def _genetic_algorithm(self, problem_definition: Dict[str, Any]) -> Tuple[Dict[str, Any], float, int]:
        """
        Genetic algorithm optimization.
        
        Args:
            problem_definition: Problem definition
            
        Returns:
            Tuple of (solution_dict, objective_value, iterations)
        """
        # Extract problem components
        objective_function = self._create_objective_function(problem_definition)
        
        # Algorithm parameters
        population_size = 50
        max_iterations = self.config["max_iterations"]
        mutation_rate = 0.1
        crossover_rate = 0.8
        
        # Initialize population
        population = [self._create_initial_solution(problem_definition) for _ in range(population_size)]
        
        # Main loop
        iteration = 0
        start_time = time.time()
        timeout = self.config["timeout_seconds"]
        
        while iteration < max_iterations and time.time() - start_time < timeout:
            # Evaluate fitness
            fitness = [1.0 / (1.0 + objective_function(p)) for p in population]
            total_fitness = sum(fitness)
            
            if total_fitness == 0:
                relative_fitness = [1.0 / len(fitness)] * len(fitness)
            else:
                relative_fitness = [f / total_fitness for f in fitness]
            
            # Select parents
            parents = []
            for _ in range(population_size // 2):
                parent1 = self._select_individual(population, relative_fitness)
                parent2 = self._select_individual(population, relative_fitness)
                parents.append((parent1, parent2))
            
            # Create next generation
            next_generation = []
            for parent1, parent2 in parents:
                if random.random() < crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2)
                else:
                    child1, child2 = parent1.copy(), parent2.copy()
                
                if random.random() < mutation_rate:
                    child1 = self._mutate(child1, problem_definition)
                if random.random() < mutation_rate:
                    child2 = self._mutate(child2, problem_definition)
                
                next_generation.extend([child1, child2])
            
            # Replace population
            population = next_generation
            iteration += 1
        
        # Find best solution
        best_index = 0
        best_objective = objective_function(population[0])
        
        for i in range(1, len(population)):
            obj = objective_function(population[i])
            if obj < best_objective:
                best_objective = obj
                best_index = i
        
        logger.info(f"Genetic algorithm completed after {iteration} iterations")
        return population[best_index], best_objective, iteration
    
    def _particle_swarm(self, problem_definition: Dict[str, Any]) -> Tuple[Dict[str, Any], float, int]:
        """
        Particle Swarm Optimization (PSO).
        
        Args:
            problem_definition: Problem definition
            
        Returns:
            Tuple of (solution_dict, objective_value, iterations)
        """
        # Extract problem components
        objective_function = self._create_objective_function(problem_definition)
        
        # Algorithm parameters
        swarm_size = 30
        max_iterations = self.config["max_iterations"]
        w = 0.7  # Inertia weight
        c1 = 1.5  # Cognitive coefficient
        c2 = 1.5  # Social coefficient
        
        # Initialize particles
        particles = [self._create_initial_solution(problem_definition) for _ in range(swarm_size)]
        velocities = [{k: 0.0 for k in p} for p in particles]
        
        # Initialize personal and global best
        personal_best = particles.copy()
        personal_best_values = [objective_function(p) for p in particles]
        
        global_best_index = min(range(swarm_size), key=lambda i: personal_best_values[i])
        global_best = personal_best[global_best_index].copy()
        global_best_value = personal_best_values[global_best_index]
        
        # Main loop
        iteration = 0
        start_time = time.time()
        timeout = self.config["timeout_seconds"]
        
        while iteration < max_iterations and time.time() - start_time < timeout:
            for i in range(swarm_size):
                particle = particles[i]
                velocity = velocities[i]
                
                # Update velocity and position
                for key in particle:
                    # Update velocity
                    r1, r2 = random.random(), random.random()
                    cognitive = c1 * r1 * (personal_best[i][key] - particle[key])
                    social = c2 * r2 * (global_best[key] - particle[key])
                    velocity[key] = w * velocity[key] + cognitive + social
                    
                    # Update position
                    particle[key] += velocity[key]
                
                # Apply constraints
                self._apply_constraints(particle, problem_definition)
                
                # Update personal best
                value = objective_function(particle)
                if value < personal_best_values[i]:
                    personal_best[i] = particle.copy()
                    personal_best_values[i] = value
                    
                    # Update global best
                    if value < global_best_value:
                        global_best = particle.copy()
                        global_best_value = value
            
            iteration += 1
        
        logger.info(f"Particle swarm optimization completed after {iteration} iterations")
        return global_best, global_best_value, iteration
    
    def _tabu_search(self, problem_definition: Dict[str, Any]) -> Tuple[Dict[str, Any], float, int]:
        """
        Tabu Search optimization algorithm.
        
        Args:
            problem_definition: Problem definition
            
        Returns:
            Tuple of (solution_dict, objective_value, iterations)
        """
        # Extract problem components
        initial_solution = self._create_initial_solution(problem_definition)
        objective_function = self._create_objective_function(problem_definition)
        
        # Algorithm parameters
        max_iterations = self.config["max_iterations"]
        tabu_tenure = 10  # How long moves stay in the tabu list
        
        # Initialize
        current_solution = initial_solution.copy()
        current_objective = objective_function(current_solution)
        best_solution = current_solution.copy()
        best_objective = current_objective
        
        tabu_list = []
        iteration = 0
        
        start_time = time.time()
        timeout = self.config["timeout_seconds"]
        
        # Main loop
        while iteration < max_iterations and time.time() - start_time < timeout:
            # Generate neighbors
            neighbors = self._generate_neighbors(current_solution, problem_definition)
            
            # Filter out neighbors in tabu list
            valid_neighbors = [n for n in neighbors if self._hash_solution(n) not in tabu_list]
            
            if not valid_neighbors and neighbors:
                # If all moves are tabu but we have neighbors, use aspiration criteria
                valid_neighbors = neighbors
            
            if not valid_neighbors:
                # No valid moves, terminate
                break
            
            # Find best non-tabu neighbor
            best_neighbor = None
            best_neighbor_objective = float('inf')
            
            for neighbor in valid_neighbors:
                neighbor_objective = objective_function(neighbor)
                
                if neighbor_objective < best_neighbor_objective:
                    best_neighbor = neighbor
                    best_neighbor_objective = neighbor_objective
            
            # Update current solution
            current_solution = best_neighbor
            current_objective = best_neighbor_objective
            
            # Add to tabu list
            tabu_list.append(self._hash_solution(current_solution))
            if len(tabu_list) > tabu_tenure:
                tabu_list.pop(0)
            
            # Update best solution if needed
            if current_objective < best_objective:
                best_solution = current_solution.copy()
                best_objective = current_objective
            
            iteration += 1
        
        logger.info(f"Tabu search completed after {iteration} iterations")
        return best_solution, best_objective, iteration
    
    def _create_initial_solution(self, problem_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an initial solution for the problem.
        
        Args:
            problem_definition: Problem definition
            
        Returns:
            Initial solution dictionary
        """
        solution = {}
        variables_def = problem_definition.get("variables", [])
        
        for var_def in variables_def:
            name = var_def.get("name", "")
            var_type = var_def.get("type", "continuous")
            lb = var_def.get("lower_bound", 0.0)
            ub = var_def.get("upper_bound", 1.0)
            
            if var_type == "integer":
                solution[name] = random.randint(int(lb), int(ub))
            elif var_type == "binary":
                solution[name] = random.choice([0, 1])
            else:
                solution[name] = lb + random.random() * (ub - lb)
        
        return solution
    
    def _create_objective_function(self, problem_definition: Dict[str, Any]) -> Callable[[Dict[str, Any]], float]:
        """
        Create an objective function from the problem definition.
        
        Args:
            problem_definition: Problem definition
            
        Returns:
            Objective function that takes a solution and returns a value
        """
        objective_def = problem_definition.get("objective", {})
        
        if "function" in objective_def:
            # Use provided function if available
            return objective_def["function"]
        else:
            # Create simple function based on coefficients
            coeffs = objective_def.get("coefficients", [])
            vars_names = objective_def.get("variables", [])
            
            def objective_function(solution: Dict[str, Any]) -> float:
                if len(coeffs) != len(vars_names):
                    return float('inf')
                
                # Compute linear combination
                value = 0.0
                for i, name in enumerate(vars_names):
                    if name in solution:
                        value += coeffs[i] * solution[name]
                
                return value
            
            return objective_function
    
    def _generate_neighbor(self, solution: Dict[str, Any], problem_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a neighboring solution.
        
        Args:
            solution: Current solution
            problem_definition: Problem definition
            
        Returns:
            Neighboring solution
        """
        neighbor = solution.copy()
        variables_def = problem_definition.get("variables", [])
        
        # Select a random variable to modify
        if variables_def:
            var_def = random.choice(variables_def)
            name = var_def.get("name", "")
            
            if name in neighbor:
                var_type = var_def.get("type", "continuous")
                lb = var_def.get("lower_bound", 0.0)
                ub = var_def.get("upper_bound", 1.0)
                
                if var_type == "integer":
                    # For integers, add or subtract a small random value
                    delta = random.choice([-2, -1, 1, 2])
                    neighbor[name] = max(int(lb), min(int(ub), neighbor[name] + delta))
                elif var_type == "binary":
                    # For binary, flip the value
                    neighbor[name] = 1 - neighbor[name]
                else:
                    # For continuous, add a small random perturbation
                    delta = (ub - lb) * 0.1 * (2 * random.random() - 1)
                    neighbor[name] = max(lb, min(ub, neighbor[name] + delta))
        
        return neighbor
    
    def _generate_neighbors(self, solution: Dict[str, Any], problem_definition: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate multiple neighbors for a solution.
        
        Args:
            solution: Current solution
            problem_definition: Problem definition
            
        Returns:
            List of neighboring solutions
        """
        num_neighbors = 10
        return [self._generate_neighbor(solution, problem_definition) for _ in range(num_neighbors)]
    
    def _apply_constraints(self, solution: Dict[str, Any], problem_definition: Dict[str, Any]) -> None:
        """
        Apply constraints to a solution in-place.
        
        Args:
            solution: Solution to modify
            problem_definition: Problem definition
        """
        variables_def = problem_definition.get("variables", [])
        
        for var_def in variables_def:
            name = var_def.get("name", "")
            
            if name in solution:
                var_type = var_def.get("type", "continuous")
                lb = var_def.get("lower_bound", 0.0)
                ub = var_def.get("upper_bound", 1.0)
                
                if var_type == "integer":
                    solution[name] = max(int(lb), min(int(ub), int(solution[name])))
                elif var_type == "binary":
                    solution[name] = 1 if solution[name] >= 0.5 else 0
                else:
                    solution[name] = max(lb, min(ub, solution[name]))
    
    def _select_individual(self, population: List[Dict[str, Any]], fitness: List[float]) -> Dict[str, Any]:
        """
        Select an individual from the population using roulette wheel selection.
        
        Args:
            population: List of individuals
            fitness: List of fitness values
            
        Returns:
            Selected individual
        """
        # Roulette wheel selection
        r = random.random()
        cumulative = 0.0
        
        for i, f in enumerate(fitness):
            cumulative += f
            if r <= cumulative:
                return population[i].copy()
        
        # Fallback
        return population[-1].copy()
    
    def _crossover(self, parent1: Dict[str, Any], parent2: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Perform crossover between two parents.
        
        Args:
            parent1: First parent
            parent2: Second parent
            
        Returns:
            Tuple of (child1, child2)
        """
        child1 = parent1.copy()
        child2 = parent2.copy()
        
        # Simple crossover: randomly exchange variables
        for key in parent1:
            if key in parent2 and random.random() < 0.5:
                child1[key], child2[key] = child2[key], child1[key]
        
        return child1, child2
    
    def _mutate(self, solution: Dict[str, Any], problem_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mutate a solution.
        
        Args:
            solution: Solution to mutate
            problem_definition: Problem definition
            
        Returns:
            Mutated solution
        """
        # Simple mutation: randomly modify a variable
        return self._generate_neighbor(solution, problem_definition)
    
    def _hash_solution(self, solution: Dict[str, Any]) -> str:
        """
        Create a hash of a solution for tabu list.
        
        Args:
            solution: Solution to hash
            
        Returns:
            String hash of the solution
        """
        # Simple hash: concatenate string representations of values
        return ";".join(f"{k}:{v}" for k, v in sorted(solution.items()))

# Register custom solver with the registry
solver_registry.register_solver(
    solver_id="custom_optimization",
    solver_class=CustomOptimizationSolver,
    capabilities={
        "problem_types": ["nonlinear", "combinatorial", "black_box", "heuristic"],
        "variable_types": ["continuous", "integer", "binary"],
        "max_variables": 1000,
        "max_constraints": 100,
        "algorithms": ["simulated_annealing", "genetic_algorithm", "particle_swarm", "tabu_search"],
        "performance_profile": {
            "speed": 0.6,
            "robustness": 0.7,
            "memory_efficiency": 0.9
        }
    }
)
