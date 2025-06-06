---
layout: default
title: Getting Started
nav_order: 2
---

# Getting Started with Four-Sided Triangle

Welcome to Four-Sided Triangle! This guide will help you get up and running with the sophisticated multi-model optimization pipeline for domain-expert knowledge extraction.

## Overview

Four-Sided Triangle is designed to overcome the limitations of traditional RAG systems through a novel recursive optimization methodology. The system employs a metacognitive orchestration layer that manages an 8-stage specialized pipeline, dynamically selecting between LLM-based reasoning and traditional mathematical solvers.

---

## Prerequisites

Before you begin, ensure you have the following installed:

### System Requirements

- **Operating System**: Linux, macOS, or Windows 10/11
- **Python**: 3.10 or higher
- **Memory**: 32GB RAM minimum (64GB recommended for optimal performance)
- **Storage**: 50GB free disk space for models and data
- **GPU**: CUDA-capable GPU with 16GB+ VRAM (recommended but not required)

### Software Dependencies

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Git**: For cloning the repository
- **CUDA Toolkit**: 11.8 or higher (if using GPU acceleration)

### API Keys (Optional)

For enhanced functionality, you may need:
- **Hugging Face API key**: For accessing certain models
- **OpenAI API key**: For fallback processing (optional)

---

## Installation Options

### Option 1: Quick Start with Docker (Recommended)

This is the fastest way to get Four-Sided Triangle running:

```bash
# Clone the repository
git clone https://github.com/your-org/four-sided-triangle.git
cd four-sided-triangle

# Start the application with Docker Compose
docker-compose up -d

# Verify the installation
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "four-sided-triangle",
  "distributed_backend": "ray",
  "pipeline_stages": 8
}
```

### Option 2: Local Development Setup

For development or customization:

```bash
# Clone the repository
git clone https://github.com/your-org/four-sided-triangle.git
cd four-sided-triangle

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up configuration
cp app/config/example.env .env
# Edit .env file with your settings

# Initialize the database (if using persistent storage)
python -m app.core.init_db

# Start the application
python -m app.main
```

### Option 3: Kubernetes Deployment

For production environments:

```bash
# Apply Kubernetes configurations
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n four-sided-triangle

# Access via load balancer
kubectl get services -n four-sided-triangle
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Application Settings
APP_NAME=four-sided-triangle
DEBUG=false
LOG_LEVEL=INFO

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Model Configuration
MODEL_CACHE_DIR=./models
ENABLE_GPU=true
GPU_MEMORY_FRACTION=0.8

# Pipeline Settings
PIPELINE_TIMEOUT=300
QUALITY_THRESHOLD=0.8
MAX_REFINEMENT_LOOPS=3

# Distributed Computing
DISTRIBUTED_BACKEND=ray
RAY_ADDRESS=auto
DASK_SCHEDULER_ADDRESS=localhost:8786

# Database (if using persistent storage)
DATABASE_URL=sqlite:///./four_sided_triangle.db

# Optional API Keys
HUGGINGFACE_API_KEY=your_hf_key_here
OPENAI_API_KEY=your_openai_key_here
```

### Configuration Files

The system uses JSON configuration files in `app/config/`:

#### Pipeline Configuration (`app/config/pipeline/stages.json`)
```json
{
  "stages": {
    "query_processor": {
      "enabled": true,
      "models": ["phi-3-mini", "mixtral", "scibert"],
      "timeout": 30,
      "quality_threshold": 0.8
    },
    "semantic_atdb": {
      "enabled": true,
      "models": ["bge-reranker"],
      "timeout": 20,
      "quality_threshold": 0.75
    }
    // ... additional stage configurations
  }
}
```

#### Orchestrator Configuration (`app/config/pipeline/orchestrator.json`)
```json
{
  "working_memory": {
    "session_timeout": 3600,
    "max_concurrent_sessions": 100,
    "cleanup_interval": 300
  },
  "process_monitor": {
    "quality_dimensions": ["completeness", "consistency", "confidence", "compliance", "correctness"],
    "refinement_triggers": ["quality_below_threshold", "inconsistency_detected"],
    "max_refinement_loops": 3
  }
}
```

---

## First Steps

### 1. Verify Installation

Test that all components are working:

```bash
# Check system health
curl http://localhost:8000/health

# Check pipeline configuration
curl http://localhost:8000/debug/pipeline-info

# Check distributed computing status
curl http://localhost:8000/debug/distributed-info
```

### 2. Process Your First Query

#### Using cURL

```bash
curl -X POST "http://localhost:8000/api/process" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What are the optimal biomechanical factors for improving sprint acceleration in elite athletes?",
       "options": {
         "domain": "sports_science",
         "detail_level": "expert",
         "include_references": true
       }
     }'
```

#### Using Python Client

```python
import requests

# Submit a query
response = requests.post(
    "http://localhost:8000/api/process",
    json={
        "query": "What are the optimal biomechanical factors for improving sprint acceleration?",
        "options": {
            "domain": "sports_science",
            "detail_level": "expert"
        }
    }
)

result = response.json()
print(f"Solutions found: {len(result['solutions'])}")
for i, solution in enumerate(result['solutions']):
    print(f"Solution {i+1}: {solution['content'][:100]}...")
```

### 3. Explore the Web Interface (Optional)

If you have the frontend enabled:

1. Open your browser to `http://localhost:3000`
2. Enter a query in the input field
3. Select options and submit
4. Monitor processing progress in real-time
5. Explore multiple solution candidates

---

## Understanding the System

### Pipeline Stages Overview

The system processes queries through 8 specialized stages:

1. **Query Processor**: Transforms natural language queries into structured representations
2. **Semantic ATDB**: Performs semantic transformation and throttle detection
3. **Domain Knowledge**: Extracts and organizes domain-specific knowledge
4. **Parallel Reasoning**: Applies mathematical and logical reasoning
5. **Solution Generation**: Produces candidate solutions from reasoning outputs
6. **Response Scoring**: Evaluates solutions using quality metrics
7. **Ensemble Diversification**: Creates diverse, high-quality solution sets
8. **Threshold Verification**: Performs final verification against quality standards

### Quality Assurance

Each stage evaluates output quality across five dimensions:
- **Completeness**: Contains all required elements
- **Consistency**: Internally coherent
- **Confidence**: System confidence in output
- **Compliance**: Meets domain requirements
- **Correctness**: Factually accurate

### Specialized Models

Different models are used for different stages:
- **Query Processing**: Phi-3-mini, Mixtral, SciBERT
- **Domain Knowledge**: BioMedLM, Mixtral, Phi-3-mini
- **Mathematical Reasoning**: Qwen, DeepSeek Math
- **Quality Assessment**: OpenAssistant Reward Model
- **Diversity Scoring**: BGE Reranker M3

---

## Common Workflows

### Research Query Processing

For academic or research queries:

```bash
curl -X POST "http://localhost:8000/api/process" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "Analyze the relationship between ground contact time and sprint velocity in competitive sprinting",
       "options": {
         "domain": "biomechanics",
         "detail_level": "research",
         "include_citations": true,
         "quality_threshold": 0.9
       }
     }'
```

### Optimization Problem Solving

For mathematical optimization:

```bash
curl -X POST "http://localhost:8000/api/process" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "Optimize training load distribution for a 400m sprinter over 12-week macrocycle",
       "options": {
         "domain": "training_optimization", 
         "include_mathematical_models": true,
         "optimization_objectives": ["performance", "injury_risk", "adaptation"]
       }
     }'
```

### Asynchronous Processing

For long-running queries:

```python
import requests
import time

# Submit async query
response = requests.post(
    "http://localhost:8000/api/async/process",
    json={
        "query": "Comprehensive biomechanical analysis of sprint technique variations",
        "options": {"domain": "biomechanics"},
        "callback_url": "https://your-app.com/webhook"  # Optional
    }
)

task_id = response.json()["task_id"]

# Poll for results
while True:
    status_response = requests.get(f"http://localhost:8000/api/tasks/{task_id}")
    status = status_response.json()
    
    if status["status"] == "completed":
        print("Results:", status["result"])
        break
    elif status["status"] == "failed":
        print("Error:", status["error"])
        break
    
    time.sleep(5)  # Wait 5 seconds before checking again
```

---

## Troubleshooting

### Common Issues

#### 1. Models Not Loading
```
Error: Failed to load model 'phi-3-mini'
```

**Solution**: Check available disk space and memory:
```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check model cache directory
ls -la ./models/
```

#### 2. GPU Out of Memory
```
Error: CUDA out of memory
```

**Solutions**:
- Reduce `GPU_MEMORY_FRACTION` in `.env`
- Enable model offloading: `ENABLE_MODEL_OFFLOADING=true`
- Use CPU-only mode: `ENABLE_GPU=false`

#### 3. Pipeline Timeout
```
Error: Pipeline processing timed out
```

**Solutions**:
- Increase `PIPELINE_TIMEOUT` in configuration
- Reduce `QUALITY_THRESHOLD` for faster processing
- Check system resources and load

#### 4. Quality Below Threshold
```
Warning: Output quality below threshold, triggering refinement
```

This is normal behavior. The system will automatically attempt refinement. To adjust:
- Lower `QUALITY_THRESHOLD` for more lenient evaluation
- Increase `MAX_REFINEMENT_LOOPS` for more attempts

### Getting Help

- **Documentation**: Browse the full documentation at [project-docs-url]
- **Issues**: Report bugs on [GitHub Issues](https://github.com/your-org/four-sided-triangle/issues)
- **Discussions**: Join [GitHub Discussions](https://github.com/your-org/four-sided-triangle/discussions)
- **Discord**: Join our community server [discord-link]

---

## Next Steps

Now that you have Four-Sided Triangle running:

1. **Explore the Architecture**: Read the [System Architecture](architecture) documentation
2. **Understand Pipeline Stages**: Review each [Pipeline Stage](pipeline) in detail
3. **API Reference**: Check the complete [API Reference](api-reference) 
4. **Customize Configuration**: Learn about [Configuration Options](configuration)
5. **Contribute**: See our [Contributing Guidelines](contributing) to get involved

---

## Performance Tips

### Optimization Recommendations

1. **Resource Allocation**:
   - Use GPU acceleration when available
   - Allocate sufficient RAM (64GB+ for large models)
   - Use SSD storage for model cache

2. **Configuration Tuning**:
   - Adjust quality thresholds based on your use case
   - Configure appropriate timeouts for your queries
   - Enable caching for repeated queries

3. **Distributed Processing**:
   - Use Ray for multi-node scaling
   - Configure worker processes based on available cores
   - Monitor resource utilization

4. **Model Selection**:
   - Use lighter models for development/testing
   - Reserve heavy models for production workloads
   - Consider model quantization for memory savings

---

Welcome to Four-Sided Triangle! You're now ready to process complex domain-expert queries with our sophisticated multi-model optimization pipeline. 