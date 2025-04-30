# Query Processor Stage (Stage 0)

This directory contains the query processing components that handle the initial processing of user queries before they are passed to the semantic analysis and solver stages.

## Components

### query_processor_service.py
The main service orchestrating the query processing pipeline. It handles:
- Initialization of dependencies
- Coordinating the flow through all processing stages
- Tracking metrics and metadata
- Returning structured query packages

### preprocessing.py
Handles the initial cleaning and normalization of raw query text:
- Removing unnecessary whitespace and special characters
- Standardizing text formatting
- Extracting key phrases and terms
- Preparing the query for further processing

### intent_classifier.py
Classifies the query's intent to determine appropriate processing paths:
- Identifying query type (informational, computational, comparison, etc.)
- Determining domain relevance
- Assessing complexity
- Providing confidence scores for classification decisions

### query_validator.py
Validates that the query meets requirements for further processing:
- Checking for required parameters
- Ensuring domain relevance
- Confirming query completeness
- Identifying potential issues or ambiguities

### context_manager.py
Enriches queries with relevant contextual information:
- Incorporating user history and preferences
- Adding domain-specific knowledge
- Resolving references and ambiguities
- Enhancing query with additional relevant information

### query_packager.py
Structures the processed query into a standardized format for subsequent stages:
- Organizing query elements and metadata
- Formatting for compatibility with downstream components
- Including validation results and confidence scores
- Preparing the final query package

## Process Flow

1. Raw query text is received
2. Query is preprocessed for standardization
3. Intent is classified to determine processing path
4. Context is incorporated to enrich the query
5. Query is validated against requirements
6. Query is packaged into a structured format
7. Structured query package is passed to the next stage 