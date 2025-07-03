#!/usr/bin/env python
"""
API Runner

This script runs the Four-Sided Triangle API using Uvicorn.
"""

import os
import uvicorn
from app.config.settings import Settings

def main():
    """Run the API server."""
    settings = Settings()
    
    # Configure Uvicorn
    uvicorn_config = {
        "host": settings.api_host,
        "port": settings.api_port,
        "log_level": "debug" if settings.debug else "info",
        "reload": settings.debug
    }
    
    print(f"Starting Four-Sided Triangle API on http://{settings.api_host}:{settings.api_port}")
    print(f"API documentation available at http://{settings.api_host}:{settings.api_port}/docs")
    
    # Run the server
    uvicorn.run("app.api.app:app", **uvicorn_config)

if __name__ == "__main__":
    main() 