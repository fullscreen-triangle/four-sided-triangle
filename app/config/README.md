# Configuration

This directory contains configuration settings for the Four-Sided Triangle application.

## Files

### settings.py
Contains environment-dependent application settings that can be overridden through environment variables:
- `MODEL_PATH`: Path to the local or remote model
- `API_PORT`: Port for the FastAPI server
- `API_HOST`: Host address for the server
- `FRONTEND_URL`: URL of the frontend application
- `MAX_QUERY_LENGTH`: Maximum allowed length for user queries
- `MODEL_TEMPERATURE`: Temperature setting for LLM generation
- `MODEL_TOP_P`: Top-p sampling parameter for LLM generation
- `MAX_TOKENS`: Maximum tokens to generate in responses
- `OPENAI_API_KEY`: API key for OpenAI services
- `ANTHROPIC_API_KEY`: API key for Anthropic services

### config.py
Contains fixed application configuration and defaults:
- `BASE_DIR`: Base directory for the application
- `APP_TITLE`: Application title for API documentation
- `APP_DESCRIPTION`: Application description
- `APP_VERSION`: Current version of the API

## Usage

The configuration system is designed to:
1. Load environment variables from a `.env` file in development
2. Use environment variables in production
3. Fall back to sensible defaults when variables are not set

To override settings:
- During development: Modify the `.env` file
- In production: Set environment variables in your deployment environment

Example `.env` file:
```
MODEL_PATH=/path/to/model
MODEL_TEMPERATURE=0.5
MAX_TOKENS=1024
OPENAI_API_KEY=your-api-key
```

The application uses dotenv for environment variable loading and provides centralized access to all configuration parameters throughout the codebase. 