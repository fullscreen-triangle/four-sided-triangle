import os
import time
import torch
from typing import Dict, Any, List, Optional, Tuple
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel, PeftConfig
import numpy as np
import logging
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get model path from environment
MODEL_PATH = os.getenv("MODEL_PATH", "./sprint-llm-distilled-20250324-040451")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "512"))
MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", "0.7"))
MODEL_TOP_P = float(os.getenv("MODEL_TOP_P", "0.9"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SprintLLM:
    """
    Handler for the sprint-llm-distilled model.
    This class loads and manages the domain expert LLM, providing methods
    for processing queries and generating responses.
    """
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Load the model and tokenizer
        self.load_model()
    
    def load_model(self):
        """
        Load the sprint-llm-distilled model and tokenizer.
        """
        try:
            start_time = time.time()
            logger.info(f"Loading model from {MODEL_PATH}")
            
            # Load configuration
            peft_config = PeftConfig.from_pretrained(MODEL_PATH)
            
            # Load base model and tokenizer
            logger.info(f"Loading base model: {peft_config.base_model_name_or_path}")
            base_model = AutoModelForCausalLM.from_pretrained(
                peft_config.base_model_name_or_path,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True
            )
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                MODEL_PATH,
                trust_remote_code=True
            )
            
            # Load adapter
            logger.info("Loading PEFT adapter")
            self.model = PeftModel.from_pretrained(
                base_model, 
                MODEL_PATH,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            )
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"Model loaded successfully in {time.time() - start_time:.2f} seconds")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise Exception(f"Failed to load the sprint-llm-distilled model: {str(e)}")
    
    def generate_response(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a response to the given query using the sprint-llm-distilled model.
        
        Args:
            query: The user query in natural language
            parameters: Optional parameters for generation
            
        Returns:
            Tuple of (response, metadata)
        """
        if self.model is None or self.tokenizer is None:
            raise Exception("Model or tokenizer not loaded. Please initialize first.")
        
        # Set default parameters if not provided
        if parameters is None:
            parameters = {}
        
        # Prepare inputs
        prompt = self._format_prompt(query)
        
        try:
            # Log and time the generation
            start_time = time.time()
            logger.info(f"Generating response for query: {query[:50]}...")
            
            # Tokenize
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            # Generate
            generation_kwargs = {
                "max_new_tokens": parameters.get("max_tokens", MAX_TOKENS),
                "temperature": parameters.get("temperature", MODEL_TEMPERATURE),
                "top_p": parameters.get("top_p", MODEL_TOP_P),
                "do_sample": True,
                "pad_token_id": self.tokenizer.eos_token_id
            }
            
            # Generate text
            with torch.no_grad():
                outputs = self.model.generate(**inputs, **generation_kwargs)
            
            # Decode and format the output
            decoded_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = self._extract_response(decoded_output, prompt)
            
            # Calculate metrics and create metadata
            generation_time = time.time() - start_time
            metadata = {
                "model": "sprint-llm-distilled",
                "generated_tokens": len(outputs[0]) - len(inputs.input_ids[0]),
                "generation_time": generation_time,
                "estimated_tokens_per_second": (len(outputs[0]) - len(inputs.input_ids[0])) / generation_time if generation_time > 0 else 0,
                "parameters": {
                    "temperature": generation_kwargs["temperature"],
                    "top_p": generation_kwargs["top_p"],
                    "max_new_tokens": generation_kwargs["max_new_tokens"]
                }
            }
            
            logger.info(f"Response generated in {generation_time:.2f} seconds")
            return response.strip(), metadata
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise Exception(f"Failed to generate response: {str(e)}")
    
    def _format_prompt(self, query: str) -> str:
        """Format the query into a prompt for the model."""
        # Simple prompt formatting for domain expert queries
        return f"""You are a domain expert in sprint running, specifically focusing on the 400m sprint.
Answer the following question with accurate, detailed information based on scientific knowledge.

Question: {query}

Answer:"""
    
    def _extract_response(self, full_text: str, prompt: str) -> str:
        """Extract just the response part from the full generated text."""
        if prompt in full_text:
            # Extract everything after the prompt
            response = full_text[len(prompt):]
        else:
            # If the prompt is not found (e.g., if the model modified it),
            # look for "Answer:" and extract everything after it
            if "Answer:" in full_text:
                response = full_text.split("Answer:", 1)[1]
            else:
                # If we can't find a clear demarcation, return the full text
                response = full_text
        
        return response.strip()
    
    def calculate_anthropometric_metrics(
        self, 
        age: float, 
        height: float, 
        weight: float, 
        gender: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Calculate anthropometric metrics based on the provided parameters.
        
        Args:
            age: Age in years
            height: Height in cm
            weight: Weight in kg
            gender: Gender (male/female)
            parameters: Additional parameters for calculation
            
        Returns:
            Tuple of (metrics_by_category, metadata)
        """
        # Note: This method uses a combination of scientific formulas and 
        # model-generated values to provide comprehensive anthropometric metrics
        
        start_time = time.time()
        
        # Prepare a query for the model to get specialized metrics
        query = (
            f"Calculate detailed anthropometric metrics for a {gender}, {age} years old, "
            f"{height} cm tall, weighing {weight} kg. Include all possible body segment measurements, "
            f"biomechanical properties, and performance predictors."
        )
        
        # Get model-based metrics
        model_response, _ = self.generate_response(query)
        
        # Parse the model response and combine with calculated metrics
        # For this implementation, we'll calculate basic metrics directly and
        # use the model to provide the more complex domain-specific ones
        
        # Calculate basic metrics
        metrics_categories = [
            self._calculate_basic_metrics(age, height, weight, gender),
            self._calculate_body_composition(age, height, weight, gender),
        ]
        
        # Extract metrics from model response
        model_metrics = self._parse_model_metrics(model_response)
        metrics_categories.extend(model_metrics)
        
        # Generate metadata
        metadata = {
            "calculation_time": time.time() - start_time,
            "model": "sprint-llm-distilled",
            "input_parameters": {
                "age": age,
                "height": height,
                "weight": weight,
                "gender": gender
            }
        }
        
        return metrics_categories, metadata
    
    def _calculate_basic_metrics(self, age: float, height: float, weight: float, gender: str) -> Dict[str, Any]:
        """Calculate basic anthropometric metrics."""
        # BMI calculation
        bmi = weight / ((height / 100) ** 2)
        
        # Body Surface Area using Du Bois formula
        bsa = 0.007184 * (height ** 0.725) * (weight ** 0.425)
        
        return {
            "category": "Basic_Anthropometrics",
            "metrics": [
                {"name": "Age", "value": age, "unit": "years"},
                {"name": "Height", "value": height, "unit": "cm"},
                {"name": "Weight", "value": weight, "unit": "kg"},
                {"name": "BMI", "value": round(bmi, 2), "unit": "kg/m²", "confidence": 0.98},
                {"name": "Body_Surface_Area", "value": round(bsa, 2), "unit": "m²", "confidence": 0.95}
            ]
        }
    
    def _calculate_body_composition(self, age: float, height: float, weight: float, gender: str) -> Dict[str, Any]:
        """Calculate body composition metrics using appropriate formulas."""
        # Calculate BMI first
        bmi = weight / ((height / 100) ** 2)
        
        # Body fat percentage estimate using Jackson-Pollock formula (simplified)
        # This is a simplification - normally would use skinfold measurements
        if gender.lower() == "male":
            body_fat_pct = 1.20 * bmi + 0.23 * age - 16.2
        else:  # female
            body_fat_pct = 1.20 * bmi + 0.23 * age - 5.4
            
        # Ensure the value is within reasonable range
        body_fat_pct = max(5, min(body_fat_pct, 45))
        
        # Calculate lean body mass
        lean_mass = weight * (1 - body_fat_pct / 100)
        
        # Estimate skeletal muscle mass (SMM)
        # Simplified formula based on lean mass
        if gender.lower() == "male":
            smm = lean_mass * 0.85 * 0.75  # males have ~85% of LBM as muscle, ~75% of that as skeletal muscle
        else:
            smm = lean_mass * 0.80 * 0.75  # females have ~80% of LBM as muscle
            
        # Bone mass estimate (simplified)
        bone_mass = weight * 0.042
        
        # Total body water estimate
        tbw = lean_mass * 0.72
        
        return {
            "category": "Body_Composition",
            "metrics": [
                {"name": "Lean_Body_Mass", "value": round(lean_mass, 2), "unit": "kg", "confidence": 0.85},
                {"name": "Body_Fat_Percentage", "value": round(body_fat_pct, 2), "unit": "%", "confidence": 0.80},
                {"name": "Skeletal_Muscle_Mass", "value": round(smm, 2), "unit": "kg", "confidence": 0.80},
                {"name": "Bone_Mass", "value": round(bone_mass, 2), "unit": "kg", "confidence": 0.75},
                {"name": "Total_Body_Water", "value": round(tbw, 2), "unit": "kg", "confidence": 0.85}
            ]
        }
    
    def _parse_model_metrics(self, model_response: str) -> List[Dict[str, Any]]:
        """
        Parse the metrics from the model response.
        Extracts structured metric categories and values from the model's text output.
        """
        metrics_categories = []
        
        # Extract segmental measurements
        if "segment" in model_response.lower() or "limb" in model_response.lower():
            # Find segmental measurement specifics in the text
            leg_value = self._extract_metric_value(model_response, "leg length", "height")
            arm_value = self._extract_metric_value(model_response, "arm length", "height")
            trunk_value = self._extract_metric_value(model_response, "trunk length", "height")
            
            metrics_categories.append({
                "category": "Segmental_Measurements",
                "metrics": [
                    {"name": "Leg_Length", "value": leg_value, "confidence": 0.85},
                    {"name": "Arm_Length", "value": arm_value, "confidence": 0.85},
                    {"name": "Trunk_Length", "value": trunk_value, "confidence": 0.85}
                ]
            })
        
        # Extract performance metrics
        if "performance" in model_response.lower() or "speed" in model_response.lower():
            # Find performance metric specifics in the text
            speed_value = self._extract_metric_value(model_response, "speed", "m/s")
            stride_value = self._extract_metric_value(model_response, "stride", "length")
            
            metrics_categories.append({
                "category": "Performance_Metrics",
                "metrics": [
                    {"name": "Estimated_Max_Speed", "value": speed_value, "confidence": 0.70},
                    {"name": "Stride_Length", "value": stride_value, "confidence": 0.75}
                ]
            })
        
        # Extract body composition if mentioned
        if "composition" in model_response.lower() or "body fat" in model_response.lower():
            # Find body composition specifics
            fat_value = self._extract_metric_value(model_response, "body fat", "percentage")
            muscle_value = self._extract_metric_value(model_response, "muscle mass", "weight")
            
            metrics_categories.append({
                "category": "Body_Composition",
                "metrics": [
                    {"name": "Body_Fat", "value": fat_value, "confidence": 0.80},
                    {"name": "Muscle_Mass", "value": muscle_value, "confidence": 0.80},
                ]
            })
        
        return metrics_categories
    
    def _extract_metric_value(self, text: str, metric_key: str, fallback_key: str) -> str:
        """
        Extract specific metric values from text using pattern matching
        
        Args:
            text: The text to search in
            metric_key: The key metric to look for
            fallback_key: The fallback context if exact value not found
            
        Returns:
            Extracted value or contextual estimation
        """
        # Look for patterns like "leg length: 95cm" or "leg length (95cm)"
        # or "leg length of 95 cm" or "leg length is about 95cm"
        patterns = [
            rf"{metric_key}[:\s]*(\d+\.?\d*)\s*(?:cm|m|kg|%|percent)",
            rf"{metric_key}.*?[(](\d+\.?\d*)\s*(?:cm|m|kg|%|percent)[)]",
            rf"{metric_key}.*?of\s+(\d+\.?\d*)\s*(?:cm|m|kg|%|percent)",
            rf"{metric_key}.*?(?:is|was|about)\s+(\d+\.?\d*)\s*(?:cm|m|kg|%|percent)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return f"{match.group(1)} {text[match.end()-2:match.end()]}"
                
        # If no direct value found, return contextual estimation
        return f"Estimated from {fallback_key}"

# Singleton instance
_model_instance = None

def get_model_instance():
    """
    Get a singleton instance of the SprintLLM model.
    """
    global _model_instance
    if _model_instance is None:
        _model_instance = SprintLLM()
    return _model_instance 