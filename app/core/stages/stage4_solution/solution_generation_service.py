"""
Solution Generation Service

This module contains the SolutionGenerationService class, which orchestrates
the process of generating optimal solutions by integrating different components
for information processing and response assembly.
"""

import logging
from typing import Dict, Any, List, Optional

from app.core.stages.stage4_solution.information_optimizer import InformationOptimizer
from app.core.stages.stage4_solution.content_structurer import ContentStructurer
from app.core.stages.stage4_solution.relevance_prioritizer import RelevancePrioritizer
from app.core.stages.stage4_solution.response_assembler import ResponseAssembler

class SolutionGenerationService:
    """
    Orchestrates the solution generation process by coordinating multiple components.
    
    This service integrates information optimization, content structuring, relevance
    prioritization, and response assembly to generate a comprehensive and optimal 
    solution tailored to the user's query.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Solution Generation Service.
        
        Args:
            config: Configuration dictionary for the service and its components
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Initialize components with their specific configurations
        optimizer_config = self.config.get("information_optimizer", {})
        structurer_config = self.config.get("content_structurer", {})
        prioritizer_config = self.config.get("relevance_prioritizer", {})
        assembler_config = self.config.get("response_assembler", {})
        
        self.information_optimizer = InformationOptimizer(optimizer_config)
        self.content_structurer = ContentStructurer(structurer_config)
        self.relevance_prioritizer = RelevancePrioritizer(prioritizer_config)
        self.response_assembler = ResponseAssembler(assembler_config)
        
        # Service-level configuration
        self.enable_optimization = self.config.get("enable_optimization", True)
        self.enable_metrics = self.config.get("enable_metrics", True)
        
        self.logger.info("Solution Generation Service initialized")
    
    async def generate_solution(self, 
                              domain_knowledge: Dict[str, Any],
                              user_query: Dict[str, Any],
                              context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an optimal solution based on domain knowledge and user query.
        
        Args:
            domain_knowledge: Processed domain knowledge from previous stages
            user_query: The user's query with enriched metadata
            context: Context information and state from previous processing
            
        Returns:
            Complete solution response with content and metadata
        """
        self.logger.info(f"Generating solution for query: {user_query.get('text', '')}")
        solution_metrics = {}
        
        # Step 1: Prioritize information by relevance and novelty
        self.logger.info("Prioritizing information by relevance and novelty")
        prioritized_info = await self.relevance_prioritizer.prioritize(
            domain_knowledge,
            user_query,
            context
        )
        
        if self.enable_metrics:
            solution_metrics["prioritization"] = prioritized_info.get("metrics", {})
        
        # Step 2: Optimize information for cognitive processing
        self.logger.info("Optimizing information")
        optimized_info = await self.information_optimizer.optimize(
            prioritized_info,
            user_query,
            context
        )
        
        if self.enable_metrics:
            solution_metrics["optimization"] = optimized_info.get("metrics", {})
        
        # Step 3: Structure content for optimal comprehension
        self.logger.info("Structuring content")
        structured_content = await self.content_structurer.structure(
            optimized_info,
            user_query,
            context
        )
        
        if self.enable_metrics:
            solution_metrics["structuring"] = structured_content.get("metrics", {})
        
        # Step 4: Assemble the final response
        self.logger.info("Assembling final response")
        response = await self.response_assembler.assemble(
            structured_content,
            prioritized_info,
            optimized_info,
            user_query,
            context
        )
        
        # Add overall solution metrics if enabled
        if self.enable_metrics:
            response["solution_metrics"] = solution_metrics
        
        self.logger.info("Solution generation completed")
        return response
    
    async def generate_quick_solution(self, 
                                    domain_knowledge: Dict[str, Any],
                                    user_query: Dict[str, Any],
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a simplified solution with reduced processing for time-sensitive scenarios.
        
        Args:
            domain_knowledge: Processed domain knowledge from previous stages
            user_query: The user's query with enriched metadata
            context: Context information and state from previous processing
            
        Returns:
            Quick solution response with content
        """
        self.logger.info(f"Generating quick solution for query: {user_query.get('text', '')}")
        
        # Simplified flow: Only prioritize and assemble
        prioritized_info = await self.relevance_prioritizer.prioritize(
            domain_knowledge,
            user_query,
            context,
            quick_mode=True
        )
        
        # Create simplified optimization data
        simplified_optimization = {
            "elements": prioritized_info.get("elements", []),
            "cognitive_load_estimate": 0.5,
            "optimization": {
                "cognitive_load_threshold": 1.0,
                "redundancy_threshold": 0.8
            }
        }
        
        # Create simple structure using top prioritized elements
        simple_structure = {
            "structure_type": "flat",
            "sections": [
                {
                    "title": "Quick Answer",
                    "element_ids": [
                        e.get("id") for e in prioritized_info.get("elements", [])[:10]
                    ]
                }
            ]
        }
        
        # Assemble with simplified components
        response = await self.response_assembler.assemble(
            simple_structure,
            prioritized_info,
            simplified_optimization,
            user_query,
            context
        )
        
        response["is_quick_solution"] = True
        self.logger.info("Quick solution generation completed")
        return response 