---
layout: default
title: Domain Knowledge Stage - Dual-Model Architecture
parent: Pipeline Stages
nav_order: 3
---

# Domain Knowledge Extraction Stage (Stage 2) - Dual-Model Architecture

The Domain Knowledge Extraction stage retrieves specialized domain knowledge from multiple expert language models, performs intelligent multi-model fusion, and establishes confidence levels for each knowledge element through consensus validation. This stage is critical for providing accurate, specialized knowledge that serves as the foundation for subsequent reasoning and solution generation stages.

## Dual-Model Expert Architecture

The enhanced stage now employs a sophisticated dual-model architecture:

### Primary Domain Expert
- **Role**: Provides comprehensive sprint knowledge, training methodology, and performance optimization
- **Model**: Enhanced GPT-2 via Ollama
- **Strengths**: Broad sprint expertise, training plans, coaching insights
- **Temperature**: 0.1 (focused responses)

### Secondary Domain Expert  
- **Role**: Advanced biomechanical analysis and technical refinements
- **Model**: sprint-llm-distilled-20250324-040451 (PEFT-adapted)
- **Strengths**: Kinematic analysis, force dynamics, energy system optimization
- **Temperature**: 0.15 (diverse technical perspectives)

### Multi-Model Fusion Engine
- **Purpose**: Intelligently combines insights from both experts
- **Features**: Consensus detection, complementary insight preservation, duplicate elimination
- **Benefits**: Enhanced knowledge depth and technical accuracy

## Components

### 1. Enhanced Domain Knowledge Service

The main service orchestrating the dual-model domain knowledge extraction process. Key functionality includes:

- **Dual-Model Coordination**: Manages simultaneous extraction from primary and secondary experts
- **Multi-Model Fusion**: Combines insights from multiple domain expert models
- **Consensus Detection**: Identifies validated insights where multiple experts agree
- Coordinating the extraction pipeline flow across multiple expert models
- Managing access to domain-specific LLMs with intelligent model selection
- Prioritizing knowledge by relevance to the query with multi-model weighting
- Establishing knowledge confidence levels through cross-model validation
- Structuring the extracted knowledge for downstream stages with source attribution

### 2. Advanced Knowledge Extractor

Core component responsible for extracting domain-specific knowledge from both expert models. Features include:

- **Model Preference Selection**: Intelligent routing between primary and secondary experts
- **Specialized Prompt Generation**: Model-specific prompts optimized for each expert's strengths
- **Simultaneous Extraction**: Parallel knowledge extraction from complementary expert models
- Specialized extraction techniques for different domains with multi-model support
- Access to domain-specific knowledge bases through multiple expert channels
- Identification of formulas, constraints, and relationships with model source attribution
- Hierarchical knowledge representation enhanced with multi-model insights
- Reference value extraction for specified parameters with confidence validation

### 3. Multi-Model Knowledge Prioritizer

Enhanced prioritizer and ranks extracted knowledge elements with fusion capabilities. Functionality includes:

- **Multi-Model Fusion**: Intelligent combination of insights from primary and secondary experts
- **Consensus Boost**: Increased confidence scoring for insights validated by multiple models
- **Complementary Insight Preservation**: Maintains unique insights from secondary expert
- **Duplicate Detection**: Identifies and merges similar insights from multiple models
- Relevance scoring for each knowledge element with model source weighting
- Dependency mapping between knowledge components across model sources
- Confidence level assessment for each element with consensus validation
- Uncertainty quantification across the knowledge set with multi-model analysis
- Priority weighting based on query requirements and model consensus

### 4. Enhanced LLM Connector

Enhanced connector that manages connections to both primary and secondary domain-expert language models. Features include:

- **Dual-Model Routing**: Intelligent routing between primary and secondary expert models
- **PEFT Integration**: Specialized handling for sprint-llm-distilled PEFT adapters
- Integration with Sprint-LLM domain expert models (both primary and secondary)
- Specialized prompt construction for knowledge extraction with model-aware optimization
- Response parsing and structured representation with source attribution
- Error handling and fallback mechanisms across multiple models
- Performance optimization for model interactions with load balancing

### 5. Cross-Model Knowledge Validator

Enhanced validator that performs cross-model validation of extracted knowledge. Functionality includes:

- **Cross-Model Validation**: Validates insights against multiple expert model outputs
- **Consensus Identification**: Identifies areas of agreement between expert models
- Consistency checking across knowledge elements from multiple sources
- Identification of contradictions or conflicts between model outputs
- Source reliability assessment with model confidence scoring
- Cross-validation with multiple sources when available
- Documentation of limitations and caveats with model-specific annotations

## Enhanced Process Flow

1. **Domain Analysis & Model Selection**
   - Analyze semantic representation from Stage 1
   - Identify required knowledge domains
   - Determine extraction priorities  
   - Select appropriate expert models (primary and/or secondary)

2. **Dual-Model Knowledge Extraction**
   - Construct specialized prompts for each expert model
   - Execute simultaneous extraction across both expert models
   - Parse model responses with source attribution
   - Build initial knowledge structure with multi-model insights

3. **Cross-Model Validation**
   - Check consistency of extracted knowledge across models
   - Identify conflicts and contradictions between expert outputs
   - Assess source reliability and model confidence
   - Perform cross-validation between expert models

4. **Multi-Model Fusion & Prioritization**
   - Perform intelligent fusion of insights from multiple experts
   - Score knowledge relevance with model source weighting
   - Map dependencies across model sources
   - Calculate confidence levels with consensus validation
   - Quantify uncertainties with multi-model analysis
   - Detect and boost consensus insights

5. **Enhanced Knowledge Integration**
   - Structure knowledge elements with multi-model attribution
   - Establish relationships across expert model outputs
   - Document dependencies and model sources
   - Prepare metadata with consensus and complementary insight analysis

## Integration Points

### Input Requirements
- Semantic representation from Stage 1
- Query context and parameters
- Domain specifications with model preference indicators
- Extraction preferences and multi-model configuration

### Output Format
- **Enhanced Structured Domain Knowledge**: Multi-model attributed knowledge elements
- **Dual-Model Confidence Metrics**: Consensus validation and individual model confidence  
- **Cross-Model Dependency Mappings**: Relationships between insights from different experts
- **Multi-Model Validation Results**: Consensus areas and divergent perspectives
- **Complementary Insight Analysis**: Unique contributions from secondary expert model

### Downstream Usage
- Informs reasoning strategies with multi-model insights
- Guides solution generation with consensus validation
- Provides validation constraints from multiple expert perspectives
- Supports result verification through cross-model validation

## Performance Considerations

### Optimization Goals
- Minimize extraction latency across multiple models
- Maximize knowledge relevance through complementary insights
- Ensure comprehensive coverage via dual-model architecture
- Maintain accuracy standards through consensus validation

### Monitoring Metrics
- **Multi-Model Extraction Success Rates**: Success rates for both primary and secondary experts
- **Consensus Validation Accuracy**: Accuracy of cross-model validation
- **Fusion Processing Times**: Performance of multi-model fusion operations
- **Individual Model Performance**: Performance metrics for each expert model
- **Complementary Insight Quality**: Quality assessment of unique secondary model contributions

## Error Handling

### Extraction Errors
- **Multi-Model Fallback Strategies**: Graceful degradation when one expert model fails
- **Cross-Model Recovery**: Use insights from functioning model when other fails
- Partial result handling from individual expert models
- Recovery mechanisms with model source attribution
- Error documentation with multi-model context

### Validation Failures
- **Consensus Conflict Resolution**: Handling disagreements between expert models
- **Model Confidence Weighting**: Prioritizing insights based on model reliability
- Alternative sources through secondary expert consultation
- Uncertainty documentation with multi-model analysis
- Quality assurance across expert model outputs

## Configuration

The stage can be configured through various parameters supporting dual-model operation:

```json
{
  "extraction": {
    "min_confidence": 0.8,
    "max_depth": 3,
    "cross_validation": true,
    "enable_dual_models": true,
    "consensus_threshold": 0.9
  },
  "models": {
    "primary": "sprint-domain-expert",
    "secondary": "sprint-domain-expert-secondary", 
    "fallback": "phi-3-mini",
    "timeout": 30,
    "enable_multi_model_fusion": true
  },
  "validation": {
    "consistency_threshold": 0.9,
    "min_sources": 2,
    "consensus_boost": 0.1,
    "cross_model_validation": true
  }
}
```

## Best Practices

1. **Multi-Model Knowledge Quality**
   - Validate all extracted knowledge across expert models
   - Document confidence levels with consensus indicators
   - Track source reliability for each expert model
   - Maintain knowledge coherence across model sources

2. **Dual-Model Management**
   - Monitor performance of both primary and secondary experts
   - Update model selection based on domain requirements
   - Optimize prompts for each expert model's strengths
   - Handle failures gracefully with cross-model fallbacks

3. **Performance Optimization**
   - Cache common knowledge across model sources
   - Parallelize extraction from multiple expert models
   - Prioritize critical paths with model consensus
   - Monitor resource usage across dual-model operations

4. **Quality Assurance**
   - Regular validation checks across expert models
   - Cross-reference sources between models
   - Update knowledge bases for both expert models
   - Track extraction metrics with multi-model attribution

## Model Specifications

### Primary Sprint Expert
- **Model**: Enhanced GPT-2 via Ollama
- **Endpoint**: http://localhost:11434  
- **Specialization**: Sprint training methodology and performance optimization
- **Strengths**: Comprehensive sprint knowledge, training plans, performance analysis

### Secondary Sprint Expert (sprint-llm-distilled-20250324-040451)
- **Model**: PEFT-adapted distilled model with LoRA adapters
- **Path**: ./sprint-llm-distilled-20250324-040451
- **Specialization**: Advanced biomechanical analysis and technical refinements
- **Strengths**: 
  - Advanced kinematic and kinetic analysis
  - Ground reaction force optimization
  - Energy system transitions during 400m races
  - Biomechanical efficiency optimization
  - Race-specific tactical analysis

## Benefits of Dual-Model Architecture

- **Enhanced Domain Coverage**: Two specialized experts provide broader knowledge spectrum
- **Technical Depth**: Secondary model adds advanced biomechanical analysis capabilities
- **Consensus Validation**: Higher confidence when both models agree on insights
- **Complementary Insights**: Unique perspectives from specialized secondary expert
- **Fault Tolerance**: Graceful degradation when one model encounters issues
- **Quality Assurance**: Cross-model validation improves overall accuracy 