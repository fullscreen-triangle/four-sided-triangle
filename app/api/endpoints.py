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
from app.turbulance import TurbulanceParser, TurbulanceCompiler, TurbulanceOrchestrator

# Configure logging
logger = logging.getLogger(__name__)

# Create routers
router = APIRouter()
query_router = APIRouter(prefix="/query", tags=["query"])
metrics_router = APIRouter(prefix="/metrics", tags=["metrics"])
modeler_router = APIRouter(prefix="/modeler", tags=["modeler"])
turbulance_router = APIRouter(prefix="/turbulance", tags=["turbulance"])

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

class TurbulanceParseRequest(BaseModel):
    """Request model for Turbulance script parsing."""
    script_content: str = Field(..., description="The Turbulance script content to parse")
    protocol_name: str = Field(..., description="Name of the research protocol")
    options: Optional[Dict[str, Any]] = Field(None, description="Parsing options")

class TurbulanceExecuteRequest(BaseModel):
    """Request model for Turbulance protocol execution."""
    script_content: str = Field(..., description="The Turbulance script content to execute")
    protocol_name: str = Field(..., description="Name of the research protocol")
    execution_options: Optional[Dict[str, Any]] = Field(None, description="Execution options")

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

def get_turbulance_orchestrator():
    """Dependency for getting the Turbulance orchestrator."""
    try:
        orchestrator = TurbulanceOrchestrator()
        yield orchestrator
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

# Turbulance DSL Endpoints

@turbulance_router.post("/parse", response_model=ModelResponse)
async def parse_turbulance_script(request: TurbulanceParseRequest):
    """Parse a Turbulance DSL script and return the parsed structure."""
    start_time = time.time()
    logger.info(f"Parsing Turbulance script: {request.protocol_name}")
    
    try:
        parser = TurbulanceParser()
        parsed_script = parser.parse_script(request.script_content, request.protocol_name)
        
        processing_time = time.time() - start_time
        
        return ModelResponse(
            status="success",
            data={
                "protocol_name": parsed_script.protocol_name,
                "nodes": len(parsed_script.nodes),
                "pipeline_calls": len(parsed_script.pipeline_calls),
                "computations": len(parsed_script.computations),
                "variables": len(parsed_script.variables),
                "dependencies": parsed_script.dependencies,
                "parsed_script": parsed_script.__dict__
            },
            processing_time=processing_time,
            metadata={
                "parser_type": "turbulance_dsl",
                "script_length": len(request.script_content)
            }
        )
    
    except Exception as e:
        logger.error(f"Error parsing Turbulance script: {str(e)}", exc_info=True)
        processing_time = time.time() - start_time
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error parsing Turbulance script: {str(e)}"
        )

@turbulance_router.post("/compile", response_model=ModelResponse)
async def compile_turbulance_protocol(request: TurbulanceParseRequest):
    """Compile a Turbulance DSL script into an executable protocol."""
    start_time = time.time()
    logger.info(f"Compiling Turbulance protocol: {request.protocol_name}")
    
    try:
        # Parse the script first
        parser = TurbulanceParser()
        parsed_script = parser.parse_script(request.script_content, request.protocol_name)
        
        # Compile the parsed script
        compiler = TurbulanceCompiler()
        compiled_protocol = compiler.compile_protocol(parsed_script)
        
        processing_time = time.time() - start_time
        
        return ModelResponse(
            status="success",
            data={
                "protocol_name": compiled_protocol.protocol_name,
                "execution_steps": len(compiled_protocol.execution_steps),
                "execution_mode": compiled_protocol.execution_mode.value,
                "total_cpu_estimate": compiled_protocol.resource_allocation.get("total_cpu", 0),
                "total_memory_estimate": compiled_protocol.resource_allocation.get("total_memory", 0),
                "auxiliary_files": list(compiled_protocol.auxiliary_files.keys()),
                "compiled_protocol": compiled_protocol.__dict__
            },
            processing_time=processing_time,
            metadata={
                "compiler_type": "turbulance_dsl",
                "optimization_level": "standard"
            }
        )
    
    except Exception as e:
        logger.error(f"Error compiling Turbulance protocol: {str(e)}", exc_info=True)
        processing_time = time.time() - start_time
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error compiling Turbulance protocol: {str(e)}"
        )

@turbulance_router.post("/execute", response_model=ModelResponse)
async def execute_turbulance_protocol(
    request: TurbulanceExecuteRequest,
    orchestrator: TurbulanceOrchestrator = Depends(get_turbulance_orchestrator)
):
    """Execute a complete Turbulance protocol through the Four-Sided Triangle pipeline."""
    start_time = time.time()
    logger.info(f"Executing Turbulance protocol: {request.protocol_name}")
    
    try:
        # Execute the protocol
        result = await orchestrator.execute_protocol(
            request.script_content, 
            request.protocol_name
        )
        
        processing_time = time.time() - start_time
        
        return ModelResponse(
            status="success" if result.success else "partial_failure",
            data={
                "protocol_name": result.protocol_name,
                "success": result.success,
                "execution_time": result.execution_time,
                "steps_completed": len([r for r in result.step_results if r.success]),
                "steps_failed": len([r for r in result.step_results if not r.success]),
                "annotated_script": result.annotated_script,
                "auxiliary_files": result.auxiliary_files,
                "execution_result": result.__dict__
            },
            processing_time=processing_time,
            metadata={
                "execution_type": "turbulance_protocol",
                "pipeline_integration": "four_sided_triangle"
            }
        )
    
    except Exception as e:
        logger.error(f"Error executing Turbulance protocol: {str(e)}", exc_info=True)
        processing_time = time.time() - start_time
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing Turbulance protocol: {str(e)}"
        )

@turbulance_router.get("/statistics", response_model=ModelResponse)
async def get_turbulance_statistics(
    orchestrator: TurbulanceOrchestrator = Depends(get_turbulance_orchestrator)
):
    """Get execution statistics for the Turbulance orchestrator."""
    start_time = time.time()
    
    try:
        stats = orchestrator.get_execution_stats()
        processing_time = time.time() - start_time
        
        return ModelResponse(
            status="success",
            data=stats,
            processing_time=processing_time,
            metadata={
                "statistics_type": "turbulance_orchestrator",
                "timestamp": time.time()
            }
        )
    
    except Exception as e:
        logger.error(f"Error getting Turbulance statistics: {str(e)}", exc_info=True)
        processing_time = time.time() - start_time
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting Turbulance statistics: {str(e)}"
        )

@turbulance_router.post("/validate", response_model=ModelResponse)
async def validate_turbulance_script(request: TurbulanceParseRequest):
    """Validate a Turbulance DSL script for syntax and structure errors."""
    start_time = time.time()
    logger.info(f"Validating Turbulance script: {request.protocol_name}")
    
    try:
        parser = TurbulanceParser()
        
        # Parse and validate the script
        parsed_script = parser.parse_script(request.script_content, request.protocol_name)
        
        # Run additional validation checks
        validation_errors = []
        warnings = []
        
        # Check for empty pipeline calls
        if not parsed_script.pipeline_calls:
            warnings.append("No pipeline stage calls found in script")
        
        # Check for dependency issues
        for var_name, deps in parsed_script.dependencies.items():
            for dep in deps:
                if dep not in parsed_script.variables:
                    validation_errors.append(f"Undefined dependency '{dep}' for variable '{var_name}'")
        
        processing_time = time.time() - start_time
        
        is_valid = len(validation_errors) == 0
        
        return ModelResponse(
            status="success" if is_valid else "validation_failed",
            data={
                "is_valid": is_valid,
                "validation_errors": validation_errors,
                "warnings": warnings,
                "script_metrics": {
                    "total_lines": len(request.script_content.split('\n')),
                    "pipeline_calls": len(parsed_script.pipeline_calls),
                    "variables": len(parsed_script.variables),
                    "dependencies": len(parsed_script.dependencies)
                }
            },
            processing_time=processing_time,
            metadata={
                "validation_type": "turbulance_dsl",
                "strict_mode": False
            }
        )
    
    except Exception as e:
        logger.error(f"Error validating Turbulance script: {str(e)}", exc_info=True)
        processing_time = time.time() - start_time
        
        return ModelResponse(
            status="validation_error",
            data={
                "is_valid": False,
                "validation_errors": [str(e)],
                "warnings": [],
                "script_metrics": {}
            },
            processing_time=processing_time,
            metadata={
                "validation_type": "turbulance_dsl",
                "error_occurred": True
            }
        )

@router.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Generic exception handler for all routes."""
    logger.error(f"Unhandled exception in {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc) if logger.level <= logging.DEBUG else "An error occurred"
        }
    )

# Register routers
router.include_router(query_router, prefix="/api")
router.include_router(metrics_router, prefix="/api")
router.include_router(modeler_router, prefix="/api") 