import logging
import time
from typing import Dict, List, Optional, Any, Tuple

from app.core import get_model_instance

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Modeler:
    """
    Modeler Component of the RAG System.
    
    This component handles:
    - Entity extraction
    - Relationship mapping
    - Parameter identification
    - Constraint recognition
    - Model integration with domain knowledge
    
    It connects the Query component with the Solver component by transforming
    unstructured queries into structured entity-relationship models.
    """
    
    def __init__(self):
        """Initialize the modeler with access to necessary LLMs."""
        # Get the domain expert LLM
        self.domain_llm = get_model_instance()
        logger.info("Modeler component initialized")
    
    def process_query(self, query_package: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a structured query package and convert it to a comprehensive knowledge model.
        
        Args:
            query_package: The structured query package from the Query component
                containing query text, intent, context, and metadata
                
        Returns:
            A knowledge model with entities, relationships, parameters, and domain context
        """
        logger.info(f"Processing query in modeler: {query_package.get('query', '')[:50]}...")
        start_time = time.time()
        
        # 1. Extract entities and relationships using the primary LLM
        model_components = self._extract_model_components(query_package)
        
        # 2. Enrich with domain knowledge using the domain expert LLM
        enriched_model = self._enrich_with_domain_knowledge(model_components, query_package)
        
        # 3. Integrate components into a unified model
        knowledge_model = self._integrate_model_components(enriched_model)
        
        # Add metadata
        processing_time = time.time() - start_time
        knowledge_model["metadata"] = {
            "processing_time": processing_time,
            "component": "modeler",
            "query_intent": query_package.get("intent", "informational"),
            "confidence": self._assess_model_confidence(knowledge_model),
        }
        
        logger.info(f"Modeler processing completed in {processing_time:.2f} seconds")
        return knowledge_model
    
    def _extract_model_components(self, query_package: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract entities, relationships, and parameters from the query.
        
        Args:
            query_package: The structured query package
            
        Returns:
            Dictionary with extracted entities, relationships, and parameters
        """
        query_text = query_package.get("query", "")
        intent = query_package.get("intent", "informational")
        
        # For entity extraction we'll use a structured prompt to the domain LLM
        extraction_prompt = self._create_extraction_prompt(query_text, intent)
        
        # Get the response from domain LLM
        response, _ = self.domain_llm.generate_response(extraction_prompt)
        
        # Parse the response into structured components
        model_components = self._parse_extraction_response(response)
        
        return model_components
    
    def _create_extraction_prompt(self, query_text: str, intent: str) -> str:
        """
        Create a prompt for entity extraction.
        
        Args:
            query_text: The raw query text
            intent: The query intent
            
        Returns:
            A formatted prompt for the LLM
        """
        return f"""As a sprint science expert, analyze this question and identify the main components:

Question: {query_text}

Identify the following components in a structured format:
1. ENTITIES: List all important sprint science concepts, objects, or actors mentioned.
2. RELATIONSHIPS: Describe how these entities relate to each other.
3. PARAMETERS: List any measurable attributes or variables mentioned or implied.
4. CONSTRAINTS: Identify any limitations, conditions, or boundaries specified.

Present your analysis in a clear, structured format suitable for further processing.
"""
    
    def _parse_extraction_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM's response into structured components.
        
        Args:
            response: The text response from the LLM
            
        Returns:
            Dictionary with parsed entities, relationships, parameters, and constraints
        """
        # This is a simple parser that looks for sections in the response
        # In a production system, we'd use a more robust parsing approach
        components = {
            "entities": [],
            "relationships": [],
            "parameters": [],
            "constraints": []
        }
        
        current_section = None
        
        for line in response.split("\n"):
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            if "ENTITIES:" in line or "1. ENTITIES:" in line or "Entities:" in line:
                current_section = "entities"
                continue
            elif "RELATIONSHIPS:" in line or "2. RELATIONSHIPS:" in line or "Relationships:" in line:
                current_section = "relationships"
                continue
            elif "PARAMETERS:" in line or "3. PARAMETERS:" in line or "Parameters:" in line:
                current_section = "parameters"
                continue
            elif "CONSTRAINTS:" in line or "4. CONSTRAINTS:" in line or "Constraints:" in line:
                current_section = "constraints"
                continue
                
            # Add content to the current section
            if current_section and line:
                # Remove list markers like "- " or "• " or "1. "
                if line.startswith("- ") or line.startswith("• "):
                    line = line[2:]
                elif len(line) > 2 and line[0].isdigit() and line[1] == "." and line[2] == " ":
                    line = line[3:]
                    
                components[current_section].append(line.strip())
        
        return components
    
    def _enrich_with_domain_knowledge(self, model_components: Dict[str, Any], query_package: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich the model components with domain-specific knowledge.
        
        Args:
            model_components: The extracted model components
            query_package: The original query package
            
        Returns:
            Enriched model components with domain knowledge
        """
        query_text = query_package.get("query", "")
        
        # Create a domain knowledge enrichment prompt
        enrichment_prompt = self._create_enrichment_prompt(model_components, query_text)
        
        # Get domain knowledge from the domain expert LLM
        response, _ = self.domain_llm.generate_response(enrichment_prompt)
        
        # Parse the response and update the model components
        enriched_components = self._parse_enrichment_response(response, model_components)
        
        return enriched_components
    
    def _create_enrichment_prompt(self, model_components: Dict[str, Any], query_text: str) -> str:
        """
        Create a prompt for domain knowledge enrichment.
        
        Args:
            model_components: The extracted model components
            query_text: The original query text
            
        Returns:
            A formatted prompt for the domain expert LLM
        """
        # Format the components for inclusion in the prompt
        entities_str = "\n".join([f"- {entity}" for entity in model_components.get("entities", [])])
        parameters_str = "\n".join([f"- {param}" for param in model_components.get("parameters", [])])
        
        return f"""As a sprint science expert, enrich the following model with specialized domain knowledge.

ORIGINAL QUESTION: {query_text}

IDENTIFIED ENTITIES:
{entities_str if entities_str else "None identified"}

IDENTIFIED PARAMETERS:
{parameters_str if parameters_str else "None identified"}

Please provide:
1. FORMULAS: Mathematical relationships relevant to these parameters.
2. ADDITIONAL PARAMETERS: Important parameters that should be included but weren't mentioned.
3. PARAMETER RELATIONSHIPS: How these parameters influence each other in sprint science.
4. DOMAIN CONTEXT: Important contextual information from sprint science relevant to this question.

Format your response under these exact headings for clear parsing.
"""
    
    def _parse_enrichment_response(self, response: str, original_components: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the domain enrichment response and update the model components.
        
        Args:
            response: The text response from the domain expert LLM
            original_components: The original model components
            
        Returns:
            Updated model components with domain enrichment
        """
        # Create a copy of the original components to enrich
        enriched = original_components.copy()
        
        # Add new component types
        enriched["formulas"] = []
        enriched["additional_parameters"] = []
        enriched["parameter_relationships"] = []
        enriched["domain_context"] = []
        
        current_section = None
        
        for line in response.split("\n"):
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            if "FORMULAS:" in line or "1. FORMULAS:" in line or "Formulas:" in line:
                current_section = "formulas"
                continue
            elif "ADDITIONAL PARAMETERS:" in line or "2. ADDITIONAL PARAMETERS:" in line or "Additional Parameters:" in line:
                current_section = "additional_parameters"
                continue
            elif "PARAMETER RELATIONSHIPS:" in line or "3. PARAMETER RELATIONSHIPS:" in line or "Parameter Relationships:" in line:
                current_section = "parameter_relationships"
                continue
            elif "DOMAIN CONTEXT:" in line or "4. DOMAIN CONTEXT:" in line or "Domain Context:" in line:
                current_section = "domain_context"
                continue
                
            # Add content to the current section
            if current_section and line:
                # Remove list markers like "- " or "• " or "1. "
                if line.startswith("- ") or line.startswith("• "):
                    line = line[2:]
                elif len(line) > 2 and line[0].isdigit() and line[1] == "." and line[2] == " ":
                    line = line[3:]
                    
                enriched[current_section].append(line.strip())
        
        # Merge additional parameters into the parameters list
        enriched["parameters"].extend(enriched.pop("additional_parameters", []))
        
        return enriched
    
    def _integrate_model_components(self, enriched_components: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integrate all model components into a unified knowledge model.
        
        Args:
            enriched_components: The enriched model components
            
        Returns:
            An integrated knowledge model
        """
        # Create a structured model from the components
        knowledge_model = {
            "entities": self._structure_entities(enriched_components.get("entities", [])),
            "relationships": self._structure_relationships(
                enriched_components.get("relationships", []),
                enriched_components.get("parameter_relationships", [])
            ),
            "parameters": self._structure_parameters(
                enriched_components.get("parameters", [])
            ),
            "formulas": self._structure_formulas(enriched_components.get("formulas", [])),
            "constraints": enriched_components.get("constraints", []),
            "domain_context": enriched_components.get("domain_context", [])
        }
        
        return knowledge_model
    
    def _structure_entities(self, entities: List[str]) -> List[Dict[str, Any]]:
        """
        Convert entity strings to structured entity objects.
        
        Args:
            entities: List of entity strings
            
        Returns:
            List of structured entity objects
        """
        structured_entities = []
        entity_id = 1
        
        for entity in entities:
            # Extract entity properties if present in parentheses or brackets
            properties = {}
            name = entity
            
            # Look for properties in parentheses: "Entity name (property: value, property2: value2)"
            if "(" in entity and ")" in entity:
                name_part, prop_part = entity.split("(", 1)
                name = name_part.strip()
                prop_text = prop_part.split(")", 1)[0].strip()
                
                # Extract individual properties
                if ":" in prop_text:
                    prop_pairs = [p.strip() for p in prop_text.split(",")]
                    for pair in prop_pairs:
                        if ":" in pair:
                            k, v = pair.split(":", 1)
                            properties[k.strip()] = v.strip()
            
            # Generate a structured entity with id and inferred type
            entity_type = self._infer_entity_type(name)
            
            structured_entities.append({
                "id": f"entity_{entity_id}",
                "name": name,
                "type": entity_type,
                "properties": properties
            })
            
            entity_id += 1
            
        return structured_entities
    
    def _infer_entity_type(self, entity: str) -> str:
        """
        Infer the type of an entity from its description.
        
        Args:
            entity: The entity string
            
        Returns:
            Entity type classification
        """
        entity_lower = entity.lower()
        
        # Define type categories with their associated terms
        type_categories = {
            "physical_property": ["velocity", "speed", "acceleration", "force", "power", "energy", "momentum"],
            "person": ["athlete", "runner", "sprinter", "person", "individual", "player", "competitor"],
            "technique": ["technique", "form", "style", "posture", "stance", "mechanics", "execution"],
            "training_method": ["training", "exercise", "workout", "drill", "regimen", "protocol", "routine"],
            "event": ["race", "event", "competition", "meet", "tournament", "championship", "olympics"],
            "body_part": ["muscle", "tendon", "joint", "ligament", "bone", "tissue", "fiber", "leg", "arm"],
            "equipment": ["shoe", "track", "apparel", "gear", "device", "implement", "technology"],
            "metric": ["time", "distance", "score", "measurement", "index", "ratio", "coefficient"]
        }
        
        # Find the category with the most term matches
        best_match = ("concept", 0)
        
        for category, terms in type_categories.items():
            # Count how many terms from this category appear in the entity name
            matches = sum(1 for term in terms if term in entity_lower)
            if matches > best_match[1]:
                best_match = (category, matches)
        
        return best_match[0]
    
    def _structure_relationships(self, relationships: List[str], parameter_relationships: List[str]) -> List[Dict[str, Any]]:
        """
        Convert relationship strings to structured relationship objects.
        
        Args:
            relationships: General relationships
            parameter_relationships: Parameter-specific relationships
            
        Returns:
            List of structured relationship objects
        """
        structured_relationships = []
        
        # Process general relationships
        for relationship in relationships:
            structured_relationships.append({
                "description": relationship,
                "type": "general"
            })
            
        # Process parameter relationships
        for relationship in parameter_relationships:
            structured_relationships.append({
                "description": relationship,
                "type": "parameter"
            })
            
        return structured_relationships
    
    def _structure_parameters(self, parameters: List[str]) -> List[Dict[str, Any]]:
        """
        Convert parameter strings to structured parameter objects.
        
        Args:
            parameters: List of parameter strings
            
        Returns:
            List of structured parameter objects
        """
        structured_parameters = []
        
        for parameter in parameters:
            # Try to extract unit if present
            unit = None
            param_name = parameter
            
            # Look for common unit patterns like "Parameter (unit)" or "Parameter [unit]"
            if "(" in parameter and ")" in parameter:
                parts = parameter.split("(")
                param_name = parts[0].strip()
                unit_part = parts[1]
                if ")" in unit_part:
                    unit = unit_part.split(")")[0].strip()
            elif "[" in parameter and "]" in parameter:
                parts = parameter.split("[")
                param_name = parts[0].strip()
                unit_part = parts[1]
                if "]" in unit_part:
                    unit = unit_part.split("]")[0].strip()
            
            structured_parameters.append({
                "name": param_name,
                "unit": unit,
                "type": self._infer_parameter_type(param_name)
            })
            
        return structured_parameters
    
    def _infer_parameter_type(self, parameter: str) -> str:
        """
        Infer the type of a parameter from its name.
        
        Args:
            parameter: The parameter name
            
        Returns:
            Parameter type classification
        """
        param_lower = parameter.lower()
        
        if any(term in param_lower for term in ["velocity", "speed", "acceleration", "pace"]):
            return "kinematic"
        elif any(term in param_lower for term in ["force", "power", "strength", "torque"]):
            return "kinetic"
        elif any(term in param_lower for term in ["time", "duration", "interval"]):
            return "temporal"
        elif any(term in param_lower for term in ["distance", "length", "height", "width"]):
            return "spatial"
        elif any(term in param_lower for term in ["angle", "orientation", "rotation"]):
            return "angular"
        elif any(term in param_lower for term in ["energy", "work", "heat", "metabolism"]):
            return "energetic"
        else:
            return "other"
    
    def _structure_formulas(self, formulas: List[str]) -> List[Dict[str, Any]]:
        """
        Convert formula strings to structured formula objects.
        
        Args:
            formulas: List of formula strings
            
        Returns:
            List of structured formula objects
        """
        structured_formulas = []
        
        for formula in formulas:
            # Try to identify the formula name and expression
            formula_name = "Unnamed Formula"
            formula_expression = formula
            
            # Look for common patterns like "Name: Expression" or "Name - Expression"
            if ":" in formula:
                parts = formula.split(":", 1)
                formula_name = parts[0].strip()
                formula_expression = parts[1].strip()
            elif " - " in formula:
                parts = formula.split(" - ", 1)
                formula_name = parts[0].strip()
                formula_expression = parts[1].strip()
            
            structured_formulas.append({
                "name": formula_name,
                "expression": formula_expression
            })
            
        return structured_formulas
    
    def _assess_model_confidence(self, knowledge_model: Dict[str, Any]) -> float:
        """
        Assess the confidence in the model completeness and coherence.
        
        Args:
            knowledge_model: The integrated knowledge model
            
        Returns:
            Confidence score between 0 and 1
        """
        confidence_scores = {}
        
        # 1. Assess entity completeness and quality
        entities = knowledge_model.get("entities", [])
        if entities:
            # Check if entities have important properties and attributes
            avg_entity_quality = sum(
                0.5 +  # Base score
                (0.2 if e.get("type") else 0) +  # Has type
                (0.3 if e.get("properties") else 0)  # Has properties
                for e in entities
            ) / len(entities)
            
            # Scale based on number of entities (more is generally better)
            entity_count_factor = min(1.0, len(entities) / 5)  # Cap at 5+ entities
            
            confidence_scores["entities"] = 0.7 * avg_entity_quality + 0.3 * entity_count_factor
        else:
            confidence_scores["entities"] = 0.0
        
        # 2. Assess parameter quality and completeness
        parameters = knowledge_model.get("parameters", [])
        if parameters:
            # Check if parameters have units and types
            avg_param_quality = sum(
                0.6 +  # Base score
                (0.2 if p.get("unit") else 0) +  # Has unit
                (0.2 if p.get("type") else 0)  # Has type
                for p in parameters
            ) / len(parameters)
            
            # Scale based on number of parameters
            param_count_factor = min(1.0, len(parameters) / 4)  # Cap at 4+ parameters
            
            confidence_scores["parameters"] = 0.8 * avg_param_quality + 0.2 * param_count_factor
        else:
            confidence_scores["parameters"] = 0.0
        
        # 3. Assess relationship completeness
        relationships = knowledge_model.get("relationships", [])
        if relationships:
            relationship_count_factor = min(1.0, len(relationships) / 3)  # Cap at 3+ relationships
            confidence_scores["relationships"] = relationship_count_factor
        else:
            confidence_scores["relationships"] = 0.0
        
        # 4. Assess formula quality
        formulas = knowledge_model.get("formulas", [])
        if formulas:
            # Check if formulas have names and expressions
            avg_formula_quality = sum(
                0.5 + 
                (0.5 if f.get("expression") else 0)  # Has expression
                for f in formulas
            ) / len(formulas)
            
            # Scale based on number of formulas
            formula_count_factor = min(1.0, len(formulas) / 2)  # Cap at 2+ formulas
            
            confidence_scores["formulas"] = 0.7 * avg_formula_quality + 0.3 * formula_count_factor
        else:
            confidence_scores["formulas"] = 0.0
        
        # 5. Assess domain context
        domain_context = knowledge_model.get("domain_context", [])
        if domain_context:
            # Scale based on number of domain context items
            context_count_factor = min(1.0, len(domain_context) / 3)  # Cap at 3+ items
            confidence_scores["domain_context"] = context_count_factor
        else:
            confidence_scores["domain_context"] = 0.0
        
        # 6. Assess constraints
        constraints = knowledge_model.get("constraints", [])
        if constraints:
            # Scale based on number of constraints
            constraint_count_factor = min(1.0, len(constraints) / 2)  # Cap at 2+ constraints
            confidence_scores["constraints"] = constraint_count_factor
        else:
            confidence_scores["constraints"] = 0.0
        
        # 7. Assess coherence by checking entity-relationship-parameter connections
        entity_names = {e.get("name", "").lower() for e in entities if e.get("name")}
        param_names = {p.get("name", "").lower() for p in parameters if p.get("name")}
        relationship_coherence = 0.0
        
        if relationships and (entity_names or param_names):
            # Check if relationships reference known entities or parameters
            coherent_count = 0
            for rel in relationships:
                desc = rel.get("description", "").lower()
                # Check if any entity or parameter names appear in the relationship description
                if any(name in desc for name in entity_names) or any(name in desc for name in param_names):
                    coherent_count += 1
            
            if relationships:
                relationship_coherence = coherent_count / len(relationships)
            
            confidence_scores["coherence"] = relationship_coherence
        else:
            confidence_scores["coherence"] = 0.0
        
        # 8. Calculate weighted confidence
        # Weight important aspects more heavily
        weights = {
            "entities": 0.25,
            "parameters": 0.20,
            "relationships": 0.15,
            "formulas": 0.15,
            "domain_context": 0.10,
            "constraints": 0.05,
            "coherence": 0.10
        }
        
        # Calculate weighted average
        weighted_confidence = sum(
            score * weights.get(component, 0)
            for component, score in confidence_scores.items()
        )
        
        # Ensure minimum confidence level of 0.4 if we have any components
        if entities or parameters or relationships:
            weighted_confidence = max(0.4, weighted_confidence)
        
        return min(1.0, weighted_confidence)


# Function to get a singleton instance
_modeler_instance = None

def get_modeler_instance():
    """
    Get a singleton instance of the Modeler.
    
    Returns:
        Singleton Modeler instance
    """
    global _modeler_instance
    if _modeler_instance is None:
        _modeler_instance = Modeler()
    return _modeler_instance 