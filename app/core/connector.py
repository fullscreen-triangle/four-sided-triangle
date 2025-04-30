"""
Core Components Connector - Integration of core components with the pipeline.

This module connects the specialized core components (Glycolytic Query Investment Cycle,
Metacognitive Task Partitioning, and Throttle Detection) with the main system pipeline,
ensuring proper data flow and coordination between components.
"""
import logging
from typing import Dict, Any, List, Optional, Tuple, Union

from app.core.glycolytic_cycle import GlycolicQueryInvestmentCycle
from app.core.metacognitive import MetacognitiveTaskManager
from app.core.throttle_detection import ThrottleAdaptiveSystem

class CoreComponentConnector:
    """
    Connector for integrating core components with the main pipeline.
    
    This class serves as the integration point between the specialized core components
    and the rest of the system, managing data flow, coordination, and providing
    a unified interface for the orchestrator to interact with these components.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Core Component Connector.
        
        Args:
            config: Optional configuration parameters
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize core components
        self.metacognitive = MetacognitiveTaskManager(
            config=self.config.get("metacognitive", {})
        )
        
        self.glycolytic = GlycolicQueryInvestmentCycle(
            config=self.config.get("glycolytic", {})
        )
        
        self.throttle_adaptive = ThrottleAdaptiveSystem(
            config=self.config.get("throttle_adaptive", {})
        )
        
        self.logger.info("Initialized Core Component Connector")
    
    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a query through all core components.
        
        Args:
            query: User query
            context: Optional context information
            
        Returns:
            Processed query with component outputs
        """
        context = context or {}
        result = {
            "original_query": query,
            "context": context,
            "processing_stages": {}
        }
        
        # Step 1: Check for throttling in previous responses (if available)
        if "previous_response" in context:
            is_throttled, pattern_type, confidence = self.throttle_adaptive.detect_throttling(
                context["previous_response"], query, context.get("performance_metrics", {})
            )
            
            result["processing_stages"]["throttle_detection"] = {
                "is_throttled": is_throttled,
                "pattern_type": pattern_type,
                "confidence": confidence
            }
            
            # Apply bypass strategy if throttling detected
            if is_throttled:
                modified_queries = self.throttle_adaptive.apply_bypass_strategy(query, pattern_type)
                result["processing_stages"]["throttle_bypass"] = {
                    "original_query": query,
                    "modified_queries": modified_queries
                }
                
                # Update query to use the first modified query
                # In a real implementation, this would be more sophisticated
                if modified_queries and "query" in modified_queries[0]:
                    query = modified_queries[0]["query"]
                    result["modified_query"] = query
        
        # Step 2: Decompose query using metacognitive task partitioning
        decomposed_query = self.metacognitive.decompose_query(query, context)
        result["processing_stages"]["metacognitive"] = {
            "domains": decomposed_query["domains"],
            "sub_queries_count": len(decomposed_query["sub_queries"]),
            "dependency_graph": decomposed_query["dependency_graph"]
        }
        
        # Step 3: Allocate resources using glycolytic investment cycle
        investments = self.glycolytic.allocate_investments(decomposed_query)
        result["processing_stages"]["glycolytic"] = {
            "investments": investments,
            "total_investment": sum(inv["allocation"] for inv in investments.values()) if investments else 0
        }
        
        # Prepare final output structure for pipeline
        result["decomposed_query"] = decomposed_query
        result["investments"] = investments
        
        # Include full sub-queries for downstream processing
        result["sub_queries"] = decomposed_query["sub_queries"]
        
        return result
    
    def process_results(self, query_id: str, results: Dict[str, Any], 
                       investments: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process results from query execution through core components.
        
        Args:
            query_id: ID of the original query
            results: Results from component execution
            investments: Original investment allocations
            
        Returns:
            Processed results with component metrics
        """
        processed_results, total_payoff = self.glycolytic.harvest_results(investments, results)
        
        return {
            "query_id": query_id,
            "processed_results": processed_results,
            "total_information_payoff": total_payoff,
            "roi": total_payoff / sum(inv["allocation"] for inv in investments.values()) if investments else 0
        }
    
    def update_throttle_strategy_performance(self, strategy_name: str, pattern_type: str, 
                                            success_score: float) -> None:
        """
        Update performance record for a throttle bypass strategy.
        
        Args:
            strategy_name: Name of the strategy
            pattern_type: Type of throttling pattern
            success_score: Score indicating how successful the strategy was
        """
        self.throttle_adaptive.update_strategy_performance(strategy_name, pattern_type, success_score)
    
    def get_recommended_execution_order(self, decomposed_query: Dict[str, Any]) -> List[str]:
        """
        Get recommended execution order for sub-queries based on dependencies.
        
        Args:
            decomposed_query: Decomposed query with dependency graph
            
        Returns:
            List of sub-query IDs in recommended execution order
        """
        # Extract the dependency graph
        dependency_graph = decomposed_query.get("dependency_graph", {})
        sub_queries = {q["id"]: q for q in decomposed_query.get("sub_queries", [])}
        
        # Build execution order using topological sort
        visited = set()
        temp_visited = set()
        order = []
        
        def visit(node_id):
            if node_id in temp_visited:
                # Cyclic dependency detected
                self.logger.warning(f"Cyclic dependency detected for node {node_id}")
                return
            
            if node_id in visited:
                return
            
            temp_visited.add(node_id)
            
            # Visit dependencies first
            for dep_id in dependency_graph.get(node_id, []):
                visit(dep_id)
            
            temp_visited.remove(node_id)
            visited.add(node_id)
            order.append(node_id)
        
        # Visit all nodes
        for node_id in sub_queries.keys():
            if node_id not in visited:
                visit(node_id)
        
        # Reverse to get correct execution order
        return list(reversed(order))
    
    def adapt_to_feedback(self, feedback: Dict[str, Any]) -> None:
        """
        Adapt component behavior based on feedback.
        
        Args:
            feedback: Feedback data for learning and adaptation
        """
        # Update throttle strategy performance if applicable
        if "throttle_strategy" in feedback:
            self.update_throttle_strategy_performance(
                feedback["throttle_strategy"].get("name", ""),
                feedback["throttle_strategy"].get("pattern_type", ""),
                feedback["throttle_strategy"].get("success_score", 0.0)
            )
        
        # Additional adaptation logic could be added here
        
        self.logger.debug(f"Adapted to feedback: {feedback}")
        
    def get_component_status(self) -> Dict[str, Any]:
        """
        Get status information about core components.
        
        Returns:
            Dictionary with component status information
        """
        return {
            "metacognitive": {
                "status": "active",
                "domains_configured": len(getattr(self.metacognitive, "knowledge_domains", {})),
                "templates_configured": len(getattr(self.metacognitive, "task_templates", {}))
            },
            "glycolytic": {
                "status": "active",
                "max_investment": getattr(self.glycolytic, "max_total_investment", 0),
                "historical_roi_tracked": len(getattr(self.glycolytic, "historical_roi", {}))
            },
            "throttle_adaptive": {
                "status": "active",
                "patterns_configured": len(getattr(self.throttle_adaptive, "throttle_patterns", {})),
                "strategies_configured": len(getattr(self.throttle_adaptive, "adaptation_strategies", {})),
                "performance_records": len(getattr(self.throttle_adaptive, "recent_performances", {}))
            }
        } 