"""
Knowledge Validator

This module contains the KnowledgeValidator class, which is responsible for
validating and verifying extracted knowledge for consistency and quality.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple

class KnowledgeValidator:
    """
    Validates and verifies extracted knowledge.
    
    This class implements techniques for checking consistency across knowledge elements,
    identifying contradictions, and assessing source reliability.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Knowledge Validator.
        
        Args:
            config: Configuration dictionary for validation parameters
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Validation thresholds
        self.confidence_threshold = self.config.get("confidence_threshold", 0.5)
        self.consistency_threshold = self.config.get("consistency_threshold", 0.7)
        
        self.logger.info("Knowledge Validator initialized")
    
    async def validate(self, raw_knowledge: Dict[str, Dict[str, Any]], 
                      context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Validate the extracted knowledge across domains.
        
        Args:
            raw_knowledge: Raw extracted knowledge organized by domain
            context: Context data from the orchestrator
            
        Returns:
            Validated knowledge
        """
        self.logger.info("Starting knowledge validation process")
        
        validated_knowledge = {}
        
        # Process each domain separately first
        for domain, domain_knowledge in raw_knowledge.items():
            self.logger.info(f"Validating knowledge for domain: {domain}")
            
            # Perform intra-domain validation
            validated_domain = await self._validate_domain(domain, domain_knowledge)
            validated_knowledge[domain] = validated_domain
        
        # Perform cross-domain validation and conflict resolution
        validated_knowledge = await self._cross_domain_validation(validated_knowledge)
        
        self.logger.info("Knowledge validation completed")
        return validated_knowledge
    
    async def _validate_domain(self, domain: str, 
                              domain_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate knowledge within a single domain.
        
        Args:
            domain: Domain identifier
            domain_knowledge: Knowledge extracted for the domain
            
        Returns:
            Validated domain knowledge
        """
        # Copy the knowledge to avoid modifying the original
        validated = {k: v for k, v in domain_knowledge.items()}
        
        # If the domain knowledge doesn't have elements, return as is
        if "elements" not in validated:
            self.logger.warning(f"No elements found in domain {domain}")
            validated["elements"] = []
            return validated
        
        validated_elements = []
        for element in validated["elements"]:
            # Filter out elements with confidence below threshold
            if "confidence" in element and element["confidence"] < self.confidence_threshold:
                self.logger.debug(f"Filtered out low-confidence element: {element.get('id', 'unknown')}")
                continue
            
            # Validate formulas if present
            if "formulas" in element:
                valid_formulas = self._validate_formulas(element["formulas"])
                element["formulas"] = valid_formulas
            
            # Validate constraints if present
            if "constraints" in element:
                valid_constraints = self._validate_constraints(element["constraints"])
                element["constraints"] = valid_constraints
            
            # Validate reference values if present
            if "reference_values" in element:
                valid_refs = self._validate_reference_values(element["reference_values"])
                element["reference_values"] = valid_refs
            
            # Add validation metadata
            element["validation"] = {
                "is_validated": True,
                "validation_timestamp": context.get("timestamp", "unknown")
            }
            
            validated_elements.append(element)
        
        validated["elements"] = validated_elements
        
        # Check intra-domain consistency
        consistency_issues = self._check_intra_domain_consistency(validated_elements)
        
        # Add validation metadata to the domain
        validated["validation_metadata"] = {
            "elements_count": len(validated_elements),
            "filtered_elements": len(domain_knowledge.get("elements", [])) - len(validated_elements),
            "consistency_issues": consistency_issues,
            "validation_level": "intra-domain"
        }
        
        return validated
    
    def _validate_formulas(self, formulas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate formulas for basic correctness.
        
        Args:
            formulas: List of formula dictionaries
            
        Returns:
            List of validated formulas
        """
        valid_formulas = []
        
        for formula in formulas:
            # Basic validation checks
            if "expression" not in formula:
                continue
            
            # Add to validated list
            valid_formulas.append(formula)
        
        return valid_formulas
    
    def _validate_constraints(self, constraints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate constraints for basic correctness.
        
        Args:
            constraints: List of constraint dictionaries
            
        Returns:
            List of validated constraints
        """
        valid_constraints = []
        
        for constraint in constraints:
            # Basic validation checks
            if "expression" not in constraint:
                continue
            
            # Add to validated list
            valid_constraints.append(constraint)
        
        return valid_constraints
    
    def _validate_reference_values(self, reference_values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate reference values for basic correctness.
        
        Args:
            reference_values: Dictionary of reference values
            
        Returns:
            Dictionary of validated reference values
        """
        valid_refs = {}
        
        for key, value in reference_values.items():
            # Basic validation checks
            if not isinstance(value, dict) or "value" not in value:
                continue
            
            # Add to validated dictionary
            valid_refs[key] = value
        
        return valid_refs
    
    def _check_intra_domain_consistency(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Check for consistency issues within a single domain's elements.
        
        Args:
            elements: List of knowledge elements
            
        Returns:
            List of consistency issues
        """
        consistency_issues = []
        
        # Build lookup maps for faster access
        element_by_id = {elem["id"]: elem for elem in elements if "id" in elem}
        
        # Check formula consistency
        formula_expressions = {}
        for element in elements:
            for formula in element.get("formulas", []):
                if "expression" not in formula:
                    continue
                
                expr = formula["expression"]
                if expr in formula_expressions:
                    # Same formula exists in multiple elements, check for consistency
                    prev_element = formula_expressions[expr]
                    prev_variables = prev_element.get("variables", {})
                    curr_variables = formula.get("variables", {})
                    
                    # Check if variable definitions are consistent
                    for var_name, var_def in curr_variables.items():
                        if var_name in prev_variables and prev_variables[var_name] != var_def:
                            consistency_issues.append({
                                "type": "formula_variable_inconsistency",
                                "elements": [element["id"], formula_expressions[expr]["element_id"]],
                                "formula": expr,
                                "variable": var_name,
                                "definitions": [prev_variables[var_name], var_def]
                            })
                else:
                    # Record this formula
                    formula_expressions[expr] = {
                        "element_id": element["id"],
                        "variables": formula.get("variables", {})
                    }
        
        # Check reference value consistency
        reference_values = {}
        for element in elements:
            for ref_key, ref_value in element.get("reference_values", {}).items():
                if "value" not in ref_value:
                    continue
                
                if ref_key in reference_values:
                    # Same reference key exists in multiple elements, check for consistency
                    prev_value = reference_values[ref_key]["value"]
                    curr_value = ref_value["value"]
                    
                    # Simple string comparison (in a real system, this would be more sophisticated)
                    if prev_value != curr_value:
                        consistency_issues.append({
                            "type": "reference_value_inconsistency",
                            "elements": [element["id"], reference_values[ref_key]["element_id"]],
                            "reference_key": ref_key,
                            "values": [prev_value, curr_value]
                        })
                else:
                    # Record this reference value
                    reference_values[ref_key] = {
                        "element_id": element["id"],
                        "value": ref_value["value"]
                    }
        
        return consistency_issues
    
    async def _cross_domain_validation(self, validated_knowledge: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Perform validation across multiple domains and resolve conflicts.
        
        Args:
            validated_knowledge: Knowledge validated within each domain
            
        Returns:
            Cross-domain validated knowledge
        """
        self.logger.info("Performing cross-domain validation")
        
        # Copy the validated knowledge to avoid modifying the original
        cross_validated = {k: v for k, v in validated_knowledge.items()}
        
        # Build a unified view of all elements across domains
        all_elements = {}
        for domain, domain_knowledge in validated_knowledge.items():
            for element in domain_knowledge.get("elements", []):
                if "id" in element:
                    element_id = element["id"]
                    if element_id in all_elements:
                        # Element ID conflict across domains
                        all_elements[element_id]["domains"].append(domain)
                        all_elements[element_id]["elements"].append(element)
                    else:
                        all_elements[element_id] = {
                            "domains": [domain],
                            "elements": [element]
                        }
        
        # Check for cross-domain conflicts
        cross_domain_issues = []
        for element_id, element_data in all_elements.items():
            if len(element_data["domains"]) > 1:
                # Element exists in multiple domains, check for consistency
                issues = self._check_cross_domain_element_consistency(
                    element_id, element_data["elements"], element_data["domains"]
                )
                cross_domain_issues.extend(issues)
                
                # Resolve conflicts if necessary
                if issues:
                    self._resolve_cross_domain_conflicts(
                        element_id, element_data["elements"], element_data["domains"], cross_validated
                    )
        
        # Add cross-domain validation metadata to each domain
        for domain, domain_knowledge in cross_validated.items():
            if "validation_metadata" not in domain_knowledge:
                domain_knowledge["validation_metadata"] = {}
            
            domain_knowledge["validation_metadata"]["cross_domain_issues"] = [
                issue for issue in cross_domain_issues 
                if domain in issue.get("domains", [])
            ]
            domain_knowledge["validation_metadata"]["validation_level"] = "cross-domain"
        
        return cross_validated
    
    def _check_cross_domain_element_consistency(self, element_id: str, 
                                              elements: List[Dict[str, Any]],
                                              domains: List[str]) -> List[Dict[str, Any]]:
        """
        Check for consistency issues in an element that exists across multiple domains.
        
        Args:
            element_id: Element identifier
            elements: List of element instances from different domains
            domains: List of domains where the element exists
            
        Returns:
            List of cross-domain consistency issues
        """
        issues = []
        
        # Compare the first element with all others
        reference = elements[0]
        
        for i, element in enumerate(elements[1:], 1):
            # Check description consistency
            if "description" in reference and "description" in element:
                if reference["description"] != element["description"]:
                    issues.append({
                        "type": "description_inconsistency",
                        "element_id": element_id,
                        "domains": [domains[0], domains[i]],
                        "descriptions": [reference["description"], element["description"]]
                    })
            
            # Check formula consistency
            ref_formulas = {f.get("expression"): f for f in reference.get("formulas", []) if "expression" in f}
            elem_formulas = {f.get("expression"): f for f in element.get("formulas", []) if "expression" in f}
            
            for expr, ref_formula in ref_formulas.items():
                if expr in elem_formulas:
                    # Same formula exists in both elements, check for consistency in variables
                    elem_formula = elem_formulas[expr]
                    ref_vars = ref_formula.get("variables", {})
                    elem_vars = elem_formula.get("variables", {})
                    
                    for var_name, ref_def in ref_vars.items():
                        if var_name in elem_vars and elem_vars[var_name] != ref_def:
                            issues.append({
                                "type": "formula_variable_inconsistency",
                                "element_id": element_id,
                                "domains": [domains[0], domains[i]],
                                "formula": expr,
                                "variable": var_name,
                                "definitions": [ref_def, elem_vars[var_name]]
                            })
            
            # Check reference value consistency
            ref_values = reference.get("reference_values", {})
            elem_values = element.get("reference_values", {})
            
            for key, ref_value in ref_values.items():
                if key in elem_values:
                    # Same reference key exists in both elements, check for consistency
                    if isinstance(ref_value, dict) and isinstance(elem_values[key], dict):
                        if "value" in ref_value and "value" in elem_values[key]:
                            if ref_value["value"] != elem_values[key]["value"]:
                                issues.append({
                                    "type": "reference_value_inconsistency",
                                    "element_id": element_id,
                                    "domains": [domains[0], domains[i]],
                                    "reference_key": key,
                                    "values": [ref_value["value"], elem_values[key]["value"]]
                                })
        
        return issues
    
    def _resolve_cross_domain_conflicts(self, element_id: str, 
                                      elements: List[Dict[str, Any]],
                                      domains: List[str],
                                      validated_knowledge: Dict[str, Dict[str, Any]]) -> None:
        """
        Resolve conflicts in an element that exists across multiple domains.
        
        Args:
            element_id: Element identifier
            elements: List of element instances from different domains
            domains: List of domains where the element exists
            validated_knowledge: Knowledge dictionary to update
        """
        # Simple resolution strategy: take the element with highest confidence
        best_element_index = 0
        best_confidence = elements[0].get("confidence", 0.0)
        
        for i, element in enumerate(elements[1:], 1):
            confidence = element.get("confidence", 0.0)
            if confidence > best_confidence:
                best_confidence = confidence
                best_element_index = i
        
        best_domain = domains[best_element_index]
        best_element = elements[best_element_index]
        
        # Add a resolution note to the selected element
        if "validation" not in best_element:
            best_element["validation"] = {}
        
        best_element["validation"]["cross_domain_resolution"] = {
            "selected_from_domain": best_domain,
            "competing_domains": [d for d in domains if d != best_domain],
            "selection_reason": "highest_confidence"
        }
        
        # Update each domain's elements with the resolved element
        for domain in domains:
            if domain == best_domain:
                continue  # Skip the domain with the best element
                
            # Find the element in this domain's elements list
            domain_elements = validated_knowledge[domain].get("elements", [])
            for i, element in enumerate(domain_elements):
                if element.get("id") == element_id:
                    # Replace with the best element but mark as imported
                    resolved_element = best_element.copy()
                    if "validation" not in resolved_element:
                        resolved_element["validation"] = {}
                    resolved_element["validation"]["imported_from_domain"] = best_domain
                    domain_elements[i] = resolved_element
                    break
            
            validated_knowledge[domain]["elements"] = domain_elements 