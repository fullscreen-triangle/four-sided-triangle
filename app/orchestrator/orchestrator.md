# Four-Sided Triangle Orchestrator

The orchestrator is the central coordination system of the Four-Sided Triangle architecture, responsible for managing the flow of information through the seven pipeline stages, controlling execution, and maintaining state across processing steps.

## Architecture Overview

The orchestration layer consists of several key components that work together to process queries through a configurable pipeline:

### Core Components

1. **Orchestrator Interface** (`interfaces.py`)
   - Defines the contract for orchestrator implementations
   - Establishes methods for registering stages, configuring pipelines, and processing queries

2. **Default Orchestrator** (`orchestrator.py`)
   - Standard implementation of the orchestrator interface
   - Coordinates sequential execution of pipeline stages
   - Manages working memory and context

3. **Metacognitive Orchestrator** (`metacognitive_orchestrator.py`)
   - Advanced implementation with self-monitoring capabilities
   - Dynamically adjusts pipeline flow based on quality evaluations
   - Supports refinement loops for improving outputs

4. **Orchestrator Service** (`orchestrator_service.py`)
   - Higher-level service for application integration
   - Manages session state and pipeline sequence selection
   - Provides interfaces for external systems

5. **Working Memory** (`working_memory.py`)
   - Maintains state across pipeline stages
   - Stores intermediate results and metadata
   - Provides session management capabilities

6. **Prompt Generator** (`prompt_generator.py`)
   - Creates optimized prompts for each pipeline stage
   - Contextualizes prompts based on working memory
   - Supports different prompt strategies

7. **Process Monitor** (`process_monitor.py`)
   - Evaluates quality of stage outputs
   - Determines when refinement is necessary
   - Tracks performance metrics across stages

8. **Output Evaluator** (`output_evaluator.py`)
   - Assesses output quality against established criteria
   - Provides feedback for refinement processes
   - Ensures outputs meet quality thresholds

### Pipeline Stage Interface

All pipeline stages implement the `PipelineStage` protocol or extend the `AbstractPipelineStage` class defined in `interfaces.py`. Key requirements include:

- Unique `stage_id` property
- `process()` method that processes inputs and generates outputs
- `refine()` method that improves outputs based on feedback
- `metrics` property for performance tracking

## Pipeline Flow

The standard pipeline for query processing involves seven stages:

1. **Query Processor** (Stage 0)
   - Handles initial query reception and preprocessing
   - Classifies query intent and complexity
   - Adds contextual information and packages query

2. **Semantic ATDB** (Stage 1)
   - Performs semantic analysis with throttle detection
   - Identifies and bypasses LLM limitations
   - Extracts comprehensive semantic models

3. **Domain Knowledge** (Stage 2)
   - Incorporates domain-specific knowledge
   - Enriches queries with expert insights
   - Resolves domain-specific references

4. **Reasoning Optimization** (Stage 3)
   - Applies advanced reasoning strategies
   - Optimizes solution approaches
   - Reduces cognitive biases

5. **Solution Generation** (Stage 4)
   - Produces candidate solutions
   - Implements strategies based on optimized reasoning
   - Generates comprehensive response options

6. **Response Scoring** (Stage 5)
   - Evaluates candidate solutions
   - Assigns confidence scores
   - Determines optimal response selection

7. **Response Comparison** (Stage 6)
   - Compares multiple response candidates
   - Performs final selection and refinement
   - Ensures output coherence and quality

## Processing Workflow

### Standard Execution Flow

1. The orchestrator receives a query and creates a session
2. A pipeline sequence is determined based on query characteristics
3. The query processor stage analyzes and packages the query
4. Subsequent stages are executed in order with working memory shared between them
5. Each stage receives inputs, a generated prompt, and context from working memory
6. Stage outputs are evaluated for quality and refined if necessary
7. The final output from the last stage is returned as the result

### Dynamic Pipeline Adjustments

The metacognitive orchestrator can modify the pipeline based on query characteristics:

- **Simple Factual Queries**: `[query_processor → semantic_atdb → solution_generation]`
- **Complex Domain Queries**: All seven stages in sequence
- **Optimization Queries**: `[query_processor → semantic_atdb → domain_knowledge → reasoning_optimization → solution_generation]`

### Refinement Loops

When stage outputs don't meet quality thresholds:

1. The process monitor evaluates output quality
2. If quality is insufficient, feedback is generated
3. The stage's `refine()` method is called with this feedback
4. The refined output is re-evaluated
5. The process continues until quality thresholds are met or maximum iterations are reached

## Integration Points

### Registering Custom Pipeline Stages

```python
from app.orchestrator.interfaces import AbstractPipelineStage

class CustomStage(AbstractPipelineStage):
    @property
    def stage_id(self) -> str:
        return "custom_stage"
    
    def process(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # Stage implementation
        return {"result": "processed_output"}

# Register with orchestrator
orchestrator.register_stage("custom_stage", CustomStage())
```

### Configuring Pipeline Flow

```python
pipeline_config = [
    {
        "id": "query_processor",
        "depends_on": []
    },
    {
        "id": "custom_stage",
        "depends_on": ["query_processor"]
    },
    # Additional stages...
]

orchestrator.configure_pipeline(pipeline_config)
```

### Processing Queries

```python
result = orchestrator.process_query(
    "What is the impact of quantum computing on cryptography?",
    {"user_id": "test_user"}
)
```

## Current Implementation Status

As of now, the following components have been implemented:

1. ✅ Orchestrator interfaces and core classes
2. ✅ Working memory system
3. ✅ Prompt generator
4. ✅ Query Processor Stage (Stage 0)
5. ✅ Semantic ATDB Stage (Stage 1)
6. ⏳ Domain Knowledge Stage (Stage 2) - In progress
7. ⏳ Reasoning Optimization Stage (Stage 3) - In progress 
8. ⏳ Solution Generation Stage (Stage 4) - In progress
9. ⏳ Response Scoring Stage (Stage 5) - In progress
10. ⏳ Response Comparison Stage (Stage 6) - In progress

The system can be extended by implementing the remaining pipeline stages and refining the existing implementations.
