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
                        semantic_representation: Dict[str, Any],
                        enable_multi_model_fusion: bool = False) -> Dict[str, Any]:
        """
        Prioritize knowledge elements by relevance, confidence, and importance.
        
        Args:
            validated_knowledge: Validated knowledge from all domains
            semantic_representation: Semantic representation for relevance scoring
            enable_multi_model_fusion: Whether to enable fusion of insights from multiple models
            
        Returns:
            Prioritized and structured knowledge elements
        """
        self.logger.info("Starting knowledge prioritization process")
        
        # Extract all knowledge elements
        all_elements = []
        for domain, knowledge in validated_knowledge.items():
            if "elements" in knowledge:
                for element in knowledge["elements"]:
                    element["source_domain"] = domain
                    all_elements.append(element)
        
        self.logger.info(f"Processing {len(all_elements)} knowledge elements for prioritization")
        
        # Perform multi-model fusion if enabled
        if enable_multi_model_fusion:
            all_elements = await self._perform_multi_model_fusion(all_elements)
            self.logger.info(f"Multi-model fusion complete, {len(all_elements)} elements after fusion")
        
        # Calculate relevance scores
        for element in all_elements:
            element["relevance_score"] = self._calculate_relevance(element, semantic_representation)
        
        # Calculate importance scores
        for element in all_elements:
            element["importance_score"] = self._calculate_importance(element)
        
        # Calculate composite priority scores
        for element in all_elements:
            element["priority_score"] = self._calculate_priority(element)
        
        # Sort by priority score (descending)
        prioritized_elements = sorted(all_elements, key=lambda x: x["priority_score"], reverse=True)
        
        # Group elements by category for better organization
        categorized_elements = self._categorize_elements(prioritized_elements)
        
        # Map dependencies between elements
        dependency_map = self._map_dependencies(prioritized_elements)
        
        # Calculate confidence distribution
        confidence_distribution = self._calculate_confidence_distribution(prioritized_elements)
        
        result = {
            "elements": prioritized_elements,
            "categories": categorized_elements,
            "dependencies": dependency_map,
            "confidence_distribution": confidence_distribution,
            "prioritization_metadata": {
                "total_elements": len(prioritized_elements),
                "multi_model_fusion_enabled": enable_multi_model_fusion,
                "average_priority": sum(e["priority_score"] for e in prioritized_elements) / len(prioritized_elements) if prioritized_elements else 0.0,
                "high_priority_count": sum(1 for e in prioritized_elements if e["priority_score"] > 0.8),
                "low_priority_count": sum(1 for e in prioritized_elements if e["priority_score"] < 0.3)
            }
        }
        
        self.logger.info(f"Knowledge prioritization completed: {len(prioritized_elements)} elements prioritized")
        return result
    
    async def _perform_multi_model_fusion(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Perform fusion of insights from multiple domain expert models.
        
        Args:
            elements: List of knowledge elements from multiple models
            
        Returns:
            Fused and deduplicated knowledge elements
        """
        self.logger.info("Performing multi-model fusion")
        
        # Group elements by domain and model source
        model_groups = {}
        for element in elements:
            domain = element.get("source_domain", "unknown")
            model_source = element.get("model_source", "primary")
            
            # Create base domain key (remove _primary/_secondary suffix)
            base_domain = domain.replace("_primary", "").replace("_secondary", "")
            
            if base_domain not in model_groups:
                model_groups[base_domain] = {"primary": [], "secondary": []}
            
            if "secondary" in domain or model_source == "secondary":
                model_groups[base_domain]["secondary"].append(element)
            else:
                model_groups[base_domain]["primary"].append(element)
        
        fused_elements = []
        
        # Process each domain group
        for domain, models in model_groups.items():
            primary_elements = models.get("primary", [])
            secondary_elements = models.get("secondary", [])
            
            # Add all primary elements
            fused_elements.extend(primary_elements)
            
            # Fuse secondary elements, avoiding duplicates
            for secondary_element in secondary_elements:
                if not self._is_duplicate_insight(secondary_element, primary_elements):
                    # Mark as complementary insight
                    secondary_element["fusion_type"] = "complementary"
                    secondary_element["complements_primary"] = True
                    fused_elements.append(secondary_element)
                else:
                    # Merge confidence scores for similar insights
                    similar_primary = self._find_similar_element(secondary_element, primary_elements)
                    if similar_primary:
                        similar_primary["confidence"] = max(
                            similar_primary.get("confidence", 0.0),
                            secondary_element.get("confidence", 0.0)
                        )
                        similar_primary["multi_model_validated"] = True
                        similar_primary["secondary_confidence"] = secondary_element.get("confidence", 0.0)
        
        # Identify consensus insights (validated by both models)
        for element in fused_elements:
            if element.get("multi_model_validated", False):
                element["consensus_insight"] = True
                element["confidence"] = min(element.get("confidence", 0.0) + 0.1, 1.0)  # Boost confidence for consensus
        
        return fused_elements
    
    def _is_duplicate_insight(self, element: Dict[str, Any], existing_elements: List[Dict[str, Any]]) -> bool:
        """Check if an insight is a duplicate of existing elements."""
        element_content = element.get("content", "").lower()
        
        for existing in existing_elements:
            existing_content = existing.get("content", "").lower()
            
            # Simple similarity check (in production, would use more sophisticated methods)
            if self._calculate_text_similarity(element_content, existing_content) > 0.7:
                return True
        
        return False
    
    def _find_similar_element(self, element: Dict[str, Any], existing_elements: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find the most similar element in existing elements."""
        element_content = element.get("content", "").lower()
        best_match = None
        best_similarity = 0.0
        
        for existing in existing_elements:
            existing_content = existing.get("content", "").lower()
            similarity = self._calculate_text_similarity(element_content, existing_content)
            
            if similarity > best_similarity and similarity > 0.7:
                best_similarity = similarity
                best_match = existing
        
        return best_match
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity score."""
        # Simple word overlap similarity (in production, would use embeddings or other methods)
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_relevance(self, element: Dict[str, Any], semantic_representation: Dict[str, Any]) -> float:
        """
        Calculate relevance score for a knowledge element based on semantic representation.
        
        Args:
            element: Knowledge element
            semantic_representation: Semantic representation for relevance scoring
            
        Returns:
            Relevance score (0.0-1.0)
        """
        query_parameters = semantic_representation.get("parameters", {})
        query_intent = semantic_representation.get("intent", "")
        
        relevance_score = self._calculate_element_relevance(element, query_parameters, query_intent)
        return relevance_score
    
    def _calculate_importance(self, element: Dict[str, Any]) -> float:
        """
        Calculate importance score for a knowledge element.
        
        Args:
            element: Knowledge element
            
        Returns:
            Importance score (0.0-1.0)
        """
        # This method needs to be implemented based on the specific importance criteria
        return 0.5  # Placeholder return, actual implementation needed
    
    def _calculate_priority(self, element: Dict[str, Any]) -> float:
        """
        Calculate priority score for a knowledge element.
        
        Args:
            element: Knowledge element
            
        Returns:
            Priority score (0.0-1.0)
        """
        # This method needs to be implemented based on the specific priority criteria
        return 0.5  # Placeholder return, actual implementation needed
    
    def _categorize_elements(self, elements: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize knowledge elements based on their source domain.
        
        Args:
            elements: List of knowledge elements
            
        Returns:
            Dictionary with categorized elements
        """
        categories = {}
        for element in elements:
            source_domain = element["source_domain"]
            if source_domain not in categories:
                categories[source_domain] = []
            categories[source_domain].append(element)
        return categories
    
    def _calculate_confidence_distribution(self, elements: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate confidence distribution for knowledge elements.
        
        Args:
            elements: List of knowledge elements
            
        Returns:
            Dictionary with confidence distribution
        """
        confidence_distribution = {}
        for element in elements:
            confidence = element.get("confidence", 0.5)
            if confidence not in confidence_distribution:
                confidence_distribution[confidence] = 0
            confidence_distribution[confidence] += 1
        total_elements = len(elements)
        for confidence in confidence_distribution:
            confidence_distribution[confidence] /= total_elements
        return confidence_distribution
    
    def _map_dependencies(self, elements: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Map dependencies between knowledge elements.
        
        Args:
            elements: List of knowledge elements
            
        Returns:
            Dictionary with dependencies
        """
        dependency_map = {}
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
                        for other_id in elem_with_deps["dependencies"]:
                            # Simple check - could be much more sophisticated
                            if other_id != element.get("id") and other_id in formula["description"]:
                                if other_id not in elem_with_deps["dependencies"]:
                                    elem_with_deps["dependencies"].append(other_id)
            
            # Check if reference values depend on other elements
            if "reference_values" in element:
                for ref_key, ref_value in element.get("reference_values", {}).items():
                    if isinstance(ref_value, dict) and "description" in ref_value:
                        for other_id in elem_with_deps["dependencies"]:
                            if other_id != element.get("id") and other_id in ref_value["description"]:
                                if other_id not in elem_with_deps["dependencies"]:
                                    elem_with_deps["dependencies"].append(other_id)
            
            dependency_map[element["id"]] = elem_with_deps["dependencies"]
        
        return dependency_map 