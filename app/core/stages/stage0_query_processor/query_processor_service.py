"""
Query Processor Service - Handles the initial processing of user queries.

Implements the following functions:
- Query Reception
- Query Preprocessing
- Intent Classification
- Context Incorporation
- Query Validation
- Query Packaging
"""

import logging
import time
from typing import Dict, Any, Optional, Tuple, List

from app.core.stages.stage0_query_processor.preprocessing import preprocess_query
from app.core.stages.stage0_query_processor.intent_classifier import classify_intent
from app.core.stages.stage0_query_processor.query_validator import validate_query_requirements
from app.core.stages.stage0_query_processor.context_manager import enrich_with_context
from app.core.stages.stage0_query_processor.query_packager import package_query
from app.utils.llm_client import LLMClient

logger = logging.getLogger(__name__)

class QueryProcessorService:
    """
    Service for processing raw user queries and transforming them into structured
    query objects ready for modeling.
    """
    
    def __init__(self):
        """
        Initialize the QueryProcessorService with necessary dependencies.
        """
        self.llm_client = LLMClient()
        logger.info("QueryProcessorService initialized")
    
    async def process_query(self, raw_query: str, parameters: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Process a raw query through all query processing stages.
        
        Args:
            raw_query: The raw user query text
            parameters: Optional parameters to control processing
            
        Returns:
            Tuple containing:
            - structured_query: The processed query package
            - metadata: Processing metadata and metrics
        """
        start_time = time.time()
        parameters = parameters or {}
        
        # Track processing stages and metrics
        metadata = {
            "processing_time": {},
            "confidence_scores": {},
            "stages_completed": []
        }
        
        # 1. Query Reception - Already handled by API endpoint
        logger.info(f"Received query: {raw_query[:50]}...")
        metadata["stages_completed"].append("query_reception")
        
        # 2. Query Preprocessing
        stage_start = time.time()
        preprocessed_query = preprocess_query(raw_query)
        metadata["processing_time"]["preprocessing"] = time.time() - stage_start
        metadata["stages_completed"].append("query_preprocessing")
        
        # 3. Intent Classification
        stage_start = time.time()
        intent_classification, intent_confidence = await classify_intent(
            preprocessed_query, 
            self.llm_client
        )
        metadata["processing_time"]["intent_classification"] = time.time() - stage_start
        metadata["confidence_scores"]["intent"] = intent_confidence
        metadata["stages_completed"].append("intent_classification")
        
        # 4. Context Incorporation
        stage_start = time.time()
        enriched_query = await enrich_with_context(
            preprocessed_query,
            intent_classification,
            parameters.get("user_history", []),
            parameters.get("preferences", {}),
            self.llm_client
        )
        metadata["processing_time"]["context_incorporation"] = time.time() - stage_start
        metadata["stages_completed"].append("context_incorporation")
        
        # 5. Query Validation
        stage_start = time.time()
        is_valid, validation_details = validate_query_requirements(
            enriched_query,
            intent_classification
        )
        metadata["processing_time"]["validation"] = time.time() - stage_start
        metadata["validation_details"] = validation_details
        metadata["stages_completed"].append("query_validation")
        
        if not is_valid:
            logger.warning(f"Query validation failed: {validation_details}")
            # Return early with validation failure details
            metadata["status"] = "validation_failed"
            metadata["total_processing_time"] = time.time() - start_time
            return {"validation_failed": True, "details": validation_details}, metadata
        
        # 6. Query Packaging
        stage_start = time.time()
        structured_query = await package_query(
            enriched_query,
            intent_classification,
            validation_details,
            parameters,
            self.llm_client
        )
        metadata["processing_time"]["packaging"] = time.time() - stage_start
        metadata["stages_completed"].append("query_packaging")
        
        # Add total processing time and successful status
        metadata["total_processing_time"] = time.time() - start_time
        metadata["status"] = "success"
        
        return structured_query, metadata 