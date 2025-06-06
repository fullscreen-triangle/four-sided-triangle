import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Model settings
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(BASE_DIR, "models"))

# API settings
API_PORT = 8000
API_HOST = "0.0.0.0"

# FastAPI configuration
APP_TITLE = "Four Sided Triangle: Domain Expert Query System"
APP_DESCRIPTION = """
A specialized API for the Four Sided Triangle system, providing domain expert knowledge in sprint running.
This system implements a recursive optimization approach to domain-expert knowledge extraction.
"""
APP_VERSION = "1.0.0"

# Query settings
MAX_QUERY_LENGTH = 1000
MODEL_TEMPERATURE = 0.2
MODEL_TOP_P = 0.9
MAX_TOKENS = 1500 