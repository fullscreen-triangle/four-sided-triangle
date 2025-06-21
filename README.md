<h1 align="center">Four Sided Triangle</h1>
<p align="center"><em> there is nothing new under the sun </em></p>

<p align="center">
  <img src="four_sided_triangle.png" alt="Four-Sided Triangle Logo" width="300"/>
</p>

## Executive Summary

Four-Sided Triangle is a sophisticated multi-model optimization pipeline designed to overcome the limitations of traditional RAG (Retrieval-Augmented Generation) systems when dealing with complex domain-expert knowledge extraction. Unlike conventional approaches that rely on simple retrieval mechanisms, this system employs a novel recursive optimization methodology that treats language models as transformation functions within a complex optimization space.

The system's metacognitive orchestration layer manages an 8-stage specialized pipeline, dynamically selecting between LLM-based reasoning and traditional mathematical solvers based on problem characteristics. This hybrid approach allows the system to handle both fuzzy reasoning tasks and precise mathematical optimization problems with equal proficiency.

The system implements a high-performance Rust core that handles computationally intensive operations, including fuzzy evidence networks, Bayesian inference, and metacognitive optimization. This Rust integration provides 10-50x performance improvements over Python implementations while maintaining full API compatibility.

Additionally, the system now supports **Turbulance DSL integration** - a revolutionary approach that allows researchers to write complete research protocols in structured scientific language rather than fragmented conversational queries. This transforms Four-Sided Triangle from a conversational RAG system into a comprehensive research execution platform.

## Why Four-Sided Triangle Is Necessary

Traditional AI approaches face several critical limitations when dealing with domain-expert knowledge:

1. **Knowledge Depth Problem**: Standard RAG systems struggle with the depth and complexity of specialized knowledge domains, often providing superficial responses that fail to incorporate expert-level insights.

2. **Optimization Complexity**: Real-world problems often require sophisticated multi-objective optimization that standard LLMs cannot perform effectively without specialized architectural support.

3. **Context Management Challenge**: Managing context across complex reasoning chains overwhelms conventional architectures, leading to context fragmentation and reasoning failures.

4. **Quality Consistency Issues**: Ensuring consistent quality in outputs across diverse problem spaces requires sophisticated monitoring and evaluation protocols absent in simple pipeline approaches.

Four-Sided Triangle addresses these challenges through its specialized architecture, providing a comprehensive solution for complex knowledge extraction and reasoning tasks.

## Turbulance DSL Integration: From Conversational to Research Protocol

### The Paradigm Shift

Traditional RAG systems require users to engage in lengthy conversational exchanges:
```
User: "I need to analyze sprint performance"
System: "What specific aspects?" 
User: "Ground reaction forces during acceleration"
System: "What data do you have?"
... (5-10 more exchanges)
```

With Turbulance integration, users can encode their complete research methodology upfront:

```turbulance
proposition SprintPerformanceOptimization:
    motion Hypothesis("Ground reaction force patterns reveal 400m pacing inefficiencies")
    
    sources:
        local("athlete_data/force_measurements.csv")
        domain_expert("sprint_biomechanics")
    
    within experiment:
        given sample_size > 20:
            item force_patterns = analyze_grf(data)
            item biomechanical_analysis = pipeline_stage("domain_knowledge", {
                expert_models: ["sprint_expert", "biomechanics_expert"],
                focus: "force_production_efficiency"
            })
            item optimization_protocol = pipeline_stage("reasoning_optimization", {
                objective: "minimize_energy_cost_maximize_power"
            })
            ensure statistical_significance(results) < 0.05

funxn execute_analysis():
    return complete_research_protocol()
```

### Key Advantages

1. **Complete Context Awareness**: Your specialized models receive the full experimental context upfront
2. **Optimal Pipeline Routing**: The system can choose the most efficient path through your 8 stages
3. **Reproducible Science**: The Turbulance script becomes documentation of the research methodology
4. **Parallel Execution**: Independent parts of the research can be processed simultaneously
5. **Enhanced Quality Control**: Process monitor can evaluate against stated research objectives

### Architecture Integration

Turbulance scripts are compiled into Four-Sided Triangle execution plans through:

- **Turbulance Parser** (Rust): Parses `.trb` files into semantic AST
- **Network Graph Compiler** (Rust): Generates `.fs` files (consciousness state visualization)
- **Resource Orchestrator** (Rust): Creates `.ghd` files (dependency management)
- **Decision Memory** (Rust): Produces `.hre` files (metacognitive tracking)
- **Pipeline Integration**: Maps Turbulance constructs to existing 8-stage pipeline

## System Architecture: Detailed Explanation

The system architecture consists of several interconnected components, each serving a critical purpose in the overall knowledge extraction and optimization process.

### 1. Metacognitive Orchestrator: The Central Intelligence

**Why It's Necessary**: Traditional pipeline approaches suffer from rigid execution paths and lack the ability to adapt to varying problem complexities. The metacognitive orchestrator provides the essential adaptive intelligence layer that coordinates all system components and dynamically adjusts processing strategies based on the nature of each query.

**Key Components**:

#### Working Memory System
This component maintains state and context throughout query processing, addressing the context fragmentation issues that plague standard LLM applications:

- **Session Management**: Creates isolated memory contexts for each query, preventing cross-contamination between concurrent processing tasks
- **Hierarchical Storage**: Implements structured hierarchical storage that mirrors human cognitive organization of information
- **Transaction Operations**: Supports transaction-like operations to ensure consistency across the pipeline
- **Memory Cleanup**: Prevents resource leaks through automated session cleanup mechanisms

#### Process Monitor
Continuously evaluates output quality across all stages, addressing the quality consistency issues:

- **Multi-Dimensional Quality Assessment**: Evaluates completeness, consistency, confidence, compliance, and correctness of all pipeline outputs
- **Stage-Specific Evaluation**: Applies specialized evaluation criteria tailored to each pipeline stage
- **Refinement Triggering**: Intelligently determines when additional refinement iterations are needed
- **Performance Analytics**: Generates detailed metrics for system optimization

#### Dynamic Prompt Generator
Enables sophisticated model interactions by dynamically creating context-aware prompts:

- **Context Enrichment**: Analyzes session state and stage requirements to create optimally contextualized prompts
- **Stage-Specific Templates**: Maintains specialized templates for each pipeline stage
- **Refinement Loop Handling**: Generates specialized prompts when output quality falls below thresholds
- **A/B Testing Support**: Allows for systematic improvement of prompt strategies

### 2. Advanced Core Components

The system implements several specialized core components inspired by biological and cognitive systems, providing sophisticated resource management and processing capabilities:

#### Glycolytic Query Investment Cycle (GQIC)

**Purpose**: Optimizes resource allocation based on expected information yield using a metabolic-inspired approach.

**Why It's Necessary**: Computational resources are limited, and different query components have varying information value. GQIC ensures optimal allocation of resources to maximize overall information gain.

**Key Capabilities**:
- **Three-Phase Cycle**: Follows a biochemically-inspired cycle:
  - **Initiation**: Identifies potential information sources and establishes resource requirements
  - **Investment**: Allocates computational resources based on expected return-on-investment
  - **Payoff**: Harvests results and measures actual information gain
- **Adaptive Learning**: Tracks historical ROI to improve future allocations
- **Information Density Optimization**: Prioritizes high-information-yield components
- **Multi-Factor Resource Allocation**: Considers complexity, domain specificity, and completion criteria

**Implementation Details**:
- Information gain calculation based on query characteristics and domain
- ROI-based resource allocation with minimum thresholds for all components
- Actual information content measurement for results, with content-type-specific metrics
- Historical performance tracking for continuous improvement

#### Metacognitive Task Partitioning (MTP)

**Purpose**: Breaks complex queries into optimally sized sub-tasks using self-interrogative principles.

**Why It's Necessary**: Complex queries often contain multiple inter-related sub-problems that are best processed separately before integration. MTP provides sophisticated decomposition capabilities essential for handling multi-faceted problems.

**Key Capabilities**:
- **Knowledge Domain Identification**: Classifies query components by relevant knowledge domains
- **Domain-Specific Task Identification**: Extracts specific tasks within each domain
- **Parameter Extraction**: Automatically extracts key parameters from natural language
- **Dependency Modeling**: Establishes relationships between sub-tasks for optimal execution order
- **Completion Criteria Definition**: Creates clear success criteria for each sub-task

**Implementation Details**:
- Four-phase decomposition process for comprehensive query understanding
- Domain-specific keyword and entity analysis for accurate classification
- Template-based sub-query formulation with parameter inference
- Dependency graph construction for coordinated execution

#### Adversarial Throttle Detection and Bypass (ATDB)

**Purpose**: Detects and overcomes throttling mechanisms in LLMs that limit their capabilities.

**Why It's Necessary**: Commercial LLMs often implement throttling mechanisms that restrict their output quality, especially for complex or specialized queries. ATDB ensures consistent high-quality responses even when facing such limitations.

**Key Capabilities**:
- **Throttle Pattern Recognition**: Identifies token limitation, depth limitation, and computation limitation patterns
- **Information Density Analysis**: Measures response quality relative to expected information content
- **Strategy Selection**: Chooses optimal bypass strategies based on historical effectiveness
- **Dynamic Adaptation**: Learns from bypass attempt outcomes to improve future strategy selection

**Bypass Strategies**:
- **Token Limitation**: Query partitioning, progressive disclosure, targeted extraction
- **Depth Limitation**: Query reframing, expert persona adoption, component assembly
- **Computation Limitation**: Step-by-step instruction, verification approaches, equation transformation

**Implementation Details**:
- Multi-dimensional throttle detection using linguistic and information-theoretic signals
- Adaptive strategy selection based on pattern type and historical performance
- Domain-specific bypass strategy customization for specialized fields
- Performance tracking for continuous improvement of bypass effectiveness

### 3. Eight-Stage Specialized Pipeline: Processing Depth and Breadth

**Why It's Necessary**: Complex domain knowledge extraction requires multiple specialized processing steps that standard end-to-end approaches cannot adequately perform. Each stage in this pipeline addresses a specific aspect of the knowledge extraction and reasoning challenge, allowing for specialization while maintaining a coherent overall process.

#### Stage 0: Query Processor
**Purpose**: Transforms ambiguous natural language queries into structured representations that downstream components can process effectively.

**Why It's Necessary**: Raw user queries are often ambiguous, underspecified, and lack the structure needed for precise processing. This stage performs the critical function of query understanding and structuring before any deeper processing can begin.

**Key Capabilities**:
- Intent classification to determine the query's fundamental purpose
- Entity extraction to identify key elements requiring specialized treatment
- Constraint identification to understand processing boundaries
- Query reformulation to resolve ambiguities while preserving original intent

**Specialized Models**:
- **Phi-3-mini (microsoft/Phi-3-mini-4k-instruct)**: A 3.8B parameter model optimized for structured output tasks. Its lightweight nature makes it CPU-friendly for forking private copies per session without saturating GPUs, while delivering excellent instruction-following capability for key-value extraction.
- **Mixtral (mistralai/Mixtral-8x22B-Instruct-v0.1)**: A sparsely-activated Mixture of Experts model providing GPT-4-class quality for handling ill-posed user queries with complex transformations, deployed behind timeout guards.
- **SciBERT (allenai/scibert_scivocab_uncased)**: Specialized for biomedical and sport-science vocabulary, providing robust Named Entity Recognition (NER) and slot filling to extract domain-specific entities.

#### Stage 1: Semantic ATDB (Advanced Throttle Detection and Bypass)
**Purpose**: Performs semantic transformation of structured queries and detects potential throttling issues.

**Why It's Necessary**: Information retrieval systems often implement throttling mechanisms that can impede knowledge extraction. This stage provides semantic query optimization and throttle detection capabilities essential for reliable operation.

**Key Capabilities**:
- Multiple transformation strategies for optimizing information retrieval
- Reranking of transformation approaches based on effectiveness
- Semantic enhancement of queries for improved downstream processing
- Throttle detection and bypass strategies for uninterrupted operation

**Specialized Models**:
- **BGE Reranker (BAAI/bge-reranker-base)**: A cross-encoder that outputs a single relevance score, used to select the most effective transformation strategy when multiple approaches are available.

#### Stage 2: Domain Knowledge Extraction
**Purpose**: Extracts and organizes domain-specific knowledge relevant to the query using dual expert model architecture.

**Why It's Necessary**: Generic knowledge bases lack the specialized information needed for expert-level responses. This stage provides targeted access to domain-specific knowledge through multiple complementary expert models, significantly enhancing response quality and technical depth in specialized fields.

**Key Capabilities**:
- **Dual-Model Architecture**: Simultaneous querying of primary and secondary domain expert models
- **Multi-Model Fusion**: Intelligent combination of insights from complementary expert models
- **Consensus Detection**: Identification of validated insights where multiple experts agree
- **Specialized model selection based on domain requirements
- **Domain-specific fine-tuning through LoRA and other adaptation techniques
- **Knowledge prioritization based on relevance to the current query
- **Confidence scoring and consensus validation for extracted knowledge elements

**Dual-Model Expert Architecture**:
- **Primary Domain Expert**: General sprint knowledge, training methodology, and performance optimization
- **Secondary Domain Expert**: Advanced biomechanical analysis, kinematic optimization, and technical refinements
- **Multi-Model Fusion Engine**: Combines complementary insights while avoiding duplication
- **Consensus Validation**: Boosts confidence when multiple experts agree on insights

**Specialized Models**:
- **Primary Sprint Expert**: Enhanced GPT-2 model via Ollama specialized for sprint training and performance
- **Secondary Sprint Expert (sprint-llm-distilled-20250324-040451)**: PEFT-adapted model focused on advanced biomechanical analysis with specialized capabilities for:
  - Advanced kinematic and kinetic analysis
  - Ground reaction force optimization  
  - Energy system transitions during 400m races
  - Biomechanical efficiency optimization
  - Race-specific tactical analysis
- **BioMedLM (stanford-crfm/BioMedLM-2.7B)**: A model trained on PubMed specifically for biomechanics and physiology, small enough for efficient LoRA and PEFT fine-tuning on specialized corpora. Serves as the base for the Scientific-Sprint-LLM.
- **Mixtral (mistralai/Mixtral-8x22B-Instruct-v0.1)**: Provides comprehensive general sports statistics and reasoning capabilities, with access to Olympic data. Deployed behind GPU quota controls.
- **Phi-3-mini (microsoft/Phi-3-mini-4k-instruct)**: Acts as a lightweight fallback option for low-latency paths or CPU-only deployments.

#### Stage 3: Parallel Reasoning
**Purpose**: Applies mathematical and logical reasoning to the problem space.

**Why It's Necessary**: Complex optimization problems require sophisticated reasoning capabilities beyond basic retrieval and generation. This stage provides the analytical foundation for generating optimal solutions.

**Key Capabilities**:
- Multi-step reasoning with chain-of-thought capabilities
- Parameter optimization within multi-dimensional spaces
- Relationship discovery between variables and constraints
- Generation of mathematical proof structures for solution validation

**Specialized Models**:
- **Qwen (Qwen/Qwen-2-7B-Instruct)**: Specialized for mathematical and gradient-style reasoning, with strong capabilities for equation manipulation and multi-objective solver tasks.
- **DeepSeek Math (deepseek-ai/deepseek-math-7b-rl)**: An alternative math reasoning model optimized for symbolic mathematics and complex equation solving.
- **Phi-3-mini (microsoft/Phi-3-mini-4k-instruct)**: Configured with "let's think" prompt engineering for fast internal chain-of-thought reasoning, achieving sub-900ms latency on A100 GPUs.

#### Stage 4: Solution Generation
**Purpose**: Produces candidate solutions based on reasoning outputs.

**Why It's Necessary**: Raw reasoning outputs must be transformed into coherent solution candidates that address the original query. This stage bridges the gap between analytical reasoning and practical solution delivery.

**Key Capabilities**:
- Integration of reasoning outputs into cohesive solutions
- Diversity generation through parameter variation
- Constraint enforcement to ensure practical viability
- Information-theoretic optimization of solution structures

**Specialized Models**:
- Multiple models are sampled with different temperatures to generate diverse solution candidates:
  - **Phi-3-mini**: Used with temperature 0.7 for creative variants
  - **Mixtral**: Used with temperature 0.3 for more focused solutions
  - **BioMedLM**: Used with temperature 0.9 for domain-specific exploratory solutions

#### Stage 5: Response Scoring
**Purpose**: Evaluates candidate solutions using sophisticated quality metrics.

**Why It's Necessary**: Not all generated solutions are equal in quality, and naive selection approaches often fail to identify truly optimal solutions. This stage provides objective quality assessment essential for solution ranking.

**Key Capabilities**:
- Multi-dimensional quality scoring incorporating various quality signals
- Reward model application based on human preference data
- Bayesian evaluation frameworks for robust assessment
- Comparative analysis across solution candidates

**Specialized Models**:
- **OpenAssistant Reward Model (OpenAssistant/reward-model-deberta-v3-large-v2)**: Trained on human-preference pairs, this model outputs scalar rewards that can be treated as P(R|Q) in Bayesian evaluation formulas.

#### Stage 6: Ensemble Diversification
**Purpose**: Creates a diverse set of high-quality solutions to present multiple perspectives.

**Why It's Necessary**: Single-solution approaches often miss important alternative perspectives or fail to account for different user preferences. This stage ensures comprehensive coverage of the solution space.

**Key Capabilities**:
- Diversity measurement using cross-encoder models
- Quality-aware diversity optimization using determinantal point processes
- Ensemble creation with complementary solution characteristics
- Coverage analysis of the overall solution space

**Specialized Models**:
- **BGE Reranker M3 (BAAI/bge-reranker-v2-m3)**: A cross-encoder used to compute pairwise diversity and quality scores for candidate solutions, which are then processed through a determinantal point process (DPP) to select a diverse, high-quality subset.

#### Stage 7: Threshold Verification
**Purpose**: Performs final verification of solutions against quality standards.

**Why It's Necessary**: Even well-scored solutions may contain subtle inconsistencies or violate domain constraints. This final verification stage ensures only truly valid solutions are delivered.

**Key Capabilities**:
- Logical consistency verification through entailment models
- Fact-checking against established domain knowledge
- Compliance verification with explicit and implicit constraints
- Final quality certification based on comprehensive criteria

**Specialized Models**:
- **BART-MNLI (facebook/bart-large-mnli)**: Performs quick entailment testing to verify that candidate answers logically follow from domain facts stored in working memory.

### 4. Dependency Injection Architecture: Flexibility and Testability

**Why It's Necessary**: Traditional monolithic architectures become unmaintainable as system complexity grows. A dependency injection approach allows for modular development, testing, and extension of the system without disrupting existing functionality.

**Key Components**:

#### ModelContainer
Serves as the central registry for all model implementations:

- Runtime registration and configuration of models
- Lifecycle management (singleton, request-scoped, transient)
- Implementation swapping for testing and optimization
- Centralized configuration management

#### Specialized Interfaces
Defines clear contracts for each component type:

- Stage-specific interface definitions ensuring consistent behavior
- Standardized input/output formats for streamlined integration
- Optional capability discovery for feature negotiation
- Version compatibility management

#### Base Implementations
Provides foundation classes that implement common functionality:

- Metric collection and telemetry standardization
- Configuration management and validation
- Capability registration and discovery
- Caching and optimization behaviors

### 5. High-Performance Rust Core: Computational Acceleration

**Why It's Necessary**: Python's performance limitations become bottlenecks in computationally intensive operations like Bayesian inference, fuzzy logic processing, and evidence network propagation. The Rust core addresses these performance constraints while maintaining seamless integration with the Python orchestration layer.

**Key Components**:

#### Fuzzy Evidence System
Implements comprehensive fuzzy logic processing with multiple membership function types:

- **Membership Functions**: Triangular, Trapezoidal, Gaussian, Sigmoid, and Custom functions
- **Fuzzy Inference Engine**: Rule-based inference with parallel processing capabilities
- **Evidence Management**: Temporal decay modeling, confidence tracking, and source reliability assessment
- **Defuzzification**: Multiple methods including centroid and maximum approaches

#### Bayesian Evidence Network
Provides sophisticated probabilistic reasoning capabilities:

- **Network Structure**: Support for multiple node types (Query, Context, Domain, Strategy, Quality, Resource, Output, Meta)
- **Relationship Modeling**: Causal, correlational, inhibitory, supportive, conditional, and temporal relationships
- **Propagation Algorithms**: Belief Propagation, Variational Bayes, Markov Chain Monte Carlo, and Particle Filter
- **Query Processing**: Marginal probability, conditional probability, most probable explanation, sensitivity analysis, and what-if scenarios

#### Metacognitive Optimizer
Implements adaptive strategy selection and pipeline optimization:

- **Strategy Types**: Query optimization, resource allocation, quality improvement, efficiency boost, error recovery, adaptive learning, context adaptation, and uncertainty reduction
- **Performance Learning**: Historical performance tracking with success rate optimization
- **Decision Context**: Multi-dimensional context analysis including complexity, resources, quality requirements, and time constraints
- **Optimization Objectives**: Multi-objective optimization with constraint handling

#### Autobahn Integration Bridge
Provides interface to external probabilistic reasoning systems:

- **Consciousness Modeling**: ATP consumption tracking, membrane coherence analysis, and entropy optimization
- **Biological Processing**: Oscillatory dynamics modeling and immune system health assessment
- **Probabilistic Delegation**: Automatic routing of complex reasoning tasks to specialized systems
- **Performance Monitoring**: Real-time status tracking and connection management

**Performance Benefits**:
- Bayesian calculations: 15-25x faster than Python
- Fuzzy inference: 20-40x faster than Python
- Evidence propagation: 10-30x faster than Python
- Network queries: 25-50x faster than Python
- Memory usage: 60-80% reduction

### 6. Hybrid Optimization System: Combining LLM and Traditional Approaches

**Why It's Necessary**: Neither LLM-based approaches nor traditional mathematical solvers alone can effectively address the full spectrum of optimization problems. A hybrid approach leverages the strengths of each method while mitigating their respective weaknesses.

**Key Components**:

#### Solver Registry
Catalogs available optimization solvers with detailed capability profiles:

- Capability-based solver registration and discovery
- Performance characteristic tracking for intelligent selection
- Resource requirement specifications for deployment optimization
- Version and compatibility management

#### Solver Dispatcher
Intelligently selects between solver types based on problem characteristics:

- Problem structure analysis to determine optimal solver approach
- Multi-objective optimization for competing quality dimensions
- Dynamic fallback mechanisms when primary solvers fail
- Learning from past solver performance to improve future selection

#### Solver Adapters
Provides standardized interfaces for diverse solver implementations:

- Unified API across different solver technologies
- Input transformation for solver-specific requirements
- Output normalization for consistent downstream processing
- Error handling and recovery mechanisms

## System Workflow in Detail

The Four-Sided Triangle system follows a sophisticated workflow that ensures comprehensive processing of queries while maintaining adaptability to varying problem complexities.

### 1. Query Submission and Initialization

When a query is submitted to the system:

1. **Session Initialization**: The metacognitive orchestrator creates a unique working memory session
2. **Query Analysis**: Initial analysis determines the general characteristics and complexity of the query
3. **Resource Allocation**: Computational resources are allocated based on estimated processing requirements
4. **Pipeline Configuration**: The processing pipeline is configured specifically for the query characteristics

### 2. Pipeline Execution

The query then proceeds through the 8-stage pipeline:

1. **Stage Sequencing**: The orchestrator determines the optimal sequence of stages for the specific query
2. **Dynamic Model Selection**: For each stage, the most appropriate models are selected based on query requirements
3. **Parallel Processing**: Where possible, stages or sub-components are processed in parallel for efficiency
4. **Intermediate Result Storage**: Working memory maintains all intermediate results for later stages
5. **Timeout Management**: Each stage operates under controlled timeouts to prevent processing stalls

### 3. Quality Monitoring and Refinement

Throughout execution, quality is continuously monitored:

1. **Stage Output Evaluation**: The process monitor evaluates outputs from each stage against quality criteria
2. **Threshold Checking**: Quality metrics are compared against predefined thresholds
3. **Refinement Triggering**: If quality falls below thresholds, refinement loops are initiated
4. **Prompt Modification**: For refinement loops, specialized prompts are generated with specific improvement instructions
5. **Resource Adjustment**: Additional computational resources may be allocated to problematic stages

### 4. Response Delivery

Once processing completes:

1. **Final Verification**: Completed solutions undergo final verification against all quality criteria
2. **Response Formatting**: Verified solutions are formatted according to client requirements
3. **Explanation Generation**: If requested, explanations of the solution process are generated
4. **Confidence Scoring**: Each solution is accompanied by confidence metrics
5. **Session Cleanup**: Working memory session is archived or cleaned up as appropriate

## Implementation Architecture

The Four-Sided Triangle system is implemented as a modern, scalable application with multiple components working together.

### Backend Architecture

The backend system is built with a focus on modularity and scalability:

- **FastAPI Framework**: Provides high-performance, async-capable API endpoints
- **Dependency Injection Container**: Manages component lifecycles and dependencies
- **Distributed Computing Support**: Integration with Ray and Dask for scalable processing
- **Configuration-Driven Design**: JSON configuration files for flexible deployment options
- **Monitoring and Telemetry**: Comprehensive metrics collection for performance optimization
- **Rust Core Integration**: High-performance computational backend with Python FFI
- **Thread-Safe Registries**: Global state management using Rust's ownership system
- **Memory-Safe Operations**: Zero-copy data transfer between Python and Rust where possible

### Frontend Architecture (Optional)

The system includes an optional frontend for interactive usage:

- **React-Based UI**: Modern, responsive interface for query submission and result visualization
- **Real-Time Progress Tracking**: Visibility into pipeline execution status
- **Interactive Result Exploration**: Tools for exploring and comparing multiple solutions
- **Visualization Components**: Graphical representation of optimization processes and results
- **Configuration Interface**: GUI for system configuration and tuning

### Deployment Options

The system supports multiple deployment configurations:

- **Local Development**: Standalone execution for development and testing
- **Docker Containers**: Containerized deployment for consistent environments
- **Kubernetes Orchestration**: Scalable deployment across compute clusters
- **Cloud Integration**: Support for major cloud providers' infrastructure
- **Hybrid On-Premise/Cloud**: Flexible resource utilization across environments

## Getting Started

### Prerequisites

- Python 3.10+
- Rust 1.70+ and Cargo (for building the core performance components)
- Docker and Docker Compose (for containerized deployment)
- CUDA-capable GPU recommended but not required

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/four-sided-triangle.git
   cd four-sided-triangle
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Build the Rust core components:
   ```bash
   cd four-sided-triangle
   cargo build --release
   ```

4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Configure the system:
   - Review and adjust configuration files in `app/config/`
   - Set environment variables as needed in `.env` file

6. Run the application:
   ```bash
   python -m app.main
   ```

### Docker Deployment

1. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

2. Access the API at http://localhost:8000

### Configuration

The system is highly configurable through JSON configuration files:

- **Pipeline Stages**: `app/config/pipeline/stages.json` - Define and configure pipeline stages
- **Orchestrator**: `app/config/pipeline/orchestrator.json` - Configure orchestration behavior
- **Distributed Computing**: `app/config/distributed.json` - Set up distributed computing options
- **Model Resources**: `app/config/resources.json` - Define resource requirements and allocations

## API Reference

The Four-Sided Triangle exposes a RESTful API:

### Main Endpoints

- **POST /api/process** - Process a query through the pipeline
  - Request body: `{ "query": "string", "options": {} }`
  - Response: `{ "solutions": [], "metadata": {} }`

- **POST /api/async/process** - Asynchronously process a query
  - Request body: `{ "query": "string", "options": {}, "callback_url": "string" }`
  - Response: `{ "task_id": "string" }`

- **GET /api/tasks/{task_id}** - Check status of an async task
  - Response: `{ "status": "string", "progress": {}, "result": {} }`

### Utility Endpoints

- **GET /health** - Check system health
  - Response: `{ "status": "string", "service": "string", "distributed_backend": "string" }`

- **GET /debug/pipeline-info** - Get pipeline configuration details
  - Response: `{ "registered_stages": [], "active_sessions": [], "configuration": {} }`

- **GET /debug/distributed-info** - Get distributed computing status
  - Response: `{ "backend": "string", "active_jobs": 0, "workers": {} }`

For detailed API documentation, visit the running application at `/docs` or `/redoc`.

## Project Structure

```
four-sided-triangle/
├── app/                          # Main application package
│   ├── api/                      # API endpoints and interfaces
│   │   ├── endpoints.py          # API route definitions
│   │   ├── app.py                # FastAPI application setup
│   │   └── interfaces.md         # API documentation
│   ├── config/                   # Configuration files
│   │   └── pipeline/             # Pipeline configuration
│   │       ├── stages.json       # Stage definitions
│   │       └── orchestrator.json # Orchestrator settings
│   ├── core/                     # Core functionality
│   │   └── rust_integration.py   # Rust FFI integration layer
│   ├── interpreter/              # Query interpretation components
│   ├── models/                   # Model implementations
│   │   ├── container.py          # Dependency injection container
│   │   ├── interfaces.py         # Model interface definitions
│   │   ├── factory.py            # Model factory implementations
│   │   ├── base_models.py        # Base model classes
│   │   └── query_processor.py    # Query processor implementation
│   ├── orchestrator/             # Metacognitive orchestrator
│   │   ├── metacognitive_orchestrator.py # Main orchestrator
│   │   ├── working_memory.py     # Working memory implementation
│   │   ├── process_monitor.py    # Quality monitoring
│   │   ├── prompt_generator.py   # Dynamic prompt generation
│   │   └── pipeline_stage.py     # Pipeline stage base
│   ├── solver/                   # Optimization solvers
│   │   ├── registry.py           # Solver registry
│   │   ├── dispatcher.py         # Solver selection logic
│   │   └── adapters/             # Solver implementations
│   └── utils/                    # Utility functions
├── backend/                      # Backend services
│   └── distributed/              # Distributed computing
│       ├── compute_manager.py    # Compute resource management
│       └── compute_helpers.py    # Helper functions
├── docs/                         # Documentation
│   └── adr/                      # Architecture Decision Records
│       └── 0003-dependency-injection.md # ADR example
├── frontend/                     # Frontend application
│   ├── public/                   # Static assets
│   └── src/                      # React components
├── scripts/                      # Utility scripts
├── src/                          # Rust core implementation
│   ├── lib.rs                    # Main Rust library with FFI exports
│   ├── autobahn_bridge.rs        # Autobahn system integration
│   ├── evidence_network.rs       # Bayesian evidence networks
│   ├── fuzzy_evidence.rs         # Fuzzy logic and inference
│   ├── metacognitive_optimizer.rs # Metacognitive optimization
│   ├── bayesian.rs               # Bayesian evaluation
│   ├── text_processing.rs        # Text processing utilities
│   ├── memory.rs                 # Memory management
│   ├── quality_assessment.rs     # Quality assessment
│   ├── optimization.rs           # Optimization algorithms
│   ├── throttle_detection.rs     # Throttle detection
│   ├── turbulance/               # Turbulance DSL processing
│   │   ├── mod.rs                # Turbulance module exports
│   │   ├── parser.rs             # Turbulance syntax parser
│   │   ├── ast.rs                # Abstract syntax tree definitions
│   │   ├── compiler.rs           # Turbulance to pipeline compiler
│   │   ├── fs_generator.rs       # Network graph (.fs) generator
│   │   ├── ghd_generator.rs      # Resource dependencies (.ghd) generator
│   │   ├── hre_generator.rs      # Decision memory (.hre) generator
│   │   └── integration.rs        # Four-Sided Triangle integration
│   ├── error.rs                  # Error handling
│   └── utils.rs                  # Utility functions
├── tests/                        # Test suite
├── Cargo.toml                    # Rust dependencies and configuration
└── Cargo.lock                    # Rust dependency lock file
```

## Architecture Decision Records

The project uses Architecture Decision Records (ADRs) to document significant architectural decisions:

- **ADR-0001**: Pipeline Architecture
- **ADR-0002**: Distributed Computing Strategy
- **ADR-0003**: Dependency Injection Pattern
- **ADR-0004**: Model Lifecycle Management
- **ADR-0005**: Quality Assurance Approach

See the `/docs/adr/` directory for detailed records.

## Contributing

Contributions are welcome! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for more information on how to get involved.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
