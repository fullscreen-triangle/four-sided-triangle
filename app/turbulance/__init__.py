"""
Turbulance DSL Integration for Four-Sided Triangle

This module provides parsers and compilers to transform Turbulance syntax
into the full Kwasa-Kwasa semantic processing network.

User writes: .trb (Turbulance research protocol)
System generates:
- .fs (Network graph consciousness state)
- .ghd (Resource orchestration dependencies) 
- .hre (Metacognitive decision memory)
"""

from .parser import TurbulanceParser
from .compiler import TurbulanceCompiler
from .orchestrator import TurbulanceOrchestrator

__all__ = ["TurbulanceParser", "TurbulanceCompiler", "TurbulanceOrchestrator"] 