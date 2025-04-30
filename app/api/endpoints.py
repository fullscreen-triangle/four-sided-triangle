"""
API Endpoints

This module contains the FastAPI endpoints and route definitions for the
Four-Sided Triangle application.
"""

import logging
import time
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.core.model import DomainExpertModel
from app.core.modeler import Modeler
from app.orchestrator.core import MetacognitiveOrchestrator
from app.orchestrator.interfaces import AbstractPipelineStage
from app.core.stages.stage0_query_processor import QueryProcessorService
from app.core.stages import PIPELINE_STAGES

# Configure logging
logger = logging.getLogger(__name__)

# Create routers
router = APIRouter()
query_router = APIRouter(prefix="/query", tags=["query"])
metrics_router = APIRouter(prefix="/metrics", tags=["metrics"])
modeler_router = APIRouter(prefix="/modeler", tags=["modeler"])

# Define request and response models
class QueryRequest(BaseModel):
    """Request model for query processing."""
    query: str = Field(..., description="The query to process")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for query processing")
    options: Optional[Dict[str, Any]] = Field(None, description="Processing options")

class MetricsRequest(BaseModel):
    """Request model for metrics calculation."""
    parameters: Dict[str, Any] = Field(..., description="Parameters for metrics calculation")
    options: Optional[Dict[str, Any]] = Field(None, description="Calculation options")

class ModelResponse(BaseModel):
    """Generic model response."""
    status: str = Field(..., description="Response status")
    data: Dict[str, Any] = Field(..., description="Response data")
    processing_time: float = Field(..., description="Processing time in seconds")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Response metadata")

# Define dependencies
def get_model():
    """Dependency for getting the domain expert model."""
    try:
        model = DomainExpertModel()
        yield model
    finally:
        # Clean up any resources if needed
        pass

def get_orchestrator():
    """Dependency for getting the metacognitive orchestrator."""
    try:
        orchestrator = MetacognitiveOrchestrator(PIPELINE_STAGES)
        yield orchestrator
    finally:
        # Clean up any resources if needed
        pass

def get_query_processor():
    """Dependency for getting the query processor service."""
    try:
        query_processor = QueryProcessorService()
        yield query_processor
    finally:
        # Clean up any resources if needed
        pass

def get_modeler():
    """Dependency for getting the modeler component."""
    try:
        modeler = Modeler()
        yield modeler
    finally:
        # Clean up any resources if needed
        pass

# Define route handlers
@router.get("/", tags=["general"])
async def root():
    """Root endpoint to check if the API is running."""
    return {"status": "active", "service": "Four-Sided Triangle API"}

@router.get("/health", tags=["general"])
async def health_check():
    """Health check endpoint for monitoring application status."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time()
    }

@query_router.post("/", response_model=ModelResponse)
async def process_query(
    request: QueryRequest,
    orchestrator: MetacognitiveOrchestrator = Depends(get_orchestrator)
):
    """Process a domain expert query through the full pipeline."""
    start_time = time.time()
    logger.info(f"Processing query: {request.query}")
    
    try:
        # Process the query through the orchestrator
        context = request.context or {}
        options = request.options or {}
        
        result = await orchestrator.process_query(
            query=request.query,
            context=context,
            options=options
        )
        
        processing_time = time.time() - start_time
        
        return ModelResponse(
            status="success",
            data=result,
            processing_time=processing_time,
            metadata={
                "pipeline_stages": orchestrator.get_pipeline_info(),
                "query_length": len(request.query)
            }
        )
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        processing_time = time.time() - start_time
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )

@query_router.post("/process", response_model=ModelResponse)
async def process_query_stage(
    request: QueryRequest,
    query_processor: QueryProcessorService = Depends(get_query_processor)
):
    """Process a query through the query processing stage only."""
    start_time = time.time()
    logger.info(f"Processing query through query processor: {request.query}")
    
    try:
        # Process the query through the query processor only
        context = request.context or {}
        
        result = query_processor.process(
            prompt=request.query,
            context=context
        )
        
        processing_time = time.time() - start_time
        
        return ModelResponse(
            status="success",
            data=result,
            processing_time=processing_time,
            metadata={
                "stage": "query_processor",
                "query_length": len(request.query)
            }
        )
    
    except Exception as e:
        logger.error(f"Error in query processing stage: {str(e)}", exc_info=True)
        processing_time = time.time() - start_time
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in query processing stage: {str(e)}"
        )

@metrics_router.post("/", response_model=ModelResponse)
async def calculate_metrics(
    request: MetricsRequest,
    model: DomainExpertModel = Depends(get_model)
):
    """Calculate anthropometric metrics."""
    start_time = time.time()
    logger.info(f"Calculating metrics with parameters: {request.parameters}")
    
    try:
        # Calculate metrics using the model
        result = model.calculate_metrics(
            parameters=request.parameters,
            options=request.options or {}
        )
        
        processing_time = time.time() - start_time
        
        return ModelResponse(
            status="success",
            data=result,
            processing_time=processing_time,
            metadata={
                "parameter_count": len(request.parameters)
            }
        )
    
    except Exception as e:
        logger.error(f"Error calculating metrics: {str(e)}", exc_info=True)
        processing_time = time.time() - start_time
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating metrics: {str(e)}"
        )

@metrics_router.post("/formatted", response_model=ModelResponse)
async def calculate_formatted_metrics(
    request: MetricsRequest,
    model: DomainExpertModel = Depends(get_model)
):
    """Calculate and format anthropometric metrics for display."""
    start_time = time.time()
    logger.info(f"Calculating formatted metrics with parameters: {request.parameters}")
    
    try:
        # Calculate and format metrics
        options = request.options or {}
        options["format"] = True
        
        result = model.calculate_metrics(
            parameters=request.parameters,
            options=options
        )
        
        processing_time = time.time() - start_time
        
        return ModelResponse(
            status="success",
            data=result,
            processing_time=processing_time,
            metadata={
                "parameter_count": len(request.parameters),
                "formatted": True
            }
        )
    
    except Exception as e:
        logger.error(f"Error calculating formatted metrics: {str(e)}", exc_info=True)
        processing_time = time.time() - start_time
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating formatted metrics: {str(e)}"
        )

@modeler_router.post("/", response_model=ModelResponse)
async def process_modeler(
    request: QueryRequest,
    modeler: Modeler = Depends(get_modeler)
):
    """Process a query through the modeler component."""
    start_time = time.time()
    logger.info(f"Processing through modeler: {request.query}")
    
    try:
        # Process through the modeler
        context = request.context or {}
        options = request.options or {}
        
        result = modeler.process_query(
            query=request.query,
            context=context,
            options=options
        )
        
        processing_time = time.time() - start_time
        
        return ModelResponse(
            status="success",
            data=result,
            processing_time=processing_time,
            metadata={
                "modeler_version": modeler.version,
                "query_length": len(request.query)
            }
        )
    
    except Exception as e:
        logger.error(f"Error in modeler processing: {str(e)}", exc_info=True)
        processing_time = time.time() - start_time
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in modeler processing: {str(e)}"
        )

# Exception handler for generic exceptions
@router.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle generic exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": f"An unexpected error occurred: {str(exc)}",
            "path": request.url.path
        }
    )

# Register routers
router.include_router(query_router, prefix="/api")
router.include_router(metrics_router, prefix="/api")
router.include_router(modeler_router, prefix="/api") 