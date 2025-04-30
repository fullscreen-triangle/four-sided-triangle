"""
Configuration Validators for the Four-Sided Triangle system.

This module provides validation utilities for configuration files to ensure
that all required settings are present and valid.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Union, Callable
from pydantic import BaseModel, Field, validator, root_validator
from pydantic import ValidationError as PydanticValidationError

from app.utils.errors import ConfigurationError

logger = logging.getLogger(__name__)

class ApiConfig(BaseModel):
    """API configuration schema."""
    port: int = Field(default=8000, ge=1024, le=65535)
    host: str = Field(default="0.0.0.0")
    title: str = Field(default="Four Sided Triangle")
    description: str = Field(default="")
    version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    
    @validator("host")
    def validate_host(cls, v):
        """Validate host is a valid address."""
        if v != "0.0.0.0" and v != "localhost" and not v.startswith("127."):
            try:
                import socket
                socket.gethostbyname(v)
            except:
                raise ValueError(f"Invalid host address: {v}")
        return v

class ModelConfig(BaseModel):
    """Model configuration schema."""
    path: Optional[str] = Field(default=None)
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    max_tokens: int = Field(default=1500, ge=1, le=8192)
    model_id: Optional[str] = Field(default=None)
    
    @root_validator
    def validate_model_source(cls, values):
        """Validate that either path or model_id is specified."""
        path = values.get("path")
        model_id = values.get("model_id")
        
        if not path and not model_id:
            raise ValueError("Either path or model_id must be specified")
        
        # If path is specified, check if it exists
        if path and not os.path.exists(path):
            logger.warning(f"Model path does not exist: {path}")
        
        return values

class QueryConfig(BaseModel):
    """Query configuration schema."""
    max_length: int = Field(default=1000, ge=1, le=10000)
    timeout_seconds: int = Field(default=60, ge=1, le=300)
    cache_enabled: bool = Field(default=True)
    max_cache_size: int = Field(default=1000, ge=10, le=10000)

class LoggingConfig(BaseModel):
    """Logging configuration schema."""
    level: str = Field(default="INFO")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_to_file: bool = Field(default=False)
    log_file: Optional[str] = Field(default=None)
    
    @validator("level")
    def validate_level(cls, v):
        """Validate log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v.upper()
    
    @root_validator
    def validate_log_file(cls, values):
        """Validate log file path if logging to file."""
        log_to_file = values.get("log_to_file")
        log_file = values.get("log_file")
        
        if log_to_file and not log_file:
            raise ValueError("log_file must be specified if log_to_file is True")
        
        return values

class ApplicationConfig(BaseModel):
    """Full application configuration schema."""
    api: ApiConfig = Field(default_factory=ApiConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    query: QueryConfig = Field(default_factory=QueryConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    distributed: Dict[str, Any] = Field(default_factory=dict)
    database: Dict[str, Any] = Field(default_factory=dict)
    additional_settings: Dict[str, Any] = Field(default_factory=dict)

def validate_config_file(file_path: str) -> Dict[str, Any]:
    """
    Validate a JSON configuration file against the appropriate schema.
    
    Args:
        file_path: Path to the configuration file
        
    Returns:
        Validated configuration dictionary
        
    Raises:
        ConfigurationError: If the configuration is invalid
    """
    try:
        # Load the configuration file
        with open(file_path, 'r') as f:
            config_data = json.load(f)
        
        # Determine the model to use based on the file name
        file_name = os.path.basename(file_path)
        
        if file_name.endswith("api.json"):
            model = ApiConfig
        elif file_name.endswith("model.json"):
            model = ModelConfig
        elif file_name.endswith("query.json"):
            model = QueryConfig
        elif file_name.endswith("logging.json"):
            model = LoggingConfig
        elif file_name.endswith("app.json") or file_name.endswith("config.json"):
            model = ApplicationConfig
        else:
            # For unknown files, just return the data without validation
            logger.warning(f"No validation schema for {file_path}, skipping validation")
            return config_data
        
        # Validate the configuration
        validated_config = model(**config_data)
        return validated_config.dict()
        
    except FileNotFoundError:
        raise ConfigurationError(f"Configuration file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ConfigurationError(f"Invalid JSON in configuration file {file_path}: {str(e)}")
    except PydanticValidationError as e:
        raise ConfigurationError(f"Configuration validation failed for {file_path}: {str(e)}")
    except Exception as e:
        raise ConfigurationError(f"Error validating configuration file {file_path}: {str(e)}")

def validate_all_config_files(config_dir: str) -> Dict[str, Dict[str, Any]]:
    """
    Validate all JSON configuration files in the given directory.
    
    Args:
        config_dir: Directory containing configuration files
        
    Returns:
        Dictionary mapping file names to validated configurations
        
    Raises:
        ConfigurationError: If any configuration is invalid
    """
    result = {}
    errors = []
    
    try:
        # Get all JSON files in the config directory
        files = [f for f in os.listdir(config_dir) if f.endswith('.json')]
        
        for file_name in files:
            file_path = os.path.join(config_dir, file_name)
            try:
                result[file_name] = validate_config_file(file_path)
            except ConfigurationError as e:
                errors.append(str(e))
                logger.error(f"Configuration error in {file_name}: {str(e)}")
        
        if errors:
            raise ConfigurationError(f"Configuration validation failed: {'; '.join(errors)}")
        
        return result
        
    except Exception as e:
        if not isinstance(e, ConfigurationError):
            raise ConfigurationError(f"Error validating configuration files: {str(e)}")
        raise 