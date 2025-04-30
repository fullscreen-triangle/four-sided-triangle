"""
Modeler API Service

FastAPI-based backend service that handles modeler requests from the frontend.
Integrates with the distributed compute framework to process modeler tasks.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
import logging
import json
import uuid
import os
from datetime import datetime

from .compute_manager import ComputeManager, get_compute_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the FastAPI app
app = FastAPI(
    title="RAG Modeler API",
    description="API for distributed modeling in RAG applications",
    version="1.0.0"
)

# Model definitions
class EntityAttributes(BaseModel):
    name: str
    value: str

class ModelEntity(BaseModel):
    id: str
    name: str
    type: str
    description: str
    attributes: List[str] = Field(default_factory=list)
    confidence: float

class ModelRelationship(BaseModel):
    id: str
    source_entity_id: str
    target_entity_id: str
    type: str
    description: str
    strength: float
    direction: str
    confidence: float

class ModelParameter(BaseModel):
    id: str
    name: str
    description: str
    data_type: str
    unit: Optional[str] = None
    range: Optional[Dict[str, float]] = None
    default_value: Optional[Any] = None
    related_entity_ids: List[str]
    formula: Optional[str] = None
    confidence: float

class DomainContext(BaseModel):
    domain: str
    subdomain: Optional[str] = None
    constraints: Optional[List[str]] = None
    assumptions: Optional[List[str]] = None

class ModelMetadata(BaseModel):
    created_at: str
    updated_at: str
    version: str
    confidence_score: float

class ModelVisualization(BaseModel):
    graph_data: Optional[Dict[str, Any]] = None
    chart_data: Optional[Dict[str, Any]] = None

class ModelData(BaseModel):
    id: str
    query: str
    entities: List[ModelEntity]
    relationships: List[ModelRelationship]
    parameters: List[ModelParameter]
    domain_context: Optional[DomainContext] = None
    metadata: ModelMetadata
    visualization: Optional[ModelVisualization] = None

class ConfidenceScores(BaseModel):
    overall: float
    entities: float
    relationships: float
    parameters: float

class ModelValidationResults(BaseModel):
    valid: bool
    issues: List[str]
    warnings: List[str]
    suggestions: List[str]
    confidence_scores: ConfidenceScores

# Request and response models
class EntityExtractionRequest(BaseModel):
    query: str
    context: Dict[str, Any] = Field(default_factory=dict)
    options: Dict[str, Any] = Field(default_factory=dict)

class EntityExtractionResponse(BaseModel):
    entities: List[ModelEntity]
    processing_time: float

class RelationshipMappingRequest(BaseModel):
    entities: List[ModelEntity]
    query: str
    options: Dict[str, Any] = Field(default_factory=dict)

class RelationshipMappingResponse(BaseModel):
    relationships: List[ModelRelationship]
    processing_time: float

class ParameterIdentificationRequest(BaseModel):
    query: str
    entities: List[ModelEntity]
    relationships: List[ModelRelationship]
    options: Dict[str, Any] = Field(default_factory=dict)

class ParameterIdentificationResponse(BaseModel):
    parameters: List[ModelParameter]
    processing_time: float

class ModelIntegrationRequest(BaseModel):
    model_data: Dict[str, Any]
    options: Dict[str, Any] = Field(default_factory=dict)

class ModelIntegrationResponse(BaseModel):
    integrated_model: ModelData
    processing_time: float

class ModelValidationRequest(BaseModel):
    model: ModelData
    validation_level: str = "detailed"

class ModelValidationResponse(BaseModel):
    validation_results: ModelValidationResults
    processing_time: float

class ModelProcessingRequest(BaseModel):
    query: str
    options: Dict[str, Any] = Field(default_factory=dict)

class ModelProcessingResponse(BaseModel):
    model: ModelData
    validation_results: Optional[ModelValidationResults] = None
    processing_time: float

# Helper functions
def generate_id() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())

def create_metadata() -> Dict[str, Any]:
    """Create model metadata"""
    now = datetime.now().isoformat()
    return {
        "created_at": now,
        "updated_at": now,
        "version": "1.0.0",
        "confidence_score": 0.0
    }

# Define the task functions for distributed processing
def extract_entities_task(query: str, context: Dict[str, Any], options: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Task function for entity extraction using NLP models
    
    Args:
        query: The user query text
        context: Additional context information
        options: Processing options
        
    Returns:
        List of extracted entities
    """
    import time
    import random
    from .compute_helpers import process_nlp_model_request
    
    # Start timing
    start_time = time.time()
    
    # Use process_nlp_model_request from compute_helpers to handle the NLP model call
    try:
        system_prompt = """
        You are an entity extraction system for a sports science platform focusing on sprint performance.
        Extract all domain-relevant entities from the user query. For each entity, identify:
        1. Entity name (the actual term or phrase)
        2. Entity type (person, measurement, body_part, performance_metric, genetic_marker, etc.)
        3. Description (brief explanation of what this entity represents)
        4. Attributes (any properties or characteristics mentioned)
        5. Confidence score (0.0-1.0 on how certain you are this is a domain entity)
        
        Return a JSON array of entities with these properties.
        """
        
        user_prompt = f"""
        Query: {query}
        
        Context: {json.dumps(context)}
        
        Extract all relevant entities from this query following the format in your instructions.
        """
        
        # Call LLM model endpoint through helper
        response = process_nlp_model_request(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model_name=options.get("model", "gpt-4-turbo"),
            temperature=options.get("temperature", 0.3),
            response_format="json"
        )
        
        # Parse the response
        entities_data = json.loads(response)
        
        # Add ids if not present
        for entity in entities_data:
            if "id" not in entity:
                entity["id"] = generate_id()
        
        return entities_data
    except Exception as e:
        logger.error(f"Error in entity extraction task: {str(e)}")
        # Return minimal data as fallback
        return [{
            "id": generate_id(),
            "name": query.split()[0] if query.split() else "unknown",
            "type": "unknown",
            "description": f"Error occurred: {str(e)}",
            "attributes": [],
            "confidence": 0.1
        }]

def map_relationships_task(entities: List[Dict[str, Any]], 
                           query: str, 
                           options: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Task function for mapping relationships between entities
    
    Args:
        entities: List of extracted entities
        query: The original user query
        options: Processing options
        
    Returns:
        List of mapped relationships
    """
    import time
    from .compute_helpers import process_nlp_model_request
    
    # Start timing
    start_time = time.time()
    
    try:
        # Create system prompt for relationship mapping
        system_prompt = """
        You are a relationship mapping system for sports science data.
        Identify relationships between entities. For each relationship, specify:
        1. Source entity ID
        2. Target entity ID
        3. Relationship type (causal, correlation, part_of, etc.)
        4. Description of the relationship
        5. Strength (0.0-1.0 with 1.0 being strongest)
        6. Direction ('one_way', 'bidirectional', or 'none')
        7. Confidence (0.0-1.0 on how certain you are)
        
        Return a JSON array of relationships.
        """
        
        user_prompt = f"""
        Query: {query}
        
        Entities:
        {json.dumps(entities, indent=2)}
        
        Identify all meaningful relationships between these entities following the format in your instructions.
        Focus on relationships that would be relevant to answering the original query.
        """
        
        # Call LLM model endpoint through helper
        response = process_nlp_model_request(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model_name=options.get("model", "gpt-4-turbo"),
            temperature=options.get("temperature", 0.3),
            response_format="json"
        )
        
        # Parse the response
        relationships_data = json.loads(response)
        
        # Add ids if not present
        for relationship in relationships_data:
            if "id" not in relationship:
                relationship["id"] = generate_id()
        
        return relationships_data
    except Exception as e:
        logger.error(f"Error in relationship mapping task: {str(e)}")
        # Return minimal data as fallback
        return [] if not entities else [{
            "id": generate_id(),
            "source_entity_id": entities[0]["id"],
            "target_entity_id": entities[-1]["id"] if len(entities) > 1 else entities[0]["id"],
            "type": "unknown",
            "description": f"Error occurred: {str(e)}",
            "strength": 0.1,
            "direction": "none",
            "confidence": 0.1
        }]

def identify_parameters_task(query: str, 
                            entities: List[Dict[str, Any]], 
                            relationships: List[Dict[str, Any]], 
                            options: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Task function for identifying parameters in the model
    
    Args:
        query: The user query
        entities: Extracted entities
        relationships: Mapped relationships
        options: Processing options
        
    Returns:
        List of identified parameters
    """
    import time
    from .compute_helpers import process_nlp_model_request
    
    # Start timing
    start_time = time.time()
    
    try:
        # Create system prompt for parameter identification
        system_prompt = """
        You are a parameter identification system for sports science models.
        Identify measurable parameters that relate to the entities and their relationships.
        For each parameter, specify:
        1. Name
        2. Description
        3. Data type (numeric, categorical, boolean, etc.)
        4. Unit (if applicable)
        5. Range (if applicable)
        6. Default value (if applicable)
        7. Related entity IDs
        8. Formula (if applicable)
        9. Confidence (0.0-1.0 on how certain you are)
        
        Return a JSON array of parameters.
        """
        
        user_prompt = f"""
        Query: {query}
        
        Entities:
        {json.dumps(entities, indent=2)}
        
        Relationships:
        {json.dumps(relationships, indent=2)}
        
        Identify all relevant parameters for these entities and relationships following the format in your instructions.
        Focus on parameters that would be necessary to model the domain concepts in the query.
        """
        
        # Call LLM model endpoint through helper
        response = process_nlp_model_request(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model_name=options.get("model", "gpt-4-turbo"),
            temperature=options.get("temperature", 0.3),
            response_format="json"
        )
        
        # Parse the response
        parameters_data = json.loads(response)
        
        # Add ids if not present
        for parameter in parameters_data:
            if "id" not in parameter:
                parameter["id"] = generate_id()
        
        return parameters_data
    except Exception as e:
        logger.error(f"Error in parameter identification task: {str(e)}")
        # Return minimal data as fallback
        return [] if not entities else [{
            "id": generate_id(),
            "name": f"Parameter for {entities[0]['name']}",
            "description": f"Error occurred: {str(e)}",
            "data_type": "numeric",
            "related_entity_ids": [entities[0]["id"]],
            "confidence": 0.1
        }]

def integrate_model_task(model_data: Dict[str, Any], 
                         options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Task function for integrating model components
    
    Args:
        model_data: Partial model data to integrate
        options: Processing options
        
    Returns:
        Integrated model data
    """
    import time
    import copy
    from .compute_helpers import process_nlp_model_request
    
    # Start timing
    start_time = time.time()
    
    # Create a deep copy to avoid modifying the original
    integrated_model = copy.deepcopy(model_data)
    
    # Generate a unique ID if not present
    if "id" not in integrated_model:
        integrated_model["id"] = generate_id()
    
    # Create metadata if not present
    if "metadata" not in integrated_model:
        integrated_model["metadata"] = create_metadata()
    else:
        # Update the timestamp
        integrated_model["metadata"]["updated_at"] = datetime.now().isoformat()
    
    # Ensure all required fields exist
    if "entities" not in integrated_model:
        integrated_model["entities"] = []
    if "relationships" not in integrated_model:
        integrated_model["relationships"] = []
    if "parameters" not in integrated_model:
        integrated_model["parameters"] = []
    
    # Enrich with domain knowledge if requested
    if options.get("enrich_with_domain_knowledge", False) and "query" in integrated_model:
        try:
            # Create system prompt for domain enrichment
            system_prompt = """
            You are a domain knowledge enrichment system for sports science models.
            Based on the provided model, add domain-specific context, constraints, and assumptions.
            Focus on enhancing the model with domain-specific knowledge relevant to sprint performance.
            Return a JSON object with domain context information including:
            1. Domain name
            2. Subdomain (if applicable)
            3. Constraints (list of relevant domain constraints)
            4. Assumptions (list of assumptions made in the model)
            """
            
            user_prompt = f"""
            Query: {integrated_model.get('query', '')}
            
            Model Data:
            {json.dumps(integrated_model, indent=2)}
            
            Analyze this model and provide domain-specific enrichment following the format in your instructions.
            """
            
            # Call LLM model endpoint
            response = process_nlp_model_request(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model_name=options.get("model", "gpt-4-turbo"),
                temperature=options.get("temperature", 0.3),
                response_format="json"
            )
            
            # Parse the response and update domain context
            domain_data = json.loads(response)
            integrated_model["domain_context"] = domain_data
        except Exception as e:
            logger.error(f"Error in domain enrichment: {str(e)}")
            # Create basic domain context as fallback
            integrated_model["domain_context"] = {
                "domain": "sports_science",
                "assumptions": ["Model may contain errors due to enrichment failure"]
            }
    
    # Calculate confidence score
    confidence_score = 0.0
    count = 0
    
    if integrated_model["entities"]:
        entity_confidence = sum(e.get("confidence", 0.0) for e in integrated_model["entities"]) / len(integrated_model["entities"])
        confidence_score += entity_confidence
        count += 1
    
    if integrated_model["relationships"]:
        relationship_confidence = sum(r.get("confidence", 0.0) for r in integrated_model["relationships"]) / len(integrated_model["relationships"])
        confidence_score += relationship_confidence
        count += 1
    
    if integrated_model["parameters"]:
        parameter_confidence = sum(p.get("confidence", 0.0) for p in integrated_model["parameters"]) / len(integrated_model["parameters"])
        confidence_score += parameter_confidence
        count += 1
    
    if count > 0:
        integrated_model["metadata"]["confidence_score"] = confidence_score / count
    else:
        integrated_model["metadata"]["confidence_score"] = 0.5  # Default mid-point
    
    return integrated_model

def validate_model_task(model: Dict[str, Any], 
                       validation_level: str = "detailed") -> Dict[str, Any]:
    """
    Task function for validating a model
    
    Args:
        model: The model to validate
        validation_level: Level of validation detail
        
    Returns:
        Validation results
    """
    import time
    from .compute_helpers import process_nlp_model_request
    
    # Start timing
    start_time = time.time()
    
    try:
        # Create system prompt for model validation
        system_prompt = """
        You are a model validation system for sports science models.
        Analyze the given model for completeness, consistency, and domain correctness.
        Provide a comprehensive validation including:
        1. Overall validity (boolean)
        2. Issues (list of critical problems)
        3. Warnings (list of potential concerns)
        4. Suggestions (list of improvement ideas)
        5. Confidence scores for different aspects of the model
        
        Return a JSON object with validation results.
        """
        
        level_instructions = ""
        if validation_level == "detailed":
            level_instructions = """
            Perform an in-depth validation covering:
            - Entity completeness and accuracy
            - Relationship coherence and validity
            - Parameter appropriateness and completeness
            - Domain knowledge correctness
            - Internal consistency of the entire model
            """
        else:
            level_instructions = """
            Perform a basic validation covering:
            - Major issues that would prevent the model from being useful
            - Basic consistency checks
            - Obvious domain knowledge errors
            """
        
        user_prompt = f"""
        Model to validate:
        {json.dumps(model, indent=2)}
        
        {level_instructions}
        
        Follow the format in your instructions for the validation response.
        """
        
        # Call LLM model endpoint
        response = process_nlp_model_request(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model_name="gpt-4-turbo",  # Use GPT-4 for validation
            temperature=0.2,  # Lower temperature for more consistent validation
            response_format="json"
        )
        
        # Parse the response
        validation_results = json.loads(response)
        
        return validation_results
    except Exception as e:
        logger.error(f"Error in model validation task: {str(e)}")
        # Return basic validation results as fallback
        return {
            "valid": False,
            "issues": [f"Validation error: {str(e)}", "Could not complete validation"],
            "warnings": ["Validation results may be incomplete"],
            "suggestions": ["Try again with a different model"],
            "confidence_scores": {
                "overall": 0.1,
                "entities": 0.1,
                "relationships": 0.1,
                "parameters": 0.1
            }
        }

# API endpoints
@app.post("/api/modeler/entities", response_model=EntityExtractionResponse)
async def extract_entities(
    request: EntityExtractionRequest,
    compute_manager: ComputeManager = Depends(get_compute_manager)
):
    """
    Extract entities from a query text
    
    Args:
        request: Entity extraction request with query and options
        
    Returns:
        Extracted entities and processing time
    """
    import time
    
    # Start timing
    start_time = time.time()
    
    try:
        # Submit task to compute manager
        task_id = compute_manager.submit_task(
            extract_entities_task,
            request.query,
            request.context,
            request.options
        )
        
        # Get result
        entities_data = compute_manager.get_result(task_id)
        
        # Convert to response format
        entities = [ModelEntity(**entity) for entity in entities_data]
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        return EntityExtractionResponse(
            entities=entities,
            processing_time=processing_time
        )
    except Exception as e:
        logger.error(f"Error extracting entities: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Entity extraction failed: {str(e)}"
        )

@app.post("/api/modeler/relationships", response_model=RelationshipMappingResponse)
async def map_relationships(
    request: RelationshipMappingRequest,
    compute_manager: ComputeManager = Depends(get_compute_manager)
):
    """
    Map relationships between entities
    
    Args:
        request: Relationship mapping request with entities and query
        
    Returns:
        Mapped relationships and processing time
    """
    import time
    
    # Start timing
    start_time = time.time()
    
    try:
        # Convert entities to dict for task
        entities_data = [entity.dict() for entity in request.entities]
        
        # Submit task to compute manager
        task_id = compute_manager.submit_task(
            map_relationships_task,
            entities_data,
            request.query,
            request.options
        )
        
        # Get result
        relationships_data = compute_manager.get_result(task_id)
        
        # Convert to response format
        relationships = [ModelRelationship(**relationship) for relationship in relationships_data]
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        return RelationshipMappingResponse(
            relationships=relationships,
            processing_time=processing_time
        )
    except Exception as e:
        logger.error(f"Error mapping relationships: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Relationship mapping failed: {str(e)}"
        )

@app.post("/api/modeler/parameters", response_model=ParameterIdentificationResponse)
async def identify_parameters(
    request: ParameterIdentificationRequest,
    compute_manager: ComputeManager = Depends(get_compute_manager)
):
    """
    Identify parameters for the model
    
    Args:
        request: Parameter identification request
        
    Returns:
        Identified parameters and processing time
    """
    import time
    
    # Start timing
    start_time = time.time()
    
    try:
        # Convert entities and relationships to dict for task
        entities_data = [entity.dict() for entity in request.entities]
        relationships_data = [relationship.dict() for relationship in request.relationships]
        
        # Submit task to compute manager
        task_id = compute_manager.submit_task(
            identify_parameters_task,
            request.query,
            entities_data,
            relationships_data,
            request.options
        )
        
        # Get result
        parameters_data = compute_manager.get_result(task_id)
        
        # Convert to response format
        parameters = [ModelParameter(**parameter) for parameter in parameters_data]
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        return ParameterIdentificationResponse(
            parameters=parameters,
            processing_time=processing_time
        )
    except Exception as e:
        logger.error(f"Error identifying parameters: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Parameter identification failed: {str(e)}"
        )

@app.post("/api/modeler/integrate", response_model=ModelIntegrationResponse)
async def integrate_model(
    request: ModelIntegrationRequest,
    compute_manager: ComputeManager = Depends(get_compute_manager)
):
    """
    Integrate model components into a complete model
    
    Args:
        request: Model integration request
        
    Returns:
        Integrated model and processing time
    """
    import time
    
    # Start timing
    start_time = time.time()
    
    try:
        # Submit task to compute manager
        task_id = compute_manager.submit_task(
            integrate_model_task,
            request.model_data,
            request.options
        )
        
        # Get result
        integrated_model_data = compute_manager.get_result(task_id)
        
        # Convert to response format
        integrated_model = ModelData(**integrated_model_data)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        return ModelIntegrationResponse(
            integrated_model=integrated_model,
            processing_time=processing_time
        )
    except Exception as e:
        logger.error(f"Error integrating model: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Model integration failed: {str(e)}"
        )

@app.post("/api/modeler/validate", response_model=ModelValidationResponse)
async def validate_model(
    request: ModelValidationRequest,
    compute_manager: ComputeManager = Depends(get_compute_manager)
):
    """
    Validate a model against domain knowledge and constraints
    
    Args:
        request: Model validation request
        
    Returns:
        Validation results and processing time
    """
    import time
    
    # Start timing
    start_time = time.time()
    
    try:
        # Convert model to dict for task
        model_data = request.model.dict()
        
        # Submit task to compute manager
        task_id = compute_manager.submit_task(
            validate_model_task,
            model_data,
            request.validation_level
        )
        
        # Get result
        validation_data = compute_manager.get_result(task_id)
        
        # Convert to response format
        validation_results = ModelValidationResults(**validation_data)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        return ModelValidationResponse(
            validation_results=validation_results,
            processing_time=processing_time
        )
    except Exception as e:
        logger.error(f"Error validating model: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Model validation failed: {str(e)}"
        )

@app.post("/api/modeler/process", response_model=ModelProcessingResponse)
async def process_model(
    request: ModelProcessingRequest,
    compute_manager: ComputeManager = Depends(get_compute_manager)
):
    """
    Process a complete model workflow from query to validated model
    
    Args:
        request: Model processing request
        
    Returns:
        Processed model, validation results, and processing time
    """
    import time
    
    # Start timing
    start_time = time.time()
    
    try:
        # 1. Extract entities
        entity_request = EntityExtractionRequest(
            query=request.query,
            context=request.options.get("context", {}),
            options=request.options
        )
        entity_response = await extract_entities(entity_request, compute_manager)
        
        # 2. Map relationships
        relationship_request = RelationshipMappingRequest(
            entities=entity_response.entities,
            query=request.query,
            options=request.options
        )
        relationship_response = await map_relationships(relationship_request, compute_manager)
        
        # 3. Identify parameters
        parameter_request = ParameterIdentificationRequest(
            query=request.query,
            entities=entity_response.entities,
            relationships=relationship_response.relationships,
            options=request.options
        )
        parameter_response = await identify_parameters(parameter_request, compute_manager)
        
        # 4. Integrate model
        model_data = {
            "id": generate_id(),
            "query": request.query,
            "entities": [entity.dict() for entity in entity_response.entities],
            "relationships": [relationship.dict() for relationship in relationship_response.relationships],
            "parameters": [parameter.dict() for parameter in parameter_response.parameters],
            "metadata": create_metadata()
        }
        
        integration_request = ModelIntegrationRequest(
            model_data=model_data,
            options=request.options
        )
        integration_response = await integrate_model(integration_request, compute_manager)
        
        # 5. Validate model if requested
        validation_results = None
        if request.options.get("validation_level"):
            validation_request = ModelValidationRequest(
                model=integration_response.integrated_model,
                validation_level=request.options.get("validation_level", "detailed")
            )
            validation_response = await validate_model(validation_request, compute_manager)
            validation_results = validation_response.validation_results
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        return ModelProcessingResponse(
            model=integration_response.integrated_model,
            validation_results=validation_results,
            processing_time=processing_time
        )
    except Exception as e:
        logger.error(f"Error processing model: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Model processing failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 