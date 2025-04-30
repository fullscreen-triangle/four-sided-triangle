"""
Solver Adapters Package for the Four-Sided Triangle system.

This package contains adapters for various optimization solvers that are
used by the Four-Sided Triangle system to solve different types of problems.
"""

from app.solver.adapters.base_adapter import BaseSolverAdapter
from app.solver.adapters.cvxpy_adapter import CVXPYOptimizationSolver
from app.solver.adapters.pulp_adapter import PuLPOptimizationSolver
from app.solver.adapters.scipy_adapter import ScipyOptimizationSolver
from app.solver.adapters.ortools_adapter import ORToolsOptimizationSolver
from app.solver.adapters.custom_adapter import CustomOptimizationSolver

# Export all adapter classes
__all__ = [
    'BaseSolverAdapter',
    'CVXPYOptimizationSolver',
    'PuLPOptimizationSolver',
    'ScipyOptimizationSolver',
    'ORToolsOptimizationSolver',
    'CustomOptimizationSolver'
]

import logging
import importlib.util
import sys

logger = logging.getLogger(__name__)

def load_adapters():
    """
    Load all solver adapters dynamically.
    
    This function attempts to import all adapter modules and register their
    solvers with the global registry.
    """
    adapter_modules = [
        "scipy_adapter",
        "pulp_adapter",
        "cvxpy_adapter",
        "ortools_adapter",
        "custom_adapter"
    ]
    
    successful_imports = 0
    
    for module_name in adapter_modules:
        try:
            # Construct the full module path
            full_module_name = f"app.solver.adapters.{module_name}"
            
            # Try to import the module
            if importlib.util.find_spec(full_module_name):
                importlib.import_module(full_module_name)
                successful_imports += 1
                logger.info(f"Successfully loaded solver adapter: {module_name}")
            else:
                logger.warning(f"Could not find solver adapter module: {module_name}")
        
        except ImportError as e:
            # Some adapters might have dependencies that aren't installed
            # We'll log this but continue attempting to load other adapters
            logger.warning(f"Could not import solver adapter {module_name}: {str(e)}")
        
        except Exception as e:
            # Log any other errors during adapter loading
            logger.error(f"Error loading solver adapter {module_name}: {str(e)}")
    
    logger.info(f"Loaded {successful_imports} out of {len(adapter_modules)} solver adapters")

# Automatically load all adapters when the package is imported
load_adapters()
