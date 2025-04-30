"""
Four-Sided Triangle - Error Handling Module

This module defines custom exceptions and error handling utilities
for consistent error management across the application.
"""

from typing import Optional, Dict, Any, List

class TriangleBaseError(Exception):
    """Base exception class for all Four-Sided Triangle errors."""
    
    def __init__(self, message: str, error_code: str = "GENERAL_ERROR", details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the exception to a dictionary representation."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


# Configuration errors
class ConfigurationError(TriangleBaseError):
    """Raised when there's an issue with application configuration."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFIG_ERROR", details)


# Pipeline and orchestration errors
class PipelineError(TriangleBaseError):
    """Base class for errors related to the pipeline processing."""
    pass


class StageRegistrationError(PipelineError):
    """Raised when there's an error registering a pipeline stage."""
    def __init__(self, message: str, stage_id: str, details: Optional[Dict[str, Any]] = None):
        stage_details = details or {}
        stage_details["stage_id"] = stage_id
        super().__init__(message, "STAGE_REGISTRATION_ERROR", stage_details)


class StageExecutionError(PipelineError):
    """Raised when a pipeline stage fails to execute."""
    def __init__(self, message: str, stage_id: str, details: Optional[Dict[str, Any]] = None):
        stage_details = details or {}
        stage_details["stage_id"] = stage_id
        super().__init__(message, "STAGE_EXECUTION_ERROR", stage_details)


# Data and validation errors
class ValidationError(TriangleBaseError):
    """Raised when data validation fails."""
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        validation_details = details or {}
        if field:
            validation_details["field"] = field
        super().__init__(message, "VALIDATION_ERROR", validation_details)


class DataError(TriangleBaseError):
    """Raised when there's an issue with data processing or transformation."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "DATA_ERROR", details)


# Solver and model errors
class SolverError(TriangleBaseError):
    """Base class for solver-related errors."""
    pass


class ModelError(TriangleBaseError):
    """Base class for model and inference errors."""
    def __init__(self, message: str, model_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        model_details = details or {}
        if model_id:
            model_details["model_id"] = model_id
        super().__init__(message, "MODEL_ERROR", model_details)


# External service errors
class ServiceUnavailableError(TriangleBaseError):
    """Raised when an external service is unavailable."""
    def __init__(self, message: str, service_name: str, details: Optional[Dict[str, Any]] = None):
        service_details = details or {}
        service_details["service_name"] = service_name
        super().__init__(message, "SERVICE_UNAVAILABLE", service_details)


class APIError(TriangleBaseError):
    """Raised when there's an error communicating with an external API."""
    def __init__(self, message: str, api_name: str, status_code: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        api_details = details or {}
        api_details["api_name"] = api_name
        if status_code:
            api_details["status_code"] = status_code
        super().__init__(message, "API_ERROR", api_details)


# Resource errors
class ResourceNotFoundError(TriangleBaseError):
    """Raised when a requested resource cannot be found."""
    def __init__(self, message: str, resource_type: str, resource_id: str, details: Optional[Dict[str, Any]] = None):
        resource_details = details or {}
        resource_details["resource_type"] = resource_type
        resource_details["resource_id"] = resource_id
        super().__init__(message, "RESOURCE_NOT_FOUND", resource_details)


# Utility functions for error handling
def format_error_response(error: Exception) -> Dict[str, Any]:
    """Format an exception into a consistent error response structure."""
    if isinstance(error, TriangleBaseError):
        return error.to_dict()
    
    # Handle non-custom exceptions
    return {
        "error_code": "SYSTEM_ERROR",
        "message": str(error),
        "details": {"exception_type": error.__class__.__name__}
    } 