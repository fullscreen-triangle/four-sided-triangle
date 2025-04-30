# Four-Sided Triangle: Restructured Architecture

## Executive Summary

This document outlines the restructured architecture for the Four-Sided Triangle system, a sophisticated multi-model optimization pipeline for domain-expert knowledge extraction. The primary goal of this restructuring is to modularize the existing components, implement a metacognitive orchestrator as the central coordination mechanism, and establish clear interfaces between system components. A key enhancement to the original design is the introduction of a hybrid AI-guided optimization approach that intelligently selects between LLM-based reasoning and traditional mathematical solvers, now supported by a specialized model architecture with dependency injection for enhanced flexibility and testability.

## System Overview

The Four-Sided Triangle system employs a novel recursive optimization approach to extract and refine domain-specific knowledge. Instead of using traditional RAG architectures, it utilizes a nested hierarchy of specialized models, treating each language model as a transformation function within a complex optimization space. The enhanced architecture now includes a specialized 8-stage pipeline with dedicated model interfaces at each stage, and a sophisticated solver selection mechanism that dynamically chooses between LLM-based approaches and traditional mathematical optimization solvers based on problem characteristics. The system leverages dependency injection throughout to ensure components are loosely coupled and highly testable.

## Key Architectural Changes

1. **Metacognitive Orchestrator**: Introduction of a central orchestration layer to manage the 8-stage pipeline
2. **Module Independence**: Ensuring each pipeline stage operates as an independent module
3. **Standardized Interfaces**: Defining clear contracts between components
4. **Configuration-Driven Pipeline**: Enabling dynamic pipeline modification via configuration
5. **Hybrid Optimization**: New AI-guided solver selection system that intelligently chooses between LLM-based reasoning and traditional mathematical solvers
6. **Solver Registry**: A comprehensive registry of optimization solvers with capability profiles
7. **Problem Analysis**: Enhanced problem structure analysis to determine optimal solution approach
8. **Dependency Injection**: Implementation of a consistent dependency injection pattern for model management
9. **Specialized Model Architecture**: New 8-stage processing pipeline with dedicated model interfaces

## Specialized Model Architecture

The Four-Sided Triangle system now incorporates a specialized model architecture that uses dependency injection and a stage-based pipeline approach for enhanced flexibility, maintainability, and performance.

### Core Components

#### Dependency Container

The system introduces a central `ModelContainer` that serves as a registry for all model implementations, allowing for:

- Runtime registration and configuration of models
- Different lifecycle scopes (singleton, request-scoped, transient)
- Easy swapping of implementations for testing or optimization
- Centralized configuration management

#### Specialized Model Interfaces

The architecture defines clear contracts for each model type in the 8-stage pipeline:

1. **QueryProcessorInterface**: For processing raw queries into structured form
2. **SemanticATDBInterface**: For semantic transformation and query reranking
3. **DomainKnowledgeInterface**: For extracting domain-specific knowledge
4. **ReasoningInterface**: For mathematical and logical reasoning
5. **SolutionGenerationInterface**: For generating candidate solutions
6. **ResponseScoringInterface**: For scoring solution candidates
7. **EnsembleDiversificationInterface**: For creating diverse solution sets
8. **ThresholdVerificationInterface**: For ensuring solution quality

#### Model Base Implementations

The architecture provides base implementations for common model types:

- **BaseModel**: Core functionality for all models (metrics, configuration, capabilities)
- **HuggingFaceModel**: Specialized for Hugging Face models with lazy loading
- **ModelWithCache**: Mixin for adding caching capabilities to any model

#### Model Pipeline Configuration

The system uses a configuration-driven approach to define the model pipeline:

- JSON-based configuration for model definitions and resource requirements
- Model-to-stage mapping for flexible pipeline composition
- Resource specifications for optimal deployment
- Default model selection for each stage

Example configuration:

```json
{
  "stage_id": "query_processor",
  "description": "Process raw queries into structured form",
  "models": [
    {
      "id": "phi3-mini-query-processor",
      "class": "app.models.query_processor.PhiQueryProcessor",
      "config": {
        "hf_model_name": "microsoft/Phi-3-mini-4k-instruct",
        "use_half_precision": true,
        "max_new_tokens": 512,
        "temperature": 0.1,
        "cache_enabled": true
      },
      "resources": {
        "gpu": 0,
        "vram": 0,
        "cpu_ram": 4,
        "disk": 1
      },
      "default": true
    },
    {
      "id": "mixtral-query-processor",
      "class": "app.models.query_processor.MixtralQueryProcessor",
      "config": {
        "hf_model_name": "mistralai/Mixtral-8x22B-Instruct-v0.1",
        "use_half_precision": true,
        "max_new_tokens": 1024,
        "temperature": 0.2,
        "cache_enabled": true
      },
      "resources": {
        "gpu": 1,
        "vram": 48,
        "cpu_ram": 16,
        "disk": 50
      },
      "default": false
    }
  ]
}
```

### The 8-Stage Processing Pipeline

The specialized architecture implements an 8-stage pipeline for comprehensive query processing:

#### Stage 0: Query Processor
- Transforms raw user queries into structured representations
- Extracts key entities, intents, and constraints
- Uses models like Phi-3-mini for fast processing or Mixtral for complex queries
- Produces structured data for downstream processing

#### Stage 1: Semantic ATDB
- Performs semantic transformation of structured queries
- Reranks multiple transformation strategies when applicable
- Uses models like BGE-Reranker for optimal transformations
- Enhances query with semantic understanding

#### Stage 2: Domain Knowledge Extraction
- Extracts domain-specific knowledge relevant to the query
- Leverages specialized models like BioMedLM for biomechanics knowledge
- Uses LoRA-enhanced domain models with domain-specific fine-tuning
- Produces comprehensive knowledge context

#### Stage 3: Parallel Reasoning
- Applies mathematical and logical reasoning to the problem
- Utilizes models optimized for mathematical operations (Qwen, DeepSeek Math)
- Performs multi-step reasoning with chain-of-thought capabilities
- Generates reasoning paths and intermediary calculations

#### Stage 4: Solution Generation
- Produces candidate solutions based on reasoning results
- Uses multiple models with varying temperatures for diverse candidates
- Applies domain knowledge constraints to solution generation
- Produces multiple candidate solutions for comparison

#### Stage 5: Response Scoring
- Scores candidate solutions using reward models
- Uses models like DeBERTa reward model with human preference training
- Applies Bayesian evaluation framework
- Produces quality metrics for each solution

#### Stage 6: Ensemble Diversification
- Selects a diverse subset of high-quality solutions
- Uses cross-encoder models to compute pairwise diversity
- Applies determinantal point process for optimal selection
- Ensures both quality and diversity in final solutions

#### Stage 7: Threshold Verification
- Verifies solutions against quality thresholds
- Uses entailment models like BART-MNLI to verify logical consistency
- Ensures solutions follow from established domain facts
- Produces final verified solutions

### Specialized Orchestrator

The architecture introduces a `SpecializedOrchestrator` that:

- Coordinates the 8-stage pipeline execution
- Manages timeouts and parallel processing
- Handles error recovery and graceful degradation
- Provides asynchronous processing capabilities
- Collects and centralizes metrics for monitoring

Code Example:

```python
# Process a query through the specialized 8-stage pipeline
orchestrator = SpecializedOrchestrator(config={
    "max_workers": 4,
    "stage_timeouts": {
        "query_processor": 10,  # seconds
        "semantic_atdb": 10,
        "domain_knowledge": 20,
        "reasoning": 30,
        "solution_generation": 45,
        "response_scoring": 15,
        "ensemble_diversification": 15,
        "threshold_verification": 10
    }
})

# Process the query
result = orchestrator.process_query(
    "What is the optimal angle for a sprinter's starting blocks?"
)
```

### Benefits of the Specialized Architecture

1. **Modularity**: Each model can be developed, tested, and replaced independently
2. **Performance**: Optimized resource allocation based on model requirements
3. **Scalability**: Models can be distributed across computing resources
4. **Flexibility**: Easy to add new models or swap implementations
5. **Maintainability**: Clear interfaces and separation of concerns
6. **Testability**: Dependency injection facilitates mocking for tests
7. **Robustness**: Graceful degradation with timeouts and error handling

## Proposed Directory Structure

```four-sided-triangle/
├── app/                          # Main application package
│   ├── orchestrator/             # Metacognitive orchestrator module
│   │   ├── __init__.py
│   │   ├── core.py               # Central orchestration logic
│   │   ├── working_memory.py     # Pipeline state management
│   │   ├── prompt_generator.py   # Dynamic prompt generation
│   │   ├── process_monitor.py    # Output quality monitoring
│   │   ├── interfaces.py         # Stage interface definitions
│   │   ├── specialized_orchestrator.py # NEW: 8-stage specialized orchestrator
│   │   └── solver_learning.py    # NEW: Solver performance tracking and learning
│   │
│   ├── core/                     # Core application logic
│   │   ├── __init__.py
│   │   ├── model.py              # Domain expert LLM handling
│   │   ├── modeler.py            # Query transformation bridge
│   │   └── stages/               # Pipeline stages
│   │       ├── __init__.py       # Stage registration
│   │       ├── stage0_query_processor/  # Initial query processing
│   │       ├── stage1_semantic_atdb/    # Semantic analysis
│   │       ├── stage2_domain_knowledge/ # Domain knowledge extraction
│   │       ├── stage3_reasoning/        # Parallel reasoning optimization
│   │       │   ├── __init__.py
│   │       │   ├── optimizer.py         # Main optimization controller
│   │       │   ├── llm_optimizer.py     # LLM-based optimization
│   │       │   └── problem_analyzer.py  # NEW: Problem structure analysis
│   │       ├── stage4_solution/         # Solution generation
│   │       ├── stage5_scoring/          # Response scoring
│   │       ├── stage6_diversification/  # Ensemble diversification
│   │       └── stage7_verification/     # Threshold verification
│   │
│   ├── models/                   # NEW: Specialized model architecture
│   │   ├── __init__.py
│   │   ├── container.py          # NEW: Dependency injection container
│   │   ├── interfaces.py         # NEW: Model interfaces
│   │   ├── base_models.py        # NEW: Base model implementations
│   │   ├── query_processor.py    # NEW: Query processor models
│   │   ├── factory.py            # NEW: Model factory and registry
│   │   ├── config/               # NEW: Model configuration
│   │   │   └── model_pipeline.py # NEW: Pipeline stage definitions
│   │   └── ... other model implementations ...
│   │
│   ├── api/                      # API endpoints and routing
│   ├── config/                   # Configuration settings
│   │   ├── __init__.py
│   │   ├── settings.py           # General application settings
│   │   └── pipeline/             # Pipeline configuration
│   │       ├── stages.json       # Stage sequence and settings
│   │       ├── orchestrator.json # Orchestrator settings
│   │       └── solvers.json      # NEW: Solver configurations
│   │
│   ├── solver/                   # Mathematical computation
│   │   ├── __init__.py
│   │   ├── registry.py           # NEW: Solver registry system
│   │   ├── dispatcher.py         # NEW: Solver selection and dispatch
│   │   └── adapters/             # NEW: Solver adapters
│   │       ├── __init__.py
│   │       ├── scipy_adapter.py  # Adapter for SciPy optimization
│   │       ├── pulp_adapter.py   # Adapter for PuLP linear programming
│   │       ├── cvxpy_adapter.py  # Adapter for CVXPY convex optimization
│   │       ├── ortools_adapter.py # Adapter for Google OR-Tools
│   │       └── custom_adapter.py # Adapter for custom solvers
│   │
│   ├── interpreter/              # Result interpretation
│   │   ├── __init__.py
│   │   └── solution_interpreter.py # NEW: Interprets solver outputs
│   │
│   ├── utils/                    # Utility functions
│   ├── examples/                 # NEW: Example scripts
│   │   └── specialized_pipeline_example.py # NEW: Demo of specialized pipeline
│   ├── main.py                   # Application entry point
│   └── __init__.py
│
├── backend/                      # Backend services
│   └── distributed/              # Distributed computing
│
├── frontend/                     # Next.js frontend
│
├── sprint-llm-distilled-*/       # Domain expert LLM
│
├── scripts/                      # Utility scripts
│   ├── setup/                    # Setup scripts
│   └── evaluation/               # Evaluation scripts
│
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   └── integration/              # Integration tests
│
├── run.py                        # Project runner
├── start.sh                      # Start script
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables
└── README.md                     # Project documentation
```

## Detailed Component Architecture

### 1. Metacognitive Orchestrator

The new orchestrator module serves as the central control mechanism for the entire pipeline. It:

- Manages working memory across pipeline stages
- Generates contextually appropriate prompts for each stage
- Monitors output quality and initiates refinement loops
- Adapts pipeline behavior based on query complexity
- Integrates with the specialized model architecture

**Key Components:**

- **Core**: Main orchestrator implementation
- **Working Memory**: State management across stages
- **Prompt Generator**: Dynamic prompt creation
- **Process Monitor**: Quality evaluation and feedback
- **Interfaces**: Stage interface definitions
- **Specialized Orchestrator**: Implementation of the 8-stage specialized pipeline

#### 1.1 Orchestration Core Mechanisms

The orchestrator's core functionality revolves around intelligent coordination of the pipeline stages:

1. **Pipeline Initialization**

   - Loads stage configurations from JSON files
   - Dynamically imports and initializes stage modules
   - Sets up working memory structures
   - Establishes monitoring endpoints
   - Initializes the specialized model system
2. **Query Execution Flow**

   - Creates a unique session for each query
   - Determines optimal stage sequence based on query characteristics
   - Manages timeouts and error recovery mechanisms
   - Tracks performance metrics and telemetry
   - Coordinates model selection for each stage

#### 1.2 Working Memory System

The working memory system maintains state and context throughout query processing:

1. **Session Management**

   - Creates isolated memory contexts for each query
   - Implements structured hierarchical storage
   - Provides atomic operations for state updates
   - Supports transaction-like operations for consistency
2. **Data Structure**

   ```json
   {
     "session_id": "unique-session-identifier",
     "original_query": "Raw user query text",
     "metadata": {
       "timestamp": "2023-06-15T14:22:33Z",
       "user_context": { /* User-specific context */ },
       "query_classification": "informational|computational|comparison"
     },
     "stage_outputs": {
       "query_processor": { /* Stage 0 output */ },
       "semantic_atdb": { /* Stage 1 output */ },
       "domain_knowledge": { /* Stage 2 output */ }
       // Additional stage outputs as processing progresses
     },
     "stage_metrics": {
       "query_processor": {
         "confidence": 0.92,
         "processing_time": 120,
         "refinement_iterations": 0
       },
       // Metrics for other stages
     },
     "contextual_insights": [
       {
         "type": "entity_recognition",
         "value": "31yo male athlete",
         "confidence": 0.97,
         "stage": "query_processor"
       },
       // Additional insights extracted during processing
     ],
     "current_stage": 3,
     "state": "processing",
     "errors": []
   }
   ```
3. **Persistence Mechanisms**

   - In-memory storage for active sessions
   - Optional disk persistence for long-running sessions
   - Session caching for similar queries
   - Memory cleanup for completed sessions

#### 1.3 Dynamic Prompt Generation

The orchestrator dynamically generates context-aware prompts for each stage:

1. **Prompt Template Management**

   - Maintains a library of stage-specific prompt templates
   - Supports version control for templates
   - Includes fallback templates for error conditions
   - Allows for A/B testing of prompt variations
2. **Context Enrichment Process**

   - Analyzes session state and current stage requirements
   - Extracts relevant context from previous stage outputs
   - Incorporates stage-specific parameters and constraints
   - Determines optimal prompt structure based on stage type
3. **Stage-Specific Prompt Generation**

   a. **Query Processor (Stage 0)**

   ```
   You are analyzing a user query to extract structured information.

   USER QUERY: "{original_query}"

   Previous processing detected: {metadata.query_classification}

   Extract the following information:
   1. Core parameters (subject characteristics, measurements)
   2. Required metrics or calculations
   3. Contextual constraints and limitations
   4. Confidence level for each extracted element

   Format your response as a properly structured JSON object.
   ```

   b. **Semantic ATDB (Stage 1)**

   ```
   You are performing semantic analysis with throttle detection.

   STRUCTURED QUERY: {stage_outputs.query_processor}

   Your task is to:
   1. Extract the semantic intent of this query
   2. Identify potential areas where model throttling might occur
   3. Prepare optimized query components to overcome limitations
   4. Ensure comprehensive coverage of the domain knowledge required

   The domain context includes: {contextual_insights[].value}

   Format your response as a properly structured JSON object.
   ```

   c. **Domain Knowledge Extraction (Stage 2)**

   ```
   You are extracting domain knowledge for a specialized query.

   SEMANTIC REPRESENTATION: {stage_outputs.semantic_atdb}

   Relevant parameters: {stage_outputs.query_processor.parameters}

   For each identified domain element:
   1. Extract relevant formulas, constraints, and relationships
   2. Provide reference values for the specified parameters
   3. Identify the confidence level for each knowledge component
   4. Establish dependencies between different knowledge elements

   Include any documented limitations or caveats in your extraction.

   Format your response as a properly structured JSON object.
   ```

   d. **Parallel Reasoning Optimization (Stage 3)**

   ```
   You are optimizing parameters within the domain knowledge space.

   DOMAIN KNOWLEDGE: {stage_outputs.domain_knowledge}

   PARAMETERS: {stage_outputs.query_processor.parameters}

   Your task is to:
   1. Identify objective functions relevant to the query
   2. Perform gradient-based optimization across all parameter dimensions
   3. Discover non-obvious relationships between parameters
   4. Determine optimal values that satisfy all constraints

   Apply the following optimization constraints:
   {stage_outputs.domain_knowledge.constraints}

   Format your response as a properly structured JSON object with detailed optimization paths.
   ```

   e. **Solution Generation (Stage 4)**

   ```
   You are generating an information-rich solution to the query.

   OPTIMIZED PARAMETERS: {stage_outputs.reasoning_optimization}

   DOMAIN KNOWLEDGE: {stage_outputs.domain_knowledge}

   ORIGINAL QUERY: {original_query}

   Your task is to:
   1. Generate a comprehensive response that maximizes mutual information
   2. Prioritize information elements by relevance and novelty
   3. Structure information to optimize cognitive processing
   4. Eliminate redundant or low-value information

   Ensure your response addresses the specific metrics requested:
   {stage_outputs.query_processor.required_metrics}

   Format your response as a properly structured JSON object.
   ```

   f. **Response Scoring (Stage 5)**

   ```
   You are evaluating the quality of the generated solution.

   GENERATED SOLUTION: {stage_outputs.solution_generation}

   DOMAIN KNOWLEDGE: {stage_outputs.domain_knowledge}

   QUERY INTENT: {stage_outputs.semantic_atdb.intent}

   Evaluate the response using the Bayesian framework:
   1. Assess posterior probability P(R|D,Q) of response given domain knowledge and query
   2. Calculate likelihood P(D|R,Q) of domain knowledge given response and query
   3. Estimate prior probability P(R|Q) of response given query
   4. Determine evidence factor P(D|Q)

   Rate each component on a scale of 0-1 for:
   - Accuracy
   - Completeness
   - Consistency
   - Relevance
   - Novelty

   Format your response as a properly structured JSON object.
   ```

   g. **Response Comparison (Stage 6)**

   ```
   You are comparing and combining multiple response candidates.

   PRIMARY RESPONSE: {stage_outputs.solution_generation}

   EVALUATION METRICS: {stage_outputs.response_scoring}

   ALTERNATIVE RESPONSES: {stage_outputs.solution_generation.alternatives}

   Your task is to:
   1. Identify the highest quality components across all responses
   2. Apply the ensemble diversification formula using α={config.alpha_parameter}
   3. Compute pairwise diversity scores between all responses
   4. Generate an optimal combined response that maximizes both quality and diversity

   Format your response as a properly structured JSON object.
   ```

   h. **Threshold Verification (Stage 7)**

   ```
   You are performing final verification of the response against quality thresholds.

   COMBINED RESPONSE: {stage_outputs.response_comparison}

   QUALITY THRESHOLDS: {config.quality_thresholds}

   Your task is to:
   1. Verify that the response meets all quality thresholds
   2. Apply Pareto optimization to identify any dominated response components
   3. Prune any components that don't meet minimum quality standards
   4. Ensure the final response maintains optimal trade-offs between objectives

   If any component falls below threshold, provide specific improvement recommendations.

   Format your verification results as a properly structured JSON object.
   ```
4. **Refinement Loop Prompts**

   - Generated when output quality falls below thresholds
   - Includes specific feedback on deficiencies
   - Maintains context from previous attempts
   - Progressively refines instructions for clarity

#### 1.4 Quality Monitoring System

The process monitor continuously evaluates stage outputs for quality:

1. **Quality Dimensions**

   - **Completeness**: Ensures all required components are present
   - **Consistency**: Verifies logical coherence with previous stages
   - **Confidence**: Assesses certainty levels of outputs
   - **Compliance**: Checks adherence to domain constraints
   - **Correctness**: Validates factual accuracy where possible
2. **Quality Assessment Process**

   - Applies stage-specific evaluation criteria
   - Computes quantitative metrics for each dimension
   - Flags outputs that fall below configured thresholds
   - Generates detailed feedback for improvement
3. **Refinement Management**

   - Determines when refinement is necessary
   - Limits refinement iterations to prevent loops
   - Identifies specific aspects needing improvement
   - Tracks refinement history for learning

### 2. Pipeline Stages

Each stage becomes an independent module with standardized interfaces:

#### Stage 0: Query Processor

- Handles initial query processing
- Performs intent classification
- Extracts key parameters and constraints
- Packages queries for subsequent stages

**Interaction with Orchestrator:**

- Receives raw query text and user context
- Provides structured output for semantic analysis
- Reports confidence scores for extracted elements
- Signals if query requires specialized handling

#### Stage 1: Semantic ATDB

- Performs semantic analysis
- Detects and bypasses throttling
- Optimizes queries for information extraction
- Monitors response quality metrics

**Interaction with Orchestrator:**

- Consumes structured query from Stage 0
- Requests additional context if needed
- Implements throttle detection strategies
- Returns enriched semantic representation

#### Stage 2: Domain Knowledge Extraction

- Retrieves specialized domain knowledge
- Accesses domain-specific LLMs
- Prioritizes knowledge elements by relevance
- Establishes knowledge confidence levels

**Interaction with Orchestrator:**

- Receives semantic query representation
- Requests domain-specific prompt generation
- Utilizes working memory for context
- Returns comprehensive domain knowledge

#### Stage 3: Parallel Reasoning Optimization

- Performs gradient-based parameter optimization
- Discovers relationships between variables
- Implements multi-objective optimization
- Applies domain constraints during optimization

**Interaction with Orchestrator:**

- Consumes domain knowledge and parameters
- Requires specialized mathematical prompts
- Reports optimization progress metrics
- Returns optimized parameters with explanations

#### Stage 4: Solution Generation

- Maximizes information content in responses
- Structures information by relevance
- Eliminates redundancy and noise
- Optimizes cognitive processing flow

**Interaction with Orchestrator:**

- Uses optimized parameters and domain knowledge
- Requires content structuring instructions
- Implements information theory principles
- Returns information-rich solution

#### Stage 5: Response Scoring

- Applies Bayesian evaluation framework
- Assesses multiple quality dimensions
- Quantifies uncertainty in each component
- Provides detailed quality assessment

**Interaction with Orchestrator:**

- Evaluates solution against domain knowledge
- Implements formal evaluation metrics
- Signals if refinement is needed
- Returns detailed scoring results

#### Stage 6: Response Comparison

- Implements ensemble diversification
- Computes pairwise diversity metrics
- Combines strengths from multiple responses
- Optimizes quality-diversity balance

**Interaction with Orchestrator:**

- Compares multiple solution candidates
- Applies configured ensemble parameters
- Requests specialized comparison prompts
- Returns optimal combined response

#### Stage 7: Threshold Verification

- Applies Pareto optimality principles
- Verifies all quality thresholds are met
- Prunes suboptimal response components
- Finalizes response for delivery

**Interaction with Orchestrator:**

- Performs final quality verification
- Applies configurable quality thresholds
- Reports verification results
- Returns verified final response

### 3. Stage Interface Contract

All stages implement a consistent interface:

```python
class PipelineStage:
    async def initialize(self, config)
    async def process(self, input_data, context)
    async def cleanup()
    @property
    def metadata()
```

### 4. Configuration-Driven Architecture

The pipeline configuration is externalized into JSON files:

- **stages.json**: Defines the sequence and configuration of pipeline stages
- **orchestrator.json**: Controls orchestrator behavior and parameters

This approach allows modification of pipeline behavior without code changes.

## Example Orchestrator Workflow

### Initial Query Processing

1. **Query Reception**

   - User submits query: "I need anthropometric predictions for a 31yo male, 79kg, 172cm"
   - API endpoint forwards query to orchestrator
   - Orchestrator creates session and initializes working memory
2. **Stage 0: Query Processing**

   - Orchestrator generates context-aware prompt for query processor
   - Query processor extracts parameters: age=31, gender=male, weight=79kg, height=172cm
   - Query intent classified as "anthropometric_prediction"
   - Confidence scores calculated for each extracted parameter
   - Results stored in working memory
3. **Quality Verification**

   - Orchestrator evaluates Stage 0 output quality
   - Checks parameter completeness and confidence scores
   - If quality issues detected, generates refinement prompt
   - If quality sufficient, proceeds to next stage

### Semantic Analysis and Knowledge Extraction

4. **Stage 1: Semantic Analysis**

   - Orchestrator generates semantic analysis prompt with extracted parameters
   - Semantic ATDB analyzes query for potential throttling points
   - Bypass strategies selected if throttling detected
   - Enhanced semantic representation stored in working memory
5. **Stage 2: Domain Knowledge Extraction**

   - Orchestrator generates domain knowledge prompt with semantic representation
   - Domain knowledge stage retrieves relevant formulas and constraints
   - Sprint-LLM domain expert model provides specialized knowledge
   - Domain knowledge structured and stored in working memory

### Optimization and Solution Generation

6. **Stage 3: Reasoning Optimization**

   - Orchestrator generates optimization prompt with domain knowledge
   - Gradient-based optimization performed across parameter space
   - Non-obvious relationships identified between parameters
   - Optimized parameter set stored in working memory
7. **Stage 4: Solution Generation**

   - Orchestrator generates solution prompt with optimized parameters
   - Information theory principles applied to maximize relevance
   - Comprehensive anthropometric metrics calculated
   - Structured solution stored in working memory

### Quality Assurance and Finalization

8. **Stage 5-7: Evaluation and Verification**

   - Response evaluated using Bayesian framework
   - Multiple solution candidates compared and combined
   - Quality thresholds verified using Pareto optimization
   - Final response formatted according to request specifications
9. **Session Completion**

   - Final response returned to user
   - Session metrics recorded for system improvement
   - Working memory state preserved for potential follow-up queries
   - Session resources eventually cleaned up

## Migration Strategy

### Phase 1: Interface Definition and Orchestrator Foundation

- Define stage interfaces
- Implement core orchestrator components
- Create configuration structure

### Phase 2: Stage Adaptation

- Adapt existing stages (query processor and semantic ATDB)
- Create adapters for backward compatibility
- Implement working memory system

### Phase 3: Pipeline Completion

- Implement remaining pipeline stages
- Integrate with orchestrator
- Create comprehensive test suite

### Phase 4: API Integration

- Update API endpoints to use orchestrator
- Implement configuration management
- Add monitoring and metrics

## Benefits of New Architecture

1. **Modularity**: Each component can be developed, tested, and maintained independently
2. **Extensibility**: New stages can be added without modifying existing code
3. **Configurability**: Pipeline behavior can be modified via configuration
4. **Scalability**: Components can be distributed across computing resources
5. **Reusability**: Components can be reused in other projects

## Conclusion

The restructured architecture transforms the Four-Sided Triangle system from a tightly coupled application into a modular, extensible framework. The introduction of the metacognitive orchestrator enables dynamic management of the pipeline, while standardized interfaces ensure clean component boundaries. This approach preserves the system's sophisticated multi-model optimization capabilities while significantly improving maintainability, extensibility, and reusability.

By implementing dynamic prompt generation and intelligent workflow management, the metacognitive orchestrator eliminates the need for hardcoded instructions, making the system more adaptable to different queries and domains. The working memory system provides a coherent state management mechanism, ensuring that context and insights are preserved throughout the pipeline execution. This architecture positions the Four-Sided Triangle system as a foundation for even more sophisticated AI systems in the future.
