#!/usr/bin/env python
"""
Specialized Pipeline Example - Demonstration of the 8-stage pipeline.

This script demonstrates how to use the specialized orchestrator and model pipeline
to process queries using the Four-Sided Triangle architecture.
"""
import os
import sys
import json
import logging
import time
from typing import Dict, Any, List, Optional

# Ensure the app package is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.orchestrator import SpecializedOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def process_query(query: str, orchestrator: Optional[SpecializedOrchestrator] = None) -> Dict[str, Any]:
    """
    Process a query using the specialized orchestrator.
    
    Args:
        query: The query string to process
        orchestrator: Optional existing orchestrator instance
        
    Returns:
        Processing results
    """
    # Create orchestrator if not provided
    if orchestrator is None:
        orchestrator = SpecializedOrchestrator(config={
            "max_workers": 4,
            "stage_timeouts": {
                "query_processor": 10,  # seconds
                "semantic_atdb": 10,
                "domain_knowledge": 20,
                "reasoning": 30,
                "solution_generation": 45,
                "response_scoring": 15,
                "ensemble_diversification": 15,
                "threshold_verification": 10
            }
        })
    
    # Process the query
    start_time = time.time()
    result = orchestrator.process_query(query)
    processing_time = time.time() - start_time
    
    # Add processing time to result
    if "metadata" in result:
        result["metadata"]["processing_time"] = processing_time
    
    return result

def main():
    """Run the example."""
    print("Four-Sided Triangle Specialized Pipeline Example")
    print("=" * 60)
    
    # Create the orchestrator
    orchestrator = SpecializedOrchestrator()
    
    # Example queries
    queries = [
        "What is the optimal angle for a sprinter's starting blocks?",
        "Calculate the force required for a 75kg sprinter to accelerate from 0 to 10m/s in 2.3 seconds",
        "Which physiological factors contribute most to elite sprint performance?",
        "Compare the biomechanics of Usain Bolt's sprinting technique to the average Olympic finalist"
    ]
    
    # Process each query
    for i, query in enumerate(queries):
        print(f"\nQuery #{i+1}: {query}")
        print("-" * 60)
        
        try:
            result = process_query(query, orchestrator)
            
            # Pretty print key parts of the result
            print("Processing completed in {:.2f} seconds".format(
                result.get("metadata", {}).get("processing_time", 0)
            ))
            
            print("\nProcessed query:")
            processed = result.get("processed_query", {})
            if processed:
                intent = processed.get("intent", "Unknown")
                complexity = processed.get("complexity", "Unknown")
                print(f"  Intent: {intent}")
                print(f"  Complexity: {complexity}")
            
            print("\nSolutions:")
            solutions = result.get("solutions", [])
            for j, solution in enumerate(solutions[:2]):  # Show just the first 2
                print(f"  Solution #{j+1}: {solution.get('summary', 'No summary')}")
            
            if len(solutions) > 2:
                print(f"  ... and {len(solutions) - 2} more solutions")
            
            # Save full result to file
            filename = f"query_{i+1}_result.json"
            with open(filename, "w") as f:
                json.dump(result, f, indent=2)
            
            print(f"\nFull result saved to {filename}")
        
        except Exception as e:
            print(f"Error processing query: {str(e)}")
    
    print("\nExample complete!")

if __name__ == "__main__":
    main() 