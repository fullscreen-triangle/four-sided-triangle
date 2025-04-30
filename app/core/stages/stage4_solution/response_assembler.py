"""
Response Assembler

This module contains the ResponseAssembler class, which is responsible for
assembling the final response based on structured and prioritized information.
"""

import logging
from typing import Dict, Any, List, Optional, Union

class ResponseAssembler:
    """
    Assembles the final response based on structured content and prioritized information.
    
    This class combines the outputs from earlier stages to construct a coherent,
    well-structured response that presents information in an optimal way for
    cognitive processing.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Response Assembler.
        
        Args:
            config: Configuration dictionary for assembly parameters
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Assembly parameters
        self.max_response_length = self.config.get("max_response_length", 4000)
        self.include_metadata = self.config.get("include_metadata", False)
        self.formatting_style = self.config.get("formatting_style", "balanced")
        self.enable_progressive_disclosure = self.config.get("enable_progressive_disclosure", True)
        
        self.logger.info("Response Assembler initialized")
    
    async def assemble(self, 
                      structured_content: Dict[str, Any],
                      prioritized_info: Dict[str, Any],
                      optimized_info: Dict[str, Any],
                      original_query: Dict[str, Any],
                      context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assemble the final response from the structured content and prioritized information.
        
        Args:
            structured_content: Content with optimal structure from ContentStructurer
            prioritized_info: Information prioritized by relevance from RelevancePrioritizer
            optimized_info: Information optimized for cognitive processing
            original_query: The original user query with metadata
            context: Context data from the orchestrator
            
        Returns:
            The assembled response with metadata
        """
        self.logger.info("Starting response assembly")
        
        # Extract query metadata
        query_intent = original_query.get("intent", {})
        
        # Step 1: Select the response format based on query intent and content
        response_format = self._select_response_format(query_intent, structured_content)
        self.logger.info(f"Selected response format: {response_format}")
        
        # Step 2: Prepare content sections based on structure
        content_sections = self._prepare_content_sections(
            structured_content, 
            prioritized_info, 
            optimized_info
        )
        
        # Step 3: Apply progressive disclosure if enabled
        if self.enable_progressive_disclosure:
            content_sections = self._apply_progressive_disclosure(content_sections, query_intent)
        
        # Step 4: Format the content according to selected style
        formatted_content = self._format_content(content_sections, response_format)
        
        # Step 5: Trim to max length if needed
        final_content = self._trim_to_length(formatted_content, self.max_response_length)
        
        # Step 6: Add metadata if configured
        response = {
            "content": final_content,
            "format": response_format,
            "structure": structured_content.get("structure_type", "hierarchical"),
        }
        
        if self.include_metadata:
            response["metadata"] = self._generate_metadata(
                structured_content, 
                prioritized_info, 
                optimized_info
            )
        
        self.logger.info("Response assembly completed")
        return response
    
    def _select_response_format(self, query_intent: Dict[str, Any], 
                              structured_content: Dict[str, Any]) -> str:
        """
        Select the appropriate response format based on query intent and content structure.
        
        Args:
            query_intent: Intent information from the query
            structured_content: The structured content
            
        Returns:
            Selected response format
        """
        # Extract intent characteristics
        intent_type = query_intent.get("type", "informational")
        detail_level = query_intent.get("detail_level", "medium")
        format_preference = query_intent.get("format_preference", None)
        
        # Extract content structure
        structure_type = structured_content.get("structure_type", "hierarchical")
        content_breadth = len(structured_content.get("sections", []))
        
        # If user specified a format, prioritize that
        if format_preference in ["narrative", "bullet_points", "q_and_a", "step_by_step", "summary"]:
            return format_preference
        
        # Otherwise, infer the best format based on content and intent
        if intent_type == "procedural":
            return "step_by_step"
        elif intent_type == "comparative":
            return "comparison_table" if content_breadth <= 5 else "bullet_points"
        elif intent_type == "explanatory" and detail_level == "high":
            return "narrative"
        elif intent_type == "informational" and detail_level == "low":
            return "summary"
        elif structure_type == "question_answer":
            return "q_and_a"
        elif content_breadth > 7 or detail_level == "low":
            return "bullet_points"
        else:
            return "narrative"  # Default format
    
    def _prepare_content_sections(self, structured_content: Dict[str, Any],
                                prioritized_info: Dict[str, Any],
                                optimized_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Prepare content sections based on structure and priority.
        
        Args:
            structured_content: Content with structure
            prioritized_info: Prioritized information
            optimized_info: Optimized information
            
        Returns:
            List of prepared content sections
        """
        # Get the hierarchical structure
        sections = structured_content.get("sections", [])
        
        # Get prioritized elements
        prioritized_elements = prioritized_info.get("elements", [])
        element_groups = prioritized_info.get("element_groups", [])
        
        # Create a map of element IDs to elements for quick lookup
        element_map = {
            element.get("id", f"element_{i}"): element 
            for i, element in enumerate(prioritized_elements)
        }
        
        # Create a map of elements to their prominence
        prominence_map = {
            element.get("id", f"element_{i}"): element.get("prominence", "medium") 
            for i, element in enumerate(prioritized_elements)
        }
        
        prepared_sections = []
        
        # Process each section in the structure
        for section in sections:
            section_copy = section.copy()
            
            # Get element IDs assigned to this section
            element_ids = section.get("element_ids", [])
            
            # Collect elements for this section
            section_elements = []
            for element_id in element_ids:
                if element_id in element_map:
                    section_elements.append(element_map[element_id])
            
            # Sort section elements by prominence and priority
            section_elements.sort(
                key=lambda e: (
                    {"high": 3, "medium": 2, "low": 1}.get(e.get("prominence", "medium"), 0),
                    e.get("final_priority", 0)
                ),
                reverse=True
            )
            
            # Apply optimization to section elements if available
            if "optimization" in optimized_info:
                section_elements = self._apply_optimization(
                    section_elements,
                    optimized_info.get("optimization", {})
                )
            
            section_copy["elements"] = section_elements
            section_copy["prominence"] = self._calculate_section_prominence(
                section_elements, prominence_map
            )
            
            prepared_sections.append(section_copy)
        
        # Sort sections by overall prominence
        prepared_sections.sort(
            key=lambda s: {"high": 3, "medium": 2, "low": 1}.get(s.get("prominence", "medium"), 0),
            reverse=True
        )
        
        return prepared_sections
    
    def _calculate_section_prominence(self, section_elements: List[Dict[str, Any]],
                                    prominence_map: Dict[str, str]) -> str:
        """
        Calculate overall prominence for a section based on its elements.
        
        Args:
            section_elements: Elements in the section
            prominence_map: Map of element IDs to prominence values
            
        Returns:
            Section prominence level (high, medium, low)
        """
        if not section_elements:
            return "low"
        
        # Count elements by prominence
        prominence_counts = {"high": 0, "medium": 0, "low": 0}
        
        for element in section_elements:
            element_id = element.get("id", "")
            prominence = element.get("prominence", prominence_map.get(element_id, "medium"))
            prominence_counts[prominence] += 1
        
        # Determine section prominence based on element distribution
        if prominence_counts["high"] > 0:
            return "high"
        elif prominence_counts["medium"] > prominence_counts["low"]:
            return "medium"
        else:
            return "low"
    
    def _apply_optimization(self, section_elements: List[Dict[str, Any]],
                          optimization: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply information optimization to section elements.
        
        Args:
            section_elements: Elements in the section
            optimization: Optimization parameters
            
        Returns:
            Optimized section elements
        """
        # Extract optimization parameters
        cognitive_load_threshold = optimization.get("cognitive_load_threshold", 0.7)
        redundancy_threshold = optimization.get("redundancy_threshold", 0.3)
        complexity_adjustment = optimization.get("complexity_adjustment", {})
        
        optimized_elements = []
        seen_concepts = set()
        
        for element in section_elements:
            # Skip highly redundant elements
            keywords = element.get("keywords", [])
            concept_hash = frozenset(keywords)
            
            redundancy = sum(1 for kw in keywords if kw in seen_concepts) / len(keywords) if keywords else 0
            
            if redundancy > redundancy_threshold and element.get("prominence") != "high":
                continue
            
            # Apply complexity adjustments
            element_copy = element.copy()
            complexity = element.get("complexity", 0.5)
            element_type = element.get("type", "")
            
            if element_type in complexity_adjustment:
                complexity_factor = complexity_adjustment[element_type]
                element_copy["adjusted_complexity"] = complexity * complexity_factor
            else:
                element_copy["adjusted_complexity"] = complexity
            
            # Add to optimized elements if doesn't exceed cognitive load threshold
            if element_copy["adjusted_complexity"] <= cognitive_load_threshold or element.get("prominence") == "high":
                optimized_elements.append(element_copy)
                seen_concepts.update(keywords)
        
        return optimized_elements
    
    def _apply_progressive_disclosure(self, content_sections: List[Dict[str, Any]],
                                    query_intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply progressive disclosure to content sections based on user intent.
        
        Args:
            content_sections: Prepared content sections
            query_intent: Intent information from the query
            
        Returns:
            Content sections with progressive disclosure applied
        """
        # Extract intent characteristics
        detail_level = query_intent.get("detail_level", "medium")
        
        # Map detail level to disclosure depth
        if detail_level == "low":
            max_disclosure_depth = 1  # Only high prominence
        elif detail_level == "medium":
            max_disclosure_depth = 2  # High and medium prominence
        else:  # high
            max_disclosure_depth = 3  # All content
        
        # Apply progressive disclosure based on detail level
        for section in content_sections:
            # Set disclosure level for the section itself
            section_prominence = section.get("prominence", "medium")
            if section_prominence == "high":
                section["disclosure_level"] = 1
            elif section_prominence == "medium":
                section["disclosure_level"] = 2
            else:
                section["disclosure_level"] = 3
            
            # Check if section should be included based on disclosure depth
            section["include_in_response"] = section["disclosure_level"] <= max_disclosure_depth
            
            # Apply to elements within the section
            elements = section.get("elements", [])
            for element in elements:
                prominence = element.get("prominence", "medium")
                
                if prominence == "high":
                    element["disclosure_level"] = 1
                elif prominence == "medium":
                    element["disclosure_level"] = 2
                else:
                    element["disclosure_level"] = 3
                
                element["include_in_response"] = element["disclosure_level"] <= max_disclosure_depth
            
            # Filter elements to include only those within disclosure depth
            section["elements"] = [
                e for e in elements if e.get("include_in_response", True)
            ]
        
        # Filter sections to include only those within disclosure depth
        disclosed_sections = [
            s for s in content_sections if s.get("include_in_response", True) and s.get("elements", [])
        ]
        
        return disclosed_sections
    
    def _format_content(self, content_sections: List[Dict[str, Any]], 
                      response_format: str) -> str:
        """
        Format content according to selected response format.
        
        Args:
            content_sections: Prepared content sections
            response_format: Selected format for the response
            
        Returns:
            Formatted content as a string
        """
        # Handle empty content
        if not content_sections:
            return "No relevant information found."
        
        formatted_result = ""
        
        # Apply the selected format
        if response_format == "narrative":
            formatted_result = self._format_as_narrative(content_sections)
        elif response_format == "bullet_points":
            formatted_result = self._format_as_bullet_points(content_sections)
        elif response_format == "step_by_step":
            formatted_result = self._format_as_steps(content_sections)
        elif response_format == "q_and_a":
            formatted_result = self._format_as_q_and_a(content_sections)
        elif response_format == "comparison_table":
            formatted_result = self._format_as_comparison(content_sections)
        elif response_format == "summary":
            formatted_result = self._format_as_summary(content_sections)
        else:
            # Default to narrative if format not recognized
            formatted_result = self._format_as_narrative(content_sections)
        
        return formatted_result
    
    def _format_as_narrative(self, content_sections: List[Dict[str, Any]]) -> str:
        """Format content as a narrative text flow."""
        result = []
        
        for section in content_sections:
            # Add section title as heading
            result.append(f"# {section.get('title', 'Section')}\n")
            
            # Add section description if available
            if section.get('description'):
                result.append(f"{section['description']}\n")
            
            # Add subsections if any
            subsections = section.get('subsections', [])
            for subsection in subsections:
                result.append(f"## {subsection.get('title', 'Subsection')}\n")
                
                if subsection.get('description'):
                    result.append(f"{subsection['description']}\n")
            
            # Add elements as paragraphs
            elements = section.get('elements', [])
            for element in elements:
                content = element.get('content', '')
                if content:
                    result.append(f"{content}\n")
            
            # Add a separator between sections
            result.append("\n")
        
        return "\n".join(result)
    
    def _format_as_bullet_points(self, content_sections: List[Dict[str, Any]]) -> str:
        """Format content as bullet points."""
        result = []
        
        for section in content_sections:
            # Add section title as heading
            result.append(f"# {section.get('title', 'Section')}\n")
            
            # Add section description if available
            if section.get('description'):
                result.append(f"{section['description']}\n")
            
            # Add subsections if any
            subsections = section.get('subsections', [])
            for subsection in subsections:
                result.append(f"## {subsection.get('title', 'Subsection')}\n")
                
                if subsection.get('description'):
                    result.append(f"{subsection['description']}\n")
            
            # Add elements as bullet points
            elements = section.get('elements', [])
            for element in elements:
                content = element.get('content', '')
                if content:
                    result.append(f"* {content}")
            
            # Add a separator between sections
            result.append("\n")
        
        return "\n".join(result)
    
    def _format_as_steps(self, content_sections: List[Dict[str, Any]]) -> str:
        """Format content as step-by-step instructions."""
        result = []
        step_counter = 1
        
        for section in content_sections:
            # Add section title as heading
            result.append(f"# {section.get('title', 'Section')}\n")
            
            # Add section description if available
            if section.get('description'):
                result.append(f"{section['description']}\n")
            
            # Add elements as numbered steps
            elements = section.get('elements', [])
            for element in elements:
                content = element.get('content', '')
                if content:
                    result.append(f"{step_counter}. {content}")
                    step_counter += 1
            
            # Add a separator between sections
            result.append("\n")
        
        return "\n".join(result)
    
    def _format_as_q_and_a(self, content_sections: List[Dict[str, Any]]) -> str:
        """Format content as questions and answers."""
        result = []
        
        for section in content_sections:
            # Add section title as heading
            result.append(f"# {section.get('title', 'Section')}\n")
            
            # Add elements as Q&A
            elements = section.get('elements', [])
            for element in elements:
                question = element.get('question', f"About {section.get('title', 'this topic')}")
                content = element.get('content', '')
                if content:
                    result.append(f"**Q: {question}**\n\nA: {content}\n")
            
            # Add a separator between sections
            result.append("\n")
        
        return "\n".join(result)
    
    def _format_as_comparison(self, content_sections: List[Dict[str, Any]]) -> str:
        """Format content as a comparison table."""
        result = []
        
        # Extract categories from sections
        categories = []
        for section in content_sections:
            categories.append(section.get('title', 'Category'))
        
        # Create table header
        result.append("| Aspect | " + " | ".join(categories) + " |")
        result.append("| ------ | " + " | ".join(["------" for _ in categories]) + " |")
        
        # Find all aspect types across all sections
        aspects = set()
        for section in content_sections:
            for element in section.get('elements', []):
                aspect = element.get('aspect', '')
                if aspect:
                    aspects.add(aspect)
        
        # Create table rows
        for aspect in sorted(aspects):
            row = [aspect]
            
            for section in content_sections:
                # Find element with this aspect
                aspect_content = ""
                for element in section.get('elements', []):
                    if element.get('aspect') == aspect:
                        aspect_content = element.get('content', '')
                        break
                
                row.append(aspect_content)
            
            result.append("| " + " | ".join(row) + " |")
        
        return "\n".join(result)
    
    def _format_as_summary(self, content_sections: List[Dict[str, Any]]) -> str:
        """Format content as a brief summary."""
        result = []
        
        # Add a title
        result.append("# Summary\n")
        
        # Extract high prominence elements from all sections
        high_prominence_elements = []
        for section in content_sections:
            for element in section.get('elements', []):
                if element.get('prominence') == 'high':
                    high_prominence_elements.append(element)
        
        # Add high prominence elements as bullet points
        for element in high_prominence_elements:
            content = element.get('content', '')
            if content:
                result.append(f"* {content}")
        
        # If we have few high prominence elements, add some medium ones
        if len(high_prominence_elements) < 3:
            medium_count = 0
            for section in content_sections:
                for element in section.get('elements', []):
                    if element.get('prominence') == 'medium' and medium_count < 3:
                        content = element.get('content', '')
                        if content:
                            result.append(f"* {content}")
                            medium_count += 1
        
        return "\n".join(result)
    
    def _trim_to_length(self, content: str, max_length: int) -> str:
        """
        Trim content to maximum length without cutting in the middle of a section.
        
        Args:
            content: Formatted content
            max_length: Maximum allowed length
            
        Returns:
            Trimmed content
        """
        if len(content) <= max_length:
            return content
        
        # Split into sections
        sections = content.split("\n\n")
        
        # Add sections until we reach the limit
        result = []
        current_length = 0
        
        for section in sections:
            section_length = len(section) + 2  # +2 for the newlines
            
            if current_length + section_length > max_length:
                # Don't add this section if it would exceed the limit
                break
            
            result.append(section)
            current_length += section_length
        
        # Add a note that content was trimmed
        if len(result) < len(sections):
            result.append("\n\n*Note: Some content was omitted due to length limitations.*")
        
        return "\n\n".join(result)
    
    def _generate_metadata(self, structured_content: Dict[str, Any],
                         prioritized_info: Dict[str, Any],
                         optimized_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate metadata about the response for debugging and analysis.
        
        Args:
            structured_content: The structured content
            prioritized_info: Prioritized information
            optimized_info: Optimized information
            
        Returns:
            Response metadata
        """
        # Count elements by prominence
        elements = prioritized_info.get("elements", [])
        prominence_counts = {"high": 0, "medium": 0, "low": 0}
        
        for element in elements:
            prominence = element.get("prominence", "medium")
            prominence_counts[prominence] += 1
        
        # Count sections and subsections
        sections = structured_content.get("sections", [])
        total_subsections = sum(len(section.get("subsections", [])) for section in sections)
        
        # Generate metadata
        metadata = {
            "element_counts": {
                "total": len(elements),
                "by_prominence": prominence_counts
            },
            "structure_metrics": {
                "sections": len(sections),
                "subsections": total_subsections,
                "structure_type": structured_content.get("structure_type", "hierarchical"),
                "cognitive_load": optimized_info.get("cognitive_load_estimate", 0.5)
            },
            "response_metrics": {
                "format": self.formatting_style,
                "progressive_disclosure": self.enable_progressive_disclosure,
                "detail_level": "high" if prominence_counts["low"] > 0 else 
                               "medium" if prominence_counts["medium"] > 0 else "low"
            }
        }
        
        return metadata 