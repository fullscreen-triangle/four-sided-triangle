"""
Fuzzy Evidence System Integration Example

This example demonstrates how to use the fuzzy evidence system with the 
metacognitive orchestrator to optimize pipeline decisions in the Four-Sided 
Triangle framework.
"""

import json
import time
from typing import Dict, Any, List
from app.core.rust_integration import rust_integration


class FuzzyEvidenceOrchestrator:
    """
    Example implementation of a metacognitive orchestrator using 
    the fuzzy evidence system for optimization.
    """
    
    def __init__(self):
        self.evidence_network_id = None
        self.optimizer_id = None
        self.fuzzy_sets = {}
        self.setup_system()
    
    def setup_system(self):
        """Initialize the fuzzy evidence system components."""
        print("Setting up Fuzzy Evidence System...")
        
        # Create evidence network
        self.evidence_network_id = rust_integration.create_evidence_network()
        print(f"Created evidence network: {self.evidence_network_id}")
        
        # Create metacognitive optimizer
        self.optimizer_id = rust_integration.create_metacognitive_optimizer()
        print(f"Created metacognitive optimizer: {self.optimizer_id}")
        
        # Setup fuzzy sets
        self.setup_fuzzy_sets()
        
        # Initialize evidence network structure
        self.initialize_evidence_network()
        
        print("Fuzzy Evidence System setup complete!")
    
    def setup_fuzzy_sets(self):
        """Create fuzzy sets for different linguistic variables."""
        
        # Query complexity fuzzy sets
        complexity_sets = [
            {
                "name": "low_complexity",
                "universe_min": 0.0,
                "universe_max": 1.0,
                "membership_function": {
                    "type": "triangular",
                    "left": 0.0,
                    "center": 0.0,
                    "right": 0.4
                }
            },
            {
                "name": "medium_complexity",
                "universe_min": 0.0,
                "universe_max": 1.0,
                "membership_function": {
                    "type": "triangular",
                    "left": 0.2,
                    "center": 0.5,
                    "right": 0.8
                }
            },
            {
                "name": "high_complexity",
                "universe_min": 0.0,
                "universe_max": 1.0,
                "membership_function": {
                    "type": "triangular",
                    "left": 0.6,
                    "center": 1.0,
                    "right": 1.0
                }
            }
        ]
        
        # Quality requirement fuzzy sets
        quality_sets = [
            {
                "name": "basic_quality",
                "universe_min": 0.0,
                "universe_max": 1.0,
                "membership_function": {
                    "type": "trapezoidal",
                    "left": 0.0,
                    "left_top": 0.0,
                    "right_top": 0.5,
                    "right": 0.7
                }
            },
            {
                "name": "high_quality",
                "universe_min": 0.0,
                "universe_max": 1.0,
                "membership_function": {
                    "type": "trapezoidal",
                    "left": 0.4,
                    "left_top": 0.7,
                    "right_top": 1.0,
                    "right": 1.0
                }
            }
        ]
        
        # Resource availability fuzzy sets
        resource_sets = [
            {
                "name": "limited_resources",
                "universe_min": 0.0,
                "universe_max": 1.0,
                "membership_function": {
                    "type": "gaussian",
                    "center": 0.3,
                    "sigma": 0.15
                }
            },
            {
                "name": "abundant_resources",
                "universe_min": 0.0,
                "universe_max": 1.0,
                "membership_function": {
                    "type": "gaussian",
                    "center": 0.8,
                    "sigma": 0.15
                }
            }
        ]
        
        # Store fuzzy sets
        self.fuzzy_sets = {
            "complexity": complexity_sets,
            "quality": quality_sets,
            "resources": resource_sets
        }
        
        print(f"Created {sum(len(sets) for sets in self.fuzzy_sets.values())} fuzzy sets")
    
    def initialize_evidence_network(self):
        """Initialize the evidence network with nodes and relationships."""
        
        # Add initial evidence for system capabilities
        base_evidence = {
            "value": 0.7,
            "membership_degree": 0.7,
            "confidence": 0.8,
            "source_reliability": 0.9,
            "temporal_decay": 1.0,
            "context_relevance": 1.0
        }
        
        # Initialize key nodes with base evidence
        key_nodes = [
            "query_complexity",
            "resource_availability", 
            "quality_requirements",
            "processing_strategy",
            "expected_performance"
        ]
        
        for node in key_nodes:
            rust_integration.update_node_evidence(
                self.evidence_network_id, 
                node, 
                base_evidence
            )
        
        print("Initialized evidence network with base evidence")
    
    def analyze_query_complexity(self, query: str, context: Dict[str, Any]) -> float:
        """Analyze query complexity using fuzzy logic."""
        
        # Simple heuristics for complexity analysis
        word_count = len(query.split())
        question_marks = query.count('?')
        technical_terms = sum(1 for word in query.lower().split() 
                            if word in ['analyze', 'compare', 'evaluate', 'optimize', 'algorithm'])
        
        # Normalize factors
        length_factor = min(word_count / 50.0, 1.0)  # Normalize to 50 words
        question_factor = min(question_marks / 3.0, 1.0)  # Normalize to 3 questions
        technical_factor = min(technical_terms / 5.0, 1.0)  # Normalize to 5 terms
        
        # Calculate overall complexity
        complexity = (length_factor * 0.4 + question_factor * 0.3 + technical_factor * 0.3)
        
        # Use fuzzy sets to get linguistic assessment
        complexity_memberships = {}
        for fuzzy_set in self.fuzzy_sets["complexity"]:
            membership = rust_integration.calculate_membership(complexity, fuzzy_set)
            complexity_memberships[fuzzy_set["name"]] = membership
        
        print(f"Query complexity analysis:")
        print(f"  Raw complexity: {complexity:.3f}")
        for name, membership in complexity_memberships.items():
            print(f"  {name}: {membership:.3f}")
        
        return complexity
    
    def assess_resource_availability(self, context: Dict[str, Any]) -> float:
        """Assess available computational resources."""
        
        available_resources = context.get("available_resources", {})
        
        # Calculate resource availability score
        cpu_available = available_resources.get("cpu", 0.5)
        memory_available = available_resources.get("memory", 0.5)
        time_available = min(available_resources.get("time", 5.0) / 10.0, 1.0)
        
        resource_score = (cpu_available * 0.4 + memory_available * 0.4 + time_available * 0.2)
        
        # Use fuzzy sets for linguistic assessment
        resource_memberships = {}
        for fuzzy_set in self.fuzzy_sets["resources"]:
            membership = rust_integration.calculate_membership(resource_score, fuzzy_set)
            resource_memberships[fuzzy_set["name"]] = membership
        
        print(f"Resource availability analysis:")
        print(f"  Raw availability: {resource_score:.3f}")
        for name, membership in resource_memberships.items():
            print(f"  {name}: {membership:.3f}")
        
        return resource_score
    
    def determine_quality_requirements(self, context: Dict[str, Any]) -> float:
        """Determine quality requirements from context."""
        
        quality_reqs = context.get("quality_requirements", {})
        
        # Extract quality requirements
        accuracy_req = quality_reqs.get("accuracy", 0.7)
        completeness_req = quality_reqs.get("completeness", 0.7)
        depth_req = quality_reqs.get("depth", 0.6)
        
        # Calculate overall quality requirement
        quality_requirement = (accuracy_req * 0.4 + completeness_req * 0.3 + depth_req * 0.3)
        
        # Use fuzzy sets for linguistic assessment
        quality_memberships = {}
        for fuzzy_set in self.fuzzy_sets["quality"]:
            membership = rust_integration.calculate_membership(quality_requirement, fuzzy_set)
            quality_memberships[fuzzy_set["name"]] = membership
        
        print(f"Quality requirements analysis:")
        print(f"  Raw requirement: {quality_requirement:.3f}")
        for name, membership in quality_memberships.items():
            print(f"  {name}: {membership:.3f}")
        
        return quality_requirement
    
    def update_evidence_network(self, query: str, context: Dict[str, Any]):
        """Update evidence network with current query and context."""
        
        print("\nUpdating evidence network...")
        
        # Analyze query complexity
        complexity = self.analyze_query_complexity(query, context)
        complexity_evidence = {
            "value": complexity,
            "membership_degree": complexity,
            "confidence": 0.8,
            "source_reliability": 0.9,
            "temporal_decay": 1.0,
            "context_relevance": 1.0
        }
        rust_integration.update_node_evidence(
            self.evidence_network_id, 
            "query_complexity", 
            complexity_evidence
        )
        
        # Assess resource availability
        resources = self.assess_resource_availability(context)
        resource_evidence = {
            "value": resources,
            "membership_degree": resources,
            "confidence": 0.9,
            "source_reliability": 0.95,
            "temporal_decay": 1.0,
            "context_relevance": 1.0
        }
        rust_integration.update_node_evidence(
            self.evidence_network_id, 
            "resource_availability", 
            resource_evidence
        )
        
        # Determine quality requirements
        quality = self.determine_quality_requirements(context)
        quality_evidence = {
            "value": quality,
            "membership_degree": quality,
            "confidence": 0.85,
            "source_reliability": 0.9,
            "temporal_decay": 1.0,
            "context_relevance": 1.0
        }
        rust_integration.update_node_evidence(
            self.evidence_network_id, 
            "quality_requirements", 
            quality_evidence
        )
        
        # Propagate evidence through network
        rust_integration.propagate_evidence(self.evidence_network_id, "belief_propagation")
        
        print("Evidence network updated and propagated")
    
    def optimize_pipeline_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use metacognitive optimizer to determine optimal pipeline strategy."""
        
        print("\nOptimizing pipeline strategy...")
        
        # Get optimization recommendations
        optimization_result = rust_integration.optimize_pipeline(self.optimizer_id, context)
        
        print("Optimization results:")
        print(f"  Selected strategies: {optimization_result['selected_strategies']}")
        print(f"  Confidence scores: {optimization_result['confidence_scores']}")
        print(f"  Expected improvements: {optimization_result['expected_improvements']}")
        print(f"  Resource allocation: {optimization_result['resource_allocation']}")
        print(f"  Risk assessment: {optimization_result['risk_assessment']}")
        
        return optimization_result
    
    def query_evidence_network(self, query_nodes: List[str]) -> Dict[str, Any]:
        """Query the evidence network for specific information."""
        
        print(f"\nQuerying evidence network for: {query_nodes}")
        
        query = {
            "target_nodes": query_nodes,
            "evidence_nodes": {},
            "query_type": "marginal_probability",
            "confidence_threshold": 0.6
        }
        
        result = rust_integration.query_network(self.evidence_network_id, query)
        
        print("Network query results:")
        for node, prob in result["probabilities"].items():
            print(f"  {node}: {prob:.3f}")
        
        return result
    
    def process_request(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Complete request processing with fuzzy evidence optimization."""
        
        print(f"\n{'='*60}")
        print(f"Processing Request: {query[:50]}...")
        print(f"{'='*60}")
        
        # Update evidence network with current context
        self.update_evidence_network(query, context)
        
        # Optimize pipeline strategy
        optimization_result = self.optimize_pipeline_strategy(context)
        
        # Query network for additional insights
        network_query_result = self.query_evidence_network([
            "processing_strategy", 
            "expected_performance"
        ])
        
        # Simulate processing with selected strategy
        processing_result = self.simulate_processing(
            query, 
            context, 
            optimization_result
        )
        
        # Update strategy performance based on results
        self.update_performance_feedback(
            context.get("request_id", "unknown"),
            processing_result
        )
        
        return {
            "query": query,
            "optimization": optimization_result,
            "network_insights": network_query_result,
            "processing_result": processing_result,
            "timestamp": time.time()
        }
    
    def simulate_processing(self, query: str, context: Dict[str, Any], optimization: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate processing with the optimized strategy."""
        
        print("\nSimulating processing...")
        
        # Extract strategy information
        selected_strategies = optimization["selected_strategies"]
        resource_allocation = optimization["resource_allocation"]
        
        # Simulate processing time based on strategy
        base_processing_time = len(query.split()) * 0.1  # Base time
        
        if "complex_query_strategy" in selected_strategies:
            processing_time = base_processing_time * 1.5
            quality_score = 0.9
        elif "fast_processing_strategy" in selected_strategies:
            processing_time = base_processing_time * 0.7
            quality_score = 0.75
        else:
            processing_time = base_processing_time
            quality_score = 0.8
        
        # Simulate resource usage
        cpu_usage = resource_allocation.get("cpu", 0.5)
        memory_usage = resource_allocation.get("memory", 0.4)
        
        # Calculate efficiency
        efficiency = quality_score / max(processing_time, 0.1)
        
        # Simulate user satisfaction
        time_satisfaction = max(0.0, 1.0 - processing_time / 10.0)
        quality_satisfaction = quality_score
        user_satisfaction = (time_satisfaction * 0.4 + quality_satisfaction * 0.6)
        
        result = {
            "processing_time": processing_time,
            "quality_score": quality_score,
            "efficiency": efficiency,
            "user_satisfaction": user_satisfaction,
            "resource_usage": {
                "cpu": cpu_usage,
                "memory": memory_usage
            },
            "selected_strategy": selected_strategies[0] if selected_strategies else "default"
        }
        
        print(f"Processing simulation results:")
        for key, value in result.items():
            if isinstance(value, dict):
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value:.3f}")
        
        return result
    
    def update_performance_feedback(self, request_id: str, processing_result: Dict[str, Any]):
        """Update strategy performance based on processing results."""
        
        print(f"\nUpdating performance feedback for request: {request_id}")
        
        # Extract performance metrics
        outcomes = {
            "quality": processing_result["quality_score"],
            "efficiency": processing_result["efficiency"],
            "user_satisfaction": processing_result["user_satisfaction"]
        }
        
        # Calculate overall feedback score
        feedback_score = (
            outcomes["quality"] * 0.4 + 
            outcomes["efficiency"] * 0.3 + 
            outcomes["user_satisfaction"] * 0.3
        )
        
        # Update strategy performance
        rust_integration.update_strategy_performance(
            self.optimizer_id,
            request_id,
            outcomes,
            feedback_score
        )
        
        print(f"Updated strategy performance with feedback score: {feedback_score:.3f}")


def run_example():
    """Run the fuzzy evidence system example."""
    
    print("Fuzzy Evidence System Integration Example")
    print("=" * 50)
    
    # Create orchestrator
    orchestrator = FuzzyEvidenceOrchestrator()
    
    # Example requests with different characteristics
    example_requests = [
        {
            "query": "What are the key differences between machine learning and deep learning?",
            "context": {
                "request_id": "req_001",
                "query_complexity": 0.6,
                "available_resources": {"cpu": 0.8, "memory": 0.7, "time": 5.0},
                "quality_requirements": {"accuracy": 0.8, "completeness": 0.7, "depth": 0.6},
                "time_constraints": 5.0,
                "uncertainty_tolerance": 0.3
            }
        },
        {
            "query": "Analyze and compare the performance characteristics, scalability limitations, and optimization strategies for distributed database systems including MongoDB, Cassandra, and CockroachDB in high-throughput, multi-region deployment scenarios.",
            "context": {
                "request_id": "req_002", 
                "query_complexity": 0.9,
                "available_resources": {"cpu": 0.6, "memory": 0.5, "time": 15.0},
                "quality_requirements": {"accuracy": 0.95, "completeness": 0.9, "depth": 0.8},
                "time_constraints": 12.0,
                "uncertainty_tolerance": 0.1
            }
        },
        {
            "query": "Quick summary of Python basics?",
            "context": {
                "request_id": "req_003",
                "query_complexity": 0.2,
                "available_resources": {"cpu": 0.9, "memory": 0.8, "time": 2.0},
                "quality_requirements": {"accuracy": 0.7, "completeness": 0.5, "depth": 0.4},
                "time_constraints": 1.5,
                "uncertainty_tolerance": 0.5
            }
        }
    ]
    
    # Process each request
    results = []
    for i, request in enumerate(example_requests, 1):
        print(f"\n\nExample {i}/{len(example_requests)}")
        result = orchestrator.process_request(request["query"], request["context"])
        results.append(result)
        
        # Small delay between requests
        time.sleep(0.5)
    
    # Summary analysis
    print(f"\n\n{'='*60}")
    print("SUMMARY ANALYSIS")
    print(f"{'='*60}")
    
    total_requests = len(results)
    avg_quality = sum(r["processing_result"]["quality_score"] for r in results) / total_requests
    avg_efficiency = sum(r["processing_result"]["efficiency"] for r in results) / total_requests
    avg_satisfaction = sum(r["processing_result"]["user_satisfaction"] for r in results) / total_requests
    
    print(f"Processed {total_requests} requests")
    print(f"Average quality score: {avg_quality:.3f}")
    print(f"Average efficiency: {avg_efficiency:.3f}")
    print(f"Average user satisfaction: {avg_satisfaction:.3f}")
    
    # Strategy usage analysis
    strategies_used = [r["processing_result"]["selected_strategy"] for r in results]
    strategy_counts = {}
    for strategy in strategies_used:
        strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
    
    print(f"\nStrategy usage:")
    for strategy, count in strategy_counts.items():
        print(f"  {strategy}: {count} times ({count/total_requests*100:.1f}%)")
    
    print(f"\nFuzzy Evidence System example completed successfully!")
    
    return results


if __name__ == "__main__":
    # Run the example
    try:
        results = run_example()
        print(f"\nExample completed with {len(results)} processed requests")
    except Exception as e:
        print(f"Example failed with error: {e}")
        import traceback
        traceback.print_exc() 