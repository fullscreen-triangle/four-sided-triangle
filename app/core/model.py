import os
import time
import torch
from typing import Dict, Any, List, Optional, Tuple
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModel
import numpy as np
import logging
import re
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from peft import PeftModel, PeftConfig

# Load environment variables
load_dotenv()

# Get model path from environment
MODEL_PATH = os.getenv("MODEL_PATH", "./models")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "512"))
MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", "0.7"))
MODEL_TOP_P = float(os.getenv("MODEL_TOP_P", "0.9"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MultiModelSprintLLM:
    """
    Multi-model handler for domain expert LLM system.
    This class loads and manages multiple specialized models:
    - Embedding model for semantic search and retrieval
    - Instruction-following models for different query types
    - Domain-specific models for specialized knowledge
    """
    def __init__(self):
        self.models = {}
        self.tokenizers = {}
        self.embedding_model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Load all available models
        self.load_models()
    
    def load_models(self):
        """
        Load all available models from the models directory.
        """
        try:
            start_time = time.time()
            logger.info(f"Loading models from {MODEL_PATH}")
            
            # Define available models and their purposes
            model_configs = {
                "embedding": {
                    "path": os.path.join(MODEL_PATH, "intfloat_e5-large-v2"),
                    "type": "embedding",
                    "description": "Semantic embedding model for retrieval"
                },
                "phi3": {
                    "path": os.path.join(MODEL_PATH, "microsoft_phi-3-mini-4k-instruct"),
                    "type": "instruction",
                    "description": "Instruction-following model for complex queries"
                },
                "distilgpt2": {
                    "path": os.path.join(MODEL_PATH, "distilgpt2"),
                    "type": "generative",
                    "description": "Generative model for creative responses"
                },
                "sprint-llm-distilled": {
                    "path": "./sprint-llm-distilled-20250324-040451",
                    "type": "domain_expert",
                    "description": "Distilled domain expert model for sprint biomechanics"
                }
            }
            
            # Load embedding model
            if os.path.exists(model_configs["embedding"]["path"]):
                logger.info("Loading embedding model: intfloat/e5-large-v2")
                try:
                    # Use SentenceTransformer for easier embedding generation
                    self.embedding_model = SentenceTransformer(model_configs["embedding"]["path"])
                    logger.info("✓ Embedding model loaded successfully")
                except Exception as e:
                    logger.warning(f"Failed to load embedding model as SentenceTransformer, trying AutoModel: {e}")
                    try:
                        self.models["embedding"] = AutoModel.from_pretrained(
                            model_configs["embedding"]["path"],
                            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                            device_map="auto" if torch.cuda.is_available() else None
                        )
                        self.tokenizers["embedding"] = AutoTokenizer.from_pretrained(
                            model_configs["embedding"]["path"]
                        )
                        logger.info("✓ Embedding model loaded as AutoModel")
                    except Exception as e2:
                        logger.error(f"Failed to load embedding model: {e2}")
            
            # Load instruction-following models (if they have model weights)
            for model_name, config in model_configs.items():
                if model_name == "embedding":
                    continue
                    
                model_path = config["path"]
                if os.path.exists(model_path):
                    # Check if model has weights (not just tokenizer)
                    has_weights = any(
                        os.path.exists(os.path.join(model_path, f))
                        for f in ["pytorch_model.bin", "model.safetensors", "pytorch_model-00001-of-*.bin", "adapter_model.safetensors"]
                    )
                    
                    if has_weights:
                        try:
                            logger.info(f"Loading {config['description']}: {model_name}")
                            
                            # Load tokenizer
                            self.tokenizers[model_name] = AutoTokenizer.from_pretrained(
                                model_path,
                                trust_remote_code=True
                            )
                            
                            # Set pad token if not exists
                            if self.tokenizers[model_name].pad_token is None:
                                self.tokenizers[model_name].pad_token = self.tokenizers[model_name].eos_token
                            
                            # Special handling for sprint-llm-distilled model with PEFT adapters
                            if model_name == "sprint-llm-distilled" and os.path.exists(os.path.join(model_path, "adapter_config.json")):
                                # Load PEFT config
                                peft_config = PeftConfig.from_pretrained(model_path)
                                
                                # Load base model
                                base_model = AutoModelForCausalLM.from_pretrained(
                                    peft_config.base_model_name_or_path,
                                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                                    device_map="auto" if torch.cuda.is_available() else None,
                                    trust_remote_code=True
                                )
                                
                                # Load PEFT model with adapters
                                self.models[model_name] = PeftModel.from_pretrained(base_model, model_path)
                                logger.info(f"✓ {model_name} loaded with PEFT adapters")
                            
                            # Load model
                            elif config["type"] == "instruction":
                                self.models[model_name] = AutoModelForCausalLM.from_pretrained(
                                    model_path,
                                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                                    device_map="auto" if torch.cuda.is_available() else None,
                                    trust_remote_code=True
                                )
                            elif config["type"] == "domain_expert":
                                # Handle domain expert models
                                self.models[model_name] = AutoModelForCausalLM.from_pretrained(
                                    model_path,
                                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                                    device_map="auto" if torch.cuda.is_available() else None,
                                    trust_remote_code=True
                                )
                            else:
                                self.models[model_name] = AutoModelForCausalLM.from_pretrained(
                                    model_path,
                                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                                    device_map="auto" if torch.cuda.is_available() else None
                                )
                            
                            self.models[model_name].eval()
                            logger.info(f"✓ {model_name} model loaded successfully")
                            
                        except Exception as e:
                            logger.error(f"Failed to load {model_name}: {str(e)}")
                    else:
                        logger.warning(f"No model weights found for {model_name}, skipping")
                else:
                    logger.warning(f"Model directory not found: {model_path}")
            
            total_time = time.time() - start_time
            logger.info(f"All models loaded in {total_time:.2f} seconds")
            logger.info(f"Available models: {list(self.models.keys())}")
            if self.embedding_model:
                logger.info("✓ Embedding model available")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise Exception(f"Failed to load models: {str(e)}")
    
    def generate_response(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a response using the best available model for the query type.
        
        Args:
            query: The user query in natural language
            parameters: Optional parameters for generation
            
        Returns:
            Tuple of (response, metadata)
        """
        if not self.models:
            raise Exception("No models loaded. Please initialize first.")
        
        # Set default parameters if not provided
        if parameters is None:
            parameters = {}
        
        # Determine best model for the query
        model_name = self._select_best_model(query)
        
        if model_name not in self.models:
            raise Exception(f"Selected model {model_name} not available")
        
        model = self.models[model_name]
        tokenizer = self.tokenizers[model_name]
        
        # Prepare inputs
        prompt = self._format_prompt(query, model_name)
        
        try:
            # Log and time the generation
            start_time = time.time()
            logger.info(f"Generating response using {model_name} for query: {query[:50]}...")
            
            # Tokenize
            inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
            if torch.cuda.is_available():
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate
            generation_kwargs = {
                "max_new_tokens": parameters.get("max_tokens", MAX_TOKENS),
                "temperature": parameters.get("temperature", MODEL_TEMPERATURE),
                "top_p": parameters.get("top_p", MODEL_TOP_P),
                "do_sample": True,
                "pad_token_id": tokenizer.pad_token_id or tokenizer.eos_token_id,
                "eos_token_id": tokenizer.eos_token_id
            }
            
            # Generate text
            with torch.no_grad():
                outputs = model.generate(**inputs, **generation_kwargs)
            
            # Decode and format the output
            decoded_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = self._extract_response(decoded_output, prompt)
            
            # Calculate metrics and create metadata
            generation_time = time.time() - start_time
            metadata = {
                "model": model_name,
                "model_type": "multi-model-sprint-llm",
                "generated_tokens": len(outputs[0]) - len(inputs.input_ids[0]),
                "generation_time": generation_time,
                "estimated_tokens_per_second": (len(outputs[0]) - len(inputs.input_ids[0])) / generation_time if generation_time > 0 else 0,
                "parameters": {
                    "temperature": generation_kwargs["temperature"],
                    "top_p": generation_kwargs["top_p"],
                    "max_new_tokens": generation_kwargs["max_new_tokens"]
                }
            }
            
            logger.info(f"Response generated in {generation_time:.2f} seconds using {model_name}")
            return response.strip(), metadata
            
        except Exception as e:
            logger.error(f"Error generating response with {model_name}: {str(e)}")
            raise Exception(f"Failed to generate response: {str(e)}")
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for the given texts using the embedding model.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Numpy array of embeddings
        """
        if self.embedding_model is None and "embedding" not in self.models:
            raise Exception("No embedding model available")
        
        try:
            if self.embedding_model:
                # Use SentenceTransformer
                embeddings = self.embedding_model.encode(texts)
                return embeddings
            else:
                # Use manual embedding generation
                model = self.models["embedding"]
                tokenizer = self.tokenizers["embedding"]
                
                embeddings = []
                for text in texts:
                    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
                    if torch.cuda.is_available():
                        inputs = {k: v.to(self.device) for k, v in inputs.items()}
                    
                    with torch.no_grad():
                        outputs = model(**inputs)
                        # Use mean pooling
                        embeddings.append(outputs.last_hidden_state.mean(dim=1).cpu().numpy())
                
                return np.vstack(embeddings)
                
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise Exception(f"Failed to generate embeddings: {str(e)}")
    
    def _select_best_model(self, query: str) -> str:
        """
        Select the best model based on query characteristics.
        
        Args:
            query: The user query
            
        Returns:
            Name of the best model to use
        """
        # Simple heuristic-based model selection
        query_lower = query.lower()
        
        # Check for instruction-following patterns
        instruction_patterns = [
            "calculate", "analyze", "explain", "describe", "how to", "what is",
            "compare", "evaluate", "recommend", "suggest"
        ]
        
        # Check for creative/generative patterns
        creative_patterns = [
            "generate", "create", "write", "compose", "imagine", "story"
        ]
        
        # Prefer phi3 for instruction-following tasks
        if "phi3" in self.models and any(pattern in query_lower for pattern in instruction_patterns):
            return "phi3"
        
        # Use distilgpt2 for creative tasks
        if "distilgpt2" in self.models and any(pattern in query_lower for pattern in creative_patterns):
            return "distilgpt2"
        
        # Default to the first available model
        available_models = list(self.models.keys())
        if "phi3" in available_models:
            return "phi3"
        elif "distilgpt2" in available_models:
            return "distilgpt2"
        else:
            return available_models[0] if available_models else None
    
    def _format_prompt(self, query: str, model_name: str) -> str:
        """Format the query into a prompt for the specific model."""
        if model_name == "phi3":
            return f"""<|system|>
You are a domain expert in sprint running, specifically focusing on the 400m sprint. Answer questions with accurate, detailed information based on scientific knowledge.
<|end|>
<|user|>
{query}
<|end|>
<|assistant|>"""
        elif model_name == "distilgpt2":
            return f"Sprint Expert: {query}\n\nAnswer:"
        else:
            # Generic format
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
            # Look for common response markers
            markers = ["<|assistant|>", "Answer:", "Response:"]
            for marker in markers:
                if marker in full_text:
                    response = full_text.split(marker, 1)[1]
                    break
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
        Calculate anthropometric metrics using the multi-model system.
        """
        start_time = time.time()
        
        # Prepare a query for the model to get specialized metrics
        query = (
            f"Calculate detailed anthropometric metrics for a {gender}, {age} years old, "
            f"{height} cm tall, weighing {weight} kg. Include all possible body segment measurements, "
            f"biomechanical properties, and performance predictors for 400m sprint running."
        )
        
        # Get model-based metrics
        model_response, model_metadata = self.generate_response(query)
        
        # Calculate basic metrics
        metrics_categories = [
            self._calculate_basic_metrics(age, height, weight, gender),
            self._calculate_body_composition(age, height, weight, gender),
        ]
        
        # Extract metrics from model response
        model_metrics = self._parse_model_metrics(model_response)
        metrics_categories.extend(model_metrics)
        
        # Create metadata
        metadata = {
            "calculation_time": time.time() - start_time,
            "model_used": model_metadata.get("model", "unknown"),
            "parameters": {
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

def get_model_instance():
    """
    Get a singleton instance of the multi-model system.
    """
    if not hasattr(get_model_instance, 'instance'):
        get_model_instance.instance = MultiModelSprintLLM()
    return get_model_instance.instance

# For backward compatibility
SprintLLM = MultiModelSprintLLM 