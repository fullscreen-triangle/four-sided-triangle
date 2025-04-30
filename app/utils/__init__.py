"""
Utility functions package for the Four-Sided Triangle system.

This package contains various utility functions and helpers used throughout
the system, including logging setup, error handling, configuration management,
and other common functionality.
"""

# Import common errors for ease of use
from app.utils.errors import (
    TriangleBaseError,
    ConfigurationError,
    PipelineError,
    ValidationError,
    DataError,
    SolverError,
    ModelError,
    ServiceUnavailableError,
    APIError,
    ResourceNotFoundError,
    format_error_response
) 