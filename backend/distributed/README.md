# Distributed Computing Module

This module provides a framework for distributed computing with support for Ray and Dask backends. It allows the application to scale horizontally across multiple machines, making it suitable for compute-intensive tasks like machine learning model training and inference.

## Overview

The distributed computing module consists of several components:

1. **ComputeManager**: Core class that manages connections to distributed backends and dispatches tasks.
2. **MLTasks**: Specialized class for distributed machine learning tasks like model training and prediction.
3. **ModelRegistry**: Service for storing, retrieving, and managing machine learning models.
4. **Compute Helpers**: Utility functions that simplify common distributed computing patterns.

## Setup

### Requirements

To use the distributed computing module, you need:

- Python 3.8+
- Ray (optional but recommended): `pip install ray[default]`
- Dask (optional): `pip install dask distributed`
- Machine learning libraries: scikit-learn, pandas, numpy
- Optional: XGBoost, LightGBM

### Configuration

The system uses a configuration file (`config.json`) to specify:

- Backend preferences (Ray or Dask)
- Cluster addresses
- Resource limits
- Scaling parameters
- Monitoring settings

Example configuration:

```json
{
  "compute": {
    "backend": "ray",
    "ray_address": "ray://localhost:10001",
    "dask_address": "localhost:8786",
    "local_workers": 4,
    "cpu_limit": 16,
    "memory_limit": "32g",
    "gpu_limit": 2
  },
  "clusters": [
    {
      "name": "primary",
      "host": "compute-primary.example.com",
      "port": 10001,
      "type": "ray",
      "resources": {
        "cpu": 32,
        "memory": "128g",
        "gpu": 4
      }
    },
    {
      "name": "analytics",
      "host": "compute-analytics.example.com",
      "port": 8786,
      "type": "dask",
      "resources": {
        "cpu": 16,
        "memory": "64g"
      }
    }
  ],
  "task_defaults": {
    "timeout": 3600,
    "retries": 3,
    "backoff_factor": 1.5
  },
  "scaling": {
    "min_workers": 2,
    "max_workers": 20,
    "target_utilization": 0.8,
    "scale_up_delay": 30,
    "scale_down_delay": 300
  },
  "monitoring": {
    "enabled": true,
    "dashboard": {
      "ray": true,
      "dask": true
    },
    "metrics_retention": {
      "days": 7
    }
  }
}
```

## Usage

### Basic Task Submission

```python
from app.distributed.compute_manager import get_compute_manager

# Get compute manager
compute = get_compute_manager()

# Define a function to run remotely
def process_data(data):
    # Complex processing here
    return result

# Submit task
task_id = compute.submit_task(process_data, input_data)

# Get result when ready
result = compute.get_result(task_id)
```

### ML Tasks

```python
from app.distributed.ml_tasks import get_ml_tasks
import pandas as pd

# Get ML tasks manager
ml_tasks = get_ml_tasks()

# Train a model
training_data = pd.read_csv("training_data.csv")
model_result = ml_tasks.train_model(
    data=training_data,
    target_col="target",
    features=["feature1", "feature2", "feature3"],
    model_type="xgboost",
    distribute_data=True
)

# Make predictions
prediction_data = pd.read_csv("prediction_data.csv")
predictions = ml_tasks.predict_batch(
    model_id=model_result["model_id"],
    data=prediction_data,
    batch_size=10000,
    distributed=True
)
```

### Using Compute Helpers

```python
from app.distributed.compute_helpers import distributed_apply
import pandas as pd

# Load large dataset
data = pd.read_csv("large_dataset.csv")

# Define function to apply to data partitions
def calculate_statistics(partition):
    return {
        "mean": partition["value"].mean(),
        "std": partition["value"].std(),
        "min": partition["value"].min(),
        "max": partition["value"].max(),
        "count": len(partition)
    }

# Apply function in distributed manner
results = distributed_apply(
    calculate_statistics,
    data,
    partition_size=10000
)
```

### Managing Models

```python
from app.distributed.model_registry import get_model_registry

# Get model registry
registry = get_model_registry()

# Register a model
model_id = registry.register_model(
    model_obj=trained_model,
    model_type="random_forest",
    metadata={"description": "Fraud detection model", "version": "1.0.0"},
    tags=["fraud", "production"]
)

# Load a model
model_data = registry.load_model(model_id)

# Update model metadata
registry.update_model_metadata(
    model_id=model_id,
    updates={"status": "deprecated", "metrics": {"accuracy": 0.95}}
)

# List models
models = registry.list_models(
    model_type="random_forest",
    tags=["fraud"],
    status="active"
)
```

## Integration with Solver

The distributed computing module integrates with the solver service, allowing complex computational tasks to be distributed across multiple machines:

```python
from app.solver.solver_service import get_solver_service

# Get solver service
solver = get_solver_service()

# Solve a problem using distributed computing
result = solver.solve(
    query_data={
        "type": "prediction",
        "entities": [...]
    },
    parameters={
        "model_type": "xgboost",
        "distribute_data": True
    }
)
```

## API Endpoints

The distributed computing module exposes several API endpoints:

- `/solver/solve`: Submit a solver task
- `/solver/task/{task_id}`: Get the status of a task
- `/solver/solve-sync`: Synchronous solver endpoint
- `/models/`: List models in the registry
- `/models/search`: Search for models
- `/models/{model_id}`: Get model metadata
- `/models/{model_id}`: Update model metadata (PATCH)
- `/models/{model_id}`: Delete a model (DELETE)
- `/models/upload`: Upload a model

## Scaling Considerations

For optimal performance in production:

1. Deploy Ray or Dask clusters on dedicated machines
2. Configure resource limits based on available hardware
3. Use auto-scaling to handle variable workloads
4. Monitor system performance and adjust parameters as needed
5. Consider using persistent storage for models (e.g., S3, GCS)

## Troubleshooting

Common issues:

- **Connection refused**: Check that the Ray/Dask clusters are running and accessible
- **Task timeout**: Increase timeout for long-running tasks
- **Out of memory**: Reduce batch sizes or increase memory allocation
- **Serialization errors**: Ensure all objects passed to remote tasks are serializable

## License

This module is part of the Four Sided Triangle project and is subject to the same licensing terms. 