"""
Knowledge Prioritizer

This module contains the KnowledgePrioritizer class, which is responsible for
prioritizing and ranking extracted knowledge elements based on relevance to the query.
"""

import logging
from typing import Dict, Any, List, Optional

class KnowledgePrioritizer:
    """
    Prioritizes and ranks extracted knowledge elements.
    
    This class implements algorithms to score knowledge elements by relevance,
    map dependencies between elements, and assess confidence levels.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Knowledge Prioritizer.
        
        Args:
            config: Configuration dictionary for prioritization parameters
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Default prioritization parameters
        self.relevance_weight = self.config.get("relevance_weight", 0.5)
        self.confidence_weight = self.config.get("confidence_weight", 0.3)
        self.specificity_weight = self.config.get("specificity_weight", 0.2)
        
        self.logger.info("Knowledge Prioritizer initialized")
    
    async def prioritize(self, validated_knowledge: Dict[str, Any], 
                        semantic_representation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prioritize knowledge elements based on relevance to the query.
        
        Args:
            validated_knowledge: Validated knowledge from the previous step
            semantic_representation: The semantic representation from Stage 1
            
        Returns:
            Knowledge with prioritized elements
        """
        self.logger.info("Starting knowledge prioritization process")
        
        # Extract parameters from semantic representation for relevance scoring
        query_parameters = semantic_representation.get("parameters", {})
        query_intent = semantic_representation.get("intent", "")
        
        # Merge elements from all domains
        all_elements = []
        for domain, domain_knowledge in validated_knowledge.items():
            if isinstance(domain_knowledge, dict) and "elements" in domain_knowledge:
                for element in domain_knowledge["elements"]:
                    # Add domain identifier to each element
                    element["domain"] = domain
                    all_elements.append(element)
        
        # Calculate relevance scores
        elements_with_scores = self._calculate_relevance_scores(
            all_elements, 
            query_parameters, 
            query_intent
        )
        
        # Map dependencies between elements
        elements_with_dependencies = self._map_dependencies(elements_with_scores)
        
        # Sort elements by combined score (descending)
        sorted_elements = sorted(
            elements_with_dependencies, 
            key=lambda x: x.get("combined_score", 0), 
            reverse=True
        )
        
        # Create result structure
        result = {
            "elements": sorted_elements,
            "metadata": {
                "total_elements": len(sorted_elements),
                "prioritization_metrics": {
                    "relevance_weight": self.relevance_weight,
                    "confidence_weight": self.confidence_weight,
                    "specificity_weight": self.specificity_weight
                }
            }
        }
        
        self.logger.info("Knowledge prioritization completed")
        return result
    
    def _calculate_relevance_scores(self, elements: List[Dict[str, Any]], 
                                  query_parameters: Dict[str, Any],
                                  query_intent: str) -> List[Dict[str, Any]]:
        """
        Calculate relevance scores for each knowledge element.
        
        Args:
            elements: List of knowledge elements
            query_parameters: Parameters extracted from the query
            query_intent: Intent of the query
            
        Returns:
            Elements with added relevance scores
        """
        scored_elements = []
        
        for element in elements:
            # Calculate relevance score based on how well the element matches the query
            relevance_score = self._calculate_element_relevance(element, query_parameters, query_intent)
            
            # Get confidence score (if available) or default to 0.5
            confidence_score = element.get("confidence", 0.5)
            
            # Calculate specificity score based on detail level of the element
            specificity_score = self._calculate_element_specificity(element)
            
            # Calculate combined score using weighted sum
            combined_score = (
                relevance_score * self.relevance_weight +
                confidence_score * self.confidence_weight +
                specificity_score * self.specificity_weight
            )
            
            # Add scores to the element
            element_with_scores = element.copy()
            element_with_scores["relevance_score"] = relevance_score
            element_with_scores["specificity_score"] = specificity_score
            element_with_scores["combined_score"] = combined_score
            
            scored_elements.append(element_with_scores)
        
        return scored_elements
    
    def _calculate_element_relevance(self, element: Dict[str, Any], 
                                   query_parameters: Dict[str, Any],
                                   query_intent: str) -> float:
        """
        Calculate how relevant an element is to the query.
        
        Args:
            element: Knowledge element
            query_parameters: Parameters from the query
            query_intent: Intent of the query
            
        Returns:
            Relevance score (0.0-1.0)
        """
        relevance_score = 0.0
        max_score = 0.0
        
        # Check if element description matches intent
        if "description" in element and query_intent:
            desc_lower = element["description"].lower()
            intent_lower = query_intent.lower()
            
            # Simple keyword matching (could be replaced with more sophisticated semantic matching)
            intent_keywords = intent_lower.split()
            intent_matches = sum(1 for kw in intent_keywords if kw in desc_lower)
            if intent_keywords:
                intent_score = intent_matches / len(intent_keywords)
                relevance_score += intent_score
                max_score += 1.0
        
        # Check if element has formulas or reference values relevant to query parameters
        if "reference_values" in element and query_parameters:
            ref_values = element.get("reference_values", {})
            param_matches = 0
            
            for param_name in query_parameters:
                if param_name in ref_values:
                    param_matches += 1
            
            if query_parameters:
                param_score = param_matches / len(query_parameters)
                relevance_score += param_score
                max_score += 1.0
        
        # Check formulas for parameter matches
        if "formulas" in element and query_parameters:
            formulas = element.get("formulas", [])
            formula_matches = 0
            
            for formula in formulas:
                if "variables" in formula:
                    for param_name in query_parameters:
                        if param_name in formula["variables"]:
                            formula_matches += 1
                            break
            
            if formulas:
                formula_score = formula_matches / len(formulas)
                relevance_score += formula_score
                max_score += 1.0
        
        # Normalize the final score
        if max_score > 0:
            normalized_score = relevance_score / max_score
        else:
            # If no scoring was possible, assign a neutral score
            normalized_score = 0.5
        
        return normalized_score
    
    def _calculate_element_specificity(self, element: Dict[str, Any]) -> float:
        """
        Calculate how specific and detailed an element is.
        
        Args:
            element: Knowledge element
            
        Returns:
            Specificity score (0.0-1.0)
        """
        specificity_score = 0.0
        max_score = 4.0  # Maximum possible points
        
        # Check if the element has formulas (more specific)
        if "formulas" in element and element["formulas"]:
            specificity_score += 1.0
            
            # More points for formulas with variables explained
            for formula in element["formulas"]:
                if "variables" in formula and formula["variables"]:
                    specificity_score += 0.5
                    break
        
        # Check if the element has constraints (more specific)
        if "constraints" in element and element["constraints"]:
            specificity_score += 1.0
        
        # Check if the element has reference values (more specific)
        if "reference_values" in element and element["reference_values"]:
            specificity_score += 1.0
        
        # Check if the element has a detailed description
        if "description" in element and len(element["description"]) > 100:
            specificity_score += 0.5
        
        # Normalize the score
        normalized_score = min(specificity_score / max_score, 1.0)
        
        return normalized_score
    
    def _map_dependencies(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Map dependencies between knowledge elements.
        
        Args:
            elements: List of knowledge elements with scores
            
        Returns:
            Elements with mapped dependencies
        """
        elements_with_deps = []
        element_by_id = {elem["id"]: elem for elem in elements if "id" in elem}
        
        for element in elements:
            elem_with_deps = element.copy()
            
            # Initialize dependencies list if not present
            if "dependencies" not in elem_with_deps:
                elem_with_deps["dependencies"] = []
            
            # Look for explicit dependencies
            # (In a real implementation, this would be more sophisticated)
            
            # Check if formulas reference other elements
            if "formulas" in element:
                for formula in element.get("formulas", []):
                    # Check formula description for element IDs
                    if "description" in formula:
                        for other_id in element_by_id:
                            # Simple check - could be much more sophisticated
                            if other_id != element.get("id") and other_id in formula["description"]:
                                if other_id not in elem_with_deps["dependencies"]:
                                    elem_with_deps["dependencies"].append(other_id)
            
            # Check if reference values depend on other elements
            if "reference_values" in element:
                for ref_key, ref_value in element.get("reference_values", {}).items():
                    if isinstance(ref_value, dict) and "description" in ref_value:
                        for other_id in element_by_id:
                            if other_id != element.get("id") and other_id in ref_value["description"]:
                                if other_id not in elem_with_deps["dependencies"]:
                                    elem_with_deps["dependencies"].append(other_id)
            
            elements_with_deps.append(elem_with_deps)
        
        return elements_with_deps 