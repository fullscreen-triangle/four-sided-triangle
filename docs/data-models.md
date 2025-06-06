---
layout: default
title: Data Models
nav_order: 4
---

# Data Models

This document provides an overview of the data models used in the Four-Sided Triangle RAG (Retrieval-Augmented Generation) system.

## Base Model

The system uses a common `BaseModel` class that all other models inherit from, providing:

- Unique ID generation
- Creation and update timestamps
- Version tracking
- Methods for converting to/from dictionaries
- Cloning functionality

## Document Model

Documents are the primary source of information in the system.

### Key Components:
- `DocumentStatus`: Tracks document processing state (NEW, PROCESSING, PROCESSED, FAILED, ARCHIVED)
- `DocumentType`: Categorizes documents (TEXT, PDF, WEBPAGE, CODE, SPREADSHEET, etc.)
- `DocumentChunk`: Represents portions of documents for efficient processing
- `Document`: Primary class representing a document with:
  - Title, content, and source information
  - Processing metadata
  - Methods for state transitions
  - Chunking functionality for breaking documents into processable pieces

## Query Model

Queries represent user questions or instructions.

### Key Components:
- `QueryIntentType`: Classifies query purpose (INFORMATIONAL, COMPUTATIONAL, COMPARISON, etc.)
- `ParameterType`: Defines data types for query parameters
- `QueryParameter`: Represents parameters extracted from queries
- `QueryIntent`: Captures the classified intent of a query
- `QueryParameters`: Collection of parameters from a query
- `QueryConstraint`: Represents constraints in a query
- `Query`: Primary class representing a user query with:
  - Raw text
  - Extracted parameters
  - Classified intent
  - Constraints and context

## Response Model

Responses are generated answers to user queries.

### Key Components:
- `ResponseType`: Classifies response types (ANSWER, ERROR, CLARIFICATION)
- `ResponseFormat`: Defines output formats (TEXT, HTML, MARKDOWN, etc.)
- `CitationType`: Classifies citation types (DOCUMENT, COMPUTATION, INFERENCE)
- `Citation`: Represents source references
- `ResponseContent`: Contains the main answer content
- `Explanation`: Provides reasoning behind responses
- `ComputationResult`: Contains results of computational queries
- `ResponseFeedback`: Tracks user feedback on responses
- `ResponseMetrics`: Stores evaluation metrics
- `Response`: Primary class representing a system response with:
  - Content and format
  - Citations and explanations
  - Metrics and feedback
  - Methods for response manipulation and formatting
- `ResponseComparison`: Facilitates comparison between multiple responses

## Embedding Model

Embeddings are vector representations of documents and queries.

### Key Components:
- `EmbeddingType`: Classifies embedding types
- `Embedding`: Represents vector embeddings with:
  - Vector data
  - Dimensionality information
  - Source tracking
  - Similarity calculation methods

## Domain Knowledge Model

Domain knowledge represents specialized information about specific domains.

### Key Components:
- `DomainKnowledgeType`: Classifies knowledge types
- `DomainConcept`: Represents concepts within a domain
- `DomainAttribute`: Describes attributes of concepts
- `DomainRelationship`: Defines relationships between concepts
- `DomainKnowledge`: Primary class for domain-specific information

## Working Memory Model

Working memory represents the system's short-term memory during query processing.

### Key Components:
- `MemoryItem`: Represents individual memory items
- `MemoryState`: Tracks the state of memory items
- `WorkingMemory`: Primary class for the system's working memory

## Relationships

- **Documents** are the primary information source
- **Queries** are processed against documents using **Embeddings** for retrieval
- **Domain Knowledge** enhances understanding of specialized topics
- **Working Memory** tracks the query processing state
- **Responses** are generated based on retrieved documents and computation

## Data Flow

1. Documents are ingested, processed, and embedded
2. User submits a query
3. System classifies query intent and extracts parameters
4. Relevant documents are retrieved using embeddings
5. Working memory tracks the processing state
6. Domain knowledge enhances understanding when applicable
7. Response is generated with appropriate citations and explanations 