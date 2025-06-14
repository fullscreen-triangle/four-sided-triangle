"""
LLM Connector

This module contains the LLMConnector class, which manages connections to
domain-expert language models for knowledge extraction.
"""

import logging
import json
from typing import Dict, Any, Optional, List
from app.core.model import get_model_instance

class LLMConnector:
    """
    Manages connections to domain-expert language models.
    
    This class handles the interaction with various LLMs specialized in different
    domains, including prompt construction, response parsing, and error handling.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the LLM Connector.
        
        Args:
            config: Configuration dictionary for the connector
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Get the multi-model system instance
        self.model_system = get_model_instance()
        
        # Domain-expert model configurations
        self.model_configs = self.config.get("model_configs", {})
        
        # Default configurations for domain expertise
        self.default_model_config = {
            "temperature": 0.1,  # Lower for more focused domain knowledge
            "max_tokens": 2000,
            "top_p": 0.9
        }
        
        # Domain-specific model mappings to available models
        self.domain_model_mapping = {
            "medical": "phi3",  # Use instruction model for medical precision
            "financial": "phi3",  # Use instruction model for financial analysis
            "technical": "phi3",  # Use instruction model for technical details
            "scientific": "phi3",  # Use instruction model for scientific accuracy
            "sprint": "phi3",  # Primary domain - sprint running expertise
            "biomechanics": "phi3",  # Sprint biomechanics
            "athletic_performance": "phi3",  # Athletic performance optimization
            "general": "distilgpt2",  # Use generative model for general queries
            "creative": "distilgpt2",  # Use generative model for creative tasks
            
            # Secondary expert mappings for dual-model querying
            "sprint_secondary": "sprint-llm-distilled",  # Secondary distilled expert
            "biomechanics_secondary": "sprint-llm-distilled",  # Secondary for biomechanics
            "athletic_performance_secondary": "sprint-llm-distilled"  # Secondary for performance
        }
        
        # Embedding model for semantic similarity and retrieval
        self.use_embeddings = hasattr(self.model_system, 'embedding_model') and self.model_system.embedding_model
        
        self.logger.info(f"LLM Connector initialized with models: {list(self.model_system.models.keys())}")
        if self.use_embeddings:
            self.logger.info("✓ Embedding model available for semantic retrieval")
    
    async def query_domain_expert(self, domain: str, prompt: str, 
                                 model_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query a domain-expert language model with the given prompt.
        
        Args:
            domain: Domain identifier for selecting the appropriate model
            prompt: Prompt to send to the model
            model_params: Additional parameters for the model
            
        Returns:
            Structured response from the model
        """
        self.logger.info(f"Querying {domain} domain expert model")
        
        # Get the appropriate model for this domain
        model_name = self.domain_model_mapping.get(domain, "phi3")
        if model_name not in self.model_system.models:
            self.logger.warning(f"Model {model_name} not available for domain {domain}, falling back to available model")
            available_models = list(self.model_system.models.keys())
            model_name = available_models[0] if available_models else None
            
        if not model_name:
            raise Exception("No models available for domain expert queries")
        
        # Merge model parameters
        merged_params = self._merge_model_params(domain, model_params)
        
        # Format the prompt for domain expertise
        formatted_prompt = self._format_domain_expert_prompt(domain, prompt)
        
        try:
            # Use the multi-model system to generate response
            response, metadata = self.model_system.generate_response(
                formatted_prompt, 
                parameters=merged_params
            )
            
            # Parse and structure the response for domain knowledge extraction
            parsed_response = self._parse_domain_response(response, domain, metadata)
            
            self.logger.info(f"Successfully queried {domain} domain expert using {metadata['model']}")
            return parsed_response
            
        except Exception as e:
            self.logger.error(f"Error querying {domain} domain expert model: {str(e)}")
            # Return fallback response
            return self._generate_fallback_response(domain, prompt, str(e))
    
    def _merge_model_params(self, domain: str, custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Merge default, domain-specific, and custom model parameters.
        
        Args:
            domain: Domain identifier
            custom_params: Custom parameters for this specific call
            
        Returns:
            Merged model parameters
        """
        # Start with default parameters
        merged = self.default_model_config.copy()
        
        # Add domain-specific parameters if available
        domain_config = self.model_configs.get(domain, {})
        merged.update(domain_config)
        
        # Add custom parameters if provided
        if custom_params:
            merged.update(custom_params)
        
        return merged
    
    def _format_domain_expert_prompt(self, domain: str, prompt: str) -> str:
        """
        Format the prompt for domain expertise extraction.
        
        Args:
            domain: Domain identifier
            prompt: Original prompt
            
        Returns:
            Formatted prompt optimized for domain knowledge extraction
        """
        # Domain-specific preambles for expert knowledge extraction
        domain_preambles = {
            "sprint": """You are an elite domain expert in 400m sprint running with deep knowledge of:
- Biomechanical optimization and sprint technique
- Training periodization and performance analytics
- Physiological adaptations and energy systems
- Race strategy and tactical decision-making
- Equipment optimization and environmental factors""",
            
            "biomechanics": """You are a sports biomechanics expert specializing in sprint running with expertise in:
- Kinematic and kinetic analysis of sprint mechanics
- Ground reaction forces and power generation
- Joint angles and movement optimization
- Muscle activation patterns and coordination
- Motion analysis and performance diagnostics""",
            
            "athletic_performance": """You are a performance optimization expert for elite sprinters with knowledge of:
- Training load management and recovery protocols
- Performance testing and monitoring systems
- Nutritional strategies for power athletes
- Psychological preparation and competitive readiness
- Technology integration and data analytics""",
            
            "medical": """You are a sports medicine expert specializing in sprint athletes with knowledge of:
- Exercise physiology and metabolic systems
- Injury prevention and rehabilitation protocols
- Performance-enhancing recovery methods
- Physiological testing and health monitoring
- Medical considerations for elite athletes""",
            
            "technical": """You are a technical expert in sprint training methodology with knowledge of:
- Training equipment and technology applications
- Data acquisition and analysis systems
- Video analysis and technique correction
- Performance measurement and monitoring tools
- Technological innovations in sprint training"""
        }
        
        # Get domain-specific preamble
        preamble = domain_preambles.get(domain, f"You are a domain expert in {domain}.")
        
        # Format the complete prompt with structured output requirements
        formatted_prompt = f"""{preamble}

{prompt}

Provide your expert analysis in the following structured JSON format:
{{
    "elements": [
        {{
            "id": "unique_element_identifier",
            "description": "Detailed description of the knowledge element",
            "confidence": 0.95,
            "category": "biomechanics|physiology|technique|training|equipment",
            "formulas": [
                {{
                    "expression": "mathematical_formula",
                    "description": "explanation_of_formula",
                    "variables": {{"var1": "description", "var2": "description"}},
                    "units": "appropriate_units",
                    "confidence": 0.90
                }}
            ],
            "constraints": [
                {{
                    "expression": "constraint_description",
                    "type": "physiological|biomechanical|equipment|environmental",
                    "confidence": 0.85
                }}
            ],
            "reference_values": {{
                "parameter_name": {{
                    "value": "typical_value_or_range",
                    "unit": "measurement_unit",
                    "context": "elite_male|elite_female|recreational",
                    "source": "research_basis"
                }}
            }},
            "dependencies": ["related_element_ids"],
            "applications": ["specific_use_cases"]
        }}
    ],
    "metadata": {{
        "domain": "{domain}",
        "complexity_level": "basic|intermediate|advanced|expert",
        "evidence_quality": "empirical|theoretical|observational",
        "applicability": "universal|specific_conditions"
    }}
}}

Ensure all numerical values, formulas, and constraints are scientifically accurate and properly cited."""
        
        return formatted_prompt
    
    def _parse_domain_response(self, response: str, domain: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and structure the response from domain expert models.
        
        Args:
            response: Raw response from the model
            domain: Domain identifier
            metadata: Generation metadata
            
        Returns:
            Structured domain knowledge response
        """
        try:
            # Try to parse as JSON if the model returned structured data
            if response.strip().startswith('{') and response.strip().endswith('}'):
                parsed_json = json.loads(response)
                if "elements" in parsed_json:
                    return parsed_json
            
            # If not structured JSON, extract knowledge elements from natural language
            return self._extract_knowledge_from_text(response, domain, metadata)
            
        except json.JSONDecodeError:
            # Fallback to text extraction
            return self._extract_knowledge_from_text(response, domain, metadata)
    
    def _extract_knowledge_from_text(self, text: str, domain: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured knowledge elements from natural language response.
        
        Args:
            text: Natural language response
            domain: Domain identifier
            metadata: Generation metadata
            
        Returns:
            Structured knowledge elements
        """
        # This is a simplified extraction - in production you might use NER, regex patterns, etc.
        elements = []
        
        # Split response into sentences/paragraphs for analysis
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        for i, sentence in enumerate(sentences):
            if len(sentence) > 20:  # Filter out very short sentences
                element = {
                    "id": f"{domain}_extracted_{i+1}",
                    "description": sentence,
                    "confidence": 0.75,  # Lower confidence for extracted vs structured
                    "category": self._categorize_content(sentence, domain),
                    "formulas": self._extract_formulas(sentence),
                    "constraints": [],
                    "reference_values": {},
                    "dependencies": [],
                    "applications": []
                }
                elements.append(element)
        
        return {
            "elements": elements,
            "metadata": {
                "domain": domain,
                "extraction_method": "text_parsing",
                "model_used": metadata.get("model", "unknown"),
                "generation_time": metadata.get("generation_time", 0),
                "complexity_level": "intermediate",
                "evidence_quality": "model_generated",
                "applicability": "general"
            }
        }
    
    def _categorize_content(self, content: str, domain: str) -> str:
        """
        Categorize content based on keywords and domain.
        
        Args:
            content: Text content to categorize
            domain: Domain context
            
        Returns:
            Category classification
        """
        content_lower = content.lower()
        
        # Sprint-specific categorization
        if any(word in content_lower for word in ['biomechanic', 'kinematic', 'force', 'angle', 'motion']):
            return "biomechanics"
        elif any(word in content_lower for word in ['physiolog', 'metabolic', 'oxygen', 'lactate', 'energy']):
            return "physiology"
        elif any(word in content_lower for word in ['technique', 'form', 'style', 'execution']):
            return "technique"
        elif any(word in content_lower for word in ['training', 'exercise', 'workout', 'program']):
            return "training"
        elif any(word in content_lower for word in ['equipment', 'technology', 'device', 'tool']):
            return "equipment"
        else:
            return "general"
    
    def _extract_formulas(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract mathematical formulas from text.
        
        Args:
            text: Text to search for formulas
            
        Returns:
            List of extracted formulas
        """
        formulas = []
        
        # Simple regex patterns for common formula patterns
        import re
        
        # Look for equations with = sign
        equation_pattern = r'([A-Za-z_][A-Za-z0-9_]*\s*=\s*[^.]*)'
        equations = re.findall(equation_pattern, text)
        
        for equation in equations:
            formulas.append({
                "expression": equation.strip(),
                "description": f"Formula extracted from: {text[:50]}...",
                "variables": {},
                "units": "",
                "confidence": 0.6
            })
        
        return formulas
    
    async def _mock_domain_expert_call(self, domain: str, prompt: str, 
                                     params: Dict[str, Any]) -> str:
        """
        Mock implementation of a call to a domain-expert LLM.
        
        In a real implementation, this would make an API call to the actual model.
        
        Args:
            domain: Domain identifier
            prompt: Formatted prompt
            params: Model parameters
            
        Returns:
            Mock response from the model
        """
        self.logger.debug(f"Mock call to {domain} domain expert with prompt: {prompt[:100]}...")
        
        # Generate a mock response based on the domain
        if domain == "medical":
            return self._generate_mock_medical_response()
        elif domain == "financial":
            return self._generate_mock_financial_response()
        else:
            # Generic response for other domains
            return json.dumps({
                "elements": [
                    {
                        "id": f"{domain}_element_1",
                        "description": f"Mock {domain} knowledge element 1",
                        "confidence": 0.85,
                        "formulas": [],
                        "constraints": [],
                        "reference_values": {}
                    },
                    {
                        "id": f"{domain}_element_2",
                        "description": f"Mock {domain} knowledge element 2",
                        "confidence": 0.78,
                        "formulas": [],
                        "constraints": [],
                        "reference_values": {}
                    }
                ]
            })
    
    def _generate_mock_medical_response(self) -> str:
        """
        Generate a mock response for medical domain queries.
        
        Returns:
            Mock medical domain response
        """
        return json.dumps({
            "elements": [
                {
                    "id": "medical_bmi",
                    "description": "Body Mass Index (BMI) calculation and interpretation",
                    "confidence": 0.95,
                    "formulas": [
                        {
                            "expression": "BMI = weight_kg / (height_m)^2",
                            "description": "Formula to calculate Body Mass Index",
                            "variables": {
                                "weight_kg": "Weight in kilograms",
                                "height_m": "Height in meters"
                            },
                            "confidence": 0.98
                        }
                    ],
                    "constraints": [
                        {
                            "expression": "weight_kg > 0 AND height_m > 0",
                            "description": "Weight and height must be positive values",
                            "confidence": 0.99
                        }
                    ],
                    "reference_values": {
                        "bmi_underweight": {
                            "value": "<18.5",
                            "description": "BMI value indicating underweight status",
                            "confidence": 0.95
                        },
                        "bmi_normal": {
                            "value": "18.5-24.9",
                            "description": "BMI value indicating normal weight status",
                            "confidence": 0.95
                        },
                        "bmi_overweight": {
                            "value": "25.0-29.9",
                            "description": "BMI value indicating overweight status",
                            "confidence": 0.95
                        },
                        "bmi_obese": {
                            "value": "≥30.0",
                            "description": "BMI value indicating obese status",
                            "confidence": 0.95
                        }
                    }
                },
                {
                    "id": "medical_blood_pressure",
                    "description": "Blood pressure classification and interpretation",
                    "confidence": 0.92,
                    "formulas": [],
                    "constraints": [],
                    "reference_values": {
                        "normal_systolic": {
                            "value": "<120 mmHg",
                            "description": "Normal systolic blood pressure range",
                            "confidence": 0.9
                        },
                        "normal_diastolic": {
                            "value": "<80 mmHg",
                            "description": "Normal diastolic blood pressure range",
                            "confidence": 0.9
                        }
                    }
                }
            ],
            "medical_standards": [
                {
                    "id": "who_bmi_standard",
                    "description": "WHO standard for BMI classification",
                    "source": "World Health Organization",
                    "confidence": 0.97
                }
            ],
            "clinical_guidelines": [
                {
                    "id": "bmi_interpretation",
                    "description": "Guidelines for interpreting BMI in clinical practice",
                    "source": "CDC Clinical Guidelines",
                    "confidence": 0.88
                }
            ]
        })
    
    def _generate_mock_financial_response(self) -> str:
        """
        Generate a mock response for financial domain queries.
        
        Returns:
            Mock financial domain response
        """
        return json.dumps({
            "elements": [
                {
                    "id": "financial_roi",
                    "description": "Return on Investment (ROI) calculation and interpretation",
                    "confidence": 0.91,
                    "formulas": [
                        {
                            "expression": "ROI = (Net Profit / Cost of Investment) * 100",
                            "description": "Formula to calculate Return on Investment",
                            "variables": {
                                "Net Profit": "Gain from investment minus cost",
                                "Cost of Investment": "Total cost of investment"
                            },
                            "confidence": 0.95
                        }
                    ],
                    "constraints": [
                        {
                            "expression": "Cost of Investment > 0",
                            "description": "Investment cost must be positive",
                            "confidence": 0.98
                        }
                    ],
                    "reference_values": {}
                },
                {
                    "id": "financial_compound_interest",
                    "description": "Compound interest calculation for investments",
                    "confidence": 0.93,
                    "formulas": [
                        {
                            "expression": "A = P(1 + r/n)^(nt)",
                            "description": "Formula to calculate compound interest",
                            "variables": {
                                "A": "Final amount",
                                "P": "Principal (initial investment)",
                                "r": "Annual interest rate (decimal)",
                                "n": "Number of times interest compounds per year",
                                "t": "Time in years"
                            },
                            "confidence": 0.94
                        }
                    ],
                    "constraints": [],
                    "reference_values": {}
                }
            ],
            "financial_models": [
                {
                    "id": "time_value_model",
                    "description": "Time value of money model",
                    "confidence": 0.9
                }
            ],
            "market_assumptions": [
                {
                    "id": "avg_market_return",
                    "description": "Average market return assumption of 7-10% annually",
                    "confidence": 0.75
                }
            ]
        })
    
    def get_semantic_embeddings(self, texts: List[str]) -> Optional[List[List[float]]]:
        """
        Get semantic embeddings for knowledge similarity and retrieval.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors, or None if embedding model unavailable
        """
        if not self.use_embeddings:
            return None
            
        try:
            embeddings = self.model_system.get_embeddings(texts)
            return embeddings.tolist()
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {e}")
            return None
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse and validate the response from the language model.
        
        Args:
            response: Raw response string from the model
            
        Returns:
            Parsed and validated response
        """
        try:
            # Parse JSON response
            parsed = json.loads(response)
            
            # Basic validation
            if not isinstance(parsed, dict):
                raise ValueError("Response is not a dictionary object")
            
            if "elements" not in parsed:
                raise ValueError("Response does not contain 'elements' field")
            
            return parsed
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {str(e)}")
            # Return minimal valid structure
            return {"elements": [], "error": f"Failed to parse JSON response: {str(e)}"}
        
        except ValueError as e:
            self.logger.error(f"Invalid response structure: {str(e)}")
            # Return minimal valid structure
            return {"elements": [], "error": f"Invalid response structure: {str(e)}"}
    
    def _generate_fallback_response(self, domain: str, prompt: str, error: str) -> Dict[str, Any]:
        """
        Generate a fallback response when the model query fails.
        
        Args:
            domain: Domain identifier
            prompt: Original prompt
            error: Error message
            
        Returns:
            Fallback response
        """
        self.logger.warning(f"Generating fallback response for domain {domain}")
        
        return {
            "elements": [
                {
                    "id": "fallback_element",
                    "description": f"Fallback knowledge element for {domain} domain",
                    "confidence": 0.3,
                    "error": error
                }
            ],
            "metadata": {
                "is_fallback": True,
                "original_domain": domain,
                "error_message": error
            }
        } 