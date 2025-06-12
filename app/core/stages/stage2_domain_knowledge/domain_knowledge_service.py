"""
Domain Knowledge Service

This service orchestrates the domain knowledge extraction process, working with
various components to extract, validate, and prioritize domain-specific knowledge.
"""

import logging
from typing import Dict, Any, List, Optional

from app.core.stages.stage2_domain_knowledge.knowledge_extractor import KnowledgeExtractor
from app.core.stages.stage2_domain_knowledge.knowledge_prioritizer import KnowledgePrioritizer
from app.core.stages.stage2_domain_knowledge.knowledge_validator import KnowledgeValidator
from app.core.stages.stage2_domain_knowledge.llm_connector import LLMConnector

class DomainKnowledgeService:
    """
    Main service for the Domain Knowledge Extraction stage.
    
    This class coordinates the extraction, validation, and prioritization of
    domain-specific knowledge from expert language models and other sources.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Domain Knowledge Service.
        
        Args:
            config: Configuration dictionary for the service and its components
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Initialize components
        self.llm_connector = LLMConnector(self.config.get("llm_connector", {}))
        self.knowledge_extractor = KnowledgeExtractor(
            self.llm_connector,
            self.config.get("knowledge_extractor", {})
        )
        self.knowledge_validator = KnowledgeValidator(self.config.get("knowledge_validator", {}))
        self.knowledge_prioritizer = KnowledgePrioritizer(self.config.get("knowledge_prioritizer", {}))
        
        self.logger.info("Domain Knowledge Service initialized")
    
    async def process(self, semantic_representation: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the semantic representation to extract domain knowledge.
        
        Args:
            semantic_representation: Structured output from the Semantic ATDB stage
            context: Context data from the orchestrator
            
        Returns:
            Structured domain knowledge with confidence levels and relationships
        """
        self.logger.info("Starting domain knowledge extraction process with dual-model querying")
        
        # Step 1: Analyze semantic representation to determine required domains
        required_domains = self._determine_required_domains(semantic_representation)
        self.logger.info(f"Required domains identified: {required_domains}")
        
        # Step 2: Extract knowledge from both primary and secondary domain experts
        # This enables querying from two different base extreme domain LLMs
        raw_knowledge = {}
        
        # Extract from primary domain expert
        for domain in required_domains:
            primary_knowledge = await self.knowledge_extractor.extract_knowledge(
                domain, 
                semantic_representation, 
                context,
                model_preference="primary"  # Use primary sprint expert
            )
            raw_knowledge[f"{domain}_primary"] = primary_knowledge
        
        # Extract from secondary domain expert for complementary insights
        for domain in required_domains:
            if domain in ["sprint", "biomechanics", "athletic_performance"]:  # Only for sprint-related domains
                secondary_knowledge = await self.knowledge_extractor.extract_knowledge(
                    domain, 
                    semantic_representation, 
                    context,
                    model_preference="secondary"  # Use secondary distilled expert
                )
                raw_knowledge[f"{domain}_secondary"] = secondary_knowledge
        
        self.logger.info(f"Extracted knowledge from {len(raw_knowledge)} domain experts")
        
        # Step 3: Validate the extracted knowledge
        validated_knowledge = await self.knowledge_validator.validate(raw_knowledge, context)
        
        # Step 4: Prioritize knowledge elements by relevance (includes multi-model fusion)
        prioritized_knowledge = await self.knowledge_prioritizer.prioritize(
            validated_knowledge, 
            semantic_representation,
            enable_multi_model_fusion=True  # Enable fusion of insights from multiple experts
        )
        
        # Step 5: Structure the knowledge with relationships and dependencies
        structured_knowledge = self._structure_knowledge(prioritized_knowledge)
        
        # Step 6: Add metadata and confidence metrics
        result = {
            "domain_knowledge": structured_knowledge,
            "metadata": {
                "domains": required_domains,
                "models_used": self._get_models_used(raw_knowledge),
                "extraction_metrics": self._calculate_extraction_metrics(structured_knowledge),
                "confidence_summary": self._summarize_confidence(structured_knowledge),
                "dual_model_insights": self._analyze_dual_model_insights(raw_knowledge)
            }
        }
        
        self.logger.info("Domain knowledge extraction completed successfully with dual-model insights")
        return result
    
    def _determine_required_domains(self, semantic_representation: Dict[str, Any]) -> List[str]:
        """
        Analyze the semantic representation to determine which domains 
        are required for knowledge extraction.
        
        Args:
            semantic_representation: Structured semantic analysis
            
        Returns:
            List of domain identifiers required for the query
        """
        domains = []
        
        # Extract domain indicators from the semantic representation
        if "domain_indicators" in semantic_representation:
            domains.extend(semantic_representation["domain_indicators"])
        
        # Extract domains from intent classification
        if "intent" in semantic_representation:
            intent = semantic_representation["intent"]
            if "medical" in intent.lower():
                domains.append("medical")
            if "financial" in intent.lower():
                domains.append("financial")
            if "technical" in intent.lower():
                domains.append("technical")
            if "scientific" in intent.lower():
                domains.append("scientific")
        
        # Extract domains from query parameters
        if "parameters" in semantic_representation:
            params = semantic_representation["parameters"]
            # Add domain detection logic based on parameters
            # This is a simplified example - real implementation would be more sophisticated
            for param, value in params.items():
                if param == "blood_pressure" or param == "heart_rate":
                    if "medical" not in domains:
                        domains.append("medical")
                if param == "investment" or param == "returns":
                    if "financial" not in domains:
                        domains.append("financial")
        
        # If no domains detected, default to general knowledge
        if not domains:
            domains.append("general")
            
        return list(set(domains))  # Remove duplicates
    
    def _structure_knowledge(self, prioritized_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """
        Structure the knowledge elements with their relationships and dependencies.
        
        Args:
            prioritized_knowledge: Prioritized knowledge elements
            
        Returns:
            Structured knowledge ready for downstream stages
        """
        structured = {
            "elements": prioritized_knowledge["elements"],
            "relationships": {},
            "formulas": [],
            "constraints": [],
            "reference_values": {}
        }
        
        # Extract relationships between elements
        for element in prioritized_knowledge["elements"]:
            if "dependencies" in element:
                elem_id = element["id"]
                structured["relationships"][elem_id] = element["dependencies"]
        
        # Extract formulas
        for element in prioritized_knowledge["elements"]:
            if "formulas" in element:
                for formula in element["formulas"]:
                    structured["formulas"].append({
                        "formula": formula["expression"],
                        "description": formula.get("description", ""),
                        "variables": formula.get("variables", {}),
                        "source_element": element["id"],
                        "confidence": formula.get("confidence", 0.0)
                    })
        
        # Extract constraints
        for element in prioritized_knowledge["elements"]:
            if "constraints" in element:
                for constraint in element["constraints"]:
                    structured["constraints"].append({
                        "constraint": constraint["expression"],
                        "description": constraint.get("description", ""),
                        "source_element": element["id"],
                        "confidence": constraint.get("confidence", 0.0)
                    })
        
        # Extract reference values
        for element in prioritized_knowledge["elements"]:
            if "reference_values" in element:
                for param, value in element["reference_values"].items():
                    if param not in structured["reference_values"]:
                        structured["reference_values"][param] = []
                    structured["reference_values"][param].append({
                        "value": value["value"],
                        "description": value.get("description", ""),
                        "source_element": element["id"],
                        "confidence": value.get("confidence", 0.0)
                    })
        
        return structured
    
    def _calculate_extraction_metrics(self, structured_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate metrics about the knowledge extraction process.
        
        Args:
            structured_knowledge: The structured knowledge
            
        Returns:
            Dictionary of extraction metrics
        """
        elements_count = len(structured_knowledge["elements"])
        formulas_count = len(structured_knowledge["formulas"])
        constraints_count = len(structured_knowledge["constraints"])
        
        # Calculate average confidence
        confidences = []
        for element in structured_knowledge["elements"]:
            if "confidence" in element:
                confidences.append(element["confidence"])
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            "elements_count": elements_count,
            "formulas_count": formulas_count,
            "constraints_count": constraints_count,
            "average_confidence": avg_confidence
        }
    
    def _summarize_confidence(self, structured_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """
        Summarize confidence levels across knowledge elements.
        
        Args:
            structured_knowledge: The structured knowledge
            
        Returns:
            Summary of confidence metrics
        """
        # Extract confidence values from elements
        element_confidences = [
            element.get("confidence", 0.0) 
            for element in structured_knowledge["elements"]
        ]
        
        # Extract confidence values from formulas
        formula_confidences = [
            formula.get("confidence", 0.0) 
            for formula in structured_knowledge["formulas"]
        ]
        
        # Extract confidence values from constraints
        constraint_confidences = [
            constraint.get("confidence", 0.0) 
            for constraint in structured_knowledge["constraints"]
        ]
        
        # Calculate aggregate metrics
        all_confidences = element_confidences + formula_confidences + constraint_confidences
        
        return {
            "min_confidence": min(all_confidences) if all_confidences else 0.0,
            "max_confidence": max(all_confidences) if all_confidences else 0.0,
            "avg_confidence": sum(all_confidences) / len(all_confidences) if all_confidences else 0.0,
            "elements_below_threshold": sum(1 for c in element_confidences if c < 0.7),
            "formulas_below_threshold": sum(1 for c in formula_confidences if c < 0.7),
            "constraints_below_threshold": sum(1 for c in constraint_confidences if c < 0.7)
        }
    
    def _get_models_used(self, raw_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about which models were used for knowledge extraction."""
        models_used = {
            "primary_experts": [],
            "secondary_experts": [],
            "total_models": 0
        }
        
        for domain_key, knowledge in raw_knowledge.items():
            if knowledge and "metadata" in knowledge:
                model_info = {
                    "domain": domain_key,
                    "model_id": knowledge["metadata"].get("model_id"),
                    "specialization": knowledge["metadata"].get("specialization"),
                    "role": knowledge["metadata"].get("role", "primary")
                }
                
                if "secondary" in domain_key or knowledge["metadata"].get("role") == "complementary_expert":
                    models_used["secondary_experts"].append(model_info)
                else:
                    models_used["primary_experts"].append(model_info)
                
                models_used["total_models"] += 1
        
        return models_used
    
    def _analyze_dual_model_insights(self, raw_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze insights from dual-model extraction."""
        analysis = {
            "complementary_insights": [],
            "consensus_areas": [],
            "divergent_perspectives": [],
            "confidence_comparison": {}
        }
        
        # Group primary and secondary insights by domain
        domain_groups = {}
        for domain_key, knowledge in raw_knowledge.items():
            if "_primary" in domain_key:
                base_domain = domain_key.replace("_primary", "")
                if base_domain not in domain_groups:
                    domain_groups[base_domain] = {}
                domain_groups[base_domain]["primary"] = knowledge
            elif "_secondary" in domain_key:
                base_domain = domain_key.replace("_secondary", "")
                if base_domain not in domain_groups:
                    domain_groups[base_domain] = {}
                domain_groups[base_domain]["secondary"] = knowledge
        
        # Compare insights between primary and secondary models
        for domain, models in domain_groups.items():
            if "primary" in models and "secondary" in models:
                primary_knowledge = models["primary"]
                secondary_knowledge = models["secondary"]
                
                # Compare confidence levels
                primary_confidence = primary_knowledge.get("confidence", 0.0)
                secondary_confidence = secondary_knowledge.get("confidence", 0.0)
                
                analysis["confidence_comparison"][domain] = {
                    "primary": primary_confidence,
                    "secondary": secondary_confidence,
                    "difference": abs(primary_confidence - secondary_confidence)
                }
                
                # Identify complementary insights (unique to secondary model)
                if "elements" in secondary_knowledge:
                    for element in secondary_knowledge["elements"]:
                        if element.get("category") == "biomechanics" or "advanced" in element.get("type", ""):
                            analysis["complementary_insights"].append({
                                "domain": domain,
                                "insight": element.get("content"),
                                "confidence": element.get("confidence", 0.0),
                                "type": element.get("type")
                            })
        
        return analysis 