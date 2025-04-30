"""
Quality Dimension Assessor

This module implements assessment of multiple quality dimensions for generated solutions
including accuracy, completeness, consistency, relevance, and novelty.
"""

import logging
from typing import Dict, Any, List, Optional

class QualityDimensionAssessor:
    """
    Assesses multiple quality dimensions of generated solutions.
    
    This class evaluates the solution along five key dimensions:
    - Accuracy: Correctness of information relative to domain knowledge
    - Completeness: Coverage of required information elements
    - Consistency: Internal logical coherence of the solution
    - Relevance: Alignment with the user's query intent
    - Novelty: Presence of non-obvious insights or connections
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Quality Dimension Assessor.
        
        Args:
            config: Configuration dictionary for the assessor
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Configure dimension-specific parameters
        self.accuracy_threshold = self.config.get("accuracy_threshold", 0.8)
        self.completeness_threshold = self.config.get("completeness_threshold", 0.7)
        self.consistency_threshold = self.config.get("consistency_threshold", 0.85)
        self.relevance_threshold = self.config.get("relevance_threshold", 0.75)
        self.novelty_threshold = self.config.get("novelty_threshold", 0.3)
        
        # Enable/disable specific dimensions
        self.enabled_dimensions = self.config.get("enabled_dimensions", 
                                                 ["accuracy", "completeness", "consistency", 
                                                  "relevance", "novelty"])
        
        self.logger.info("Quality Dimension Assessor initialized")
    
    def assess_dimensions(self, solution: Dict[str, Any], domain_knowledge: Dict[str, Any],
                        query_intent: Dict[str, Any], 
                        bayesian_metrics: Dict[str, float]) -> Dict[str, float]:
        """
        Assess the solution across multiple quality dimensions.
        
        Args:
            solution: The generated solution to evaluate
            domain_knowledge: Domain knowledge used to generate the solution
            query_intent: The semantic intent of the user's query
            bayesian_metrics: Metrics from Bayesian evaluation
            
        Returns:
            Dictionary of quality scores for each dimension
        """
        self.logger.info("Assessing quality dimensions")
        
        dimension_scores = {}
        
        # Assess each enabled dimension
        if "accuracy" in self.enabled_dimensions:
            dimension_scores["accuracy"] = self._assess_accuracy(
                solution, domain_knowledge, bayesian_metrics)
        
        if "completeness" in self.enabled_dimensions:
            dimension_scores["completeness"] = self._assess_completeness(
                solution, domain_knowledge, query_intent)
        
        if "consistency" in self.enabled_dimensions:
            dimension_scores["consistency"] = self._assess_consistency(
                solution)
        
        if "relevance" in self.enabled_dimensions:
            dimension_scores["relevance"] = self._assess_relevance(
                solution, query_intent, bayesian_metrics)
        
        if "novelty" in self.enabled_dimensions:
            dimension_scores["novelty"] = self._assess_novelty(
                solution, domain_knowledge)
        
        self.logger.info(f"Quality dimension assessment completed with scores: {dimension_scores}")
        return dimension_scores
    
    def _assess_accuracy(self, solution: Dict[str, Any], domain_knowledge: Dict[str, Any],
                       bayesian_metrics: Dict[str, float]) -> float:
        """
        Assess the accuracy of the solution relative to domain knowledge.
        
        This measures the factual correctness of information in the solution.
        
        Args:
            solution: The generated solution
            domain_knowledge: Domain knowledge used to generate the solution
            bayesian_metrics: Metrics from Bayesian evaluation
            
        Returns:
            Accuracy score between 0 and 1
        """
        # Extract solution content and domain knowledge elements
        solution_elements = solution.get("content", {}).get("elements", [])
        domain_elements = domain_knowledge.get("elements", [])
        
        if not solution_elements or not domain_elements:
            return 0.5  # Default with insufficient data
        
        # Extract facts and formulas from domain knowledge
        domain_facts = []
        domain_formulas = {}
        
        for element in domain_elements:
            if element.get("type") == "fact":
                domain_facts.append(element.get("content", ""))
            elif element.get("type") == "formula":
                formula_name = element.get("name")
                formula_content = element.get("formula")
                if formula_name and formula_content:
                    domain_formulas[formula_name] = formula_content
        
        # Check solution elements for factual consistency with domain knowledge
        accuracy_scores = []
        
        for element in solution_elements:
            element_content = element.get("content", "")
            element_type = element.get("type", "")
            
            # Skip non-factual elements
            if element_type not in ["fact", "formula", "calculation", "assertion"]:
                continue
            
            # Check facts
            if element_type == "fact":
                # Simple check: is this fact supported by domain knowledge?
                fact_accuracy = 0.0
                for domain_fact in domain_facts:
                    if self._fact_similarity(element_content, domain_fact) > 0.7:
                        fact_accuracy = 1.0
                        break
                accuracy_scores.append(fact_accuracy)
            
            # Check formulas
            elif element_type == "formula":
                formula_name = element.get("name", "")
                formula_content = element.get("content", "")
                
                if formula_name in domain_formulas:
                    formula_accuracy = self._formula_similarity(
                        formula_content, domain_formulas[formula_name])
                    accuracy_scores.append(formula_accuracy)
        
        # If no factual elements were checked, use Bayesian likelihood as fallback
        if not accuracy_scores:
            return bayesian_metrics.get("likelihood", 0.5)
        
        # Calculate overall accuracy score
        accuracy_score = sum(accuracy_scores) / len(accuracy_scores)
        
        # Apply threshold to determine if accuracy is sufficient
        return accuracy_score
    
    def _assess_completeness(self, solution: Dict[str, Any], domain_knowledge: Dict[str, Any],
                           query_intent: Dict[str, Any]) -> float:
        """
        Assess the completeness of the solution.
        
        This measures how thoroughly the solution covers the required information.
        
        Args:
            solution: The generated solution
            domain_knowledge: Domain knowledge used to generate the solution
            query_intent: The semantic intent of the user's query
            
        Returns:
            Completeness score between 0 and 1
        """
        # Extract solution content and required components from query intent
        solution_content = solution.get("content", {})
        solution_elements = solution_content.get("elements", [])
        required_metrics = query_intent.get("required_metrics", [])
        
        if not solution_elements:
            return 0.0  # No solution elements means incomplete
        
        # If no specific metrics are required, check coverage of key domain concepts
        if not required_metrics:
            domain_elements = domain_knowledge.get("elements", [])
            key_concepts = [elem.get("concept") for elem in domain_elements 
                           if elem.get("importance", 0) > 0.7]
            
            if not key_concepts:
                return 0.5  # Default with insufficient data
            
            # Check coverage of key concepts in solution
            concepts_covered = 0
            for concept in key_concepts:
                if any(concept.lower() in elem.get("content", "").lower() 
                      for elem in solution_elements if concept):
                    concepts_covered += 1
            
            completeness_score = concepts_covered / len(key_concepts) if key_concepts else 0.5
        
        # If specific metrics are required, check if they're present
        else:
            metrics_covered = 0
            for metric in required_metrics:
                if any(metric.lower() in elem.get("content", "").lower() 
                      for elem in solution_elements):
                    metrics_covered += 1
            
            completeness_score = metrics_covered / len(required_metrics) if required_metrics else 0.5
        
        return completeness_score
    
    def _assess_consistency(self, solution: Dict[str, Any]) -> float:
        """
        Assess the internal consistency of the solution.
        
        This measures the logical coherence and absence of contradictions.
        
        Args:
            solution: The generated solution
            
        Returns:
            Consistency score between 0 and 1
        """
        # Extract solution content and structure
        solution_content = solution.get("content", {})
        solution_elements = solution_content.get("elements", [])
        solution_sections = solution_content.get("sections", [])
        
        if not solution_elements:
            return 0.5  # Default with insufficient data
        
        # Simple structural consistency check: are elements organized in sections?
        if solution_sections:
            # Check if all referenced element_ids exist in elements
            element_ids = [elem.get("id") for elem in solution_elements if elem.get("id")]
            referenced_ids = []
            
            for section in solution_sections:
                section_element_ids = section.get("element_ids", [])
                referenced_ids.extend(section_element_ids)
            
            # Calculate structural consistency based on valid references
            valid_references = sum(1 for ref_id in referenced_ids if ref_id in element_ids)
            structural_consistency = valid_references / len(referenced_ids) if referenced_ids else 0.0
        else:
            structural_consistency = 0.5  # No sections means basic structure
        
        # Check for logical consistency between factual elements
        fact_elements = [elem for elem in solution_elements 
                        if elem.get("type") in ["fact", "assertion", "calculation"]]
        
        # Simple consistency estimation based on element types and ordering
        if len(fact_elements) > 1:
            # Check if calculations follow facts (a simple heuristic)
            logical_order = True
            fact_positions = [i for i, elem in enumerate(solution_elements) 
                             if elem.get("type") == "fact"]
            calc_positions = [i for i, elem in enumerate(solution_elements) 
                             if elem.get("type") == "calculation"]
            
            if fact_positions and calc_positions:
                logical_order = min(calc_positions) > min(fact_positions)
            
            logical_consistency = 0.8 if logical_order else 0.5
        else:
            logical_consistency = 0.7  # Few elements, so reasonable consistency
        
        # Combine structural and logical consistency
        consistency_score = (structural_consistency + logical_consistency) / 2
        
        return consistency_score
    
    def _assess_relevance(self, solution: Dict[str, Any], query_intent: Dict[str, Any],
                        bayesian_metrics: Dict[str, float]) -> float:
        """
        Assess the relevance of the solution to the user's query.
        
        This measures how well the solution addresses the specific query intent.
        
        Args:
            solution: The generated solution
            query_intent: The semantic intent of the user's query
            bayesian_metrics: Metrics from Bayesian evaluation
            
        Returns:
            Relevance score between 0 and 1
        """
        # Use mutual information from Bayesian metrics as a strong signal
        mutual_information = bayesian_metrics.get("mutual_information", 0.0)
        
        # Extract query intent components and solution elements
        intent_components = query_intent.get("components", {})
        solution_elements = solution.get("content", {}).get("elements", [])
        
        if not intent_components or not solution_elements:
            return mutual_information  # Default to mutual information with insufficient data
        
        # Extract query intent terms and priorities
        intent_terms = []
        for component in intent_components.values():
            intent_terms.extend(component.get("key_terms", []))
        
        if not intent_terms:
            return mutual_information
        
        # Count solution elements directly addressing intent terms
        relevant_elements = 0
        for element in solution_elements:
            element_content = element.get("content", "").lower()
            if any(term.lower() in element_content for term in intent_terms):
                relevant_elements += 1
        
        # Calculate direct relevance ratio
        direct_relevance = relevant_elements / len(solution_elements) if solution_elements else 0.0
        
        # Calculate focused relevance: how concentrated the solution is on the query
        focused_relevance = (relevant_elements / len(intent_terms)) if intent_terms else 0.0
        focused_relevance = min(1.0, focused_relevance)  # Cap at 1.0
        
        # Combine direct relevance, focused relevance, and mutual information
        relevance_score = (direct_relevance * 0.3) + (focused_relevance * 0.3) + (mutual_information * 0.4)
        
        return relevance_score
    
    def _assess_novelty(self, solution: Dict[str, Any], domain_knowledge: Dict[str, Any]) -> float:
        """
        Assess the novelty of the solution.
        
        This measures the presence of non-obvious insights or connections.
        
        Args:
            solution: The generated solution
            domain_knowledge: Domain knowledge used to generate the solution
            
        Returns:
            Novelty score between 0 and 1
        """
        # Extract solution insights and domain knowledge
        solution_insights = solution.get("insights", [])
        solution_elements = solution.get("content", {}).get("elements", [])
        domain_elements = domain_knowledge.get("elements", [])
        
        if not solution_elements:
            return 0.0  # No elements means no novelty
        
        # Check for explicit insights
        if solution_insights:
            # Explicit insights are a strong indicator of novelty
            insight_ratio = min(1.0, len(solution_insights) / 5)  # Cap at 1.0, normalize to 5 insights
            explicit_novelty = insight_ratio * 0.7  # Weight of explicit insights
        else:
            explicit_novelty = 0.0
        
        # Check for connections between domain elements
        if domain_elements:
            # Look for elements that connect multiple domain concepts
            connection_elements = 0
            
            # Extract domain concepts
            domain_concepts = [elem.get("concept") for elem in domain_elements if elem.get("concept")]
            
            for element in solution_elements:
                element_content = element.get("content", "").lower()
                concepts_connected = sum(1 for concept in domain_concepts 
                                        if concept and concept.lower() in element_content)
                
                # If element connects multiple concepts, count it as a connection
                if concepts_connected >= 2:
                    connection_elements += 1
            
            # Calculate connection ratio
            connection_ratio = min(1.0, connection_elements / max(1, len(solution_elements) / 4))
            connection_novelty = connection_ratio * 0.3  # Weight of concept connections
        else:
            connection_novelty = 0.0
        
        # Combine novelty indicators
        novelty_score = explicit_novelty + connection_novelty
        
        # Apply threshold to determine if novelty is significant
        return novelty_score if novelty_score > self.novelty_threshold else 0.0
    
    def _fact_similarity(self, fact1: str, fact2: str) -> float:
        """
        Calculate a simple similarity score between two factual statements.
        
        Args:
            fact1: First fact string
            fact2: Second fact string
            
        Returns:
            Similarity score between 0 and 1
        """
        # Simple keyword-based similarity
        # In a production system, this would use advanced NLP techniques
        
        # Convert to lowercase and split into words
        words1 = set(fact1.lower().split())
        words2 = set(fact2.lower().split())
        
        # Calculate Jaccard similarity (intersection over union)
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _formula_similarity(self, formula1: str, formula2: str) -> float:
        """
        Calculate similarity between two mathematical formulas.
        
        Args:
            formula1: First formula string
            formula2: Second formula string
            
        Returns:
            Similarity score between 0 and 1
        """
        # In a production system, this would use specialized formula comparison
        # For now, use simple character-level matching after normalization
        
        # Normalize by removing spaces and converting to lowercase
        norm1 = formula1.replace(" ", "").lower()
        norm2 = formula2.replace(" ", "").lower()
        
        # Check exact match
        if norm1 == norm2:
            return 1.0
        
        # Calculate string edit distance similarity
        # Using simple overlap method for demonstration
        if len(norm1) > len(norm2):
            norm1, norm2 = norm2, norm1  # Ensure norm1 is shorter
            
        # Calculate overlap coefficient
        matches = sum(1 for i in range(len(norm1)) if i < len(norm2) and norm1[i] == norm2[i])
        similarity = matches / len(norm1) if len(norm1) > 0 else 0.0
        
        return similarity 