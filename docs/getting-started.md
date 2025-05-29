---
layout: default
title: Getting Started
nav_order: 2
---

# Getting Started with Four Sided Triangle

This guide will help you get up and running with Four Sided Triangle quickly.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- Docker and Docker Compose (for containerized deployment)
- Git

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/four-sided-triangle.git
cd four-sided-triangle
```

2. Set up a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Using Docker (Recommended)

1. Build and start the containers:
```bash
docker-compose up --build
```

2. Access the web interface at `http://localhost:3000`

### Manual Setup

1. Start the backend API:
```bash
python run_api.py
```

2. In a new terminal, start the frontend:
```bash
cd frontend
npm install
npm start
```

## Basic Configuration

The system can be configured through several key files:

1. `config/pipeline.yaml`: Define your processing pipeline
2. `config/models.yaml`: Configure model parameters
3. `config/api.yaml`: API settings

Example pipeline configuration:
```yaml
pipeline:
  stages:
    - name: input_processing
      model: SciBert
      config:
        threshold: 0.85
    - name: verification
      model: BART-MNLI
      config:
        confidence_threshold: 0.75
```

## Running Your First Pipeline

1. Prepare your input data in the required format
2. Use the API endpoint to submit a processing request:
```bash
curl -X POST http://localhost:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Your input text here"}'
```

## Next Steps

- Read the [Architecture Overview](/architecture) to understand the system design
- Explore available [Models](/models) and their capabilities
- Learn how to [customize the pipeline](/pipeline)
- Check out the complete [API Reference](/api-reference)

## Troubleshooting

Common issues and their solutions:

1. **Model loading errors**:
   - Ensure all model weights are downloaded
   - Check model configuration paths

2. **API connection issues**:
   - Verify the API is running
   - Check port configurations

3. **Pipeline errors**:
   - Validate pipeline configuration
   - Check model compatibility

For more detailed troubleshooting, consult the [GitHub issues](https://github.com/yourusername/four-sided-triangle/issues). 