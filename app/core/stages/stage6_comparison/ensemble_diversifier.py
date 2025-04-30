"""
Ensemble Diversifier

This module implements ensemble diversification techniques to create an optimal
ensemble of response candidates that maximizes both quality and diversity.
"""

import logging
import math
from typing import Dict, Any, List, Optional, Set, Tuple

class EnsembleDiversifier:
    """
    Implements ensemble diversification to maximize both quality and diversity.
    
    This class applies diversification algorithms to create an optimal ensemble
    of response candidates, balancing between quality and diversity based on
    a configurable alpha parameter.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Ensemble Diversifier.
        
        Args:
            config: Configuration dictionary for the diversifier
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Configure diversification parameters
        self.min_ensemble_size = self.config.get("min_ensemble_size", 2)
        self.max_ensemble_size = self.config.get("max_ensemble_size", 5)
        self.diversity_threshold = self.config.get("diversity_threshold", 0.3)
        self.default_alpha = self.config.get("default_alpha", 0.7)
        
        self.logger.info("Ensemble Diversifier initialized")
    
    def diversify(self, primary_response: Dict[str, Any], 
                alternative_responses: List[Dict[str, Any]],
                diversity_scores: Dict[str, Any],
                alpha: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Create a diversified ensemble of responses.
        
        Args:
            primary_response: The primary response from solution generation
            alternative_responses: List of alternative response candidates
            diversity_scores: Diversity metrics between responses
            alpha: Quality-diversity trade-off parameter (0-1, higher values favor quality)
            
        Returns:
            List of selected responses forming the diversified ensemble
        """
        self.logger.info("Creating diversified ensemble")
        
        alpha = alpha if alpha is not None else self.default_alpha
        
        # Ensure alpha is within valid range
        alpha = max(0.0, min(1.0, alpha))
        
        # If no alternatives, return just the primary response
        if not alternative_responses:
            return [primary_response]
        
        # Combine primary and alternatives into candidates
        candidates = [primary_response] + alternative_responses
        
        # Get quality scores for all candidates (primary always has highest quality)
        quality_scores = self._extract_quality_scores(primary_response, alternative_responses)
        
        # Apply diversification algorithm
        if self.config.get("algorithm", "greedy") == "greedy":
            selected_indices = self._apply_greedy_diversification(
                candidates, quality_scores, diversity_scores, alpha)
        else:
            # Default to maximal marginal relevance (MMR)
            selected_indices = self._apply_mmr_diversification(
                candidates, quality_scores, diversity_scores, alpha)
        
        # Construct the final ensemble
        ensemble = [candidates[idx] for idx in selected_indices]
        
        # Ensure primary response is always included
        if 0 not in selected_indices:
            ensemble.insert(0, primary_response)
        
        # Apply ensemble size constraints
        if len(ensemble) < self.min_ensemble_size and len(candidates) >= self.min_ensemble_size:
            # Add more candidates to meet minimum size
            missing = self.min_ensemble_size - len(ensemble)
            unselected_indices = [i for i in range(len(candidates)) if i not in selected_indices]
            additional_indices = unselected_indices[:missing]
            ensemble.extend([candidates[idx] for idx in additional_indices])
            
        if len(ensemble) > self.max_ensemble_size:
            # Trim ensemble to maximum size, always keeping primary
            ensemble = ensemble[:self.max_ensemble_size]
        
        self.logger.info(f"Diversified ensemble created with {len(ensemble)} responses")
        return ensemble
    
    def _extract_quality_scores(self, primary_response: Dict[str, Any],
                              alternative_responses: List[Dict[str, Any]]) -> List[float]:
        """
        Extract quality scores for all candidates.
        
        Args:
            primary_response: The primary response
            alternative_responses: List of alternative responses
            
        Returns:
            List of quality scores (normalized to [0, 1])
        """
        # Primary response is assumed to have highest quality (1.0)
        primary_quality = 1.0
        
        # For alternatives, either use explicit quality or assign scaled values
        alternative_qualities = []
        
        for i, alt in enumerate(alternative_responses):
            # If quality is explicitly available, use it
            if "quality_score" in alt:
                quality = alt["quality_score"]
            else:
                # Otherwise, assign decreasing quality scores
                decay_factor = 0.15 * (i + 1)
                quality = max(0.2, primary_quality - decay_factor)
            
            alternative_qualities.append(quality)
        
        # Combine all quality scores
        quality_scores = [primary_quality] + alternative_qualities
        
        # Normalize to [0, 1] range
        max_quality = max(quality_scores)
        if max_quality > 0:
            quality_scores = [q / max_quality for q in quality_scores]
        
        return quality_scores
    
    def _apply_greedy_diversification(self, candidates: List[Dict[str, Any]],
                                    quality_scores: List[float],
                                    diversity_scores: Dict[str, Any],
                                    alpha: float) -> List[int]:
        """
        Apply greedy diversification algorithm.
        
        This algorithm iteratively selects the candidate with the highest
        marginal contribution to the ensemble.
        
        Args:
            candidates: List of all response candidates
            quality_scores: Quality score for each candidate
            diversity_scores: Diversity metrics between candidates
            alpha: Quality-diversity trade-off parameter
            
        Returns:
            List of selected candidate indices
        """
        if not candidates:
            return []
            
        # Extract pairwise diversity scores
        pairwise_diversity = diversity_scores.get("pairwise_scores", [])
        
        # Start with the primary response (highest quality)
        selected_indices = [0]
        candidate_count = len(candidates)
        
        # Calculate target ensemble size
        target_size = min(self.max_ensemble_size, max(self.min_ensemble_size, 
                                                    candidate_count // 2 + 1))
        
        # Iteratively add candidates that maximize marginal gain
        while len(selected_indices) < target_size and len(selected_indices) < candidate_count:
            best_score = -1
            best_idx = -1
            
            # Evaluate each unselected candidate
            for idx in range(candidate_count):
                if idx in selected_indices:
                    continue
                
                # Calculate quality component
                quality_component = quality_scores[idx] * alpha
                
                # Calculate diversity component (average diversity to already selected)
                diversity_component = 0
                if pairwise_diversity and selected_indices:
                    diversity_sum = 0
                    for selected_idx in selected_indices:
                        pair_key = f"{min(idx, selected_idx)}-{max(idx, selected_idx)}"
                        diversity_sum += pairwise_diversity.get(pair_key, 0)
                    diversity_component = diversity_sum / len(selected_indices) * (1 - alpha)
                
                # Combined score
                combined_score = quality_component + diversity_component
                
                if combined_score > best_score:
                    best_score = combined_score
                    best_idx = idx
            
            # Add the best candidate to selected set
            if best_idx >= 0:
                selected_indices.append(best_idx)
            else:
                break
        
        return selected_indices
    
    def _apply_mmr_diversification(self, candidates: List[Dict[str, Any]],
                                 quality_scores: List[float],
                                 diversity_scores: Dict[str, Any],
                                 alpha: float) -> List[int]:
        """
        Apply Maximal Marginal Relevance (MMR) diversification algorithm.
        
        This algorithm balances between quality and diversity by maximizing
        marginal relevance in each selection step.
        
        Args:
            candidates: List of all response candidates
            quality_scores: Quality score for each candidate
            diversity_scores: Diversity metrics between candidates
            alpha: Quality-diversity trade-off parameter
            
        Returns:
            List of selected candidate indices
        """
        if not candidates:
            return []
            
        # Extract pairwise diversity scores
        pairwise_diversity = diversity_scores.get("pairwise_scores", {})
        
        # Start with empty selection
        selected_indices = []
        unselected_indices = set(range(len(candidates)))
        candidate_count = len(candidates)
        
        # Calculate target ensemble size
        target_size = min(self.max_ensemble_size, max(self.min_ensemble_size, 
                                                    candidate_count // 2 + 1))
        
        # First, always select the primary response (highest quality)
        selected_indices.append(0)
        unselected_indices.remove(0)
        
        # Iteratively apply MMR to select the remaining candidates
        while len(selected_indices) < target_size and unselected_indices:
            best_mmr = -float('inf')
            best_idx = -1
            
            # Find the candidate with highest MMR
            for idx in unselected_indices:
                # Quality term (first part of MMR)
                quality_term = quality_scores[idx] * alpha
                
                # Diversity term (second part of MMR)
                if not selected_indices:
                    similarity_term = 0
                else:
                    # Find maximum similarity (minimum diversity) to any selected item
                    max_similarity = 0
                    for selected_idx in selected_indices:
                        pair_key = f"{min(idx, selected_idx)}-{max(idx, selected_idx)}"
                        # Convert diversity to similarity (1 - diversity)
                        similarity = 1 - pairwise_diversity.get(pair_key, 0)
                        max_similarity = max(max_similarity, similarity)
                    
                    similarity_term = max_similarity * (1 - alpha)
                
                # MMR = quality_term - similarity_term
                mmr = quality_term - similarity_term
                
                if mmr > best_mmr:
                    best_mmr = mmr
                    best_idx = idx
            
            # Add the best candidate to selected set
            if best_idx >= 0:
                selected_indices.append(best_idx)
                unselected_indices.remove(best_idx)
            else:
                break
        
        return selected_indices 