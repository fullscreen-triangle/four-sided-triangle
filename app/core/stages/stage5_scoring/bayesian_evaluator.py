"""
Bayesian Evaluator

This module implements a Bayesian framework for evaluating the quality of generated 
solutions by calculating posterior probabilities, likelihoods, and priors.
"""

import logging
import math
from typing import Dict, Any, List, Optional

class BayesianEvaluator:
    """
    Implements a Bayesian framework for evaluating response quality.
    
    This class calculates:
    - P(R|D,Q): Posterior probability of response given domain knowledge and query
    - P(D|R,Q): Likelihood of domain knowledge given response and query
    - P(R|Q): Prior probability of response given query
    - P(D|Q): Evidence factor (domain knowledge given query)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Bayesian Evaluator.
        
        Args:
            config: Configuration dictionary for the evaluator
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Configure Bayesian priors and smoothing parameters
        self.prior_weight = self.config.get("prior_weight", 0.3)
        self.smoothing_factor = self.config.get("smoothing_factor", 0.05)
        self.information_gain_weight = self.config.get("information_gain_weight", 0.5)
        self.mutual_information_threshold = self.config.get("mutual_information_threshold", 0.1)
        
        self.logger.info("Bayesian Evaluator initialized")
    
    def evaluate(self, solution: Dict[str, Any], domain_knowledge: Dict[str, Any], 
                query_intent: Dict[str, Any]) -> Dict[str, float]:
        """
        Evaluate the solution using Bayesian probability framework.
        
        Args:
            solution: The generated solution to evaluate
            domain_knowledge: Domain knowledge used to generate the solution
            query_intent: The semantic intent of the user's query
            
        Returns:
            Dictionary of Bayesian metrics including posterior, likelihood, prior, and evidence
        """
        self.logger.info("Performing Bayesian evaluation")
        
        # Calculate prior probability P(R|Q)
        prior_probability = self._calculate_prior_probability(solution, query_intent)
        
        # Calculate likelihood P(D|R,Q)
        likelihood = self._calculate_likelihood(solution, domain_knowledge, query_intent)
        
        # Calculate evidence factor P(D|Q)
        evidence_factor = self._calculate_evidence_factor(domain_knowledge, query_intent)
        
        # Calculate posterior probability P(R|D,Q) using Bayes' theorem
        # P(R|D,Q) = P(D|R,Q) * P(R|Q) / P(D|Q)
        posterior_probability = (likelihood * prior_probability) / evidence_factor if evidence_factor > 0 else 0.0
        
        # Apply smoothing to avoid extreme values
        posterior_probability = self._apply_smoothing(posterior_probability)
        
        # Calculate additional metrics
        information_gain = self._calculate_information_gain(solution, domain_knowledge, query_intent)
        mutual_information = self._calculate_mutual_information(solution, domain_knowledge, query_intent)
        
        # Combine into final evaluation metrics
        metrics = {
            "posterior_probability": posterior_probability,
            "likelihood": likelihood,
            "prior_probability": prior_probability,
            "evidence_factor": evidence_factor,
            "information_gain": information_gain,
            "mutual_information": mutual_information
        }
        
        self.logger.info(f"Bayesian evaluation completed with posterior probability: {posterior_probability:.4f}")
        return metrics
    
    def _calculate_prior_probability(self, solution: Dict[str, Any], 
                                   query_intent: Dict[str, Any]) -> float:
        """
        Calculate the prior probability P(R|Q) of the response given the query.
        
        This measures how well the response aligns with the query intent
        without considering domain knowledge.
        
        Args:
            solution: The generated solution
            query_intent: The semantic intent of the query
            
        Returns:
            Prior probability value between 0 and 1
        """
        # Extract key elements from solution and query intent
        solution_elements = solution.get("content", {}).get("elements", [])
        intent_components = query_intent.get("components", {})
        
        if not solution_elements or not intent_components:
            return 0.5  # Default to neutral prior with insufficient data
        
        # Check how many query intent components are addressed in the solution
        addressed_components = 0
        total_components = len(intent_components)
        
        # Simple implementation: check if key terms from intent components
        # appear in the solution elements
        for component_name, component in intent_components.items():
            component_terms = component.get("key_terms", [])
            
            # Check if component terms appear in solution elements
            for element in solution_elements:
                element_content = element.get("content", "")
                if any(term.lower() in element_content.lower() for term in component_terms):
                    addressed_components += 1
                    break
        
        # Calculate coverage ratio and apply prior weight
        coverage_ratio = addressed_components / total_components if total_components > 0 else 0.5
        prior_probability = self.prior_weight + (1 - self.prior_weight) * coverage_ratio
        
        return prior_probability
    
    def _calculate_likelihood(self, solution: Dict[str, Any], domain_knowledge: Dict[str, Any],
                            query_intent: Dict[str, Any]) -> float:
        """
        Calculate the likelihood P(D|R,Q) of the domain knowledge given response and query.
        
        This measures how well the domain knowledge is represented in the solution.
        
        Args:
            solution: The generated solution
            domain_knowledge: Domain knowledge used to generate the solution
            query_intent: The semantic intent of the query
            
        Returns:
            Likelihood value between 0 and 1
        """
        # Extract key elements from solution and domain knowledge
        solution_elements = solution.get("content", {}).get("elements", [])
        domain_elements = domain_knowledge.get("elements", [])
        
        if not solution_elements or not domain_elements:
            return 0.5  # Default to neutral likelihood with insufficient data
        
        # Measure coverage of domain elements in solution
        domain_element_count = len(domain_elements)
        elements_covered = 0
        
        # Track important domain concepts and formulas
        domain_concepts = [elem.get("concept") for elem in domain_elements if elem.get("importance", 0) > 0.7]
        domain_formulas = [elem.get("formula") for elem in domain_elements if elem.get("type") == "formula"]
        
        # Count domain elements represented in solution
        for element in solution_elements:
            element_content = element.get("content", "")
            
            # Check concepts and formulas
            if any(concept and concept.lower() in element_content.lower() for concept in domain_concepts if concept):
                elements_covered += 1
            
            if any(formula and formula.lower() in element_content.lower() for formula in domain_formulas if formula):
                elements_covered += 1
        
        # Calculate representation ratio
        concepts_and_formulas = len(domain_concepts) + len(domain_formulas)
        representation_ratio = elements_covered / concepts_and_formulas if concepts_and_formulas > 0 else 0.5
        
        return representation_ratio
    
    def _calculate_evidence_factor(self, domain_knowledge: Dict[str, Any],
                                 query_intent: Dict[str, Any]) -> float:
        """
        Calculate the evidence factor P(D|Q) representing domain knowledge given query.
        
        This acts as a normalization factor in Bayes' theorem.
        
        Args:
            domain_knowledge: Domain knowledge used in solution generation
            query_intent: The semantic intent of the query
            
        Returns:
            Evidence factor between 0.1 and 1
        """
        # Measure relevance of domain knowledge to query intent
        domain_elements = domain_knowledge.get("elements", [])
        intent_components = query_intent.get("components", {})
        
        if not domain_elements or not intent_components:
            return 0.5  # Default with insufficient data
        
        # Extract query intent terms
        intent_terms = []
        for component in intent_components.values():
            intent_terms.extend(component.get("key_terms", []))
        
        # Count domain elements relevant to query
        relevant_elements = 0
        
        for element in domain_elements:
            element_content = str(element.get("content", ""))
            if any(term.lower() in element_content.lower() for term in intent_terms):
                relevant_elements += 1
        
        # Calculate relevance ratio with minimum bound to avoid division by zero
        relevance_ratio = relevant_elements / len(domain_elements) if len(domain_elements) > 0 else 0.5
        
        # Ensure evidence factor is never zero (would make posterior zero)
        return max(0.1, relevance_ratio)
    
    def _apply_smoothing(self, probability: float) -> float:
        """
        Apply smoothing to probability values to avoid extremes.
        
        Args:
            probability: Raw probability value
            
        Returns:
            Smoothed probability between smoothing_factor and (1-smoothing_factor)
        """
        # Apply smoothing to keep probabilities away from extremes 0 and 1
        smoothed = self.smoothing_factor + (1 - 2 * self.smoothing_factor) * probability
        return max(0.0, min(1.0, smoothed))
    
    def _calculate_information_gain(self, solution: Dict[str, Any], 
                                 domain_knowledge: Dict[str, Any],
                                 query_intent: Dict[str, Any]) -> float:
        """
        Calculate information gain provided by the solution.
        
        This measures how much information the solution adds beyond
        what is directly available in the domain knowledge.
        
        Args:
            solution: The generated solution
            domain_knowledge: Domain knowledge used to generate the solution
            query_intent: The semantic intent of the query
            
        Returns:
            Information gain value between 0 and 1
        """
        # Extract solution components
        solution_elements = solution.get("content", {}).get("elements", [])
        solution_insights = solution.get("insights", [])
        
        # Default information gain with insufficient data
        if not solution_elements:
            return 0.0
        
        # Calculate base level of information from domain knowledge
        domain_elements = domain_knowledge.get("elements", [])
        domain_info_size = len(domain_elements)
        
        # Count new insights and connections in solution
        new_insights = len(solution_insights)
        
        # Estimate information gain based on insights and new connections
        gain_ratio = min(1.0, (new_insights / max(1, domain_info_size)) * self.information_gain_weight)
        
        return gain_ratio
    
    def _calculate_mutual_information(self, solution: Dict[str, Any],
                                   domain_knowledge: Dict[str, Any],
                                   query_intent: Dict[str, Any]) -> float:
        """
        Calculate mutual information between solution and query intent.
        
        This measures how effectively the solution addresses the specific
        information needs expressed in the query.
        
        Args:
            solution: The generated solution
            domain_knowledge: Domain knowledge used to generate the solution
            query_intent: The semantic intent of the query
            
        Returns:
            Mutual information value between 0 and 1
        """
        # Extract solution content and query components
        solution_content = solution.get("content", {})
        solution_sections = solution_content.get("sections", [])
        intent_components = query_intent.get("components", {})
        
        # Default mutual information with insufficient data
        if not solution_sections or not intent_components:
            return 0.5
        
        # Calculate how many intent components are directly addressed in solution sections
        total_components = len(intent_components)
        addressed_components = 0
        
        # Extract intent terms
        intent_terms = {}
        for component_name, component in intent_components.items():
            intent_terms[component_name] = component.get("key_terms", [])
        
        # Check if solution sections address intent components
        for section in solution_sections:
            section_title = section.get("title", "").lower()
            section_elements = section.get("element_ids", [])
            
            # See if this section addresses any intent component
            for component_name, terms in intent_terms.items():
                if any(term.lower() in section_title for term in terms):
                    addressed_components += 1
                    break
        
        # Calculate mutual information ratio
        mi_ratio = addressed_components / total_components if total_components > 0 else 0.0
        
        # Apply threshold to identify significant mutual information
        return mi_ratio if mi_ratio > self.mutual_information_threshold else 0.0 