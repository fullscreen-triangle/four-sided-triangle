"""
Response Combiner

This module combines optimized components from multiple response candidates 
into an integrated response that maximizes both quality and diversity.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional, Set, Tuple

class ResponseCombiner:
    """
    Combines optimized components into an integrated response.
    
    This class takes optimized elements from multiple response candidates and
    combines them into a coherent, integrated response that preserves the
    structure while maximizing information value.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Response Combiner.
        
        Args:
            config: Configuration dictionary for the combiner
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Configure combiner parameters
        self.max_elements = self.config.get("max_elements", 50)
        self.max_sections = self.config.get("max_sections", 10)
        self.preserve_section_order = self.config.get("preserve_section_order", True)
        self.element_overlap_threshold = self.config.get("element_overlap_threshold", 0.8)
        
        self.logger.info("Response Combiner initialized")
    
    def combine(self, optimized_components: Dict[str, Any],
              primary_response: Dict[str, Any],
              evaluation_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine optimized components into an integrated response.
        
        Args:
            optimized_components: Dictionary of optimized components from QualityDiversityOptimizer
            primary_response: The primary response candidate
            evaluation_metrics: Evaluation metrics from response scoring
            
        Returns:
            Integrated response combining the best elements
        """
        self.logger.info("Combining optimized components into integrated response")
        
        # Extract optimized elements and component weights
        optimized_elements = optimized_components.get("optimized_elements", [])
        component_weights = optimized_components.get("component_weights", {})
        pareto_optimal_indices = optimized_components.get("pareto_optimal_indices", [0])
        
        # Start with a copy of the primary response
        combined_response = self._create_base_response(primary_response)
        
        # Get the content structure from primary response
        primary_content = primary_response.get("content", {})
        primary_sections = primary_content.get("sections", [])
        
        # Limit the number of elements for efficiency
        if len(optimized_elements) > self.max_elements:
            self.logger.info(f"Limiting optimized elements from {len(optimized_elements)} to {self.max_elements}")
            optimized_elements = optimized_elements[:self.max_elements]
        
        # Restructure elements into sections
        combined_sections = self._restructure_sections(
            optimized_elements, 
            primary_sections, 
            pareto_optimal_indices
        )
        
        # Build the combined content
        combined_content = {
            "elements": optimized_elements,
            "sections": combined_sections
        }
        
        # Add content to the combined response
        combined_response["content"] = combined_content
        
        # Calculate primary contribution ratio
        primary_elements = sum(1 for e in optimized_elements if e.get("source_response", 0) == 0)
        if optimized_elements:
            primary_contribution_ratio = primary_elements / len(optimized_elements)
        else:
            primary_contribution_ratio = 1.0
        
        # Add metadata about the combination
        combined_response["primary_contribution_ratio"] = primary_contribution_ratio
        combined_response["ensemble_composition"] = {
            "component_weights": component_weights,
            "component_counts": self._count_components(optimized_elements)
        }
        
        # Add overall metrics
        quality_score = evaluation_metrics.get("overall_score", 0.8)
        combined_response["combined_quality_score"] = quality_score
        
        self.logger.info(f"Response combination completed with {len(optimized_elements)} elements in {len(combined_sections)} sections")
        return combined_response
    
    def _create_base_response(self, primary_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a base response structure from the primary response.
        
        Args:
            primary_response: The primary response candidate
            
        Returns:
            Base response with metadata but without content
        """
        # Copy metadata from primary response, but not content
        base_response = {}
        
        # Copy top-level fields except 'content'
        for key, value in primary_response.items():
            if key != "content":
                base_response[key] = value
        
        # Add combination metadata
        base_response["is_combined"] = True
        base_response["combination_timestamp"] = self._get_timestamp()
        
        return base_response
    
    def _restructure_sections(self, optimized_elements: List[Dict[str, Any]],
                           primary_sections: List[Dict[str, Any]],
                           pareto_indices: List[int]) -> List[Dict[str, Any]]:
        """
        Restructure elements into coherent sections.
        
        Args:
            optimized_elements: List of optimized elements
            primary_sections: Sections from the primary response
            pareto_indices: Indices of Pareto-optimal responses
            
        Returns:
            List of restructured sections
        """
        # If no primary sections, create a single section with all elements
        if not primary_sections:
            element_ids = [elem.get("id") for elem in optimized_elements if elem.get("id")]
            return [{
                "title": "Combined Information",
                "element_ids": element_ids
            }]
        
        # Map element IDs to their positions in the optimized elements list
        element_map = {elem.get("id"): i for i, elem in enumerate(optimized_elements) if elem.get("id")}
        
        # Start with the primary sections structure
        restructured_sections = []
        
        # Process each primary section
        for section in primary_sections:
            new_section = dict(section)
            original_element_ids = section.get("element_ids", [])
            
            # Filter element IDs to only include those in the optimized elements
            new_element_ids = [eid for eid in original_element_ids if eid in element_map]
            
            # Add the section if it has elements
            if new_element_ids:
                new_section["element_ids"] = new_element_ids
                restructured_sections.append(new_section)
        
        # Find elements not yet assigned to any section
        assigned_element_ids = set()
        for section in restructured_sections:
            assigned_element_ids.update(section.get("element_ids", []))
        
        unassigned_elements = [
            elem for elem in optimized_elements 
            if elem.get("id") and elem.get("id") not in assigned_element_ids
        ]
        
        # If there are unassigned elements, create new sections or add to existing ones
        if unassigned_elements:
            # Group unassigned elements by source response
            source_groups = {}
            for elem in unassigned_elements:
                source = elem.get("source_response", 0)
                if source not in source_groups:
                    source_groups[source] = []
                source_groups[source].append(elem)
            
            # For each source group, create a new section or add to most relevant existing section
            for source, elements in source_groups.items():
                if source == 0 or source not in pareto_indices:
                    # For primary or non-optimal sources, add to existing sections based on relevance
                    self._add_to_existing_sections(elements, restructured_sections)
                else:
                    # For Pareto-optimal sources, create new sections
                    self._create_new_section(elements, restructured_sections, f"Additional Information {source}")
        
        # Limit the number of sections
        if len(restructured_sections) > self.max_sections:
            # Sort sections by number of elements (descending)
            restructured_sections.sort(
                key=lambda s: len(s.get("element_ids", [])), 
                reverse=True
            )
            restructured_sections = restructured_sections[:self.max_sections]
        
        # Ensure all sections have unique titles
        self._ensure_unique_section_titles(restructured_sections)
        
        return restructured_sections
    
    def _add_to_existing_sections(self, elements: List[Dict[str, Any]], 
                               sections: List[Dict[str, Any]]) -> None:
        """
        Add elements to existing sections based on relevance.
        
        Args:
            elements: List of elements to add
            sections: List of existing sections
            
        Modifies sections in place.
        """
        # Sort sections by number of elements (ascending) to balance distribution
        sections_by_size = sorted(
            [(i, s) for i, s in enumerate(sections)], 
            key=lambda x: len(x[1].get("element_ids", []))
        )
        
        # Distribute elements among sections
        for elem in elements:
            elem_id = elem.get("id")
            if not elem_id:
                continue
                
            # Find most appropriate section based on element type or content
            best_section_idx = None
            best_match_score = -1
            
            for idx, section in sections_by_size:
                match_score = self._calculate_section_match(elem, section, sections[idx])
                if match_score > best_match_score:
                    best_match_score = match_score
                    best_section_idx = idx
            
            # Add to best matching section or the smallest if no good match
            if best_section_idx is not None:
                sections[best_section_idx]["element_ids"].append(elem_id)
            elif sections:
                # Add to smallest section if no good match
                smallest_idx = sections_by_size[0][0]
                sections[smallest_idx]["element_ids"].append(elem_id)
    
    def _create_new_section(self, elements: List[Dict[str, Any]], 
                         sections: List[Dict[str, Any]],
                         title_prefix: str) -> None:
        """
        Create a new section for a group of elements.
        
        Args:
            elements: List of elements for the new section
            sections: List of existing sections
            title_prefix: Prefix for the section title
            
        Modifies sections in place.
        """
        if not elements:
            return
            
        # Extract element IDs
        element_ids = [elem.get("id") for elem in elements if elem.get("id")]
        
        if not element_ids:
            return
            
        # Try to determine a more specific title based on element types or content
        element_types = set(elem.get("type", "") for elem in elements if elem.get("type"))
        
        section_title = title_prefix
        if len(element_types) == 1:
            element_type = next(iter(element_types))
            section_title = f"{title_prefix} - {element_type.capitalize()}"
        
        # Create the new section
        new_section = {
            "title": section_title,
            "element_ids": element_ids
        }
        
        # Add the new section
        sections.append(new_section)
    
    def _calculate_section_match(self, element: Dict[str, Any], 
                              section_info: Tuple[int, Dict[str, Any]],
                              section: Dict[str, Any]) -> float:
        """
        Calculate how well an element matches a section.
        
        Args:
            element: Element to match
            section_info: Tuple of (index, section) from sections_by_size
            section: The actual section from the sections list
            
        Returns:
            Match score between 0 and 1
        """
        section_size = len(section.get("element_ids", []))
        
        # Base score inversely proportional to section size
        base_score = 1.0 / (1 + section_size)
        
        # Get element type and title keywords
        element_type = element.get("type", "").lower()
        element_content = element.get("content", "").lower()
        section_title = section.get("title", "").lower()
        
        # Match based on element type appearing in section title
        type_match = element_type in section_title
        
        # Match based on content keywords in section title
        content_match = False
        if element_content:
            # Extract key terms (first few words)
            words = element_content.split()[:5]
            content_match = any(word in section_title for word in words if len(word) > 3)
        
        # Increase score based on matches
        score = base_score
        if type_match:
            score += 0.4
        if content_match:
            score += 0.3
        
        return score
    
    def _ensure_unique_section_titles(self, sections: List[Dict[str, Any]]) -> None:
        """
        Ensure all section titles are unique.
        
        Args:
            sections: List of sections
            
        Modifies sections in place.
        """
        seen_titles = set()
        
        for section in sections:
            original_title = section.get("title", "")
            title = original_title
            suffix = 1
            
            # Add numbering until title is unique
            while title in seen_titles:
                title = f"{original_title} ({suffix})"
                suffix += 1
            
            section["title"] = title
            seen_titles.add(title)
    
    def _count_components(self, elements: List[Dict[str, Any]]) -> Dict[int, int]:
        """
        Count elements from each source response.
        
        Args:
            elements: List of optimized elements
            
        Returns:
            Dictionary mapping source response indices to element counts
        """
        counts = {}
        
        for elem in elements:
            source = elem.get("source_response", 0)
            counts[source] = counts.get(source, 0) + 1
        
        return counts
    
    def _get_timestamp(self) -> str:
        """
        Get current timestamp as string.
        
        Returns:
            Timestamp string
        """
        from datetime import datetime
        return datetime.now().isoformat() 