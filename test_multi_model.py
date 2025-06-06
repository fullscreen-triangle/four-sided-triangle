#!/usr/bin/env python3
"""
Test script for the new multi-model SprintLLM system.
This script tests the loading and basic functionality of all available models.
"""

import os
import sys
import logging
from app.core.model import get_model_instance

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_model_loading():
    """Test that models can be loaded successfully."""
    logger.info("Testing multi-model system loading...")
    
    try:
        # Get model instance
        model_system = get_model_instance()
        
        # Check what models were loaded
        logger.info(f"Available models: {list(model_system.models.keys())}")
        
        if model_system.embedding_model:
            logger.info("✓ Embedding model is available")
        else:
            logger.info("✗ Embedding model not available")
        
        return model_system
        
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        return None

def test_text_generation(model_system):
    """Test text generation with different query types."""
    if not model_system or not model_system.models:
        logger.error("No models available for testing")
        return
    
    test_queries = [
        {
            "query": "Explain the biomechanics of the 400m sprint start.",
            "expected_model": "phi3",
            "type": "instruction"
        },
        {
            "query": "Calculate the optimal stride length for a 180cm tall runner.",
            "expected_model": "phi3", 
            "type": "calculation"
        },
        {
            "query": "Write a training plan for improving 400m performance.",
            "expected_model": "distilgpt2",
            "type": "creative"
        }
    ]
    
    for test in test_queries:
        logger.info(f"\nTesting query: {test['query'][:50]}...")
        
        try:
            # Test model selection
            selected_model = model_system._select_best_model(test['query'])
            logger.info(f"Selected model: {selected_model}")
            
            if selected_model in model_system.models:
                # Test actual generation
                response, metadata = model_system.generate_response(
                    test['query'], 
                    parameters={"max_tokens": 100}
                )
                
                logger.info(f"✓ Response generated successfully")
                logger.info(f"  Model used: {metadata['model']}")
                logger.info(f"  Generation time: {metadata['generation_time']:.2f}s")
                logger.info(f"  Response length: {len(response)} characters")
                logger.info(f"  First 100 chars: {response[:100]}...")
                
            else:
                logger.warning(f"Selected model {selected_model} not available")
                
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")

def test_embeddings(model_system):
    """Test embedding generation."""
    if not model_system or (not model_system.embedding_model and "embedding" not in model_system.models):
        logger.warning("No embedding model available for testing")
        return
    
    test_texts = [
        "400m sprint biomechanics",
        "running technique optimization", 
        "athletic performance analysis"
    ]
    
    try:
        logger.info(f"\nTesting embeddings for {len(test_texts)} texts...")
        embeddings = model_system.get_embeddings(test_texts)
        logger.info(f"✓ Embeddings generated successfully")
        logger.info(f"  Shape: {embeddings.shape}")
        logger.info(f"  First embedding preview: {embeddings[0][:5]}...")
        
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")

def test_anthropometric_calculation(model_system):
    """Test the anthropometric metrics calculation."""
    if not model_system or not model_system.models:
        logger.warning("No models available for anthropometric testing")
        return
        
    try:
        logger.info(f"\nTesting anthropometric calculations...")
        metrics, metadata = model_system.calculate_anthropometric_metrics(
            age=25.0,
            height=180.0,
            weight=75.0,
            gender="male"
        )
        
        logger.info(f"✓ Anthropometric metrics calculated successfully")
        logger.info(f"  Model used: {metadata['model_used']}")
        logger.info(f"  Calculation time: {metadata['calculation_time']:.2f}s")
        logger.info(f"  Number of metric categories: {len(metrics)}")
        
    except Exception as e:
        logger.error(f"Failed to calculate anthropometric metrics: {e}")

def main():
    """Run all tests."""
    logger.info("="*60)
    logger.info("Multi-Model SprintLLM System Test")
    logger.info("="*60)
    
    # Test model loading
    model_system = test_model_loading()
    
    if model_system is None:
        logger.error("Model loading failed. Exiting.")
        sys.exit(1)
    
    # Test different functionalities
    test_text_generation(model_system)
    test_embeddings(model_system)
    test_anthropometric_calculation(model_system)
    
    logger.info("\n" + "="*60)
    logger.info("Test completed!")
    logger.info("="*60)

if __name__ == "__main__":
    main() 