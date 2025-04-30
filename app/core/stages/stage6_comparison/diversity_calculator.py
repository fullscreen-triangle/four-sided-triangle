"""
Diversity Calculator

This module calculates diversity metrics between response candidates,
measuring how different responses are from each other across multiple dimensions.
"""

import logging
import math
from typing import Dict, Any, List, Optional, Set, Tuple

class DiversityCalculator:
    """
    Computes pairwise diversity scores between response candidates.
    
    This class measures how different responses are from each other across
    multiple dimensions including content, structure, and information emphasis.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Diversity Calculator.
        
        Args:
            config: Configuration dictionary for the calculator
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Configure diversity calculation parameters
        self.content_weight = self.config.get("content_weight", 0.5)
        self.structure_weight = self.config.get("structure_weight", 0.3)
        self.emphasis_weight = self.config.get("emphasis_weight", 0.2)
        self.element_sample_size = self.config.get("element_sample_size", 20)
        
        self.logger.info("Diversity Calculator initialized")
    
    def calculate_diversity(self, primary_response: Dict[str, Any],
                          alternative_responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate diversity metrics between response candidates.
        
        Args:
            primary_response: The primary response from solution generation
            alternative_responses: List of alternative response candidates
            
        Returns:
            Dictionary of diversity metrics including pairwise scores
        """
        self.logger.info("Calculating diversity metrics")
        
        # If no alternatives, return empty diversity metrics
        if not alternative_responses:
            return {
                "average_diversity": 0.0,
                "pairwise_scores": {},
                "diversity_components": {}
            }
        
        # Combine primary and alternatives into all candidates
        all_responses = [primary_response] + alternative_responses
        n_responses = len(all_responses)
        
        # Calculate pairwise diversity scores
        pairwise_scores = {}
        content_diversity = {}
        structure_diversity = {}
        emphasis_diversity = {}
        
        for i in range(n_responses):
            for j in range(i + 1, n_responses):
                # Calculate diversity components
                content_div = self._calculate_content_diversity(all_responses[i], all_responses[j])
                structure_div = self._calculate_structure_diversity(all_responses[i], all_responses[j])
                emphasis_div = self._calculate_emphasis_diversity(all_responses[i], all_responses[j])
                
                # Calculate weighted diversity score
                weighted_div = (
                    content_div * self.content_weight +
                    structure_div * self.structure_weight +
                    emphasis_div * self.emphasis_weight
                )
                
                # Store pairwise scores
                pair_key = f"{i}-{j}"
                pairwise_scores[pair_key] = weighted_div
                content_diversity[pair_key] = content_div
                structure_diversity[pair_key] = structure_div
                emphasis_diversity[pair_key] = emphasis_div
        
        # Calculate average diversity
        if pairwise_scores:
            average_diversity = sum(pairwise_scores.values()) / len(pairwise_scores)
        else:
            average_diversity = 0.0
        
        # Create diversity components dictionary
        diversity_components = {
            "content_diversity": content_diversity,
            "structure_diversity": structure_diversity,
            "emphasis_diversity": emphasis_diversity
        }
        
        # Combine all diversity metrics
        diversity_metrics = {
            "average_diversity": average_diversity,
            "pairwise_scores": pairwise_scores,
            "diversity_components": diversity_components
        }
        
        self.logger.info(f"Diversity calculation completed with average diversity: {average_diversity:.4f}")
        return diversity_metrics
    
    def _calculate_content_diversity(self, response1: Dict[str, Any], 
                                  response2: Dict[str, Any]) -> float:
        """
        Calculate content diversity between two responses.
        
        This measures how different the actual content is between responses.
        
        Args:
            response1: First response
            response2: Second response
            
        Returns:
            Content diversity score between 0 and 1
        """
        # Extract elements from responses
        elements1 = response1.get("content", {}).get("elements", [])
        elements2 = response2.get("content", {}).get("elements", [])
        
        # If either has no elements, assign medium diversity
        if not elements1 or not elements2:
            return 0.5
        
        # Limit element size for efficient calculation
        elements1 = elements1[:self.element_sample_size]
        elements2 = elements2[:self.element_sample_size]
        
        # Calculate content overlap using Jaccard similarity
        content_set1 = set()
        content_set2 = set()
        
        for elem in elements1:
            content = elem.get("content", "")
            # Create n-grams for better comparison
            tokens = self._tokenize(content)
            ngrams = self._create_ngrams(tokens, n=3)
            content_set1.update(ngrams)
        
        for elem in elements2:
            content = elem.get("content", "")
            tokens = self._tokenize(content)
            ngrams = self._create_ngrams(tokens, n=3)
            content_set2.update(ngrams)
        
        # Calculate Jaccard similarity
        if content_set1 and content_set2:
            intersection = len(content_set1.intersection(content_set2))
            union = len(content_set1.union(content_set2))
            similarity = intersection / union if union > 0 else 0.0
        else:
            similarity = 0.0
        
        # Convert similarity to diversity (1 - similarity)
        diversity = 1.0 - similarity
        
        return diversity
    
    def _calculate_structure_diversity(self, response1: Dict[str, Any], 
                                    response2: Dict[str, Any]) -> float:
        """
        Calculate structure diversity between two responses.
        
        This measures how differently the content is organized and structured.
        
        Args:
            response1: First response
            response2: Second response
            
        Returns:
            Structure diversity score between 0 and 1
        """
        # Extract sections from responses
        sections1 = response1.get("content", {}).get("sections", [])
        sections2 = response2.get("content", {}).get("sections", [])
        
        # If either has no sections, use elements instead
        if not sections1 or not sections2:
            elements1 = response1.get("content", {}).get("elements", [])
            elements2 = response2.get("content", {}).get("elements", [])
            
            # If no elements either, assign medium diversity
            if not elements1 or not elements2:
                return 0.5
            
            # Compare element counts
            count_diff = abs(len(elements1) - len(elements2)) / max(len(elements1), len(elements2))
            
            # Calculate type distributions
            types1 = self._calculate_type_distribution(elements1)
            types2 = self._calculate_type_distribution(elements2)
            
            type_diff = self._calculate_distribution_difference(types1, types2)
            
            # Combine metrics for elements
            return (count_diff + type_diff) / 2
        
        # Compare section structures
        
        # 1. Compare section count
        count_diff = abs(len(sections1) - len(sections2)) / max(len(sections1), len(sections2))
        
        # 2. Compare section titles
        titles1 = [section.get("title", "").lower() for section in sections1]
        titles2 = [section.get("title", "").lower() for section in sections2]
        
        # Calculate title overlap using Jaccard similarity
        title_set1 = set(titles1)
        title_set2 = set(titles2)
        
        title_intersection = len(title_set1.intersection(title_set2))
        title_union = len(title_set1.union(title_set2))
        title_similarity = title_intersection / title_union if title_union > 0 else 0.0
        title_diff = 1.0 - title_similarity
        
        # 3. Compare section sizes
        size1 = [len(section.get("element_ids", [])) for section in sections1]
        size2 = [len(section.get("element_ids", [])) for section in sections2]
        
        # Normalize section sizes
        if size1:
            total1 = sum(size1)
            size_dist1 = [s / total1 if total1 > 0 else 0 for s in size1]
        else:
            size_dist1 = []
            
        if size2:
            total2 = sum(size2)
            size_dist2 = [s / total2 if total2 > 0 else 0 for s in size2]
        else:
            size_dist2 = []
        
        # If size distributions are available, calculate difference
        if size_dist1 and size_dist2:
            # Pad shorter distribution with zeros
            max_len = max(len(size_dist1), len(size_dist2))
            size_dist1 = size_dist1 + [0] * (max_len - len(size_dist1))
            size_dist2 = size_dist2 + [0] * (max_len - len(size_dist2))
            
            # Calculate sum of absolute differences
            size_diff = sum(abs(s1 - s2) for s1, s2 in zip(size_dist1, size_dist2)) / max_len
        else:
            size_diff = 0.5
        
        # Combine structure metrics
        structure_diversity = (count_diff + title_diff + size_diff) / 3
        
        return structure_diversity
    
    def _calculate_emphasis_diversity(self, response1: Dict[str, Any], 
                                   response2: Dict[str, Any]) -> float:
        """
        Calculate emphasis diversity between two responses.
        
        This measures how differently the responses emphasize various aspects
        of the information.
        
        Args:
            response1: First response
            response2: Second response
            
        Returns:
            Emphasis diversity score between 0 and 1
        """
        # Extract elements and relevance scores
        elements1 = response1.get("content", {}).get("elements", [])
        elements2 = response2.get("content", {}).get("elements", [])
        
        # If either has no elements, assign medium diversity
        if not elements1 or not elements2:
            return 0.5
        
        # Calculate emphasis based on relevance scores and positioning
        
        # 1. Extract relevance scores
        relevance1 = [elem.get("relevance", 0.5) for elem in elements1]
        relevance2 = [elem.get("relevance", 0.5) for elem in elements2]
        
        # Calculate relevance distributions
        if relevance1:
            rel_dist1 = [r / sum(relevance1) if sum(relevance1) > 0 else 1/len(relevance1) 
                       for r in relevance1]
        else:
            rel_dist1 = []
            
        if relevance2:
            rel_dist2 = [r / sum(relevance2) if sum(relevance2) > 0 else 1/len(relevance2) 
                       for r in relevance2]
        else:
            rel_dist2 = []
        
        # If distributions are available, calculate difference
        if rel_dist1 and rel_dist2:
            # Calculate emphasis difference using Jensen-Shannon divergence
            # (simplified version using average absolute difference)
            max_len = max(len(rel_dist1), len(rel_dist2))
            rel_dist1 = rel_dist1 + [0] * (max_len - len(rel_dist1))
            rel_dist2 = rel_dist2 + [0] * (max_len - len(rel_dist2))
            
            emphasis_diff = sum(abs(r1 - r2) for r1, r2 in zip(rel_dist1, rel_dist2)) / max_len
        else:
            emphasis_diff = 0.5
        
        # 2. Compare element types emphasis
        types1 = self._calculate_type_distribution(elements1)
        types2 = self._calculate_type_distribution(elements2)
        
        type_diff = self._calculate_distribution_difference(types1, types2)
        
        # Combine emphasis metrics
        emphasis_diversity = (emphasis_diff + type_diff) / 2
        
        return emphasis_diversity
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        # Simple tokenization by splitting on whitespace and removing punctuation
        tokens = []
        if text:
            # Remove common punctuation and split
            cleaned = text.lower()
            for char in ".,;:!?()[]{}\"'":
                cleaned = cleaned.replace(char, " ")
            tokens = [t for t in cleaned.split() if t]
        
        return tokens
    
    def _create_ngrams(self, tokens: List[str], n: int = 3) -> Set[str]:
        """
        Create n-grams from a list of tokens.
        
        Args:
            tokens: List of tokens
            n: Size of n-grams
            
        Returns:
            Set of n-grams
        """
        ngrams = set()
        if len(tokens) >= n:
            for i in range(len(tokens) - n + 1):
                ngram = " ".join(tokens[i:i+n])
                ngrams.add(ngram)
        
        return ngrams
    
    def _calculate_type_distribution(self, elements: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate distribution of element types.
        
        Args:
            elements: List of content elements
            
        Returns:
            Dictionary mapping element types to their frequency
        """
        type_counts = {}
        
        # Count each element type
        for elem in elements:
            elem_type = elem.get("type", "unknown")
            type_counts[elem_type] = type_counts.get(elem_type, 0) + 1
        
        # Convert to distribution
        total = sum(type_counts.values())
        type_dist = {t: c / total if total > 0 else 0 for t, c in type_counts.items()}
        
        return type_dist
    
    def _calculate_distribution_difference(self, dist1: Dict[str, float], 
                                        dist2: Dict[str, float]) -> float:
        """
        Calculate difference between two distributions.
        
        Args:
            dist1: First distribution
            dist2: Second distribution
            
        Returns:
            Difference score between 0 and 1
        """
        # Get all keys from both distributions
        all_keys = set(dist1.keys()).union(set(dist2.keys()))
        
        if not all_keys:
            return 0.0
        
        # Calculate sum of absolute differences
        diff_sum = 0.0
        for key in all_keys:
            val1 = dist1.get(key, 0.0)
            val2 = dist2.get(key, 0.0)
            diff_sum += abs(val1 - val2)
        
        # Normalize by number of keys
        avg_diff = diff_sum / len(all_keys)
        
        return avg_diff 