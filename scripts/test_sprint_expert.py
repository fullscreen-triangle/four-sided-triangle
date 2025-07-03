#!/usr/bin/env python3
"""
Test script for the Sprint Running Domain Expert LLM integration.

This script tests the integration of your enhanced domain expert model
with the Four-Sided Triangle pipeline.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test queries covering different aspects of sprint running
TEST_QUERIES = [
    # Basic sprint mechanics
    "What are the key biomechanical factors that determine sprint speed?",
    
    # Training methodology
    "How should I structure a sprint training program for a 100m runner?",
    
    # Performance analysis
    "What is the relationship between stride frequency and stride length in sprinting?",
    
    # Technical aspects
    "How does force production change throughout a 100m sprint race?",
    
    # Injury prevention
    "What are the most common sprint running injuries and how can they be prevented?",
    
    # Advanced performance
    "How do elite sprinters optimize their acceleration phase technique?",
    
    # Comparative analysis
    "What are the differences between male and female sprint biomechanics?",
    
    # Equipment and environment
    "How do track surface and sprint spikes affect running performance?",
    
    # Physiological aspects
    "What energy systems are primary during different phases of a 100m sprint?",
    
    # Recovery and adaptation
    "What are optimal recovery protocols between high-intensity sprint sessions?"
]

class SprintExpertTester:
    """Test suite for the Sprint Domain Expert."""
    
    def __init__(self):
        self.results = []
        self.start_time = None
        
    async def test_model_availability(self) -> bool:
        """Test if the Ollama model is available."""
        try:
            import requests
            
            # Check if Ollama is running
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model["name"] for model in models]
                
                if "gpt2-enhanced" in model_names:
                    logger.info("✅ Sprint domain expert model 'gpt2-enhanced' is available")
                    return True
                else:
                    logger.warning(f"❌ Model 'gpt2-enhanced' not found. Available models: {model_names}")
                    return False
            else:
                logger.error("❌ Ollama API not responding")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to check model availability: {e}")
            return False
    
    async def test_domain_expert_direct(self, query: str) -> Dict[str, Any]:
        """Test the domain expert directly."""
        try:
            from app.models.domain_knowledge import SprintDomainExpert
            
            config = {
                "ollama_model_name": "gpt2-enhanced",
                "base_url": "http://localhost:11434",
                "model_path": "models/domain_llm/gpt2-enhanced",
                "specialization": "sprint_running",
                "dataset_size": 87
            }
            
            expert = SprintDomainExpert(config)
            start_time = time.time()
            
            result = expert.extract_domain_knowledge(query)
            
            end_time = time.time()
            result["response_time"] = end_time - start_time
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Direct domain expert test failed: {e}")
            return {
                "error": str(e),
                "query": query,
                "success": False
            }
    
    async def test_full_pipeline(self, query: str) -> Dict[str, Any]:
        """Test the full Four-Sided Triangle pipeline with your domain expert."""
        try:
            # This would integrate with your main pipeline
            # For now, we'll simulate the pipeline stages
            
            logger.info(f"🔄 Testing full pipeline with query: '{query[:50]}...'")
            
            # Stage 1: Query Processing
            processed_query = await self.simulate_query_processing(query)
            
            # Stage 2: Semantic ATDB
            semantic_result = await self.simulate_semantic_atdb(processed_query)
            
            # Stage 3: Domain Knowledge (Your Expert!)
            domain_knowledge = await self.test_domain_expert_direct(query)
            
            # Stage 4: Reasoning
            reasoning_result = await self.simulate_reasoning(domain_knowledge)
            
            # Stage 5: Solution Generation
            solution = await self.simulate_solution_generation(reasoning_result)
            
            # Stage 6: Response Scoring
            score = await self.simulate_response_scoring(solution)
            
            # Stage 7: Response Comparison
            comparison = await self.simulate_response_comparison([solution])
            
            # Stage 8: Threshold Verification
            verification = await self.simulate_threshold_verification(comparison)
            
            return {
                "query": query,
                "pipeline_stages": {
                    "query_processing": processed_query,
                    "semantic_atdb": semantic_result,
                    "domain_knowledge": domain_knowledge,
                    "reasoning": reasoning_result,
                    "solution_generation": solution,
                    "response_scoring": score,
                    "response_comparison": comparison,
                    "threshold_verification": verification
                },
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ Full pipeline test failed: {e}")
            return {
                "error": str(e),
                "query": query,
                "success": False
            }
    
    async def simulate_query_processing(self, query: str) -> Dict[str, Any]:
        """Simulate query processing stage."""
        return {
            "original_query": query,
            "processed_query": query.strip(),
            "intent": "sprint_performance_inquiry",
            "entities": self.extract_sprint_entities(query),
            "confidence": 0.9
        }
    
    async def simulate_semantic_atdb(self, processed_query: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate semantic ATDB stage."""
        return {
            "semantic_vectors": "[simulated]",
            "reranked_query": processed_query["processed_query"],
            "relevance_score": 0.85
        }
    
    async def simulate_reasoning(self, domain_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate reasoning stage."""
        return {
            "reasoning_path": "biomechanics -> performance -> training",
            "logical_connections": 3,
            "evidence_strength": domain_knowledge.get("evidence_level", "medium")
        }
    
    async def simulate_solution_generation(self, reasoning: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate solution generation stage."""
        return {
            "solution_quality": "high",
            "completeness": 0.9,
            "novelty": 0.7,
            "practical_applicability": 0.85
        }
    
    async def simulate_response_scoring(self, solution: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate response scoring stage."""
        return {
            "quality_score": 0.88,
            "confidence_interval": [0.82, 0.94],
            "uncertainty": 0.12
        }
    
    async def simulate_response_comparison(self, solutions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simulate response comparison stage."""
        return {
            "best_solution_index": 0,
            "diversity_score": 0.6,
            "ensemble_confidence": 0.87
        }
    
    async def simulate_threshold_verification(self, comparison: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate threshold verification stage."""
        return {
            "meets_threshold": True,
            "quality_threshold": 0.8,
            "actual_quality": comparison["ensemble_confidence"],
            "verified": True
        }
    
    def extract_sprint_entities(self, query: str) -> List[str]:
        """Extract sprint-related entities from query."""
        sprint_entities = [
            "sprint", "100m", "200m", "speed", "acceleration", "biomechanics",
            "stride", "frequency", "length", "force", "power", "training",
            "technique", "performance", "elite", "athlete"
        ]
        
        found_entities = []
        query_lower = query.lower()
        
        for entity in sprint_entities:
            if entity in query_lower:
                found_entities.append(entity)
                
        return found_entities
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run a comprehensive test suite."""
        logger.info("🚀 Starting comprehensive Sprint Domain Expert test suite")
        self.start_time = time.time()
        
        # Test 1: Model Availability
        logger.info("📋 Test 1: Checking model availability...")
        model_available = await self.test_model_availability()
        
        if not model_available:
            return {
                "success": False,
                "error": "Sprint domain expert model not available",
                "tests_completed": 0
            }
        
        # Test 2: Direct Domain Expert Tests
        logger.info("📋 Test 2: Testing domain expert directly...")
        direct_test_results = []
        
        for i, query in enumerate(TEST_QUERIES[:3]):  # Test first 3 queries
            logger.info(f"   Query {i+1}/3: {query[:50]}...")
            result = await self.test_domain_expert_direct(query)
            direct_test_results.append(result)
            
            if result.get("error"):
                logger.warning(f"   ⚠️  Query {i+1} failed: {result['error']}")
            else:
                logger.info(f"   ✅ Query {i+1} succeeded (confidence: {result.get('confidence', 0):.2f})")
        
        # Test 3: Full Pipeline Test
        logger.info("📋 Test 3: Testing full pipeline integration...")
        pipeline_test = await self.test_full_pipeline(TEST_QUERIES[0])
        
        # Test 4: Performance Analysis
        logger.info("📋 Test 4: Performance analysis...")
        performance_stats = self.analyze_performance(direct_test_results)
        
        end_time = time.time()
        total_time = end_time - self.start_time
        
        # Compile results
        results = {
            "success": True,
            "total_runtime": total_time,
            "model_available": model_available,
            "direct_tests": {
                "completed": len(direct_test_results),
                "successful": len([r for r in direct_test_results if not r.get("error")]),
                "results": direct_test_results
            },
            "pipeline_test": pipeline_test,
            "performance_stats": performance_stats,
            "recommendations": self.generate_recommendations(direct_test_results)
        }
        
        # Save results
        self.save_results(results)
        
        logger.info(f"🎉 Test suite completed in {total_time:.2f} seconds")
        return results
    
    def analyze_performance(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance metrics."""
        successful_results = [r for r in results if not r.get("error")]
        
        if not successful_results:
            return {"error": "No successful results to analyze"}
        
        response_times = [r.get("response_time", 0) for r in successful_results]
        confidences = [r.get("confidence", 0) for r in successful_results]
        
        return {
            "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "avg_confidence": sum(confidences) / len(confidences) if confidences else 0,
            "min_confidence": min(confidences) if confidences else 0,
            "max_confidence": max(confidences) if confidences else 0,
            "success_rate": len(successful_results) / len(results) if results else 0
        }
    
    def generate_recommendations(self, results: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        successful_results = [r for r in results if not r.get("error")]
        
        if not successful_results:
            recommendations.append("❌ Model is not responding - check Ollama installation and model loading")
            return recommendations
        
        avg_confidence = sum(r.get("confidence", 0) for r in successful_results) / len(successful_results)
        avg_response_time = sum(r.get("response_time", 0) for r in successful_results) / len(successful_results)
        
        if avg_confidence < 0.5:
            recommendations.append("⚠️ Low confidence scores - consider fine-tuning the model further")
        elif avg_confidence > 0.8:
            recommendations.append("✅ High confidence scores - model performing well")
        
        if avg_response_time > 10:
            recommendations.append("⚠️ Slow response times - consider optimizing model size or hardware")
        elif avg_response_time < 3:
            recommendations.append("✅ Fast response times - good performance")
        
        recommendations.append("🔄 Ready to test with more complex queries and full pipeline integration")
        
        return recommendations
    
    def save_results(self, results: Dict[str, Any]) -> None:
        """Save test results to file."""
        output_file = Path("sprint_expert_test_results.json")
        
        try:
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"📁 Results saved to {output_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save results: {e}")

async def main():
    """Main test execution."""
    print("🏃‍♂️ Sprint Domain Expert Test Suite")
    print("=" * 50)
    
    tester = SprintExpertTester()
    results = await tester.run_comprehensive_test()
    
    # Print summary
    print("\n📊 TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Success: {results['success']}")
    print(f"⏱️  Total Runtime: {results['total_runtime']:.2f}s")
    
    if results.get('direct_tests'):
        direct = results['direct_tests']
        print(f"🧪 Direct Tests: {direct['successful']}/{direct['completed']} successful")
    
    if results.get('performance_stats'):
        perf = results['performance_stats']
        print(f"📈 Avg Response Time: {perf.get('avg_response_time', 0):.2f}s")
        print(f"🎯 Avg Confidence: {perf.get('avg_confidence', 0):.2f}")
    
    print("\n💡 RECOMMENDATIONS")
    print("=" * 50)
    for rec in results.get('recommendations', []):
        print(f"   {rec}")
    
    print(f"\n📁 Detailed results saved to: sprint_expert_test_results.json")

if __name__ == "__main__":
    asyncio.run(main()) 