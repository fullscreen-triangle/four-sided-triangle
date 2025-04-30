import logging
from typing import Dict, Any, List
import re

logger = logging.getLogger(__name__)

class BypassStrategySelector:
    """
    Selects and configures bypass strategies to overcome LLM throttling.
    
    This class implements multiple strategies to bypass different types of
    throttling detected in LLM responses.
    """
    
    def __init__(self):
        """Initialize the bypass strategy selector."""
        self.available_strategies = {
            "token_limitation": self._create_partition_strategy,
            "depth_limitation": self._create_reframing_strategy,
            "computation_limitation": self._create_progressive_strategy
        }
    
    def select_strategy(
        self, 
        throttle_pattern: str, 
        query: str,
        initial_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Select an appropriate bypass strategy based on the throttle pattern.
        
        Args:
            throttle_pattern: The detected throttle pattern
            query: The original query
            initial_response: The initial LLM response
            
        Returns:
            A configured bypass strategy
        """
        # Get strategy creator function
        if throttle_pattern in self.available_strategies:
            strategy_creator = self.available_strategies[throttle_pattern]
        else:
            # Default to partition strategy
            logger.warning(f"Unknown throttle pattern: {throttle_pattern}. Using default strategy.")
            strategy_creator = self._create_partition_strategy
        
        # Create and return the strategy
        return strategy_creator(query, initial_response)
    
    def _create_partition_strategy(
        self, 
        query: str, 
        initial_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a query partitioning strategy.
        
        This splits the query into multiple focused sub-queries.
        """
        # Extract key subject and parameters from initial response
        subject = initial_response.get("keySubject", "")
        
        # Determine aspects to partition based on domain
        aspects = self._identify_query_aspects(query, subject)
        
        # Create subqueries for each aspect
        subqueries = []
        for aspect in aspects:
            subquery_text = self._create_focused_subquery(query, subject, aspect)
            subqueries.append({
                "text": subquery_text,
                "aspect": aspect
            })
        
        return {
            "name": "query_partitioning",
            "subqueries": subqueries,
            "original_query": query
        }
    
    def _create_reframing_strategy(
        self, 
        query: str, 
        initial_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a depth reframing strategy.
        
        This reframes the query to encourage deeper analysis.
        """
        # Extract key subject from initial response
        subject = initial_response.get("keySubject", "")
        
        # Generate depth-encouraging instruction
        depth_instruction = (
            "Perform an exhaustive and comprehensive analysis. "
            "Explore all possible parameters, relationships, and implications, "
            "including those not explicitly mentioned in the query. "
            "Consider edge cases, special conditions, and domain-specific knowledge."
        )
        
        # Reframe the query to encourage depth
        reframed_query = (
            f"I need a comprehensive and thorough analysis of the following query, "
            f"including ALL possible parameters and interpretations: {query}"
        )
        
        return {
            "name": "depth_reframing",
            "reframed_query": reframed_query,
            "reframed_instruction": depth_instruction,
            "original_query": query,
            "key_subject": subject
        }
    
    def _create_progressive_strategy(
        self, 
        query: str, 
        initial_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a progressive disclosure strategy.
        
        This breaks the analysis into multiple progressive steps.
        """
        # Initial query focuses on basic parameter identification
        initial_query = f"Identify the core parameters and entities in: {query}"
        
        # Follow-up queries build upon initial findings
        followup_queries = [
            f"For the query '{query}', analyze relationships between the parameters previously identified.",
            f"For the query '{query}', identify any edge cases, implicit parameters, and secondary effects not mentioned earlier."
        ]
        
        return {
            "name": "progressive_disclosure",
            "initial_query": initial_query,
            "followup_queries": followup_queries,
            "original_query": query
        }
    
    def _identify_query_aspects(self, query: str, subject: str) -> List[str]:
        """Identify query aspects for partitioning."""
        # Default aspects for different domains
        domain_aspects = {
            "sprint": ["biomechanics", "performance", "physiology", "technique"],
            "body": ["composition", "segments", "dimensions", "metrics"],
            "athlete": ["performance", "measurements", "characteristics", "capabilities"],
            "genetic": ["markers", "traits", "influences", "potentials"]
        }
        
        # Find matching domain
        matching_domain = None
        for domain in domain_aspects:
            if domain in query.lower() or domain in subject.lower():
                matching_domain = domain
                break
        
        # If no specific domain matches, use a general set
        if not matching_domain:
            return ["main_parameters", "relationships", "implications", "edge_cases"]
        
        return domain_aspects[matching_domain]
    
    def _create_focused_subquery(self, query: str, subject: str, aspect: str) -> str:
        """Create a focused subquery for a specific aspect."""
        # Clean up the aspect name for readability
        readable_aspect = aspect.replace("_", " ")
        
        return (
            f"Regarding {subject} in the context of this query: '{query}', "
            f"focus specifically on analyzing the {readable_aspect} aspect. "
            f"Identify all parameters, relationships, and implications related to {readable_aspect}."
        )
