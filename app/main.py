"""
Four-Sided Triangle - Main Application Entry Point

This module serves as the main entry point for the Four-Sided Triangle system.
It initializes the metacognitive orchestrator, registers pipeline stages,
and sets up the FastAPI application.
"""

import logging
import os
import json
from typing import Dict, Any, List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.orchestrator.core import MetacognitiveOrchestrator
from app.orchestrator.working_memory import WorkingMemory
from app.orchestrator.process_monitor import ProcessMonitor
from app.orchestrator.prompt_generator import PromptGenerator

# Import distributed computing components
from backend.distributed.compute_manager import get_compute_manager, ComputeManager
from backend.distributed.compute_helpers import distributed_apply

from app.api.router import router as api_router
from app.utils.utils import format_response

# Configure logging
logging.basicConfig(
    level=logging.INFO if not os.getenv("DEBUG") else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Four-Sided Triangle",
    description="A sophisticated multi-model optimization pipeline for domain-expert knowledge extraction",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load configuration
def load_config():
    """Load application configuration from JSON files"""
    config = {}
    
    # Load pipeline stage configuration
    try:
        with open("app/config/pipeline/stages.json", "r") as f:
            config["stages"] = json.load(f)
    except FileNotFoundError:
        logger.warning("Stage configuration not found, using defaults")
        config["stages"] = {}
    
    # Load orchestrator configuration
    try:
        with open("app/config/pipeline/orchestrator.json", "r") as f:
            config["orchestrator"] = json.load(f)
    except FileNotFoundError:
        logger.warning("Orchestrator configuration not found, using defaults")
        config["orchestrator"] = {}
    
    # Load distributed computing configuration
    try:
        with open("app/config/distributed.json", "r") as f:
            config["distributed"] = json.load(f)
            logger.info("Loaded distributed computing configuration")
    except FileNotFoundError:
        logger.warning("Distributed computing configuration not found, using defaults")
        config["distributed"] = {
            "backend": "local",
            "ray_address": None,
            "dask_scheduler": None,
            "n_local_workers": os.cpu_count()
        }
    
    return config

# Initialize the orchestrator
def initialize_orchestrator(config: Dict[str, Any]):
    """Initialize and configure the metacognitive orchestrator"""
    
    # Create core components
    working_memory = WorkingMemory()
    process_monitor = ProcessMonitor(
        quality_thresholds=config["orchestrator"].get("quality_thresholds", {})
    )
    prompt_generator = PromptGenerator(
        templates_dir=config["orchestrator"].get("templates_dir", "app/orchestrator/templates")
    )
    
    # Create orchestrator instance
    orchestrator = MetacognitiveOrchestrator(
        working_memory=working_memory,
        process_monitor=process_monitor,
        prompt_generator=prompt_generator,
        config=config
    )
    
    # Register pipeline stages
    stages_config = config["stages"]
    for stage_id, stage_config in stages_config.items():
        if stage_config.get("enabled", True):
            try:
                orchestrator.register_stage(
                    stage_id=stage_id,
                    stage_config=stage_config
                )
                logger.info(f"Registered pipeline stage: {stage_id}")
            except Exception as e:
                logger.error(f"Failed to register stage {stage_id}: {str(e)}")
    
    logger.info(f"Orchestrator initialized with {len(orchestrator.stages)} stages")
    return orchestrator

# Initialize distributed computing
def initialize_distributed_computing(config: Dict[str, Any]) -> ComputeManager:
    """Initialize distributed computing backend"""
    distributed_config = config.get("distributed", {})
    
    # Create compute manager with configuration
    compute_manager = get_compute_manager(
        backend=distributed_config.get("backend"),
        ray_address=distributed_config.get("ray_address"),
        dask_scheduler=distributed_config.get("dask_scheduler"),
        n_local_workers=distributed_config.get("n_local_workers")
    )
    
    logger.info(f"Distributed computing initialized with backend: {compute_manager.backend}")
    return compute_manager

# Create dependency for accessing orchestrator
def get_orchestrator():
    """Dependency to get the orchestrator instance"""
    return app.state.orchestrator

# Create dependency for accessing compute manager
def get_compute():
    """Dependency to get the compute manager instance"""
    return app.state.compute_manager

# Register API routes
app.include_router(api_router, prefix="/api")

# Add health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return format_response({
        "status": "ok", 
        "service": "four-sided-triangle",
        "distributed_backend": app.state.compute_manager.backend if hasattr(app.state, "compute_manager") else "not_initialized"
    })

# Add debug info endpoint
@app.get("/debug/pipeline-info")
async def pipeline_info(orchestrator: MetacognitiveOrchestrator = Depends(get_orchestrator)):
    """Get debug information about the pipeline configuration"""
    return format_response({
        "registered_stages": list(orchestrator.stages.keys()),
        "active_sessions": orchestrator.working_memory.list_sessions(),
        "configuration": orchestrator.config
    })

# Add distributed computing info endpoint
@app.get("/debug/distributed-info")
async def distributed_info(compute_manager: ComputeManager = Depends(get_compute)):
    """Get information about the distributed computing setup"""
    return format_response({
        "backend": compute_manager.backend,
        "ray_address": compute_manager.ray_address,
        "dask_scheduler": compute_manager.dask_scheduler,
        "active_jobs": len(compute_manager.active_jobs),
        "local_workers": compute_manager.n_local_workers
    })

# Application startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    logger.info("Starting Four-Sided Triangle system")
    
    # Load configuration
    config = load_config()
    logger.info("Configuration loaded")
    
    # Initialize distributed computing
    compute_manager = initialize_distributed_computing(config)
    app.state.compute_manager = compute_manager
    logger.info("Distributed computing initialized")
    
    # Initialize orchestrator
    orchestrator = initialize_orchestrator(config)
    app.state.orchestrator = orchestrator
    
    # Validate pipeline configuration
    await orchestrator.validate_pipeline()
    logger.info("Pipeline validation completed")
    
    logger.info("Four-Sided Triangle system started successfully")

# Application shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    logger.info("Shutting down Four-Sided Triangle system")
    
    # Clean up orchestrator resources
    if hasattr(app.state, "orchestrator"):
        await app.state.orchestrator.cleanup()
    
    # Shutdown distributed computing
    if hasattr(app.state, "compute_manager"):
        app.state.compute_manager.shutdown()
        logger.info("Distributed computing resources released")
    
    logger.info("Shutdown complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )
