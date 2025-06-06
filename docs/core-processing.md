---
layout: default
title: Core Processing
nav_order: 5
---

# Core Processing

The core processing component contains the central processing logic and model implementation for the Four-Sided Triangle application.

## Components

### Model Implementation (`model.py`)

The `SprintLLM` class handles the core model functionality:

- Loading and management of the domain expert LLM
- Query processing and response generation
- Anthropometric metrics calculation
- Utility functions for prompt formatting and response extraction

Key functions:
- `load_model()`: Loads the sprint-llm-distilled model and tokenizer
- `generate_response()`: Generates responses to user queries
- `calculate_anthropometric_metrics()`: Calculates metrics based on user parameters
- `get_model_instance()`: Factory function to get a model instance

### Modeler (`modeler.py`)

The `Modeler` class acts as a bridge between query processing and solving:

- Transforms unstructured queries into structured entity-relationship models
- Extracts entities, relationships, parameters, and constraints
- Enriches models with domain knowledge
- Integrates components into unified knowledge models

Key functions:
- `process_query()`: Processes query packages into knowledge models
- `_extract_model_components()`: Extracts structured data from queries
- `_enrich_with_domain_knowledge()`: Adds domain-specific context
- `_integrate_model_components()`: Creates unified knowledge models
- `get_modeler_instance()`: Factory function to get a modeler instance

## Processing Pipeline

The core processing is organized into distinct stages, each handling a specific aspect of query processing:

### Stage 0: Query Processing
- Initial query analysis
- Intent classification
- Parameter extraction
- Query validation

### Stage 1: Semantic ATDB
- Semantic analysis
- Throttle detection
- Behavioral pattern recognition
- Performance optimization

Each stage is designed to be modular and maintainable, allowing for easy updates and improvements to individual components without affecting the entire pipeline. 