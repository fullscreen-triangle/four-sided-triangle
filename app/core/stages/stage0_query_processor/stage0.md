# Stage 0: Query Processor

The Query Processor is the first stage in the Four-Sided Triangle pipeline, responsible for the initial processing, enrichment, and structuring of user queries. This stage prepares the query for all subsequent stages and determines the optimal processing path through the pipeline.

## Architectural Overview

### Components

The Query Processor stage consists of several specialized components:

1. **Query Processor Service**
   - Central coordinator for the query processing workflow
   - Manages the sequence of processing steps
   - Aggregates metrics and metadata
   - Interfaces with the orchestration layer

2. **Preprocessing Module**
   - Handles text normalization and cleaning
   - Removes extraneous characters and formatting
   - Standardizes text representation
   - Extracts initial key terms and entities

3. **Intent Classifier**
   - Determines query type and domain
   - Classifies queries into categories (informational, computational, etc.)
   - Assesses query complexity
   - Provides confidence scores for classifications

4. **Context Manager**
   - Enriches queries with contextual information
   - Incorporates user history and preferences
   - Resolves ambiguous references
   - Adds domain-specific context when relevant

5. **Query Validator**
   - Ensures queries meet processing requirements
   - Identifies incomplete or malformed queries
   - Validates domain relevance
   - Flags potential issues for handling

6. **Query Packager**
   - Creates structured query representations
   - Formats query data for downstream stages
   - Incorporates metadata and processing outputs
   - Ensures compatibility with the pipeline format

### Integration with Orchestrator

The `QueryProcessorStage` class provides the integration point with the orchestrator:

- Implements the `AbstractPipelineStage` interface
- Manages lifecycle of the Query Processor service
- Handles asynchronous processing and error management
- Provides refinement capabilities for invalid queries

## Processing Flow

1. **Query Reception**
   - Raw text query is received from user
   - Session and request metadata is collected
   - Initial logging and tracking begins

2. **Preprocessing**
   - Query is cleaned and normalized
   - Standardized formatting is applied
   - Initial structural analysis is performed
   - Key terms are identified and normalized

3. **Intent Classification**
   - Query intent is determined (informational, computational, etc.)
   - Domain relevance is assessed
   - Complexity is evaluated
   - Confidence scores are assigned

4. **Context Incorporation**
   - User history is analyzed for relevance
   - User preferences are applied
   - Domain context is incorporated
   - Ambiguous references are resolved

5. **Query Validation**
   - Completeness and well-formedness are verified
   - Required parameters are checked
   - Domain appropriateness is confirmed
   - Potential issues are identified

6. **Query Packaging**
   - Structured representation is created
   - Metadata and processing results are incorporated
   - Query elements are organized in standard format
   - Final package is prepared for subsequent stages

## Output Format

The Query Processor produces a structured query package containing:

```json
{
  "query_text": "Original normalized query text",
  "query_type": "informational|computational|comparison|etc",
  "entities": [
    {
      "name": "Entity name",
      "type": "Entity type",
      "relevance": 0.95
    }
  ],
  "parameters": [
    {
      "name": "Parameter name",
      "value": "Parameter value",
      "required": true
    }
  ],
  "relationships": [
    {
      "source": "Source entity",
      "target": "Target entity",
      "type": "Relationship type"
    }
  ],
  "constraints": [
    {
      "type": "Constraint type",
      "value": "Constraint value"
    }
  ],
  "metadata": {
    "processing_time": {
      "preprocessing": 0.05,
      "intent_classification": 0.12,
      "context_incorporation": 0.08,
      "validation": 0.03,
      "packaging": 0.07
    },
    "confidence_scores": {
      "intent": 0.92,
      "domain": 0.87
    },
    "validation_details": {
      "is_valid": true,
      "issues": []
    }
  }
}
```

## Usage by Downstream Stages

The structured output from the Query Processor is used by subsequent stages to:

1. **Determine Pipeline Path**
   - The orchestrator uses `query_type` to select appropriate pipeline sequence
   - Specialized processing paths may be chosen based on classification

2. **Semantic Analysis Guidance**
   - The Semantic ATDB stage uses entity and relationship information
   - Intent classification informs analysis priority and depth

3. **Domain Knowledge Retrieval**
   - Identified entities guide knowledge retrieval processes
   - Relationships inform knowledge graph navigation

4. **Reasoning Pattern Selection**
   - Query type and complexity determine reasoning strategies
   - Constraints guide reasoning boundaries

## Error Handling and Refinement

When query validation fails:

1. The stage returns a validation failure response with detailed issues
2. The orchestrator can request refinement with specific guidance
3. The stage attempts to address validation issues through refinement
4. If refinement succeeds, processing continues; otherwise, an error is returned

## Metrics and Monitoring

The stage collects detailed metrics on:

- Processing times for each sub-component
- Confidence scores for classifications
- Validation success rates
- Refinement frequencies and success rates

These metrics are used for monitoring performance, identifying improvement areas, and optimizing the processing flow.
