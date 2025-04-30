"""
Response Comparison Service

This module contains the ResponseComparisonService class, which orchestrates
the process of comparing and combining multiple response candidates to
generate an optimal combined response.
"""

import logging
from typing import Dict, Any, List, Optional

from app.core.stages.stage6_comparison.ensemble_diversifier import EnsembleDiversifier
from app.core.stages.stage6_comparison.diversity_calculator import DiversityCalculator
from app.core.stages.stage6_comparison.quality_diversity_optimizer import QualityDiversityOptimizer
from app.core.stages.stage6_comparison.response_combiner import ResponseCombiner
from app.orchestrator.interfaces import AbstractPipelineStage

class ResponseComparisonService(AbstractPipelineStage):
    """
    Orchestrates the response comparison process by implementing ensemble diversification,
    computing pairwise diversity scores, and optimizing quality-diversity balance.
    
    This service integrates ensemble diversification, diversity calculation,
    quality-diversity optimization, and response combination to generate an
    optimal combined response from multiple candidates.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Response Comparison Service.
        
        Args:
            config: Configuration dictionary for the service and its components
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Initialize components with their specific configurations
        ensemble_config = self.config.get("ensemble_diversifier", {})
        diversity_config = self.config.get("diversity_calculator", {})
        optimizer_config = self.config.get("quality_diversity_optimizer", {})
        combiner_config = self.config.get("response_combiner", {})
        
        self.ensemble_diversifier = EnsembleDiversifier(ensemble_config)
        self.diversity_calculator = DiversityCalculator(diversity_config)
        self.quality_diversity_optimizer = QualityDiversityOptimizer(optimizer_config)
        self.response_combiner = ResponseCombiner(combiner_config)
        
        # Service-level configuration
        self.alpha_parameter = self.config.get("alpha_parameter", 0.7)
        self.enable_alternative_generation = self.config.get("enable_alternative_generation", True)
        self.max_alternatives = self.config.get("max_alternatives", 3)
        
        self.logger.info("Response Comparison Service initialized")
    
    @property
    def stage_id(self) -> str:
        """Get the unique identifier for this pipeline stage."""
        return "response_comparison"
    
    def process(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and compare multiple response candidates.
        
        Args:
            prompt: The prompt for response comparison
            context: The current session context containing primary response and evaluation metrics
            
        Returns:
            Optimized combined response with diversity metrics
        """
        self.logger.info("Comparing and combining response candidates")
        
        # Extract relevant data from context
        primary_response = context.get("stage_outputs", {}).get("solution_generation", {})
        evaluation_metrics = context.get("stage_outputs", {}).get("response_scoring", {})
        
        # Get alternative responses if available, or generate them if enabled
        alternative_responses = primary_response.get("alternatives", [])
        
        if not alternative_responses and self.enable_alternative_generation:
            self.logger.info("Generating alternative responses")
            alternative_responses = self._generate_alternative_responses(
                primary_response, 
                context, 
                self.max_alternatives
            )
        
        # If still no alternatives, return primary response with minimal processing
        if not alternative_responses:
            self.logger.info("No alternative responses available, using primary response only")
            return self._process_single_response(primary_response, evaluation_metrics)
        
        # Step 1: Calculate pairwise diversity scores
        self.logger.info("Calculating pairwise diversity scores")
        diversity_scores = self.diversity_calculator.calculate_diversity(
            primary_response,
            alternative_responses
        )
        
        # Step 2: Apply ensemble diversification
        self.logger.info("Applying ensemble diversification")
        diversified_ensemble = self.ensemble_diversifier.diversify(
            primary_response,
            alternative_responses,
            diversity_scores,
            alpha=self.alpha_parameter
        )
        
        # Step 3: Optimize quality-diversity balance
        self.logger.info("Optimizing quality-diversity balance")
        optimized_components = self.quality_diversity_optimizer.optimize(
            diversified_ensemble,
            evaluation_metrics,
            diversity_scores
        )
        
        # Step 4: Combine responses into optimal integrated response
        self.logger.info("Combining responses into optimal integrated response")
        combined_response = self.response_combiner.combine(
            optimized_components,
            primary_response,
            evaluation_metrics
        )
        
        # Add diversity and ensemble metrics to response
        combined_response["diversity_metrics"] = diversity_scores
        combined_response["ensemble_metrics"] = {
            "alpha_parameter": self.alpha_parameter,
            "ensemble_size": len(diversified_ensemble),
            "quality_diversity_trade_off": self.quality_diversity_optimizer.get_trade_off_metrics()
        }
        
        # Update metrics for monitoring
        self._update_metrics({
            "diversity_avg": diversity_scores.get("average_diversity", 0.0),
            "ensemble_size": len(diversified_ensemble),
            "primary_contribution": combined_response.get("primary_contribution_ratio", 0.0)
        })
        
        self.logger.info("Response comparison completed")
        return combined_response
    
    def refine(self, refinement_prompt: str, context: Dict[str, Any], previous_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Refine the combined response based on feedback.
        
        Args:
            refinement_prompt: Prompt specifically for refinement
            context: The current session context
            previous_output: The previous combined response
            
        Returns:
            Refined combined response
        """
        self.logger.info("Refining combined response")
        
        # Re-process with updated context containing refinement data
        refined_response = self.process(refinement_prompt, context)
        
        # Add refinement tracking
        refined_response["is_refinement"] = True
        refined_response["refinement_changes"] = self._track_refinement_changes(
            previous_output, refined_response)
        
        self.logger.info("Response refinement completed")
        return refined_response
    
    def _process_single_response(self, primary_response: Dict[str, Any], 
                               evaluation_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single response when no alternatives are available.
        
        Args:
            primary_response: The primary response from solution generation
            evaluation_metrics: Evaluation metrics from response scoring
            
        Returns:
            Processed response with minimal ensemble metrics
        """
        # Shallow copy the primary response
        processed_response = dict(primary_response)
        
        # Add ensemble metrics
        processed_response["ensemble_metrics"] = {
            "ensemble_size": 1,
            "alpha_parameter": self.alpha_parameter,
            "single_response": True
        }
        
        # Add diversity metrics (none since single response)
        processed_response["diversity_metrics"] = {
            "average_diversity": 0.0,
            "pairwise_scores": [],
            "diversity_components": {}
        }
        
        # Add contribution ratio
        processed_response["primary_contribution_ratio"] = 1.0
        
        return processed_response
    
    def _generate_alternative_responses(self, primary_response: Dict[str, Any],
                                      context: Dict[str, Any],
                                      max_alternatives: int) -> List[Dict[str, Any]]:
        """
        Generate alternative response candidates when none are provided.
        
        Args:
            primary_response: The primary response from solution generation
            context: The current session context
            max_alternatives: Maximum number of alternatives to generate
            
        Returns:
            List of alternative response candidates
        """
        # In a full implementation, this would use techniques like:
        # 1. Parameter perturbation
        # 2. Different structuring approaches
        # 3. Alternative optimization objectives
        
        # For this implementation, we create simplified alternatives
        alternatives = []
        
        # Extract original elements
        original_elements = primary_response.get("content", {}).get("elements", [])
        if not original_elements:
            return []
        
        # Create a structure-focused alternative (emphasis on organization)
        if len(alternatives) < max_alternatives and len(original_elements) > 5:
            structure_alt = dict(primary_response)
            structure_alt["id"] = "structure_alternative"
            structure_alt["content"] = dict(primary_response.get("content", {}))
            
            # Reorganize sections with different grouping
            if "sections" in structure_alt["content"]:
                sections = structure_alt["content"]["sections"]
                if len(sections) > 1:
                    # Merge some sections in this alternative
                    merged_sections = []
                    for i in range(0, len(sections), 2):
                        if i + 1 < len(sections):
                            merged = {
                                "title": f"{sections[i]['title']} + {sections[i+1]['title']}",
                                "element_ids": sections[i].get("element_ids", []) + sections[i+1].get("element_ids", [])
                            }
                            merged_sections.append(merged)
                        else:
                            merged_sections.append(sections[i])
                    
                    structure_alt["content"]["sections"] = merged_sections
            
            alternatives.append(structure_alt)
        
        # Create a conciseness-focused alternative (fewer but higher relevance elements)
        if len(alternatives) < max_alternatives and len(original_elements) > 4:
            concise_alt = dict(primary_response)
            concise_alt["id"] = "concise_alternative"
            concise_alt["content"] = dict(primary_response.get("content", {}))
            
            # Select only highest relevance elements
            top_elements = sorted(
                original_elements, 
                key=lambda x: x.get("relevance", 0.0), 
                reverse=True
            )[:max(3, len(original_elements) // 2)]
            
            concise_alt["content"]["elements"] = top_elements
            
            # Adjust sections to only include these elements
            top_element_ids = [elem.get("id") for elem in top_elements]
            if "sections" in concise_alt["content"]:
                for section in concise_alt["content"]["sections"]:
                    section["element_ids"] = [
                        elem_id for elem_id in section.get("element_ids", [])
                        if elem_id in top_element_ids
                    ]
            
            alternatives.append(concise_alt)
        
        # Create a complementary-information alternative (different emphasis)
        if len(alternatives) < max_alternatives and len(original_elements) > 3:
            complement_alt = dict(primary_response)
            complement_alt["id"] = "complementary_alternative"
            complement_alt["content"] = dict(primary_response.get("content", {}))
            
            # Prioritize different elements
            if "elements" in complement_alt["content"]:
                elements = complement_alt["content"]["elements"]
                # Boost the relevance of lower-scored elements
                for elem in elements:
                    if "relevance" in elem:
                        # Invert the relevance within bounds
                        elem["relevance"] = 1.0 - (elem["relevance"] * 0.5)
            
            alternatives.append(complement_alt)
        
        return alternatives
    
    def _track_refinement_changes(self, previous_output: Dict[str, Any], 
                                refined_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track changes between previous and refined output.
        
        Args:
            previous_output: The output before refinement
            refined_output: The output after refinement
            
        Returns:
            Dictionary of tracked changes
        """
        changes = {
            "element_count_change": 0,
            "section_count_change": 0,
            "component_changes": [],
        }
        
        # Compare element counts
        prev_elements = previous_output.get("content", {}).get("elements", [])
        refined_elements = refined_output.get("content", {}).get("elements", [])
        changes["element_count_change"] = len(refined_elements) - len(prev_elements)
        
        # Compare section counts
        prev_sections = previous_output.get("content", {}).get("sections", [])
        refined_sections = refined_output.get("content", {}).get("sections", [])
        changes["section_count_change"] = len(refined_sections) - len(prev_sections)
        
        # Track key metric changes
        for key in ["primary_contribution_ratio", "average_diversity"]:
            if key in previous_output and key in refined_output:
                changes[f"{key}_change"] = refined_output[key] - previous_output[key]
        
        return changes 