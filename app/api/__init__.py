"""
API Package

This package contains the FastAPI endpoints and route definitions for the
Four-Sided Triangle application.
"""

from app.api.app import app, create_app

__all__ = ["app", "create_app"] 