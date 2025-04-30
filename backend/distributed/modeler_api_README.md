# RAG Modeler API

This module provides a FastAPI-based backend service for processing and modeling data in Retrieval-Augmented Generation (RAG) systems. It integrates with the distributed computing framework to parallelize modeling tasks and provide scalable performance.

## Architecture

The Modeler API follows a multi-stage pipeline architecture that transforms natural language queries into structured knowledge models:

1. **Entity Extraction**: Identifies domain-relevant objects, concepts, and actors from queries
2. **Relationship Mapping**: Determines connections between entities (causal, correlative, hierarchical)
3. **Parameter Identification**: Extracts measurable attributes relevant to the query
4. **Model Integration**: Synthesizes entities, relationships, and parameters into a coherent model
5. **Model Validation**: Verifies the model against domain knowledge and constraints

## Key Components

- **FastAPI Application**: Provides REST endpoints for each modeling stage
- **Distributed Tasks**: Long-running model processing tasks run in the distributed compute framework
- **Pydantic Models**: Enforce strong typing and validation for requests/responses
- **LLM Integration**: Uses domain-specialized large language models for processing

## API Endpoints

### Entity Extraction

```
POST /api/modeler/entities
```

Extracts domain-relevant entities from a query text.

**Request:**
```json
{
  "query": "How does muscle fiber composition affect sprint performance?",
  "context": {
    "modeling_context": "sports_science"
  },
  "options": {
    "detailed_attributes": true,
    "confidence_threshold": 0.6
  }
}
```

**Response:**
```json
{
  "entities": [
    {
      "id": "entity_1",
      "name": "muscle fiber composition",
      "type": "physiological_property",
      "description": "Distribution of different muscle fiber types within muscles",
      "attributes": ["fast-twitch", "slow-twitch", "type I", "type II"],
      "confidence": 0.95
    },
    {
      "id": "entity_2",
      "name": "sprint performance",
      "type": "performance_metric",
      "description": "Measure of ability in short distance high-speed running",
      "attributes": ["speed", "acceleration", "power output"],
      "confidence": 0.92
    }
  ],
  "processing_time": 0.456
}
```

### Relationship Mapping

```
POST /api/modeler/relationships
```

Maps relationships between entities.

**Request:**
```json
{
  "entities": [
    {
      "id": "entity_1",
      "name": "muscle fiber composition",
      "type": "physiological_property",
      "description": "Distribution of different muscle fiber types within muscles",
      "attributes": ["fast-twitch", "slow-twitch", "type I", "type II"],
      "confidence": 0.95
    },
    {
      "id": "entity_2",
      "name": "sprint performance",
      "type": "performance_metric",
      "description": "Measure of ability in short distance high-speed running",
      "attributes": ["speed", "acceleration", "power output"],
      "confidence": 0.92
    }
  ],
  "query": "How does muscle fiber composition affect sprint performance?",
  "options": {
    "include_indirect": true,
    "min_confidence": 0.7
  }
}
```

**Response:**
```json
{
  "relationships": [
    {
      "id": "relationship_1",
      "source_entity_id": "entity_1",
      "target_entity_id": "entity_2",
      "type": "causal",
      "description": "Muscle fiber composition affects sprint performance",
      "strength": 0.85,
      "direction": "one_way",
      "confidence": 0.88
    }
  ],
  "processing_time": 0.345
}
```

### Parameter Identification

```
POST /api/modeler/parameters
```

Identifies parameters for the model.

**Request:**
```json
{
  "query": "How does muscle fiber composition affect sprint performance?",
  "entities": [...],
  "relationships": [...],
  "options": {
    "include_derived": true,
    "include_domain_specific": true
  }
}
```

**Response:**
```json
{
  "parameters": [
    {
      "id": "parameter_1",
      "name": "fast_twitch_percentage",
      "description": "Percentage of fast-twitch muscle fibers in key sprint muscles",
      "data_type": "numeric",
      "unit": "%",
      "range": {
        "min": 0,
        "max": 100
      },
      "related_entity_ids": ["entity_1"],
      "formula": null,
      "confidence": 0.89
    },
    {
      "id": "parameter_2",
      "name": "sprint_time",
      "description": "Time to complete a 100m sprint",
      "data_type": "numeric",
      "unit": "s",
      "range": {
        "min": 9,
        "max": 15
      },
      "related_entity_ids": ["entity_2"],
      "formula": null,
      "confidence": 0.92
    }
  ],
  "processing_time": 0.422
}
```

### Model Integration

```
POST /api/modeler/integrate
```

Integrates model components into a complete model.

**Request:**
```json
{
  "model_data": {
    "query": "How does muscle fiber composition affect sprint performance?",
    "entities": [...],
    "relationships": [...],
    "parameters": [...]
  },
  "options": {
    "validate": true,
    "enrich_with_domain_knowledge": true
  }
}
```

**Response:**
```json
{
  "integrated_model": {
    "id": "model_1",
    "query": "How does muscle fiber composition affect sprint performance?",
    "entities": [...],
    "relationships": [...],
    "parameters": [...],
    "domain_context": {
      "domain": "sports_science",
      "subdomain": "sprint_physiology",
      "constraints": [
        "Analysis assumes healthy adult athletes",
        "Genetic factors may introduce individual variation"
      ],
      "assumptions": [
        "Sprint events are primarily anaerobic",
        "Fast-twitch fibers provide greater power output"
      ]
    },
    "metadata": {
      "created_at": "2023-05-15T14:22:33.456Z",
      "updated_at": "2023-05-15T14:22:33.456Z",
      "version": "1.0.0",
      "confidence_score": 0.87
    }
  },
  "processing_time": 0.876
}
```

### Model Validation

```
POST /api/modeler/validate
```

Validates a model against domain knowledge and constraints.

**Request:**
```json
{
  "model": {
    "id": "model_1",
    "query": "How does muscle fiber composition affect sprint performance?",
    "entities": [...],
    "relationships": [...],
    "parameters": [...],
    "domain_context": {...},
    "metadata": {...}
  },
  "validation_level": "detailed"
}
```

**Response:**
```json
{
  "validation_results": {
    "valid": true,
    "issues": [],
    "warnings": [
      "Model does not account for training adaptations"
    ],
    "suggestions": [
      "Consider adding 'training history' as an entity",
      "Include relationship between muscle fiber recruitment and fatigue"
    ],
    "confidence_scores": {
      "overall": 0.88,
      "entities": 0.92,
      "relationships": 0.85,
      "parameters": 0.86
    }
  },
  "processing_time": 0.543
}
```

### Full Model Processing

```
POST /api/modeler/process
```

Processes a complete model workflow from query to validated model.

**Request:**
```json
{
  "query": "How does muscle fiber composition affect sprint performance?",
  "options": {
    "context": {
      "user_expertise": "novice",
      "domain_focus": "sports_science"
    },
    "include_visualization": true,
    "validation_level": "detailed"
  }
}
```

**Response:**
```json
{
  "model": {
    "id": "model_1",
    "query": "How does muscle fiber composition affect sprint performance?",
    "entities": [...],
    "relationships": [...],
    "parameters": [...],
    "domain_context": {...},
    "metadata": {...},
    "visualization": {
      "graph_data": {...},
      "chart_data": {...}
    }
  },
  "validation_results": {...},
  "processing_time": 2.345
}
```

## Getting Started

### Prerequisites

- Python 3.8+
- FastAPI
- Uvicorn
- Ray or Dask for distributed computing
- Environment variables:
  - `OPENAI_API_KEY`: API key for OpenAI
  - `ANTHROPIC_API_KEY`: (Optional) API key for Anthropic Claude models
  - `CUSTOM_MODEL_API_URL`: (Optional) URL for custom model API

### Installation

1. Install requirements:
```bash
pip install fastapi uvicorn pydantic python-dotenv ray[default] openai anthropic
```

2. Set up environment variables in a `.env` file:
```
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

### Running the Server

Run the server using the provided script:

```bash
python backend/run_modeler_api.py --reload --port 8000
```

Or directly with Uvicorn:

```bash
uvicorn backend.distributed.modeler_api:app --reload --host 0.0.0.0 --port 8000
```

## Integration with Frontend

The frontend integrates with this API through the `modeler-backend.service.ts` service, which provides methods that correspond to each API endpoint. The service handles API requests, error handling, and data transformation.

## Scaling Considerations

- The API is designed to work with the distributed computing framework for horizontal scaling
- Long-running tasks are executed asynchronously in the cluster
- Implement rate limiting and authentication for production use
- Consider implementing a caching layer for frequently requested models 