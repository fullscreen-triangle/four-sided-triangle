# Core Component

The core directory contains the central processing logic and model implementation for the Four-Sided Triangle application.

## Files

### model.py
Contains the `SprintLLM` class which handles:
- Loading and management of the domain expert LLM
- Query processing and response generation
- Anthropometric metrics calculation
- Utility functions for prompt formatting and response extraction

Key functions:
- `load_model()`: Loads the sprint-llm-distilled model and tokenizer
- `generate_response()`: Generates responses to user queries
- `calculate_anthropometric_metrics()`: Calculates metrics based on user parameters
- `get_model_instance()`: Factory function to get a model instance

### modeler.py
Contains the `Modeler` class which acts as a bridge between query processing and solving:
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

## Subdirectories

### stages/
Contains the processing pipeline stages for the application:
- `stage0_query_processor`: Initial query processing and intent classification
- `stage1_semantic_atdb`: Semantic analysis and throttle detection

Each stage represents a distinct step in the application's processing pipeline, enhancing modularity and maintainability. 