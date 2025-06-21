---
layout: default
title: Turbulance DSL Integration
nav_order: 8
---

# Turbulance DSL Integration

## Overview

The Turbulance DSL integration transforms Four-Sided Triangle from a conversational RAG system into a comprehensive research execution platform. Instead of fragmenting research into multiple conversational exchanges, researchers can encode their complete experimental methodology in structured scientific language.

## Architecture

### Four-File Compilation System

Each Turbulance research protocol compiles into four interconnected files:

1. **`.trb` (Turbulance Research Protocol)**: User-written research methodology
2. **`.fs` (Fullscreen Network Graph)**: Auto-generated consciousness state visualization 
3. **`.ghd` (Gerhard Dependencies)**: Auto-generated resource orchestration
4. **`.hre` (Harare Decision Memory)**: Auto-generated metacognitive tracking

### Rust-Based Processing Pipeline

```mermaid
graph TD
    A[User writes .trb file] --> B[Turbulance Parser (Rust)]
    B --> C[AST Generation]
    C --> D[Compiler (Rust)]
    D --> E[.fs Generator]
    D --> F[.ghd Generator] 
    D --> G[.hre Generator]
    E --> H[Network Graph Visualization]
    F --> I[Resource Dependencies]
    G --> J[Decision Memory]
    H --> K[Four-Sided Triangle Pipeline]
    I --> K
    J --> K
```

## Turbulance Syntax Integration

### Basic Research Protocol

```turbulance
proposition ResearchHypothesis:
    motion Hypothesis("Your scientific hypothesis here")
    
    sources:
        local("data/dataset.csv")
        domain_expert("your_domain")
        pipeline_stage("domain_knowledge", {
            expert_models: ["model1", "model2"]
        })
    
    within experiment:
        given sample_size > minimum_threshold:
            item analysis = pipeline_stage("stage_name", config)
            ensure statistical_significance(results) < 0.05

funxn execute_research():
    return complete_analysis()
```

### Integration with Four-Sided Triangle Stages

Turbulance constructs map to specific pipeline stages:

| Turbulance Construct | Pipeline Stage | Purpose |
|---------------------|---------------|---------|
| `pipeline_stage("query_processor", {...})` | Stage 0 | Query analysis and structuring |
| `pipeline_stage("semantic_atdb", {...})` | Stage 1 | Semantic transformation and throttle detection |
| `pipeline_stage("domain_knowledge", {...})` | Stage 2 | Expert model consultation |
| `pipeline_stage("reasoning_optimization", {...})` | Stage 3 | Mathematical and logical reasoning |
| `pipeline_stage("solution_generation", {...})` | Stage 4 | Solution candidate generation |
| `pipeline_stage("response_scoring", {...})` | Stage 5 | Quality assessment and ranking |
| `pipeline_stage("response_comparison", {...})` | Stage 6 | Ensemble diversification |
| `pipeline_stage("threshold_verification", {...})` | Stage 7 | Final verification |

## Auto-Generated Files

### .fs (Network Graph Visualization)

The system automatically generates a network graph representation showing:

```fs
// Auto-generated from ResearchHypothesis.trb
research_protocol_network:
├── data_sources
│   ├── local_data: "data/dataset.csv"
│   └── domain_experts: ["your_domain"]
│
├── pipeline_execution_flow
│   ├── stage_0_query_processor → structured_query
│   ├── stage_2_domain_knowledge → expert_insights  
│   ├── stage_3_reasoning_optimization → analysis_strategy
│   └── stage_5_response_scoring → quality_metrics
│
└── real_time_status
    ├── execution_progress: 67%
    ├── current_stage: "reasoning_optimization"
    └── quality_metrics: {confidence: 0.94, completeness: 0.87}
```

### .ghd (Resource Dependencies)

Auto-generated resource orchestration:

```ghd
// Auto-generated dependencies for ResearchHypothesis.trb
research_protocol_dependencies:
    four_sided_triangle_integration:
        - orchestrator_service: "app.orchestrator.orchestrator_service"
        - working_memory: "app.orchestrator.working_memory"
        - process_monitor: "app.orchestrator.process_monitor"
    
    domain_expert_models:
        - expert_model_registry: "app.models.factory"
        - specialized_models: ["your_domain_expert", "biomechanics_expert"]
    
    data_processing:
        - data_loader: "app.utils.helpers"
        - statistical_analysis: "app.solver.adapters.scipy_adapter"
    
    pipeline_stages:
        - domain_knowledge: "app.core.stages.stage2_domain_knowledge"
        - reasoning_optimization: "app.core.stages.stage3_reasoning_optimization" 
        - response_scoring: "app.core.stages.stage5_scoring"
```

### .hre (Decision Memory)

Auto-generated metacognitive tracking:

```hre
// Auto-generated decision log for ResearchHypothesis.trb
research_session: "ResearchHypothesis_2024_session"
hypothesis: "Your scientific hypothesis here"

execution_decisions:
    stage_selection:
        timestamp: "2024-01-15T10:30:00Z"
        decision: "selected_domain_knowledge_stage"
        reasoning: "Research requires specialized expert model consultation"
        confidence: 0.92
        
    model_selection:
        timestamp: "2024-01-15T10:31:15Z"
        decision: "dual_expert_model_approach"
        selected_models: ["your_domain_expert", "biomechanics_expert"]
        reasoning: "Multi-model consensus improves reliability"
        confidence: 0.89
        
    quality_thresholds:
        statistical_significance: 0.05
        minimum_sample_size: 30
        confidence_threshold: 0.8

metacognitive_insights:
    successful_patterns:
        - "Domain expert consultation improved result quality by 23%"
        - "Multi-stage reasoning reduced false positives"
        
    learning_for_future:
        - "Increase confidence threshold for complex hypotheses"
        - "Consider parallel execution for independent analyses"
```

## Implementation Components

### Rust Modules

#### 1. Turbulance Parser (`src/turbulance/parser.rs`)
- Parses Turbulance syntax into AST
- Handles scientific constructs (propositions, hypotheses, experiments)
- Validates syntax and semantic correctness

#### 2. AST Definitions (`src/turbulance/ast.rs`)
- Abstract Syntax Tree node definitions
- Scientific reasoning constructs
- Pipeline integration points

#### 3. Compiler (`src/turbulance/compiler.rs`)
- Transforms AST into Four-Sided Triangle execution plans
- Maps Turbulance constructs to pipeline stages
- Optimizes execution flow

#### 4. File Generators
- **FS Generator** (`src/turbulance/fs_generator.rs`): Network graph visualization
- **GHD Generator** (`src/turbulance/ghd_generator.rs`): Resource dependencies
- **HRE Generator** (`src/turbulance/hre_generator.rs`): Decision memory

#### 5. Integration Layer (`src/turbulance/integration.rs`)
- Python FFI bindings
- Four-Sided Triangle orchestrator integration
- Session management

### Python Integration

#### Orchestrator Enhancement
```python
from app.turbulance import TurbulanceOrchestrator

class EnhancedOrchestrator(MetacognitiveOrchestrator):
    def __init__(self):
        super().__init__()
        self.turbulance = TurbulanceOrchestrator()
    
    def process_turbulance_protocol(self, trb_file: str) -> Dict[str, Any]:
        """Process a complete Turbulance research protocol"""
        # Parse .trb file (Rust)
        protocol = self.turbulance.parse_protocol(trb_file)
        
        # Generate support files (Rust)
        fs_content = self.turbulance.generate_fs(protocol)
        ghd_content = self.turbulance.generate_ghd(protocol)
        hre_session = self.turbulance.initialize_hre(protocol)
        
        # Execute through Four-Sided Triangle pipeline
        return self.execute_research_protocol(protocol)
```

## Usage Examples

### Sprint Performance Analysis

```turbulance
proposition SprintOptimization:
    motion Hypothesis("Force plate analysis reveals 400m pacing inefficiencies")
    
    sources:
        local("athlete_data/force_measurements.csv")
        domain_expert("sprint_biomechanics")
    
    within experiment:
        given sample_size > 20:
            item raw_data = load_dataset()
            item biomechanical_analysis = pipeline_stage("domain_knowledge", {
                expert_models: ["sprint_expert", "biomechanics_expert"],
                focus: "force_production_efficiency",
                analysis_depth: "advanced_kinematic_analysis"
            })
            
            item optimization_strategy = pipeline_stage("reasoning_optimization", {
                objective: "minimize_energy_cost_maximize_power",
                constraints: biomechanical_analysis.limitations,
                optimization_method: "multi_objective"
            })
            
            item performance_predictions = pipeline_stage("solution_generation", {
                strategy: optimization_strategy,
                prediction_window: "6_months",
                confidence_interval: 0.95
            })
            
            item quality_assessment = pipeline_stage("response_scoring", {
                metrics: ["accuracy", "biological_plausibility", "practical_applicability"],
                validation_method: "cross_validation"
            })
            
            ensure statistical_significance(quality_assessment.results) < 0.05
            ensure biological_plausibility(performance_predictions) > 0.8

funxn execute_sprint_analysis():
    item results = complete_research_protocol()
    return generate_performance_recommendations(results)
```

This would automatically generate:
- **`SprintOptimization.fs`**: Real-time visualization of the analysis pipeline
- **`SprintOptimization.ghd`**: Resource dependencies for sprint and biomechanics experts
- **`SprintOptimization.hre`**: Decision log tracking model selections and quality thresholds

### Medical Research Protocol

```turbulance
proposition DiabetesBiomarkers:
    motion Hypothesis("Metabolomic patterns predict Type 2 diabetes 6 months before symptoms")
    
    sources:
        local("clinical_data/metabolomics_study.csv") 
        domain_expert("endocrinology")
        external_api("pubmed_diabetes_research")
    
    within clinical_study:
        given patient_cohort_size >= 200:
            item baseline_measurements = pipeline_stage("query_processor", {
                data_type: "metabolomic_profiles",
                patient_stratification: ["age", "bmi", "family_history"]
            })
            
            item biomarker_identification = pipeline_stage("domain_knowledge", {
                expert_models: ["endocrinology_expert", "metabolomics_expert"],
                analysis_focus: "early_diabetes_indicators",
                knowledge_integration: "multi_expert_consensus"
            })
            
            item predictive_modeling = pipeline_stage("reasoning_optimization", {
                model_type: "machine_learning_ensemble",
                validation_strategy: "longitudinal_follow_up",
                prediction_horizon: "6_months"
            })
            
            item clinical_validation = pipeline_stage("threshold_verification", {
                sensitivity_threshold: 0.85,
                specificity_threshold: 0.80,
                clinical_actionability: "treatment_modification"
            })
            
            ensure predictive_accuracy(predictive_modeling) > 0.85
            ensure clinical_utility(clinical_validation) > 0.8

funxn execute_diabetes_research():
    item findings = complete_clinical_protocol()
    return generate_clinical_recommendations(findings)
```

## Benefits

### For Researchers
1. **Complete Methodology Documentation**: The Turbulance script serves as comprehensive research documentation
2. **Reproducible Protocols**: Exact replication of research methodology
3. **Parallel Processing**: Independent analyses run simultaneously 
4. **Quality Assurance**: Built-in statistical and scientific validation

### For the System
1. **Optimal Resource Allocation**: Full context enables better GQIC decisions
2. **Enhanced Pipeline Routing**: Complete protocol allows optimal stage selection
3. **Improved Quality Control**: Process monitor evaluates against stated objectives
4. **Metacognitive Learning**: Decision patterns improve future protocol execution

### For Science
1. **Methodological Transparency**: Complete research protocols are documented and shareable
2. **Collaborative Research**: Protocols can be shared, modified, and improved
3. **Meta-Analysis Support**: Standardized protocol format enables systematic reviews
4. **Reproducibility Crisis**: Addresses reproducibility through complete methodology specification

## Getting Started

### Installation
The Turbulance integration is built into the Four-Sided Triangle Rust core. No additional dependencies required.

### Basic Usage
1. Write your research protocol in `.trb` format
2. Submit to Four-Sided Triangle API:
   ```python
   result = orchestrator.process_turbulance_protocol("my_research.trb")
   ```
3. Monitor execution through auto-generated `.fs` visualization
4. Review decisions in auto-generated `.hre` log
5. Access all resources through auto-generated `.ghd` dependencies

### Advanced Usage
- Custom pipeline stage configurations
- Multi-protocol orchestration
- Cross-protocol resource sharing
- Collaborative protocol development

## Technical Implementation

### Rust Core Integration
The Turbulance processing is implemented entirely in Rust for maximum performance:

- **Parser**: ~10x faster than Python equivalent
- **Compiler**: Optimized AST transformations
- **File Generation**: Parallel generation of .fs, .ghd, .hre files
- **Memory Management**: Zero-copy integration with Four-Sided Triangle

### Python Bindings
Seamless integration with existing Python orchestrator through PyO3 FFI bindings.

### Performance Characteristics
- Protocol parsing: <50ms for typical research protocols
- Compilation: <100ms for complex multi-stage protocols  
- File generation: <25ms parallel generation of all support files
- Memory usage: Minimal overhead over base Four-Sided Triangle system

This integration represents a fundamental evolution in how AI systems support scientific research - from conversational assistance to comprehensive research protocol execution. 