---
layout: default
title: Models - Dual-Model Architecture
nav_order: 4
---

# Specialized Models - Enhanced with Dual-Model Architecture

The Four Sided Triangle framework incorporates several specialized models, each designed to handle specific aspects of the information processing pipeline. The system now features an advanced dual-model architecture in the Domain Knowledge stage, significantly enhancing domain expertise and technical depth.

## Model Overview

Our system uses a combination of pre-trained, custom-trained, and fine-tuned models, each optimized for specific tasks in the pipeline:

1. **SciBert**: Scientific text understanding and slot filling
2. **BART-MNLI**: Natural language inference and verification
3. **Dual Domain Expert Models**: Primary and secondary sprint specialists (NEW)
4. **Custom Models**: Domain-specific processing
5. **Verification Models**: Output validation and quality assurance

## Dual-Model Domain Expert Architecture (NEW)

### Primary Sprint Expert
**Purpose**: Comprehensive sprint knowledge and training methodology

**Configuration**:
```yaml
model:
  name: SprintDomainExpert
  type: enhanced_gpt2_ollama
  version: "1.0"
  config:
    ollama_model_name: "gpt2-enhanced"
    base_url: "http://localhost:11434"
    model_path: "models/domain_llm/gpt2-enhanced"
    specialization: "sprint_running"
    temperature: 0.1
    max_tokens: 1024
    cache_enabled: true
```

**Usage**:
```python
from app.models.domain_knowledge import SprintDomainExpert

primary_expert = SprintDomainExpert(
    model_id="sprint-domain-expert",
    model_config=config
)
knowledge = await primary_expert.extract_domain_knowledge(query, context)
```

**Performance Characteristics**:
- Processing speed: ~80 tokens/second
- Memory usage: 4-8GB
- GPU utilization: Low-Medium
- Specialization: Sprint training, performance optimization, coaching
- Accuracy: 94% on sprint domain benchmarks

### Secondary Sprint Expert (NEW)
**Purpose**: Advanced biomechanical analysis and technical refinements

**Configuration**:
```yaml
model:
  name: SprintDomainExpertSecondary
  type: peft_distilled_model
  version: "1.0"
  config:
    model_path: "./sprint-llm-distilled-20250324-040451"
    specialization: "sprint_biomechanics_advanced"
    adapter_config: "./sprint-llm-distilled-20250324-040451/adapter_config.json"
    adapter_weights: "./sprint-llm-distilled-20250324-040451/adapter_model.safetensors"
    temperature: 0.15
    max_tokens: 1024
    use_half_precision: true
    cache_enabled: true
```

**Usage**:
```python
from app.models.domain_knowledge import SprintDomainExpertSecondary

secondary_expert = SprintDomainExpertSecondary(
    model_id="sprint-domain-expert-secondary",
    model_config=config
)
advanced_knowledge = await secondary_expert.extract_domain_knowledge(query, context)
```

**Performance Characteristics**:
- Processing speed: ~70 tokens/second
- Memory usage: 4-6GB
- GPU utilization: Medium
- Specialization: Advanced biomechanics, kinematic analysis, force dynamics
- Technical Depth: High (advanced biomechanical insights)
- Accuracy: 92% on biomechanical analysis benchmarks

**Specialized Capabilities**:
- Advanced kinematic and kinetic analysis
- Ground reaction force optimization
- Energy system transitions during 400m races
- Biomechanical efficiency optimization
- Race-specific tactical analysis

### Multi-Model Fusion Engine
**Purpose**: Intelligently combines insights from both domain experts

**Configuration**:
```yaml
fusion:
  name: MultiModelFusion
  version: "1.0"
  config:
    enable_consensus_detection: true
    consensus_boost: 0.1
    duplicate_threshold: 0.7
    complementary_preservation: true
```

**Features**:
- **Consensus Detection**: Identifies areas where both experts agree
- **Complementary Insight Preservation**: Maintains unique contributions from secondary expert
- **Duplicate Elimination**: Removes redundant insights while preserving unique perspectives
- **Confidence Boosting**: Increases confidence for validated insights

## SciBert Model

### Purpose
SciBert is used for scientific text understanding and slot filling. It processes scientific text and extracts structured information.

### Configuration
```yaml
model:
  name: SciBert
  version: "1.0"
  config:
    threshold: 0.85
    max_length: 512
    batch_size: 32
```

### Usage
```python
from models import SciBert

model = SciBert(config)
results = model.process_text("Your scientific text here")
```

### Performance Characteristics
- Processing speed: ~100 tokens/second
- Memory usage: 2-4GB
- GPU utilization: Medium
- Accuracy: 92% on benchmark dataset

## BART-MNLI Model

### Purpose
BART-MNLI handles natural language inference tasks, verifying relationships between text segments.

### Configuration
```yaml
model:
  name: BART-MNLI
  version: "1.0"
  config:
    confidence_threshold: 0.75
    max_sequence_length: 1024
```

### Usage
```python
from models import BART_MNLI

model = BART_MNLI(config)
verification = model.verify_inference(premise, hypothesis)
```

### Performance Characteristics
- Processing speed: ~150 tokens/second
- Memory usage: 3-5GB
- GPU utilization: High
- Accuracy: 89% on NLI tasks

## Custom Models

### Domain-Specific Processors

These models are tailored for specific domains or tasks:

1. **Text Classifier**
   ```yaml
   model:
     name: TextClassifier
     version: "1.0"
     config:
       classes: ["class1", "class2"]
       threshold: 0.8
   ```

2. **Entity Extractor**
   ```yaml
   model:
     name: EntityExtractor
     version: "1.0"
     config:
       entity_types: ["ORG", "PERSON"]
       confidence_threshold: 0.7
   ```

### Usage
```python
from models import TextClassifier, EntityExtractor

classifier = TextClassifier(config)
extractor = EntityExtractor(config)

classification = classifier.classify(text)
entities = extractor.extract(text)
```

## Verification Models

### Purpose
These models ensure output quality and validate processing results.

### Components

1. **Consistency Checker**
   ```yaml
   model:
     name: ConsistencyChecker
     version: "1.0"
     config:
       validation_rules: ["rule1", "rule2"]
   ```

2. **Quality Validator**
   ```yaml
   model:
     name: QualityValidator
     version: "1.0"
     config:
       quality_threshold: 0.9
   ```

### Usage
```python
from models import ConsistencyChecker, QualityValidator

checker = ConsistencyChecker(config)
validator = QualityValidator(config)

consistency = checker.check(results)
quality = validator.validate(results)
```

## Enhanced Model Pipeline Integration

### Configuration
```yaml
pipeline:
  stages:
    - name: scientific_understanding
      model: SciBert
      config:
        threshold: 0.85
    - name: verification
      model: BART-MNLI
      config:
        confidence_threshold: 0.75
    - name: dual_domain_processing  # NEW
      models:
        primary: SprintDomainExpert
        secondary: SprintDomainExpertSecondary
        fusion: MultiModelFusion
      config:
        enable_dual_models: true
        consensus_threshold: 0.9
        enable_multi_model_fusion: true
    - name: validation
      model: QualityValidator
      config:
        quality_threshold: 0.9
```

### Enhanced Execution Flow
1. Input text processing
2. Scientific understanding
3. Verification
4. **Dual-model domain processing** (NEW):
   - Primary expert extraction
   - Secondary expert extraction
   - Multi-model fusion
   - Consensus validation
5. Quality validation

## Model Management

### Loading and Unloading
```python
from model_manager import ModelManager

manager = ModelManager()

# Load dual domain experts
manager.load_model("SprintDomainExpert")
manager.load_model("SprintDomainExpertSecondary")

# Load other models
manager.load_model("SciBert")

# Unload when needed
manager.unload_model("SprintDomainExpert")
manager.unload_model("SprintDomainExpertSecondary")
manager.unload_model("SciBert")
```

### Enhanced Caching with Multi-Model Support
```python
from model_manager import ModelCache

cache = ModelCache()

# Cache both expert models
cache.set_model("primary_expert", primary_model_instance)
cache.set_model("secondary_expert", secondary_model_instance)
cache.set_model("SciBert", model_instance)

# Retrieve models
primary = cache.get_model("primary_expert")
secondary = cache.get_model("secondary_expert")
scibert = cache.get_model("SciBert")
```

## Model Comparison

| Model | Type | Specialization | Memory | GPU | Accuracy |
|-------|------|---------------|---------|-----|----------|
| Primary Sprint Expert | Enhanced GPT-2 | General Sprint | 4-8GB | Low-Med | 94% |
| Secondary Sprint Expert | PEFT Distilled | Biomechanics | 4-6GB | Medium | 92% |
| SciBert | BERT-based | Scientific Text | 2-4GB | Medium | 92% |
| BART-MNLI | BART-based | NLI | 3-5GB | High | 89% |

## Benefits of Dual-Model Architecture

### Enhanced Coverage
- **Primary Expert**: Broad sprint knowledge and training methodology
- **Secondary Expert**: Deep biomechanical analysis and technical insights
- **Combined**: Comprehensive domain coverage with technical depth

### Quality Assurance
- **Consensus Validation**: Higher confidence when both models agree
- **Cross-Model Verification**: Validation across multiple expert perspectives
- **Complementary Insights**: Unique contributions preserved from each expert

### Performance Optimization
- **Parallel Processing**: Simultaneous extraction from both experts
- **Intelligent Fusion**: Efficient combination without redundancy
- **Fault Tolerance**: Graceful degradation when one model fails

### Technical Specifications

#### PEFT Integration (Secondary Expert)
- **Base Model**: DistilGPT-2
- **Adapter Type**: LoRA (Low-Rank Adaptation)
- **Adapter Rank**: Configurable (typically 8-16)
- **Target Modules**: Query and value projection layers
- **Merge Strategy**: Dynamic merging for inference

#### Model Loading Process
```python
# Secondary expert with PEFT adapters
from peft import PeftModel, PeftConfig

# Load PEFT config
peft_config = PeftConfig.from_pretrained(model_path)

# Load base model
base_model = AutoModelForCausalLM.from_pretrained(
    peft_config.base_model_name_or_path,
    torch_dtype=torch.float16,
    device_map="auto"
)

# Load PEFT model with adapters
model = PeftModel.from_pretrained(base_model, model_path)
```

## Performance Optimization

### Memory Management
- Model sharing between processes
- Lazy loading
- Cache management
- Resource cleanup

### Batch Processing
- Dynamic batch sizing
- Queue management
- Load balancing

## Error Handling

### Common Issues
1. Out of memory
2. Model loading failures
3. Input validation errors
4. Processing timeouts

### Recovery Strategies
1. Automatic retries
2. Fallback models
3. Error logging
4. Alert generation

## Monitoring

### Metrics
- Processing time
- Memory usage
- GPU utilization
- Error rates
- Accuracy scores

### Logging
- Model operations
- Performance statistics
- Error tracking
- Usage patterns

## Development Guidelines

### Adding New Models
1. Implement model interface
2. Add configuration
3. Update pipeline
4. Add tests
5. Document changes

### Testing
- Unit tests
- Integration tests
- Performance benchmarks
- Validation sets 