# Four-Sided Triangle API Documentation

This document provides comprehensive documentation for the public APIs exposed by the Four-Sided Triangle system.

## API Overview

The Four-Sided Triangle system exposes a RESTful API that provides access to various capabilities:

- **Query Processing**: Process queries through the metacognitive orchestrator pipeline
- **Metrics Calculation**: Calculate domain-specific metrics
- **Modeler Interaction**: Interact with the domain modeling components

## Endpoints

### General Endpoints

#### `GET /`

Root endpoint to check if the API is running.

**Response:**
```json
{
  "status": "active",
  "service": "Four-Sided Triangle API"
}
```

#### `GET /health`

Health check endpoint for monitoring application status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": 1634567890.123
}
```

### Query Endpoints

#### `POST /query/`

Process a domain expert query through the full pipeline.

**Request Body:**
```json
{
  "query": "string",
  "context": {
    "additional_field1": "value1",
    "additional_field2": "value2"
  },
  "options": {
    "option1": "value1",
    "option2": "value2"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "result_field1": "value1",
    "result_field2": "value2"
  },
  "processing_time": 0.123,
  "metadata": {
    "pipeline_stages": ["stage1", "stage2"],
    "query_length": 42
  }
}
```

#### `POST /query/process`

Process a query through the query processing stage only.

**Request Body:**
```json
{
  "query": "string",
  "context": {
    "additional_field1": "value1",
    "additional_field2": "value2"
  },
  "options": {
    "option1": "value1",
    "option2": "value2"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "result_field1": "value1",
    "result_field2": "value2"
  },
  "processing_time": 0.123,
  "metadata": {
    "stage": "query_processor",
    "query_length": 42
  }
}
```

### Metrics Endpoints

#### `POST /metrics/`

Calculate anthropometric metrics.

**Request Body:**
```json
{
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  },
  "options": {
    "option1": "value1",
    "option2": "value2"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "metric1": 42.0,
    "metric2": 3.14
  },
  "processing_time": 0.123,
  "metadata": {
    "model_version": "1.0.0"
  }
}
```

#### `POST /metrics/formatted`

Calculate formatted metrics with additional processing.

**Request Body:**
```json
{
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  },
  "options": {
    "option1": "value1",
    "option2": "value2"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "formatted_metrics": {
      "category1": {
        "metric1": "42.0 units",
        "metric2": "3.14 units"
      }
    }
  },
  "processing_time": 0.123,
  "metadata": {
    "format_version": "1.0.0"
  }
}
```

### Modeler Endpoints

#### `POST /modeler/`

Process domain modeling tasks.

**Request Body:**
```json
{
  "query": "string",
  "context": {
    "additional_field1": "value1",
    "additional_field2": "value2"
  },
  "options": {
    "option1": "value1",
    "option2": "value2"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "model_result": {
      "field1": "value1",
      "field2": "value2"
    }
  },
  "processing_time": 0.123,
  "metadata": {
    "model_type": "domain_expert"
  }
}
```

## Error Handling

All endpoints follow a consistent error handling pattern. When an error occurs, the API returns an appropriate HTTP status code and a JSON object with details about the error:

```json
{
  "error_code": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {
    "field1": "value1",
    "field2": "value2"
  }
}
```

### Common Error Codes

- `CONFIG_ERROR`: Configuration-related errors
- `VALIDATION_ERROR`: Input validation failures
- `STAGE_EXECUTION_ERROR`: Errors during pipeline stage execution
- `MODEL_ERROR`: Errors in the domain expert model
- `SERVICE_UNAVAILABLE`: External service unavailability
- `API_ERROR`: Errors communicating with external APIs
- `RESOURCE_NOT_FOUND`: Resource not found errors
- `SYSTEM_ERROR`: General system errors

## Authentication and Authorization

The API uses API keys for authentication. Include the API key in the `Authorization` header of your requests:

```
Authorization: Bearer YOUR_API_KEY
```

Different API keys have different permission levels, which determine which endpoints can be accessed. 