"""
Content Structurer

This module contains the ContentStructurer class, which organizes information
into a structure that optimizes cognitive processing and comprehension.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
import re

class ContentStructurer:
    """
    Structures content for optimal cognitive processing and comprehension.
    
    This class organizes information into a coherent structure that:
    - Groups related concepts
    - Applies cognitive scaffolding
    - Creates logical progression
    - Balances depth and breadth
    - Optimizes for working memory constraints
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Content Structurer.
        
        Args:
            config: Configuration dictionary for structuring parameters
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Load configuration with defaults
        self.max_hierarchy_depth = self.config.get("max_hierarchy_depth", 3)
        self.chunking_threshold = self.config.get("chunking_threshold", 5)
        self.progression_type = self.config.get("progression_type", "logical")
        self.include_summaries = self.config.get("include_summaries", True)
        self.memory_constraint_factor = self.config.get("memory_constraint_factor", 7)  # Miller's Law (~7±2)
        self.enable_advanced_grouping = self.config.get("enable_advanced_grouping", True)
        
        self.logger.info("Content Structurer initialized")
    
    async def structure(self, 
                     optimized_info: Dict[str, Any], 
                     user_query: Dict[str, Any],
                     context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Structure information for optimal comprehension and cognitive processing.
        
        Args:
            optimized_info: Optimized information content
            user_query: The user's query with enriched metadata
            context: Context information and state
            
        Returns:
            Structured content with metadata
        """
        self.logger.info("Starting content structuring")
        
        # Extract information elements
        elements = optimized_info.get("elements", [])
        if not elements:
            self.logger.warning("No elements to structure")
            return {
                "structure": {
                    "type": "sequential",
                    "sections": []
                },
                "elements": [],
                "structuring": {
                    "progression_type": self.progression_type,
                    "max_hierarchy_depth": self.max_hierarchy_depth
                },
                "metrics": {
                    "element_count": 0,
                    "section_count": 0,
                    "average_section_depth": 0,
                    "coherence_score": 0
                }
            }
        
        # Step 1: Identify concept groups and relationships
        concept_groups = self._identify_concept_groups(elements, user_query)
        
        # Step 2: Create preliminary structure
        preliminary_structure = self._create_preliminary_structure(concept_groups, user_query)
        
        # Step 3: Apply cognitive scaffolding
        scaffolded_structure = self._apply_cognitive_scaffolding(preliminary_structure, user_query)
        
        # Step 4: Optimize for working memory
        memory_optimized = self._optimize_for_working_memory(scaffolded_structure)
        
        # Step 5: Create logical progression
        final_structure = self._create_logical_progression(memory_optimized, user_query)
        
        # Calculate structure metrics
        structure_metrics = self._calculate_structure_metrics(final_structure, elements)
        
        structured_result = {
            "structure": final_structure,
            "elements": elements,
            "structuring": {
                "progression_type": self.progression_type,
                "max_hierarchy_depth": self.max_hierarchy_depth,
                "chunking_threshold": self.chunking_threshold
            },
            "metrics": structure_metrics
        }
        
        self.logger.info(f"Content structuring complete. Sections: {structure_metrics['section_count']}")
        return structured_result
    
    def _identify_concept_groups(self, 
                              elements: List[Dict[str, Any]], 
                              user_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify concept groups and relationships among information elements.
        
        Args:
            elements: Optimized information elements
            user_query: The user's query with enriched metadata
            
        Returns:
            List of concept groups with their elements
        """
        self.logger.debug("Identifying concept groups")
        
        # Extract topics/concepts from each element
        for element in elements:
            if "topics" not in element:
                element["topics"] = self._extract_topics(element)
        
        # Group elements by topics
        topic_groups = {}
        for element in elements:
            element_topics = element.get("topics", [])
            
            for topic in element_topics:
                if topic not in topic_groups:
                    topic_groups[topic] = []
                topic_groups[topic].append(element)
        
        # Create concept groups with primary and secondary elements
        concept_groups = []
        processed_elements = set()
        
        # Sort topics by the number of elements they contain (descending)
        sorted_topics = sorted(topic_groups.keys(), 
                             key=lambda t: len(topic_groups[t]), 
                             reverse=True)
        
        for topic in sorted_topics:
            # Skip small topic groups if they're subsets of larger groups
            if self._is_subset_of_larger_group(topic, topic_groups, sorted_topics[:sorted_topics.index(topic)]):
                continue
            
            # Get elements for this topic
            group_elements = topic_groups[topic]
            
            # Identify primary elements that have this topic as their main topic
            primary_elements = []
            secondary_elements = []
            
            for element in group_elements:
                element_topics = element.get("topics", [])
                if element_topics and element_topics[0] == topic:
                    # This is a primary element for this topic
                    primary_elements.append(element)
                else:
                    # This is a secondary element
                    secondary_elements.append(element)
            
            # Create the concept group
            concept_group = {
                "topic": topic,
                "primary_elements": primary_elements,
                "secondary_elements": secondary_elements,
                "strength": len(group_elements)
            }
            
            concept_groups.append(concept_group)
            
            # Mark elements as processed
            for element in group_elements:
                processed_elements.add(id(element))
        
        # Add orphaned elements (not in any concept group)
        orphaned_elements = [e for e in elements if id(e) not in processed_elements]
        if orphaned_elements:
            concept_groups.append({
                "topic": "additional_information",
                "primary_elements": orphaned_elements,
                "secondary_elements": [],
                "strength": len(orphaned_elements)
            })
        
        return concept_groups
    
    def _is_subset_of_larger_group(self, 
                                topic: str, 
                                topic_groups: Dict[str, List[Dict[str, Any]]], 
                                larger_topics: List[str]) -> bool:
        """
        Check if a topic group is a subset of a larger group.
        
        Args:
            topic: The topic to check
            topic_groups: Mapping of topics to their elements
            larger_topics: List of topics that are larger than this one
            
        Returns:
            True if this topic group is a subset of a larger group
        """
        current_elements = set(id(e) for e in topic_groups[topic])
        
        for larger_topic in larger_topics:
            larger_elements = set(id(e) for e in topic_groups[larger_topic])
            
            # If 80% or more of the current elements are in the larger group,
            # consider it a subset
            if len(current_elements) > 0:
                overlap_ratio = len(current_elements.intersection(larger_elements)) / len(current_elements)
                if overlap_ratio >= 0.8:
                    return True
        
        return False
    
    def _extract_topics(self, element: Dict[str, Any]) -> List[str]:
        """
        Extract topics/concepts from an element.
        
        Args:
            element: Information element
            
        Returns:
            List of topics/concepts
        """
        topics = []
        
        # Extract from element type or category
        if "type" in element:
            topics.append(element["type"].lower())
        
        if "category" in element:
            topics.append(element["category"].lower())
        
        # Extract from tags if available
        if "tags" in element and isinstance(element["tags"], list):
            topics.extend([tag.lower() for tag in element["tags"]])
        
        # Extract from keywords if available
        if "keywords" in element and isinstance(element["keywords"], list):
            topics.extend([keyword.lower() for keyword in element["keywords"]])
        
        # Extract from content using simple approach
        if "content" in element and isinstance(element["content"], str):
            # In a real implementation, this would use NLP/entity extraction
            content = element["content"]
            
            # Simple extraction of capitalized phrases as potential topics
            potential_topics = re.findall(r'\b[A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)*\b', content)
            topics.extend([topic.lower() for topic in potential_topics])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_topics = []
        for topic in topics:
            if topic not in seen:
                seen.add(topic)
                unique_topics.append(topic)
        
        return unique_topics
    
    def _create_preliminary_structure(self, 
                                   concept_groups: List[Dict[str, Any]], 
                                   user_query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a preliminary content structure based on concept groups.
        
        Args:
            concept_groups: Concept groups with associated elements
            user_query: The user's query with enriched metadata
            
        Returns:
            Preliminary structure
        """
        self.logger.debug("Creating preliminary structure")
        
        # Determine appropriate structure type based on query
        structure_type = self._determine_structure_type(user_query)
        
        # Create sections based on concept groups
        sections = []
        for group in concept_groups:
            # Skip empty groups
            if not group["primary_elements"] and not group["secondary_elements"]:
                continue
            
            section = {
                "title": self._generate_section_title(group["topic"]),
                "type": "section",
                "elements": group["primary_elements"] + group["secondary_elements"],
                "importance": group["strength"],
                "subsections": []
            }
            
            # Create subsections if appropriate
            if len(section["elements"]) > self.chunking_threshold and self.enable_advanced_grouping:
                subsections = self._create_subsections(section["elements"])
                if subsections:
                    section["subsections"] = subsections
                    # Keep main elements for intro/summary, move others to subsections
                    if len(section["elements"]) > 2:
                        # Keep first two elements for introduction
                        section["elements"] = section["elements"][:2]
            
            sections.append(section)
        
        # Sort sections by importance
        sections.sort(key=lambda s: s["importance"], reverse=True)
        
        # Create the structure
        structure = {
            "type": structure_type,
            "sections": sections
        }
        
        return structure
    
    def _determine_structure_type(self, user_query: Dict[str, Any]) -> str:
        """
        Determine the appropriate structure type based on the query.
        
        Args:
            user_query: The user's query with enriched metadata
            
        Returns:
            Structure type (hierarchical, sequential, etc.)
        """
        query_text = user_query.get("text", "").lower()
        intent = user_query.get("intent", "").lower()
        
        # Look for specific structure indicators in the query
        if any(term in query_text for term in ["compare", "versus", "vs", "difference"]):
            return "comparative"
        
        if any(term in query_text for term in ["step", "how to", "process", "procedure"]):
            return "sequential"
        
        if any(term in query_text for term in ["explain", "why", "reason"]):
            return "explanatory"
        
        if any(term in intent for term in ["exploration", "discovery"]):
            return "hierarchical"
        
        # Default to the configured progression type
        if self.progression_type in ["logical", "chronological", "complexity_based"]:
            return "sequential"
        
        return "hierarchical"
    
    def _generate_section_title(self, topic: str) -> str:
        """
        Generate a section title from a topic.
        
        Args:
            topic: Topic name
            
        Returns:
            Section title
        """
        # Convert underscores to spaces
        title = topic.replace("_", " ")
        
        # Capitalize words
        title = " ".join(word.capitalize() for word in title.split())
        
        return title
    
    def _create_subsections(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create subsections from a group of elements.
        
        Args:
            elements: Elements to organize into subsections
            
        Returns:
            List of subsections
        """
        if len(elements) <= self.chunking_threshold:
            return []
        
        # Group elements by subtopics
        element_topics = {}
        for element in elements:
            topics = element.get("topics", [])
            if topics:
                # Use the second topic as subtopic if available
                subtopic = topics[1] if len(topics) > 1 else topics[0]
                if subtopic not in element_topics:
                    element_topics[subtopic] = []
                element_topics[subtopic].append(element)
        
        # Create subsections based on subtopics
        subsections = []
        for subtopic, subtopic_elements in element_topics.items():
            # Only create subsection if it has multiple elements
            if len(subtopic_elements) >= 2:
                subsection = {
                    "title": self._generate_section_title(subtopic),
                    "type": "subsection",
                    "elements": subtopic_elements,
                    "importance": len(subtopic_elements)
                }
                subsections.append(subsection)
        
        # Sort subsections by importance
        subsections.sort(key=lambda s: s["importance"], reverse=True)
        
        # Limit depth based on configuration
        return subsections[:min(len(subsections), self.memory_constraint_factor)]
    
    def _apply_cognitive_scaffolding(self, 
                                  structure: Dict[str, Any], 
                                  user_query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply cognitive scaffolding to improve comprehension.
        
        Args:
            structure: Preliminary content structure
            user_query: The user's query with enriched metadata
            
        Returns:
            Structure with cognitive scaffolding
        """
        self.logger.debug("Applying cognitive scaffolding")
        
        # Make a deep copy to avoid modifying the original
        result = {
            "type": structure["type"],
            "sections": []
        }
        
        # Process each section
        for section in structure.get("sections", []):
            section_copy = section.copy()
            
            # Add introduction if appropriate
            if self.include_summaries and section_copy.get("elements", []):
                intro_elements = self._create_scaffold_elements("introduction", section_copy)
                if intro_elements:
                    section_copy["introduction"] = intro_elements
            
            # Process subsections
            if "subsections" in section_copy:
                processed_subsections = []
                for subsection in section_copy["subsections"]:
                    subsection_copy = subsection.copy()
                    
                    # Add introduction to subsection if it has enough elements
                    if self.include_summaries and len(subsection.get("elements", [])) >= 3:
                        intro_elements = self._create_scaffold_elements("introduction", subsection)
                        if intro_elements:
                            subsection_copy["introduction"] = intro_elements
                    
                    processed_subsections.append(subsection_copy)
                
                section_copy["subsections"] = processed_subsections
            
            # Add summary if appropriate
            if self.include_summaries and len(section_copy.get("elements", [])) >= 3:
                summary_elements = self._create_scaffold_elements("summary", section_copy)
                if summary_elements:
                    section_copy["summary"] = summary_elements
            
            result["sections"].append(section_copy)
        
        # Add overall introduction and summary if needed
        if self.include_summaries and len(result.get("sections", [])) >= 2:
            intro_elements = self._create_overall_scaffolding("introduction", result)
            if intro_elements:
                result["introduction"] = intro_elements
            
            summary_elements = self._create_overall_scaffolding("summary", result)
            if summary_elements:
                result["summary"] = summary_elements
        
        return result
    
    def _create_scaffold_elements(self, scaffold_type: str, section: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create scaffold elements (introduction or summary) for a section.
        
        Args:
            scaffold_type: Type of scaffold ('introduction' or 'summary')
            section: Section data
            
        Returns:
            List of scaffold elements
        """
        # For a real implementation, this would generate actual content
        # For now, we'll just create placeholders
        
        if scaffold_type == "introduction":
            return [{
                "type": "introduction",
                "role": "cognitive_scaffolding",
                "content": f"Introduction to {section['title']}",
                "generated": True
            }]
        elif scaffold_type == "summary":
            return [{
                "type": "summary",
                "role": "cognitive_scaffolding",
                "content": f"Summary of {section['title']}",
                "generated": True
            }]
        
        return []
    
    def _create_overall_scaffolding(self, scaffold_type: str, structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create overall scaffold elements for the entire response.
        
        Args:
            scaffold_type: Type of scaffold ('introduction' or 'summary')
            structure: Overall content structure
            
        Returns:
            List of scaffold elements
        """
        if scaffold_type == "introduction":
            return [{
                "type": "overall_introduction",
                "role": "cognitive_scaffolding",
                "content": "Overall introduction",
                "generated": True
            }]
        elif scaffold_type == "summary":
            return [{
                "type": "overall_summary",
                "role": "cognitive_scaffolding",
                "content": "Overall summary",
                "generated": True
            }]
        
        return []
    
    def _optimize_for_working_memory(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize structure based on working memory constraints.
        
        Args:
            structure: Content structure with scaffolding
            
        Returns:
            Memory-optimized structure
        """
        self.logger.debug("Optimizing for working memory constraints")
        
        # Make a deep copy to avoid modifying the original
        result = {
            "type": structure["type"]
        }
        
        # Copy introduction and summary if they exist
        if "introduction" in structure:
            result["introduction"] = structure["introduction"]
        
        if "summary" in structure:
            result["summary"] = structure["summary"]
        
        # Apply chunking to sections
        sections = structure.get("sections", [])
        chunked_sections = self._apply_chunking(sections)
        result["sections"] = chunked_sections
        
        return result
    
    def _apply_chunking(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply chunking to sections to optimize for working memory.
        
        Args:
            sections: List of sections
            
        Returns:
            Chunked sections
        """
        # Apply Miller's Law (7±2) to limit cognitive load
        max_top_sections = self.memory_constraint_factor
        
        if len(sections) <= max_top_sections:
            return sections
        
        # Group smaller sections together if there are too many
        result = []
        current_index = 0
        
        # Include the most important sections as-is
        important_sections = sections[:max_top_sections - 1]
        result.extend(important_sections)
        current_index = len(important_sections)
        
        # Combine remaining sections into an "Additional Information" section
        if current_index < len(sections):
            remaining_sections = sections[current_index:]
            combined_section = {
                "title": "Additional Information",
                "type": "section",
                "subsections": remaining_sections,
                "elements": [],
                "importance": sum(s.get("importance", 1) for s in remaining_sections) / len(remaining_sections)
            }
            result.append(combined_section)
        
        return result
    
    def _create_logical_progression(self, 
                                 structure: Dict[str, Any], 
                                 user_query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create logical progression through the content.
        
        Args:
            structure: Memory-optimized structure
            user_query: The user's query with enriched metadata
            
        Returns:
            Structure with logical progression
        """
        self.logger.debug("Creating logical progression")
        
        # Make a deep copy to avoid modifying the original
        result = structure.copy()
        sections = result.get("sections", [])
        
        # Determine progression type based on structure type and query
        progression_type = self._determine_progression_type(structure["type"], user_query)
        
        # Apply the appropriate progression
        if progression_type == "complexity_based":
            sections = self._apply_complexity_progression(sections)
        elif progression_type == "chronological":
            sections = self._apply_chronological_progression(sections)
        elif progression_type == "logical":
            sections = self._apply_logical_dependencies_progression(sections)
        
        result["sections"] = sections
        result["progression"] = progression_type
        
        return result
    
    def _determine_progression_type(self, structure_type: str, user_query: Dict[str, Any]) -> str:
        """
        Determine the appropriate progression type.
        
        Args:
            structure_type: Type of structure
            user_query: The user's query with enriched metadata
            
        Returns:
            Progression type
        """
        # Use configured progression type as default
        progression_type = self.progression_type
        
        # Override based on structure type if appropriate
        if structure_type == "sequential":
            progression_type = "chronological"
        elif structure_type == "explanatory":
            progression_type = "logical"
        elif structure_type == "comparative":
            progression_type = "logical"
        
        # Check query for progression indicators
        query_text = user_query.get("text", "").lower()
        
        if any(term in query_text for term in ["first", "then", "after", "before", "step"]):
            progression_type = "chronological"
        
        if any(term in query_text for term in ["simple", "complex", "basics", "advanced"]):
            progression_type = "complexity_based"
        
        if any(term in query_text for term in ["why", "because", "reason", "therefore"]):
            progression_type = "logical"
        
        return progression_type
    
    def _apply_complexity_progression(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply complexity-based progression to sections.
        
        Args:
            sections: List of sections
            
        Returns:
            Sections ordered by complexity
        """
        # Calculate complexity for each section
        for section in sections:
            complexity = 0.5  # Default medium complexity
            
            # Calculate based on elements
            elements = section.get("elements", [])
            if elements:
                # Use information entropy or cognitive load if available
                entropies = [e.get("information_entropy", 0.5) for e in elements]
                complexity = sum(entropies) / len(entropies)
            
            section["complexity"] = complexity
        
        # Sort by complexity (simple to complex)
        sorted_sections = sorted(sections, key=lambda s: s.get("complexity", 0.5))
        
        return sorted_sections
    
    def _apply_chronological_progression(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply chronological progression to sections.
        
        Args:
            sections: List of sections
            
        Returns:
            Sections ordered chronologically
        """
        # In a real implementation, this would look for temporal indicators
        # For now, we'll assume the existing order is chronological
        # with some simple heuristics
        
        # Look for temporal indicators in section titles
        temporal_sections = []
        non_temporal_sections = []
        
        temporal_indicators = [
            "first", "second", "third", "fourth", "fifth",
            "start", "begin", "introduction", "background",
            "then", "next", "after", "before", "during",
            "conclusion", "final", "last", "end", "summary"
        ]
        
        for section in sections:
            title = section.get("title", "").lower()
            
            # Check if title contains temporal indicators
            has_temporal = False
            for indicator in temporal_indicators:
                if indicator in title:
                    has_temporal = True
                    break
            
            if has_temporal:
                temporal_sections.append((section, self._get_temporal_priority(title)))
            else:
                non_temporal_sections.append(section)
        
        # Sort temporal sections by priority
        sorted_temporal = [s[0] for s in sorted(temporal_sections, key=lambda x: x[1])]
        
        # Return temporal sections first, then non-temporal
        return sorted_temporal + non_temporal_sections
    
    def _get_temporal_priority(self, title: str) -> int:
        """
        Get the temporal priority of a section title.
        
        Args:
            title: Section title
            
        Returns:
            Priority value (lower = earlier)
        """
        # Look for specific temporal indicators
        if any(word in title for word in ["first", "start", "begin", "introduction", "background"]):
            return 0
        if "second" in title:
            return 1
        if "third" in title:
            return 2
        if "fourth" in title:
            return 3
        if "fifth" in title:
            return 4
        if any(word in title for word in ["conclusion", "final", "last", "end", "summary"]):
            return 100  # Always put at the end
        
        # Default priority based on position in title
        for i, word in enumerate(title.split()):
            if word in ["then", "next", "after"]:
                return 50 + i
        
        return 50  # Middle priority
    
    def _apply_logical_dependencies_progression(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply logical dependencies progression to sections.
        
        Args:
            sections: List of sections
            
        Returns:
            Sections ordered by logical dependencies
        """
        # In a sophisticated implementation, this would build a dependency graph
        # For this implementation, we'll use a simpler approach
        
        # Initialize dependencies
        for section in sections:
            section["dependencies"] = set()
        
        # Identify potential dependencies between sections
        for i, section in enumerate(sections):
            section_topics = self._extract_section_topics(section)
            
            for j, other_section in enumerate(sections):
                if i == j:
                    continue
                
                other_topics = self._extract_section_topics(other_section)
                
                # Check if other section references topics from this section
                for topic in section_topics:
                    if self._references_topic(other_section, topic):
                        # The other section depends on this section
                        other_section["dependencies"].add(i)
        
        # Topological sort based on dependencies
        sorted_sections = self._topological_sort(sections)
        
        return sorted_sections
    
    def _extract_section_topics(self, section: Dict[str, Any]) -> List[str]:
        """
        Extract main topics from a section.
        
        Args:
            section: Section data
            
        Returns:
            List of main topics
        """
        topics = []
        
        # Add section title words
        title = section.get("title", "")
        title_words = [word.lower() for word in title.split() if len(word) > 3]
        topics.extend(title_words)
        
        # Add topics from elements
        for element in section.get("elements", []):
            element_topics = element.get("topics", [])
            topics.extend(element_topics)
        
        # Remove duplicates
        return list(set(topics))
    
    def _references_topic(self, section: Dict[str, Any], topic: str) -> bool:
        """
        Check if a section references a specific topic.
        
        Args:
            section: Section data
            topic: Topic to check for
            
        Returns:
            True if the section references the topic
        """
        # Check title
        if topic in section.get("title", "").lower():
            return True
        
        # Check elements
        for element in section.get("elements", []):
            content = element.get("content", "")
            if content and topic in content.lower():
                return True
        
        return False
    
    def _topological_sort(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Perform topological sort of sections based on dependencies.
        
        Args:
            sections: Sections with dependencies
            
        Returns:
            Topologically sorted sections
        """
        # Create a copy of the sections to avoid modifying the original
        sections_copy = [section.copy() for section in sections]
        
        # Convert dependencies to list for each section
        for section in sections_copy:
            section["dependencies"] = list(section["dependencies"])
        
        # Initialize result
        result = []
        temp_marked = set()
        perm_marked = set()
        
        # Topological sort function
        def visit(i):
            if i in perm_marked:
                return
            if i in temp_marked:
                # Cycle detected, skip
                return
            
            temp_marked.add(i)
            
            # Visit dependencies
            for j in sections_copy[i].get("dependencies", []):
                visit(j)
            
            temp_marked.remove(i)
            perm_marked.add(i)
            result.append(sections_copy[i])
        
        # Visit each node
        for i in range(len(sections_copy)):
            if i not in perm_marked:
                visit(i)
        
        # Reverse the result to get the correct order
        result.reverse()
        
        # Clean up the dependencies field
        for section in result:
            if "dependencies" in section:
                del section["dependencies"]
        
        return result
    
    def _calculate_structure_metrics(self, 
                                  structure: Dict[str, Any], 
                                  elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate metrics for the structured content.
        
        Args:
            structure: Final content structure
            elements: Original elements
            
        Returns:
            Structure metrics
        """
        # Count sections and subsections
        section_count = len(structure.get("sections", []))
        subsection_count = 0
        max_depth = 1
        
        for section in structure.get("sections", []):
            subsections = section.get("subsections", [])
            subsection_count += len(subsections)
            
            if subsections:
                max_depth = 2
        
        # Calculate average section depth
        total_sections = section_count + subsection_count
        if section_count > 0:
            average_depth = (section_count * 1 + subsection_count * 2) / total_sections
        else:
            average_depth = 0
        
        # Calculate coherence score (simplified)
        coherence_score = 0.8  # Default high coherence
        
        return {
            "element_count": len(elements),
            "section_count": section_count,
            "subsection_count": subsection_count,
            "max_depth": max_depth,
            "average_section_depth": average_depth,
            "coherence_score": coherence_score
        } 