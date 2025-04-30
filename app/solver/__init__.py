"""
Mathematical Solver module for the Four-Sided Triangle system.

This module provides a comprehensive collection of mathematical optimization
capabilities, including a solver registry, dispatcher, and adapters for various
optimization libraries.
"""

import logging

# Setup logging
logger = logging.getLogger(__name__)

# Import core components
from app.solver.registry import SolverRegistry, solver_registry
from app.solver.dispatcher import SolverDispatcher, solver_dispatcher

# Import adapters package to ensure adapters are registered
import app.solver.adapters

# Define public API
__all__ = [
    'SolverRegistry',
    'solver_registry',
    'SolverDispatcher',
    'solver_dispatcher',
    'solve'
]

async def solve(problem_definition, context=None):
    """
    Convenience function to solve an optimization problem.
    
    Args:
        problem_definition: Complete problem definition
        context: Optional additional context for solver selection
        
    Returns:
        Solution dictionary
    """
    return await solver_dispatcher.solve(problem_definition, context)

logger.info("Solver module initialized")
