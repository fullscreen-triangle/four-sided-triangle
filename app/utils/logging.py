"""
Standardized Logging Setup for the Four-Sided Triangle system.

This module provides consistent logging configuration across all components
of the Four-Sided Triangle system.
"""

import logging
import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional, Union
from pathlib import Path

# Default log format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Log level mapping
LOG_LEVEL_MAP = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

def configure_logging(
    level: Union[str, int] = "info",
    log_format: str = DEFAULT_LOG_FORMAT,
    log_file: Optional[str] = None,
    log_to_console: bool = True,
    log_directory: Optional[str] = None
) -> None:
    """
    Configure logging for the entire application.
    
    Args:
        level: Log level, either as string or as logging module constant
        log_format: Format string for log messages
        log_file: Path to log file, or None for no file logging
        log_to_console: Whether to log to console
        log_directory: Directory for log files, creates if not exists
    """
    # Convert string level to logging constant if needed
    if isinstance(level, str):
        level = LOG_LEVEL_MAP.get(level.lower(), logging.INFO)
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    formatter = logging.Formatter(log_format)
    
    # Add console handler if requested
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Add file handler if log file specified
    if log_file:
        # Create log directory if needed
        if log_directory:
            log_dir_path = Path(log_directory)
            log_dir_path.mkdir(parents=True, exist_ok=True)
            log_file_path = log_dir_path / log_file
        else:
            log_file_path = Path(log_file)
            
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Log the configuration
    logging.info(f"Logging configured with level={logging.getLevelName(level)}")
    if log_file:
        logging.info(f"Logging to file: {log_file_path}")

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.
    
    This is a wrapper around logging.getLogger that ensures consistent usage
    across the codebase.
    
    Args:
        name: Logger name, typically __name__ of the calling module
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

def load_logging_config(config_file: str) -> Dict[str, Any]:
    """
    Load logging configuration from a JSON file.
    
    Args:
        config_file: Path to JSON configuration file
        
    Returns:
        Dictionary with configuration options
        
    Raises:
        FileNotFoundError: If the config file doesn't exist
        json.JSONDecodeError: If the config file isn't valid JSON
    """
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    return config

def configure_logging_from_file(config_file: str) -> None:
    """
    Configure logging from a JSON configuration file.
    
    Args:
        config_file: Path to configuration file
        
    Raises:
        FileNotFoundError: If the config file doesn't exist
        json.JSONDecodeError: If the config file isn't valid JSON
    """
    config = load_logging_config(config_file)
    
    configure_logging(
        level=config.get("level", "info"),
        log_format=config.get("format", DEFAULT_LOG_FORMAT),
        log_file=config.get("log_file"),
        log_to_console=config.get("log_to_console", True),
        log_directory=config.get("log_directory")
    )
    
    logging.info(f"Logging configured from {config_file}") 