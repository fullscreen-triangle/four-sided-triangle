"""
Turbulance DSL Integration for Four-Sided Triangle

This module provides parsers and compilers to transform Turbulance syntax
into executable Four-Sided Triangle pipeline sequences.

User writes: .trb (Turbulance research protocol)
System outputs: executed pipeline with annotated results

Supports Python-native implementation with optional Rust acceleration.
"""

import json
import logging
from typing import Dict, Any, Optional

from .parser import TurbulanceParser
from .compiler import TurbulanceCompiler
from .orchestrator import TurbulanceOrchestrator

# Try to import Rust acceleration functions
try:
    import four_sided_triangle_core as rust_core
    RUST_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("Rust acceleration available for Turbulance DSL")
except ImportError:
    RUST_AVAILABLE = False
    rust_core = None
    logger = logging.getLogger(__name__)
    logger.warning("Rust acceleration not available, using Python implementation")

class TurbulanceProcessor:
    """
    High-level processor that coordinates parsing, compilation, and execution
    with optional Rust acceleration.
    """
    
    def __init__(self, use_rust_acceleration: bool = True):
        """
        Initialize the Turbulance processor.
        
        Args:
            use_rust_acceleration: Whether to use Rust implementation when available
        """
        self.use_rust = use_rust_acceleration and RUST_AVAILABLE
        self.processor_id = None
        
        if self.use_rust:
            try:
                # Create Rust processor
                config = {
                    "enable_rust_acceleration": True,
                    "enable_fuzzy_inference": True,
                    "enable_bayesian_evaluation": True,
                    "enable_evidence_networks": True,
                    "enable_metacognitive_optimization": True,
                    "max_execution_time_seconds": 300.0,
                    "confidence_threshold": 0.8
                }
                self.processor_id = rust_core.py_create_turbulance_processor(json.dumps(config))
                logger.info(f"Created Rust Turbulance processor: {self.processor_id}")
            except Exception as e:
                logger.warning(f"Failed to create Rust processor, falling back to Python: {e}")
                self.use_rust = False
        
        # Always create Python components as fallback
        self.python_parser = TurbulanceParser()
        self.python_compiler = TurbulanceCompiler()
        self.python_orchestrator = TurbulanceOrchestrator()
    
    async def process_script(self, script_content: str, protocol_name: str) -> Dict[str, Any]:
        """
        Process a complete Turbulance script from parsing to execution.
        
        Args:
            script_content: The Turbulance script content
            protocol_name: Name of the research protocol
            
        Returns:
            Complete processing result with annotated script
        """
        if self.use_rust and self.processor_id:
            try:
                # Use Rust implementation
                result_json = rust_core.py_process_turbulance_script(
                    self.processor_id, script_content, protocol_name
                )
                return json.loads(result_json)
            except Exception as e:
                logger.error(f"Rust processing failed, falling back to Python: {e}")
                # Fall through to Python implementation
        
        # Use Python implementation
        return await self.python_orchestrator.execute_protocol(script_content, protocol_name)
    
    def parse_script(self, script_content: str, protocol_name: str) -> Dict[str, Any]:
        """
        Parse a Turbulance script.
        
        Args:
            script_content: The script content to parse
            protocol_name: Name of the protocol
            
        Returns:
            Parsed script structure
        """
        if self.use_rust:
            try:
                result_json = rust_core.py_parse_turbulance_script(script_content, protocol_name)
                return json.loads(result_json)
            except Exception as e:
                logger.error(f"Rust parsing failed, falling back to Python: {e}")
        
        # Use Python implementation
        parsed_script = self.python_parser.parse_script(script_content, protocol_name)
        return parsed_script.__dict__
    
    def compile_script(self, script_content: str, protocol_name: str) -> Dict[str, Any]:
        """
        Compile a Turbulance script into executable protocol.
        
        Args:
            script_content: The script content to compile
            protocol_name: Name of the protocol
            
        Returns:
            Compiled protocol
        """
        if self.use_rust:
            try:
                # First parse with Rust
                parsed_json = rust_core.py_parse_turbulance_script(script_content, protocol_name)
                # Then compile
                compiled_json = rust_core.py_compile_turbulance_protocol(parsed_json)
                return json.loads(compiled_json)
            except Exception as e:
                logger.error(f"Rust compilation failed, falling back to Python: {e}")
        
        # Use Python implementation
        parsed_script = self.python_parser.parse_script(script_content, protocol_name)
        compiled_protocol = self.python_compiler.compile_protocol(parsed_script)
        return compiled_protocol.__dict__
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get processing statistics.
        
        Returns:
            Statistics from the processor
        """
        stats = {
            "rust_acceleration": self.use_rust,
            "processor_type": "rust" if self.use_rust else "python"
        }
        
        if self.use_rust and self.processor_id:
            try:
                rust_stats_json = rust_core.py_get_processor_statistics(self.processor_id)
                rust_stats = json.loads(rust_stats_json)
                stats.update(rust_stats)
            except Exception as e:
                logger.error(f"Failed to get Rust statistics: {e}")
        
        # Add Python orchestrator stats
        python_stats = self.python_orchestrator.get_execution_stats()
        stats["python_orchestrator"] = python_stats
        
        return stats
    
    def __del__(self):
        """Clean up Rust processor when object is destroyed."""
        if self.use_rust and self.processor_id:
            try:
                rust_core.py_remove_processor(self.processor_id)
            except Exception as e:
                logger.error(f"Failed to clean up Rust processor: {e}")

# Convenience functions for direct access to Rust functions
def parse_with_rust(script_content: str, protocol_name: str) -> Optional[Dict[str, Any]]:
    """Parse script using Rust implementation directly."""
    if not RUST_AVAILABLE:
        return None
    
    try:
        result_json = rust_core.py_parse_turbulance_script(script_content, protocol_name)
        return json.loads(result_json)
    except Exception as e:
        logger.error(f"Rust parsing error: {e}")
        return None

def get_rust_parser_statistics() -> Optional[Dict[str, Any]]:
    """Get parser statistics from Rust implementation."""
    if not RUST_AVAILABLE:
        return None
    
    try:
        stats_json = rust_core.py_get_parser_statistics()
        return json.loads(stats_json)
    except Exception as e:
        logger.error(f"Failed to get Rust parser statistics: {e}")
        return None

def get_rust_orchestrator_statistics() -> Optional[Dict[str, Any]]:
    """Get orchestrator statistics from Rust implementation."""
    if not RUST_AVAILABLE:
        return None
    
    try:
        stats_json = rust_core.py_get_orchestrator_statistics()
        return json.loads(stats_json)
    except Exception as e:
        logger.error(f"Failed to get Rust orchestrator statistics: {e}")
        return None

# Export main classes and processor
__all__ = [
    "TurbulanceParser", 
    "TurbulanceCompiler", 
    "TurbulanceOrchestrator",
    "TurbulanceProcessor",
    "parse_with_rust",
    "get_rust_parser_statistics", 
    "get_rust_orchestrator_statistics",
    "RUST_AVAILABLE"
] 