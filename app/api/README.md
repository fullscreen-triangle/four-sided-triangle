# API Endpoints

This directory contains the FastAPI endpoints and route definitions for the Four-Sided Triangle application.

## Files

### endpoints.py
Contains the main API router and endpoint definitions:

#### Core Endpoints
- `GET /`: Root endpoint to check if the API is running
- `GET /health`: Health check endpoint for monitoring application status

#### Query Endpoints
- `POST /api/query`: Process a domain expert query through the model
- `POST /api/query/process`: Process a query through the query processing stage

#### Metrics Endpoints
- `POST /api/metrics`: Calculate anthropometric metrics
- `POST /api/metrics/formatted`: Calculate and format anthropometric metrics for display

#### Modeler Endpoints
- `POST /api/modeler`: Process a query through the modeler component

### Dependencies
The endpoints.py file manages several important application dependencies:
- Model initialization and access via dependency injection
- Query processor service initialization and access
- Error handling through decorators
- Request validation and processing

## Router Structure
The API implements multiple routers for different functional areas:
- `router`: Main API router for general endpoints
- `query_router`: Specialized router for query processing endpoints

## Error Handling
API endpoints implement comprehensive error handling:
- Input validation using Pydantic models
- Try-except blocks with standardized error responses
- HTTP exception handling with appropriate status codes
- Logging for troubleshooting and monitoring

## Authentication
The API is designed for extension with authentication mechanisms as needed.

## Performance
Performance metrics are recorded for all API calls:
- Processing time
- Model usage statistics
- Response generation metrics 