"""
Knowledge Extractor

This module contains the KnowledgeExtractor class, which is responsible for
extracting domain-specific knowledge using LLMs and other knowledge sources.
"""

import logging
from typing import Dict, Any, List, Optional

from app.core.stages.stage2_domain_knowledge.llm_connector import LLMConnector

class KnowledgeExtractor:
    """
    Extracts domain-specific knowledge using specialized language models and knowledge bases.
    
    This class implements techniques for identifying formulas, constraints, relationships,
    and reference values within specific domains.
    """
    
    def __init__(self, llm_connector: LLMConnector, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Knowledge Extractor.
        
        Args:
            llm_connector: Connector for accessing domain-expert language models
            config: Configuration dictionary for extraction parameters
        """
        self.logger = logging.getLogger(__name__)
        self.llm_connector = llm_connector
        self.config = config or {}
        
        # Domain-specific extraction strategies
        self.extraction_strategies = {
            "medical": self._extract_medical_knowledge,
            "financial": self._extract_financial_knowledge,
            "technical": self._extract_technical_knowledge,
            "scientific": self._extract_scientific_knowledge,
            "general": self._extract_general_knowledge
        }
        
        self.logger.info("Knowledge Extractor initialized")
    
    async def extract_knowledge(self, domain: str, semantic_representation: Dict[str, Any], 
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract domain-specific knowledge based on the semantic representation.
        
        Args:
            domain: The knowledge domain to extract from
            semantic_representation: The semantic representation from the previous stage
            context: Context data from the orchestrator
            
        Returns:
            Extracted knowledge for the specified domain
        """
        self.logger.info(f"Extracting knowledge for domain: {domain}")
        
        # Select the appropriate extraction strategy
        if domain in self.extraction_strategies:
            extraction_func = self.extraction_strategies[domain]
        else:
            self.logger.warning(f"No specific extraction strategy for domain {domain}, using general strategy")
            extraction_func = self._extract_general_knowledge
        
        # Extract knowledge using the selected strategy
        domain_knowledge = await extraction_func(semantic_representation, context)
        
        # Extract common elements across all domains
        common_elements = await self._extract_common_elements(domain, semantic_representation, context)
        
        # Merge domain-specific and common knowledge
        merged_knowledge = self._merge_knowledge(domain_knowledge, common_elements)
        
        # Add metadata
        merged_knowledge["metadata"] = {
            "domain": domain,
            "element_count": len(merged_knowledge["elements"]),
            "extraction_confidence": self._calculate_extraction_confidence(merged_knowledge)
        }
        
        self.logger.info(f"Extracted {len(merged_knowledge['elements'])} knowledge elements for domain {domain}")
        return merged_knowledge
    
    async def _extract_medical_knowledge(self, semantic_representation: Dict[str, Any], 
                                        context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract knowledge specific to the medical domain.
        
        Args:
            semantic_representation: The semantic representation from the previous stage
            context: Context data from the orchestrator
            
        Returns:
            Extracted medical domain knowledge
        """
        # Construct specialized prompt for medical knowledge extraction
        prompt = self._construct_medical_prompt(semantic_representation)
        
        # Get response from medical expert LLM
        response = await self.llm_connector.query_domain_expert(
            "medical", 
            prompt, 
            context.get("model_parameters", {})
        )
        
        # Process and structure the response
        structured_knowledge = self._structure_medical_knowledge(response)
        
        return {
            "elements": structured_knowledge["elements"],
            "domain_specific": {
                "medical_standards": structured_knowledge.get("medical_standards", []),
                "clinical_guidelines": structured_knowledge.get("clinical_guidelines", [])
            }
        }
    
    async def _extract_financial_knowledge(self, semantic_representation: Dict[str, Any], 
                                         context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract knowledge specific to the financial domain.
        
        Args:
            semantic_representation: The semantic representation from the previous stage
            context: Context data from the orchestrator
            
        Returns:
            Extracted financial domain knowledge
        """
        # Construct specialized prompt for financial knowledge extraction
        prompt = self._construct_financial_prompt(semantic_representation)
        
        # Get response from financial expert LLM
        response = await self.llm_connector.query_domain_expert(
            "financial", 
            prompt, 
            context.get("model_parameters", {})
        )
        
        # Process and structure the response
        structured_knowledge = self._structure_financial_knowledge(response)
        
        return {
            "elements": structured_knowledge["elements"],
            "domain_specific": {
                "financial_models": structured_knowledge.get("financial_models", []),
                "market_assumptions": structured_knowledge.get("market_assumptions", [])
            }
        }
    
    async def _extract_technical_knowledge(self, semantic_representation: Dict[str, Any], 
                                         context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract knowledge specific to the technical domain.
        
        Args:
            semantic_representation: The semantic representation from the previous stage
            context: Context data from the orchestrator
            
        Returns:
            Extracted technical domain knowledge
        """
        # Construct specialized prompt for technical knowledge extraction
        prompt = self._construct_technical_prompt(semantic_representation)
        
        # Get response from technical expert LLM
        response = await self.llm_connector.query_domain_expert(
            "technical", 
            prompt, 
            context.get("model_parameters", {})
        )
        
        # Process and structure the response
        structured_knowledge = self._structure_technical_knowledge(response)
        
        return {
            "elements": structured_knowledge["elements"],
            "domain_specific": {
                "technical_standards": structured_knowledge.get("technical_standards", []),
                "engineering_principles": structured_knowledge.get("engineering_principles", [])
            }
        }
    
    async def _extract_scientific_knowledge(self, semantic_representation: Dict[str, Any], 
                                          context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract knowledge specific to the scientific domain.
        
        Args:
            semantic_representation: The semantic representation from the previous stage
            context: Context data from the orchestrator
            
        Returns:
            Extracted scientific domain knowledge
        """
        # Construct specialized prompt for scientific knowledge extraction
        prompt = self._construct_scientific_prompt(semantic_representation)
        
        # Get response from scientific expert LLM
        response = await self.llm_connector.query_domain_expert(
            "scientific", 
            prompt, 
            context.get("model_parameters", {})
        )
        
        # Process and structure the response
        structured_knowledge = self._structure_scientific_knowledge(response)
        
        return {
            "elements": structured_knowledge["elements"],
            "domain_specific": {
                "scientific_theories": structured_knowledge.get("scientific_theories", []),
                "empirical_evidence": structured_knowledge.get("empirical_evidence", [])
            }
        }
    
    async def _extract_general_knowledge(self, semantic_representation: Dict[str, Any], 
                                        context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract general knowledge when no specific domain is identified.
        
        Args:
            semantic_representation: The semantic representation from the previous stage
            context: Context data from the orchestrator
            
        Returns:
            Extracted general knowledge
        """
        # Construct general knowledge extraction prompt
        prompt = self._construct_general_prompt(semantic_representation)
        
        # Get response from general knowledge LLM
        response = await self.llm_connector.query_domain_expert(
            "general", 
            prompt, 
            context.get("model_parameters", {})
        )
        
        # Process and structure the response
        structured_knowledge = self._structure_general_knowledge(response)
        
        return {
            "elements": structured_knowledge["elements"],
            "domain_specific": {}
        }
    
    async def _extract_common_elements(self, domain: str, semantic_representation: Dict[str, Any], 
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract common knowledge elements that apply across domains.
        
        Args:
            domain: The primary knowledge domain
            semantic_representation: The semantic representation from the previous stage
            context: Context data from the orchestrator
            
        Returns:
            Common knowledge elements
        """
        # Construct prompt for common elements
        prompt = self._construct_common_elements_prompt(domain, semantic_representation)
        
        # Get response for common elements
        response = await self.llm_connector.query_domain_expert(
            "general", 
            prompt, 
            context.get("model_parameters", {})
        )
        
        # Process and structure the response
        structured_common = self._structure_common_elements(response)
        
        return {
            "elements": structured_common["elements"]
        }
    
    def _merge_knowledge(self, domain_knowledge: Dict[str, Any], 
                         common_elements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge domain-specific knowledge with common knowledge elements.
        
        Args:
            domain_knowledge: Domain-specific knowledge
            common_elements: Common knowledge elements
            
        Returns:
            Merged knowledge
        """
        # Start with domain knowledge
        merged = {
            "elements": domain_knowledge["elements"].copy(),
            "domain_specific": domain_knowledge.get("domain_specific", {})
        }
        
        # Add common elements, avoiding duplicates
        domain_element_ids = [elem["id"] for elem in domain_knowledge["elements"]]
        for common_elem in common_elements["elements"]:
            if common_elem["id"] not in domain_element_ids:
                merged["elements"].append(common_elem)
        
        return merged
    
    def _construct_medical_prompt(self, semantic_representation: Dict[str, Any]) -> str:
        """
        Construct a specialized prompt for medical knowledge extraction.
        
        Args:
            semantic_representation: The semantic representation from the previous stage
            
        Returns:
            Prompt for medical knowledge extraction
        """
        parameters = []
        if "parameters" in semantic_representation:
            for param, value in semantic_representation["parameters"].items():
                parameters.append(f"{param}: {value}")
        
        parameters_str = "\n".join(parameters) if parameters else "No specific parameters identified."
        
        intent = semantic_representation.get("intent", "General medical query")
        
        return f"""
        You are extracting specialized medical knowledge for a query.
        
        QUERY INTENT: {intent}
        
        PARAMETERS:
        {parameters_str}
        
        Extract the following information:
        
        1. Relevant medical formulas and calculations related to the parameters
        2. Medical standards and clinical guidelines applicable to this query
        3. Typical reference ranges for the parameters
        4. Relationships between different parameters
        5. Constraints and limitations in medical interpretation
        
        For each knowledge element, provide:
        - A unique identifier
        - A clear description
        - The confidence level (0.0-1.0)
        - Any formulas with their variables explained
        - Relevant reference values
        - Dependencies on other knowledge elements
        
        Format your response as a properly structured JSON object.
        """
    
    def _structure_medical_knowledge(self, llm_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and structure the medical knowledge from LLM response.
        
        Args:
            llm_response: Response from the medical expert LLM
            
        Returns:
            Structured medical knowledge
        """
        # This is a simplified implementation
        # In a real system, this would include robust parsing and validation
        
        structured = {
            "elements": [],
            "medical_standards": [],
            "clinical_guidelines": []
        }
        
        # Extract knowledge elements
        if "elements" in llm_response:
            structured["elements"] = llm_response["elements"]
        
        # Extract medical standards
        if "medical_standards" in llm_response:
            structured["medical_standards"] = llm_response["medical_standards"]
        
        # Extract clinical guidelines
        if "clinical_guidelines" in llm_response:
            structured["clinical_guidelines"] = llm_response["clinical_guidelines"]
        
        return structured
    
    def _construct_financial_prompt(self, semantic_representation: Dict[str, Any]) -> str:
        """
        Construct a specialized prompt for financial knowledge extraction.
        
        Args:
            semantic_representation: The semantic representation from the previous stage
            
        Returns:
            Prompt for financial knowledge extraction
        """
        # Simplified placeholder implementation
        parameters = []
        if "parameters" in semantic_representation:
            for param, value in semantic_representation["parameters"].items():
                parameters.append(f"{param}: {value}")
        
        parameters_str = "\n".join(parameters) if parameters else "No specific parameters identified."
        
        intent = semantic_representation.get("intent", "General financial query")
        
        return f"""
        You are extracting specialized financial knowledge for a query.
        
        QUERY INTENT: {intent}
        
        PARAMETERS:
        {parameters_str}
        
        Extract the following information:
        
        1. Relevant financial formulas and calculations
        2. Financial models applicable to this query
        3. Market assumptions and typical values
        4. Relationships between different financial parameters
        5. Constraints and limitations in financial modeling
        
        For each knowledge element, provide:
        - A unique identifier
        - A clear description
        - The confidence level (0.0-1.0)
        - Any formulas with their variables explained
        - Relevant reference values
        - Dependencies on other knowledge elements
        
        Format your response as a properly structured JSON object.
        """
    
    def _structure_financial_knowledge(self, llm_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and structure the financial knowledge from LLM response.
        
        Args:
            llm_response: Response from the financial expert LLM
            
        Returns:
            Structured financial knowledge
        """
        # Simplified placeholder implementation
        structured = {
            "elements": [],
            "financial_models": [],
            "market_assumptions": []
        }
        
        # Extract knowledge elements
        if "elements" in llm_response:
            structured["elements"] = llm_response["elements"]
        
        # Extract financial models
        if "financial_models" in llm_response:
            structured["financial_models"] = llm_response["financial_models"]
        
        # Extract market assumptions
        if "market_assumptions" in llm_response:
            structured["market_assumptions"] = llm_response["market_assumptions"]
        
        return structured
    
    def _construct_technical_prompt(self, semantic_representation: Dict[str, Any]) -> str:
        """
        Construct a specialized prompt for technical knowledge extraction.
        
        Args:
            semantic_representation: The semantic representation from the previous stage
            
        Returns:
            Prompt for technical knowledge extraction
        """
        # Simplified placeholder implementation
        return "Technical knowledge extraction prompt - to be implemented"
    
    def _structure_technical_knowledge(self, llm_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and structure the technical knowledge from LLM response.
        
        Args:
            llm_response: Response from the technical expert LLM
            
        Returns:
            Structured technical knowledge
        """
        # Simplified placeholder implementation
        return {
            "elements": llm_response.get("elements", []),
            "technical_standards": llm_response.get("technical_standards", []),
            "engineering_principles": llm_response.get("engineering_principles", [])
        }
    
    def _construct_scientific_prompt(self, semantic_representation: Dict[str, Any]) -> str:
        """
        Construct a specialized prompt for scientific knowledge extraction.
        
        Args:
            semantic_representation: The semantic representation from the previous stage
            
        Returns:
            Prompt for scientific knowledge extraction
        """
        # Simplified placeholder implementation
        return "Scientific knowledge extraction prompt - to be implemented"
    
    def _structure_scientific_knowledge(self, llm_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and structure the scientific knowledge from LLM response.
        
        Args:
            llm_response: Response from the scientific expert LLM
            
        Returns:
            Structured scientific knowledge
        """
        # Simplified placeholder implementation
        return {
            "elements": llm_response.get("elements", []),
            "scientific_theories": llm_response.get("scientific_theories", []),
            "empirical_evidence": llm_response.get("empirical_evidence", [])
        }
    
    def _construct_general_prompt(self, semantic_representation: Dict[str, Any]) -> str:
        """
        Construct a prompt for general knowledge extraction.
        
        Args:
            semantic_representation: The semantic representation from the previous stage
            
        Returns:
            Prompt for general knowledge extraction
        """
        # Simplified placeholder implementation
        return "General knowledge extraction prompt - to be implemented"
    
    def _structure_general_knowledge(self, llm_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and structure the general knowledge from LLM response.
        
        Args:
            llm_response: Response from the general knowledge LLM
            
        Returns:
            Structured general knowledge
        """
        # Simplified placeholder implementation
        return {
            "elements": llm_response.get("elements", [])
        }
    
    def _construct_common_elements_prompt(self, domain: str, semantic_representation: Dict[str, Any]) -> str:
        """
        Construct a prompt for extracting common knowledge elements.
        
        Args:
            domain: The primary knowledge domain
            semantic_representation: The semantic representation from the previous stage
            
        Returns:
            Prompt for common knowledge elements extraction
        """
        # Simplified placeholder implementation
        return f"Common elements extraction prompt for domain {domain} - to be implemented"
    
    def _structure_common_elements(self, llm_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and structure the common knowledge elements from LLM response.
        
        Args:
            llm_response: Response from the LLM
            
        Returns:
            Structured common knowledge elements
        """
        # Simplified placeholder implementation
        return {
            "elements": llm_response.get("elements", [])
        }
    
    def _calculate_extraction_confidence(self, knowledge: Dict[str, Any]) -> float:
        """
        Calculate the overall confidence in the knowledge extraction.
        
        Args:
            knowledge: The extracted knowledge
            
        Returns:
            Confidence score (0.0-1.0)
        """
        # Calculate average confidence from knowledge elements
        confidences = [
            element.get("confidence", 0.0) 
            for element in knowledge["elements"]
        ]
        
        return sum(confidences) / len(confidences) if confidences else 0.0 