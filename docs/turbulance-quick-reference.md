---
layout: default
title: Turbulance Quick Reference
nav_order: 9
---

# Turbulance DSL Quick Reference

## Essential Syntax

### Basic Research Protocol Structure
```turbulance
proposition YourHypothesisName:
    motion Hypothesis("Your scientific hypothesis statement")
    
    sources:
        local("data/your_dataset.csv")
        domain_expert("your_field")
    
    within experiment:
        given condition > threshold:
            item analysis = pipeline_stage("stage_name", config)
            ensure validation_criteria < threshold

funxn execute_research():
    return complete_analysis()
```

### Four-Sided Triangle Pipeline Integration

| Function | Pipeline Stage | Purpose |
|----------|---------------|---------|
| `pipeline_stage("query_processor", config)` | Stage 0 | Query structuring |
| `pipeline_stage("semantic_atdb", config)` | Stage 1 | Semantic optimization |
| `pipeline_stage("domain_knowledge", config)` | Stage 2 | Expert consultation |
| `pipeline_stage("reasoning_optimization", config)` | Stage 3 | Mathematical reasoning |
| `pipeline_stage("solution_generation", config)` | Stage 4 | Solution generation |
| `pipeline_stage("response_scoring", config)` | Stage 5 | Quality assessment |
| `pipeline_stage("response_comparison", config)` | Stage 6 | Ensemble diversification |
| `pipeline_stage("threshold_verification", config)` | Stage 7 | Final verification |

### Common Configuration Patterns

#### Domain Knowledge Stage
```turbulance
item expert_analysis = pipeline_stage("domain_knowledge", {
    expert_models: ["sprint_expert", "biomechanics_expert"],
    focus: "specific_research_area",
    analysis_depth: "advanced",
    consensus_threshold: 0.8
})
```

#### Reasoning Optimization Stage  
```turbulance
item optimization = pipeline_stage("reasoning_optimization", {
    objective: "minimize_cost_maximize_efficiency",
    optimization_method: "multi_objective",
    constraints: previous_analysis.limitations,
    solver_type: "mathematical" // or "llm_based"
})
```

#### Solution Generation Stage
```turbulance
item solutions = pipeline_stage("solution_generation", {
    strategy: optimization_results,
    diversity_requirement: 0.7,
    confidence_interval: 0.95,
    solution_count: 5
})
```

#### Quality Assessment Stage
```turbulance
item quality = pipeline_stage("response_scoring", {
    metrics: ["accuracy", "biological_plausibility", "practical_applicability"],
    validation_method: "cross_validation",
    minimum_confidence: 0.8
})
```

### Scientific Constructs

#### Hypotheses
```turbulance
proposition ResearchName:
    motion Hypothesis("Clear, testable scientific hypothesis")
    motion AlternativeHypothesis("Alternative explanation if needed")
    
    sources:
        local("path/to/data.csv")
        domain_expert("field_name")
        external_api("research_database")
```

#### Experimental Conditions
```turbulance
within experiment:
    given sample_size >= 30:
        // Your analysis steps
        
    given confidence_level > 0.95:
        // High-confidence analysis path
        
    alternatively:
        // Fallback analysis method
```

#### Validation Requirements
```turbulance
ensure statistical_significance(results) < 0.05
ensure effect_size(analysis) > 0.3
ensure biological_plausibility(findings) > 0.8
ensure reproducibility(protocol) > 0.9
```

### Data Sources

#### Local Data
```turbulance
sources:
    local("relative/path/to/data.csv")
    local("/absolute/path/to/dataset.json")
```

#### Domain Experts
```turbulance
sources:
    domain_expert("sprint_biomechanics")
    domain_expert("endocrinology") 
    domain_expert("machine_learning")
```

#### External APIs
```turbulance
sources:
    external_api("pubmed_search")
    external_api("clinical_trials_database")
    external_api("genomics_repository")
```

### Auto-Generated Files

When you submit a `.trb` file, the system automatically creates:

#### `.fs` - Network Visualization
Shows real-time execution progress and system consciousness state.

#### `.ghd` - Resource Dependencies  
Lists all required models, data sources, and computational resources.

#### `.hre` - Decision Memory
Logs all system decisions with reasoning and confidence scores.

## Common Research Patterns

### Sprint Performance Analysis
```turbulance
proposition SprintOptimization:
    motion Hypothesis("Training protocol X improves 400m performance")
    
    sources:
        local("athlete_data/performance_metrics.csv")
        domain_expert("sprint_biomechanics")
    
    within performance_study:
        given athlete_count >= 20:
            item baseline = analyze_current_performance(data)
            item biomechanics = pipeline_stage("domain_knowledge", {
                expert_models: ["sprint_expert", "biomechanics_expert"],
                focus: "400m_race_optimization"
            })
            item protocol = pipeline_stage("reasoning_optimization", {
                objective: "maximize_400m_time_improvement",
                constraints: biomechanics.safety_limits
            })
            ensure improvement_significance(protocol.results) < 0.05
```

### Medical Research
```turbulance
proposition ClinicalTrial:
    motion Hypothesis("Treatment Y reduces symptoms by >30%")
    
    sources:
        local("clinical_data/patient_outcomes.csv")
        domain_expert("clinical_medicine")
        external_api("clinical_trials_database")
    
    within clinical_study:
        given patient_cohort >= 100:
            item baseline_symptoms = assess_baseline(patients)
            item treatment_analysis = pipeline_stage("domain_knowledge", {
                expert_models: ["clinical_expert", "pharmacology_expert"],
                focus: "treatment_efficacy"
            })
            item statistical_analysis = pipeline_stage("reasoning_optimization", {
                analysis_type: "randomized_controlled_trial",
                primary_endpoint: "symptom_reduction"
            })
            ensure clinical_significance(treatment_analysis.effect_size) > 0.3
```

### Data Science Research
```turbulance
proposition MachineLearningStudy:
    motion Hypothesis("Algorithm Z outperforms current state-of-the-art")
    
    sources:
        local("datasets/benchmark_data.json")
        domain_expert("machine_learning")
    
    within ml_experiment:
        given dataset_size >= 10000:
            item preprocessing = clean_and_prepare(raw_data)
            item model_development = pipeline_stage("reasoning_optimization", {
                optimization_type: "hyperparameter_tuning",
                validation_strategy: "k_fold_cross_validation"
            })
            item performance_comparison = pipeline_stage("response_comparison", {
                baseline_models: ["current_sota", "standard_benchmarks"],
                metrics: ["accuracy", "f1_score", "computational_efficiency"]
            })
            ensure statistical_superiority(performance_comparison) < 0.01
```

## Integration with Four-Sided Triangle

### Accessing Specialized Models
```turbulance
// Use your existing sprint expert model
item sprint_analysis = pipeline_stage("domain_knowledge", {
    expert_models: ["sprint_expert"],
    query_focus: "400m_pacing_strategy"
})

// Access biomechanics expert
item biomech_analysis = pipeline_stage("domain_knowledge", {
    expert_models: ["biomechanics_expert", "sprint_expert"],
    consensus_required: true
})
```

### Leveraging GQIC Resource Allocation
```turbulance
// High-priority analysis gets more resources
within high_priority_research:
    item complex_analysis = pipeline_stage("reasoning_optimization", {
        resource_priority: "high",
        computational_budget: "unlimited",
        quality_threshold: 0.95
    })
```

### Working with Process Monitor
```turbulance
// Set quality thresholds for automatic refinement
item analysis = pipeline_stage("solution_generation", {
    quality_monitor: {
        minimum_confidence: 0.8,
        maximum_refinement_iterations: 3,
        auto_refinement: true
    }
})
```

## Error Handling

### Graceful Degradation
```turbulance
within experiment:
    given optimal_conditions_met:
        item full_analysis = complete_pipeline()
    alternatively:
        item simplified_analysis = reduced_pipeline()
```

### Validation Failures
```turbulance
// Handle validation failures gracefully
item results = pipeline_stage("threshold_verification", {
    failure_handling: "graceful_degradation",
    fallback_strategy: "reduced_confidence_analysis"
})
```

## Performance Tips

1. **Parallel Execution**: Independent analyses run automatically in parallel
2. **Resource Optimization**: GQIC allocates resources based on full protocol context
3. **Cached Results**: Identical pipeline stages with same config are cached
4. **Incremental Processing**: Large datasets are processed incrementally

## File Organization

```
research_project/
├── hypothesis.trb              # Your research protocol
├── hypothesis.fs               # Auto-generated visualization  
├── hypothesis.ghd              # Auto-generated dependencies
├── hypothesis.hre              # Auto-generated decision log
└── data/
    ├── raw_data.csv
    └── processed_results.json
```

This quick reference covers the essential patterns for integrating Turbulance DSL with Four-Sided Triangle's specialized pipeline system. 