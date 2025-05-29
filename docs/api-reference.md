---
layout: default
title: API Reference
nav_order: 6
---

# API Reference

The Four-Sided Triangle system exposes a comprehensive RESTful API that provides access to its various capabilities. This document details all available endpoints, their usage, and integration patterns.

## API Overview

The API provides access to three main functional areas:

- **Query Processing**: Process queries through the metacognitive orchestrator pipeline
- **Metrics Calculation**: Calculate domain-specific metrics
- **Modeler Interaction**: Interact with the domain modeling components

## Base URL

All API endpoints are relative to the base URL:

```
http://localhost:8000
```

## Authentication

The API supports various authentication mechanisms that can be configured based on deployment requirements. Contact your system administrator for authentication credentials and configuration.

## Endpoints

### General Endpoints

#### Health Check

```http
GET /health
```

Check the health status of the API service.

**Response**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": 1634567890.123
}
```

### Query Processing

#### Process Full Query

```http
POST /query
```

Process a domain expert query through the complete pipeline, including all stages from query processing to threshold verification.

**Request Body**
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

**Response**
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

#### Process Query Stage

```http
POST /query/process
```

Process a query through the query processing stage only, useful for debugging or when only structured query representation is needed.

**Request Body**
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

**Response**
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

### Metrics Calculation

#### Calculate Metrics

```http
POST /metrics
```

Calculate raw anthropometric metrics based on provided parameters.

**Request Body**
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

**Response**
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

#### Calculate Formatted Metrics

```http
POST /metrics/formatted
```

Calculate metrics with additional formatting and categorization.

**Request Body**
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

**Response**
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

### Domain Modeling

#### Process Model

```http
POST /modeler
```

Process domain modeling tasks using the specialized modeling components.

**Request Body**
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

**Response**
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

The API implements comprehensive error handling with standardized error responses:

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

| Error Code | Description |
|------------|-------------|
| `CONFIG_ERROR` | Configuration-related errors |
| `VALIDATION_ERROR` | Input validation failures |
| `STAGE_EXECUTION_ERROR` | Errors during pipeline stage execution |
| `MODEL_ERROR` | Errors in the domain expert model |
| `SERVICE_UNAVAILABLE` | External service unavailability |
| `API_ERROR` | Errors communicating with external APIs |
| `RESOURCE_NOT_FOUND` | Resource not found errors |
| `SYSTEM_ERROR` | General system errors |

## Performance Monitoring

The API includes built-in performance monitoring:

- Processing time tracking for all endpoints
- Model usage statistics
- Response generation metrics
- Pipeline stage execution metrics

## Integration Guidelines

When integrating with the API:

1. Always check response status codes
2. Implement proper error handling
3. Use appropriate timeout values
4. Monitor response times
5. Cache responses when appropriate
6. Follow rate limiting guidelines 