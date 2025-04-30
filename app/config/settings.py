import os
from pathlib import Path
from typing import List, Union
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    """Application settings."""
    
    # Base settings
    debug: bool = Field(os.getenv("DEBUG", "False") == "True", description="Debug mode")
    app_title: str = Field(os.getenv("APP_TITLE", "Four Sided Triangle API"), description="Application title")
    app_description: str = Field(os.getenv("APP_DESCRIPTION", "API for the Four Sided Triangle sprint running domain expert system"), description="Application description")
    app_version: str = Field(os.getenv("APP_VERSION", "1.0.0"), description="Application version")
    
    # API settings
    api_port: int = Field(int(os.getenv("PORT", "8000")), description="API port")
    api_host: str = Field(os.getenv("HOST", "0.0.0.0"), description="API host")
    
    # CORS settings
    cors_origins: List[str] = Field(
        os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
        description="CORS allowed origins"
    )
    
    # Frontend settings
    frontend_url: str = Field(os.getenv("FRONTEND_URL", "http://localhost:3000"), description="Frontend URL")
    
    # Model settings
    model_path: str = Field(os.getenv("MODEL_PATH", "./sprint-llm-distilled"), description="Model path")
    max_query_length: int = Field(int(os.getenv("MAX_QUERY_LENGTH", "1000")), description="Maximum query length")
    model_temperature: float = Field(float(os.getenv("MODEL_TEMPERATURE", "0.7")), description="Model temperature")
    model_top_p: float = Field(float(os.getenv("MODEL_TOP_P", "0.9")), description="Model top p")
    max_tokens: int = Field(int(os.getenv("MAX_TOKENS", "512")), description="Maximum tokens")
    
    # LLM API settings
    openai_api_key: str = Field(os.getenv("OPENAI_API_KEY", ""), description="OpenAI API key")
    anthropic_api_key: str = Field(os.getenv("ANTHROPIC_API_KEY", ""), description="Anthropic API key")
    
    # Additional verification settings
    quality_thresholds: dict = Field({
        "accuracy": 0.7,
        "completeness": 0.7,
        "consistency": 0.7,
        "relevance": 0.8,
        "novelty": 0.5
    }, description="Quality thresholds for verification")
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False 