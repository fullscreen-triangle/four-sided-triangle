"""
Information Optimizer

This module contains the InformationOptimizer class, which optimizes information content 
by applying information theory principles to reduce redundancy, maximize information gain,
and improve cognitive processing efficiency.
"""

import logging
import math
from typing import Dict, Any, List, Optional, Set, Tuple
import numpy as np

class InformationOptimizer:
    """
    Optimizes information content using information theory principles.
    
    This class applies techniques to:
    - Remove redundant information
    - Maximize information gain
    - Balance cognitive load
    - Optimize information density
    - Enhance information transfer efficiency
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Information Optimizer.
        
        Args:
            config: Configuration dictionary for the optimizer
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Load configuration with defaults
        self.redundancy_threshold = self.config.get("redundancy_threshold", 0.7)
        self.cognitive_load_threshold = self.config.get("cognitive_load_threshold", 0.8)
        self.information_density_target = self.config.get("information_density_target", 0.75)
        self.max_elements = self.config.get("max_elements", 50)
        self.entropy_weight = self.config.get("entropy_weight", 0.5)
        self.enable_advanced_filtering = self.config.get("enable_advanced_filtering", True)
        
        self.logger.info("Information Optimizer initialized")
    
    async def optimize(self, 
                     prioritized_info: Dict[str, Any],
                     user_query: Dict[str, Any], 
                     context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize information content for maximum utility and minimal cognitive load.
        
        Args:
            prioritized_info: Information elements prioritized by relevance
            user_query: The user's query with enriched metadata
            context: Context information and state from previous processing
            
        Returns:
            Optimized information content with metadata
        """
        self.logger.info("Starting information optimization")
        
        # Extract information elements
        elements = prioritized_info.get("elements", [])
        if not elements:
            self.logger.warning("No elements to optimize")
            return {
                "elements": [],
                "optimization": {
                    "redundancy_threshold": self.redundancy_threshold,
                    "cognitive_load_threshold": self.cognitive_load_threshold,
                    "information_density_target": self.information_density_target
                },
                "metrics": {
                    "original_element_count": 0,
                    "optimized_element_count": 0,
                    "redundancy_eliminated": 0,
                    "information_density": 0,
                    "cognitive_load_estimate": 0
                }
            }
        
        # Step 1: Calculate information metrics for the elements
        elements_with_metrics = self._calculate_information_metrics(elements)
        
        # Step 2: Eliminate redundancy
        non_redundant_elements, redundancy_stats = self._eliminate_redundancy(
            elements_with_metrics
        )
        
        # Step 3: Optimize for cognitive load
        optimized_elements, cognitive_stats = self._optimize_cognitive_load(
            non_redundant_elements,
            user_query
        )
        
        # Step 4: Enhance information density
        final_elements, density_stats = self._enhance_information_density(
            optimized_elements,
            user_query
        )
        
        # Compile optimization metrics
        optimization_metrics = {
            "original_element_count": len(elements),
            "optimized_element_count": len(final_elements),
            "redundancy_eliminated": redundancy_stats["redundancy_eliminated"],
            "information_density": density_stats["information_density"],
            "cognitive_load_estimate": cognitive_stats["cognitive_load_estimate"]
        }
        
        optimization_result = {
            "elements": final_elements,
            "cognitive_load_estimate": cognitive_stats["cognitive_load_estimate"],
            "optimization": {
                "redundancy_threshold": self.redundancy_threshold,
                "cognitive_load_threshold": self.cognitive_load_threshold,
                "information_density_target": self.information_density_target
            },
            "metrics": optimization_metrics
        }
        
        self.logger.info(f"Information optimization complete. Elements: {len(final_elements)}")
        return optimization_result
    
    def _calculate_information_metrics(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate information-theoretic metrics for each element.
        
        Args:
            elements: List of information elements
            
        Returns:
            Elements with added information metrics
        """
        self.logger.debug("Calculating information metrics")
        
        # Create a copy to avoid modifying the original
        enriched_elements = []
        
        # Prepare for TF-IDF like calculation
        all_content = " ".join([e.get("content", "") for e in elements if "content" in e])
        total_words = len(all_content.split())
        
        for element in elements:
            element_copy = element.copy()
            
            # Calculate information entropy (complexity and uniqueness)
            content = element_copy.get("content", "")
            if not content:
                element_copy["information_entropy"] = 0
                element_copy["information_density"] = 0
                enriched_elements.append(element_copy)
                continue
                
            # Simple entropy calculation based on character distribution
            char_counts = {}
            for char in content:
                if char in char_counts:
                    char_counts[char] += 1
                else:
                    char_counts[char] = 1
                    
            entropy = 0
            for count in char_counts.values():
                probability = count / len(content)
                entropy -= probability * math.log2(probability)
            
            # Normalize entropy to 0-1 range (assuming typical text has entropy between 3.5-5.0)
            normalized_entropy = min(1.0, entropy / 5.0)
            
            # Calculate information density (ratio of unique terms to total)
            words = content.split()
            unique_words = set(words)
            density = len(unique_words) / len(words) if words else 0
            
            # Calculate term specificity (similar to TF-IDF concept)
            specificity = 0
            if words and total_words:
                word_count = len(words)
                doc_ratio = word_count / total_words
                specificity = -math.log(doc_ratio) * (word_count / total_words)
                specificity = min(1.0, specificity * 5)  # Scale to 0-1
            
            # Add metrics to the element
            element_copy["information_entropy"] = normalized_entropy
            element_copy["information_density"] = density
            element_copy["information_specificity"] = specificity
            element_copy["information_value"] = (
                normalized_entropy * 0.4 + 
                density * 0.3 + 
                specificity * 0.3
            )
            
            enriched_elements.append(element_copy)
        
        return enriched_elements
    
    def _eliminate_redundancy(self, elements: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Eliminate redundant information using similarity detection.
        
        Args:
            elements: Information elements with metrics
            
        Returns:
            Non-redundant elements and redundancy statistics
        """
        self.logger.debug("Eliminating redundancy")
        
        if not elements:
            return [], {"redundancy_eliminated": 0, "elements_removed": 0}
            
        # Sort elements by priority first, then information value
        sorted_elements = sorted(
            elements,
            key=lambda x: (x.get("priority_score", 0), x.get("information_value", 0)),
            reverse=True
        )
        
        non_redundant = []
        redundant_count = 0
        seen_content_hashes = set()
        
        for element in sorted_elements:
            # Skip elements without content
            if not element.get("content"):
                continue
                
            # Create a simple content fingerprint
            content = element.get("content", "").lower()
            content_words = set(content.split())
            
            # Check for high similarity with already included elements
            is_redundant = False
            
            for included_element in non_redundant:
                included_content = included_element.get("content", "").lower()
                included_words = set(included_content.split())
                
                # Calculate Jaccard similarity
                if not included_words or not content_words:
                    continue
                    
                intersection = len(content_words.intersection(included_words))
                union = len(content_words.union(included_words))
                similarity = intersection / union if union > 0 else 0
                
                # Check if similarity exceeds threshold
                if similarity > self.redundancy_threshold:
                    is_redundant = True
                    redundant_count += 1
                    
                    # If the redundant element has higher information value or priority,
                    # replace the existing element
                    current_info_value = element.get("information_value", 0)
                    current_priority = element.get("priority_score", 0)
                    included_info_value = included_element.get("information_value", 0)
                    included_priority = included_element.get("priority_score", 0)
                    
                    if (current_priority > included_priority or 
                        (current_priority == included_priority and 
                         current_info_value > included_info_value)):
                        # Replace the existing element
                        non_redundant.remove(included_element)
                        element["replaced_redundant"] = True
                        non_redundant.append(element)
                    
                    break
            
            # If not redundant, add to the non-redundant list
            if not is_redundant:
                non_redundant.append(element)
                
            # Apply maximum elements limit if specified
            if len(non_redundant) >= self.max_elements:
                break
        
        # Calculate stats
        redundancy_stats = {
            "redundancy_eliminated": redundant_count / len(elements) if elements else 0,
            "elements_removed": redundant_count
        }
        
        return non_redundant, redundancy_stats
    
    def _optimize_cognitive_load(self, 
                               elements: List[Dict[str, Any]], 
                               user_query: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Optimize elements to manage cognitive load based on complexity and user context.
        
        Args:
            elements: Non-redundant information elements
            user_query: The user's query with enriched metadata
            
        Returns:
            Cognitively optimized elements and cognitive load statistics
        """
        self.logger.debug("Optimizing cognitive load")
        
        if not elements:
            return [], {"cognitive_load_estimate": 0}
            
        # Sort elements by priority and information value
        sorted_elements = sorted(
            elements,
            key=lambda x: (x.get("priority_score", 0), x.get("information_value", 0)),
            reverse=True
        )
        
        # Estimate cognitive load for each element based on:
        # - Information complexity (entropy)
        # - Content length
        # - Conceptual depth
        for element in sorted_elements:
            content = element.get("content", "")
            entropy = element.get("information_entropy", 0)
            
            # Calculate length factor (longer content = higher cognitive load)
            length = len(content.split())
            length_factor = min(1.0, length / 200)  # Normalize to 0-1
            
            # Calculate conceptual depth (based on domain-specific terminology)
            # This is a simplified implementation - in a real system, we would use
            # a more sophisticated analysis of domain terminology
            conceptual_depth = 0.5  # Default middle value
            
            # Calculate total cognitive load
            cognitive_load = (
                entropy * 0.4 +
                length_factor * 0.3 +
                conceptual_depth * 0.3
            )
            
            element["cognitive_load"] = cognitive_load
        
        # Determine target cognitive load threshold based on query complexity
        query_complexity = self._estimate_query_complexity(user_query)
        adjusted_threshold = self.cognitive_load_threshold * (1.0 + query_complexity * 0.2)
        
        # Filter elements based on cognitive load threshold
        optimized_elements = []
        total_cognitive_load = 0
        cumulative_load = 0
        
        for element in sorted_elements:
            cognitive_load = element.get("cognitive_load", 0)
            
            # Always include highest priority elements
            if len(optimized_elements) < 5:  # Ensure at least 5 elements are included
                optimized_elements.append(element)
                cumulative_load += cognitive_load
            elif cumulative_load < adjusted_threshold:
                # Add element if it doesn't exceed the threshold
                optimized_elements.append(element)
                cumulative_load += cognitive_load
            else:
                # Skip this element as it would exceed cognitive load threshold
                pass
                
            total_cognitive_load += cognitive_load
            
            # Apply maximum elements limit if specified
            if len(optimized_elements) >= self.max_elements:
                break
                
        # Calculate average cognitive load
        avg_cognitive_load = total_cognitive_load / len(elements) if elements else 0
        normalized_cumulative_load = cumulative_load / (len(optimized_elements) if optimized_elements else 1)
        
        cognitive_stats = {
            "cognitive_load_estimate": normalized_cumulative_load,
            "average_element_load": avg_cognitive_load
        }
        
        return optimized_elements, cognitive_stats
    
    def _enhance_information_density(self, 
                                   elements: List[Dict[str, Any]],
                                   user_query: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Enhance information density by prioritizing information-rich elements.
        
        Args:
            elements: Cognitively optimized elements
            user_query: The user's query with enriched metadata
            
        Returns:
            Density-optimized elements and density statistics
        """
        self.logger.debug("Enhancing information density")
        
        if not elements:
            return [], {"information_density": 0}
            
        # Calculate target information density based on query complexity
        query_complexity = self._estimate_query_complexity(user_query)
        target_density = self.information_density_target * (1.0 + query_complexity * 0.1)
        
        # Sort elements by information density and priority
        density_sorted = sorted(
            elements,
            key=lambda x: (x.get("information_density", 0), x.get("priority_score", 0)),
            reverse=True
        )
        
        # Ensure we have high information density elements
        high_density_elements = [
            e for e in density_sorted 
            if e.get("information_density", 0) > target_density
        ]
        
        # If we have enough high density elements, prioritize them
        final_elements = []
        if len(high_density_elements) >= min(5, len(elements) // 2):
            # Include all high density elements
            final_elements.extend(high_density_elements)
            
            # Add remaining elements by priority
            priority_sorted = sorted(
                [e for e in elements if e not in high_density_elements],
                key=lambda x: x.get("priority_score", 0),
                reverse=True
            )
            
            remaining_slots = self.max_elements - len(final_elements)
            final_elements.extend(priority_sorted[:remaining_slots])
        else:
            # Not enough high density elements, use original elements
            final_elements = elements
            
        # Calculate average information density
        total_density = sum(e.get("information_density", 0) for e in final_elements)
        avg_density = total_density / len(final_elements) if final_elements else 0
        
        density_stats = {
            "information_density": avg_density,
            "high_density_ratio": len(high_density_elements) / len(elements) if elements else 0
        }
        
        return final_elements, density_stats
    
    def _estimate_query_complexity(self, user_query: Dict[str, Any]) -> float:
        """
        Estimate the complexity of the user query.
        
        Args:
            user_query: The user's query with enriched metadata
            
        Returns:
            Complexity score (0.0-1.0)
        """
        complexity = 0.5  # Default medium complexity
        
        query_text = user_query.get("text", "")
        if not query_text:
            return complexity
            
        # Calculate based on query length and structure
        words = query_text.split()
        
        # Length factor
        length_factor = min(1.0, len(words) / 20)  # Normalize to 0-1
        
        # Structure factor (presence of complex constructs)
        structure_markers = ["why", "how", "compare", "contrast", "relationship", "impact"]
        structure_factor = 0
        for marker in structure_markers:
            if marker in query_text.lower():
                structure_factor += 0.1
        structure_factor = min(1.0, structure_factor)
        
        # Intent complexity
        intent = user_query.get("intent", "")
        intent_complexity = 0.5  # Default medium
        
        if intent:
            complex_intents = ["explanation", "analysis", "synthesis", "evaluation"]
            simple_intents = ["factual", "definition", "lookup", "confirmation"]
            
            for c_intent in complex_intents:
                if c_intent in intent.lower():
                    intent_complexity = 0.8
                    break
                    
            for s_intent in simple_intents:
                if s_intent in intent.lower():
                    intent_complexity = 0.3
                    break
        
        # Calculate combined complexity
        complexity = (
            length_factor * 0.2 +
            structure_factor * 0.3 +
            intent_complexity * 0.5
        )
        
        return min(1.0, complexity) 