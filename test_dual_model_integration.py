#!/usr/bin/env python3
"""
Test script for dual-model integration in the Four-Sided Triangle RAG system.
This tests the integration of primary and secondary sprint domain experts.
"""

import asyncio
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_dual_model_integration():
    """Test the dual-model integration functionality."""
    
    logger.info("="*60)
    logger.info("Testing Dual-Model Integration in Four-Sided Triangle RAG")
    logger.info("="*60)
    
    # Test query for sprint biomechanics
    test_query = "What are the optimal biomechanical strategies for improving 400m sprint performance?"
    
    # Simulated semantic representation (normally from Stage 1)
    semantic_representation = {
        "transformed_query": test_query,
        "intent": "performance_optimization",
        "parameters": {
            "distance": "400m",
            "focus": "biomechanics",
            "goal": "performance_improvement"
        },
        "domain_indicators": ["sprint", "biomechanics", "athletic_performance"]
    }
    
    try:
        # Import the domain knowledge service
        from app.core.stages.stage2_domain_knowledge.domain_knowledge_service import DomainKnowledgeService
        
        # Initialize the service
        config = {
            "llm_connector": {
                "model_configs": {
                    "sprint": {"temperature": 0.1, "max_tokens": 1024},
                    "biomechanics": {"temperature": 0.15, "max_tokens": 1024}
                }
            },
            "knowledge_extractor": {},
            "knowledge_validator": {},
            "knowledge_prioritizer": {}
        }
        
        service = DomainKnowledgeService(config)
        logger.info("✓ Domain Knowledge Service initialized")
        
        # Process the query with dual-model extraction
        context = {
            "session_id": f"test_session_{datetime.now().isoformat()}",
            "stage": "domain_knowledge_extraction",
            "enable_dual_models": True
        }
        
        logger.info(f"Processing query: {test_query}")
        
        result = await service.process(semantic_representation, context)
        
        # Analyze the results
        logger.info("\n" + "="*50)
        logger.info("DUAL-MODEL EXTRACTION RESULTS")
        logger.info("="*50)
        
        metadata = result.get("metadata", {})
        
        # Models used
        models_used = metadata.get("models_used", {})
        logger.info(f"\nModels Used:")
        logger.info(f"  Primary Experts: {len(models_used.get('primary_experts', []))}")
        logger.info(f"  Secondary Experts: {len(models_used.get('secondary_experts', []))}")
        logger.info(f"  Total Models: {models_used.get('total_models', 0)}")
        
        for expert in models_used.get("primary_experts", []):
            logger.info(f"    Primary: {expert.get('model_id')} ({expert.get('specialization')})")
        
        for expert in models_used.get("secondary_experts", []):
            logger.info(f"    Secondary: {expert.get('model_id')} ({expert.get('specialization')})")
        
        # Knowledge extraction metrics
        extraction_metrics = metadata.get("extraction_metrics", {})
        logger.info(f"\nExtraction Metrics:")
        logger.info(f"  Total Elements: {extraction_metrics.get('total_elements', 0)}")
        logger.info(f"  High Confidence: {extraction_metrics.get('elements_high_confidence', 0)}")
        logger.info(f"  Low Confidence: {extraction_metrics.get('elements_low_confidence', 0)}")
        
        # Dual-model insights analysis
        dual_insights = metadata.get("dual_model_insights", {})
        logger.info(f"\nDual-Model Analysis:")
        logger.info(f"  Complementary Insights: {len(dual_insights.get('complementary_insights', []))}")
        logger.info(f"  Consensus Areas: {len(dual_insights.get('consensus_areas', []))}")
        logger.info(f"  Divergent Perspectives: {len(dual_insights.get('divergent_perspectives', []))}")
        
        # Show confidence comparison
        confidence_comparison = dual_insights.get("confidence_comparison", {})
        for domain, scores in confidence_comparison.items():
            logger.info(f"  {domain.title()} Domain:")
            logger.info(f"    Primary Model Confidence: {scores.get('primary', 0.0):.2f}")
            logger.info(f"    Secondary Model Confidence: {scores.get('secondary', 0.0):.2f}")
            logger.info(f"    Confidence Difference: {scores.get('difference', 0.0):.2f}")
        
        # Show sample complementary insights
        complementary_insights = dual_insights.get("complementary_insights", [])
        if complementary_insights:
            logger.info(f"\nSample Complementary Insights:")
            for i, insight in enumerate(complementary_insights[:3]):  # Show first 3
                logger.info(f"  {i+1}. {insight.get('insight', 'N/A')[:100]}...")
                logger.info(f"     Domain: {insight.get('domain')}, Confidence: {insight.get('confidence', 0.0):.2f}")
        
        # Knowledge elements summary
        domain_knowledge = result.get("domain_knowledge", {})
        elements = domain_knowledge.get("elements", [])
        
        logger.info(f"\nKnowledge Elements Summary:")
        logger.info(f"  Total Elements Extracted: {len(elements)}")
        
        # Categorize by model source
        primary_count = sum(1 for e in elements if e.get("model_source") == "primary")
        secondary_count = sum(1 for e in elements if e.get("model_source") == "secondary")
        consensus_count = sum(1 for e in elements if e.get("consensus_insight", False))
        
        logger.info(f"  From Primary Expert: {primary_count}")
        logger.info(f"  From Secondary Expert: {secondary_count}")
        logger.info(f"  Consensus Insights: {consensus_count}")
        
        # Show sample elements
        if elements:
            logger.info(f"\nSample Knowledge Elements:")
            for i, element in enumerate(elements[:5]):  # Show first 5
                model_source = element.get("model_source", "unknown")
                confidence = element.get("confidence", 0.0)
                content = element.get("content", "N/A")[:80]
                consensus = " [CONSENSUS]" if element.get("consensus_insight") else ""
                logger.info(f"  {i+1}. [{model_source.upper()}] {content}...{consensus}")
                logger.info(f"     Confidence: {confidence:.2f}")
        
        logger.info("\n" + "="*50)
        logger.info("DUAL-MODEL INTEGRATION TEST COMPLETED SUCCESSFULLY!")
        logger.info("="*50)
        
        return True
        
    except Exception as e:
        logger.error(f"Error during dual-model integration test: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Run the test."""
    success = asyncio.run(test_dual_model_integration())
    
    if success:
        logger.info("\n✓ All tests passed! Dual-model integration is working correctly.")
    else:
        logger.error("\n✗ Tests failed! Please check the configuration and try again.")

if __name__ == "__main__":
    main() 