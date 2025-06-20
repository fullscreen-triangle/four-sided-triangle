"""
Autobahn Probabilistic Reasoning Engine Interface

This module provides a comprehensive interface for connecting the Four-Sided Triangle
framework to the Autobahn Oscillatory Bio-Metabolic RAG System for all probabilistic
reasoning tasks including Bayesian inference, fuzzy logic, evidence networks, and
consciousness emergence modeling.
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import numpy as np

logger = logging.getLogger(__name__)


class AutobahnConnectionStatus(Enum):
    """Connection status to Autobahn system."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    INITIALIZING = "initializing"


class MetabolicMode(Enum):
    """Metabolic processing modes in Autobahn."""
    FLIGHT = "flight"  # High-energy rapid processing
    COLD_BLOODED = "cold_blooded"  # Energy-efficient sustained processing
    MAMMALIAN = "mammalian"  # Balanced performance and efficiency
    ANAEROBIC = "anaerobic"  # Emergency low-resource processing


class HierarchyLevel(Enum):
    """Temporal hierarchy levels for oscillatory processing."""
    PLANCK = "planck"  # 10^-44s
    QUANTUM = "quantum"  # 10^-23s
    MOLECULAR = "molecular"  # 10^-12s
    CELLULAR = "cellular"  # 10^-3s
    BIOLOGICAL = "biological"  # 1s
    PSYCHOLOGICAL = "psychological"  # 10^2s
    SOCIAL = "social"  # 10^4s
    CULTURAL = "cultural"  # 10^7s
    GEOLOGICAL = "geological"  # 10^9s
    COSMIC = "cosmic"  # 10^13s


class ConsciousnessLevel(Enum):
    """Consciousness emergence levels."""
    NONE = "none"
    MINIMAL = "minimal"
    EMERGING = "emerging"
    FUNCTIONAL = "functional"
    SELF_AWARE = "self_aware"
    METACOGNITIVE = "metacognitive"


@dataclass
class AutobahnConfiguration:
    """Configuration for Autobahn interface."""
    base_url: str = "http://localhost:8080"
    api_version: str = "v1"
    timeout_seconds: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Biological intelligence parameters
    max_frequency_hz: float = 1000.0
    atp_budget_per_query: float = 150.0
    coherence_threshold: float = 0.85
    target_entropy: float = 2.2
    immune_sensitivity: float = 0.8
    consciousness_emergence_threshold: float = 0.7
    
    # Processing preferences
    default_metabolic_mode: MetabolicMode = MetabolicMode.MAMMALIAN
    default_hierarchy_level: HierarchyLevel = HierarchyLevel.BIOLOGICAL
    enable_consciousness_modeling: bool = True
    enable_biological_processing: bool = True
    enable_oscillatory_dynamics: bool = True


@dataclass
class BayesianInferenceRequest:
    """Request for Bayesian inference processing."""
    evidence_data: Dict[str, Any]
    prior_beliefs: Dict[str, float]
    hypothesis_space: List[str]
    inference_method: str = "belief_propagation"  # belief_propagation, variational_bayes, mcmc, particle_filter
    confidence_threshold: float = 0.7
    metabolic_mode: MetabolicMode = MetabolicMode.MAMMALIAN
    hierarchy_level: HierarchyLevel = HierarchyLevel.BIOLOGICAL


@dataclass
class FuzzyLogicRequest:
    """Request for fuzzy logic processing."""
    fuzzy_sets: List[Dict[str, Any]]
    rules: List[Dict[str, Any]]
    input_variables: Dict[str, float]
    defuzzification_method: str = "centroid"
    t_norm: str = "minimum"
    s_norm: str = "maximum"
    linguistic_hedges: Optional[Dict[str, float]] = None


@dataclass
class EvidenceNetworkRequest:
    """Request for evidence network processing."""
    network_structure: Dict[str, Any]
    evidence_updates: List[Dict[str, Any]]
    query_nodes: List[str]
    propagation_algorithm: str = "belief_propagation"
    temporal_decay_factor: float = 0.95
    uncertainty_modeling: bool = True


@dataclass
class MetacognitiveOptimizationRequest:
    """Request for metacognitive optimization."""
    decision_context: Dict[str, Any]
    available_strategies: List[Dict[str, Any]]
    optimization_objectives: List[Dict[str, Any]]
    constraints: List[Dict[str, Any]]
    learning_enabled: bool = True
    consciousness_integration: bool = True


@dataclass
class ProbabilisticReasoningRequest:
    """General probabilistic reasoning request."""
    query_type: str  # "bayesian", "fuzzy", "evidence_network", "metacognitive", "consciousness"
    input_data: Dict[str, Any]
    processing_parameters: Dict[str, Any]
    quality_requirements: Dict[str, float]
    resource_constraints: Dict[str, float]


@dataclass
class AutobahnResponse:
    """Response from Autobahn system."""
    success: bool
    result: Dict[str, Any]
    quality_score: float
    consciousness_level: float
    atp_consumption: float
    membrane_coherence: float
    entropy_optimization: float
    processing_time: float
    oscillatory_efficiency: float
    immune_system_health: float
    phi_value: Optional[float] = None  # IIT consciousness measurement
    threat_analysis: Optional[Dict[str, Any]] = None
    metabolic_state: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class AutobahnInterface:
    """
    Interface for connecting to the Autobahn Oscillatory Bio-Metabolic RAG System.
    Handles all probabilistic reasoning tasks including Bayesian inference, fuzzy logic,
    evidence networks, and consciousness emergence modeling.
    """
    
    def __init__(self, config: Optional[AutobahnConfiguration] = None):
        self.config = config or AutobahnConfiguration()
        self.connection_status = AutobahnConnectionStatus.DISCONNECTED
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(__name__)
        
        # Performance tracking
        self.request_count = 0
        self.total_processing_time = 0.0
        self.average_quality_score = 0.0
        self.average_consciousness_level = 0.0
        
        # Circuit breaker for fault tolerance
        self.circuit_breaker_failures = 0
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_reset_time = 60.0
        self.last_failure_time = 0.0
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    async def connect(self) -> bool:
        """Establish connection to Autobahn system."""
        try:
            self.connection_status = AutobahnConnectionStatus.INITIALIZING
            
            # Create aiohttp session with custom timeout
            timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            self.session = aiohttp.ClientSession(timeout=timeout)
            
            # Test connection with health check
            health_status = await self._health_check()
            if health_status:
                self.connection_status = AutobahnConnectionStatus.CONNECTED
                self.logger.info("Successfully connected to Autobahn system")
                return True
            else:
                self.connection_status = AutobahnConnectionStatus.ERROR
                self.logger.error("Failed to connect to Autobahn system")
                return False
                
        except Exception as e:
            self.connection_status = AutobahnConnectionStatus.ERROR
            self.logger.error(f"Error connecting to Autobahn: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Autobahn system."""
        if self.session:
            await self.session.close()
            self.session = None
        self.connection_status = AutobahnConnectionStatus.DISCONNECTED
        self.logger.info("Disconnected from Autobahn system")
    
    async def _health_check(self) -> bool:
        """Check if Autobahn system is healthy and responsive."""
        try:
            url = f"{self.config.base_url}/{self.config.api_version}/health"
            async with self.session.get(url) as response:
                if response.status == 200:
                    health_data = await response.json()
                    return health_data.get("status") == "healthy"
                return False
        except Exception as e:
            self.logger.warning(f"Health check failed: {e}")
            return False
    
    def _is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open due to repeated failures."""
        if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
            if time.time() - self.last_failure_time < self.circuit_breaker_reset_time:
                return True
            else:
                # Reset circuit breaker after timeout
                self.circuit_breaker_failures = 0
        return False
    
    def _record_failure(self):
        """Record a failure for circuit breaker logic."""
        self.circuit_breaker_failures += 1
        self.last_failure_time = time.time()
    
    def _record_success(self):
        """Record a success, resetting circuit breaker if needed."""
        self.circuit_breaker_failures = max(0, self.circuit_breaker_failures - 1)
    
    async def _make_request(self, endpoint: str, data: Dict[str, Any], retries: int = None) -> AutobahnResponse:
        """Make HTTP request to Autobahn with retry logic."""
        if retries is None:
            retries = self.config.max_retries
        
        # Check circuit breaker
        if self._is_circuit_breaker_open():
            return AutobahnResponse(
                success=False,
                result={},
                quality_score=0.0,
                consciousness_level=0.0,
                atp_consumption=0.0,
                membrane_coherence=0.0,
                entropy_optimization=0.0,
                processing_time=0.0,
                oscillatory_efficiency=0.0,
                immune_system_health=0.0,
                error_message="Circuit breaker open - too many failures"
            )
        
        url = f"{self.config.base_url}/{self.config.api_version}/{endpoint}"
        
        for attempt in range(retries + 1):
            try:
                start_time = time.time()
                
                async with self.session.post(url, json=data) as response:
                    processing_time = time.time() - start_time
                    
                    if response.status == 200:
                        result_data = await response.json()
                        
                        # Parse response
                        autobahn_response = AutobahnResponse(
                            success=True,
                            result=result_data.get("result", {}),
                            quality_score=result_data.get("quality_score", 0.0),
                            consciousness_level=result_data.get("consciousness_level", 0.0),
                            atp_consumption=result_data.get("atp_consumption", 0.0),
                            membrane_coherence=result_data.get("membrane_coherence", 0.0),
                            entropy_optimization=result_data.get("entropy_optimization", 0.0),
                            processing_time=processing_time,
                            oscillatory_efficiency=result_data.get("oscillatory_efficiency", 0.0),
                            immune_system_health=result_data.get("immune_system_health", 0.0),
                            phi_value=result_data.get("phi_value"),
                            threat_analysis=result_data.get("threat_analysis"),
                            metabolic_state=result_data.get("metabolic_state")
                        )
                        
                        # Update statistics
                        self._update_statistics(autobahn_response)
                        self._record_success()
                        
                        return autobahn_response
                    
                    elif response.status == 429:  # Rate limited
                        await asyncio.sleep(self.config.retry_delay * (attempt + 1))
                        continue
                    
                    else:
                        error_text = await response.text()
                        raise Exception(f"HTTP {response.status}: {error_text}")
            
            except Exception as e:
                if attempt == retries:
                    self._record_failure()
                    return AutobahnResponse(
                        success=False,
                        result={},
                        quality_score=0.0,
                        consciousness_level=0.0,
                        atp_consumption=0.0,
                        membrane_coherence=0.0,
                        entropy_optimization=0.0,
                        processing_time=time.time() - start_time,
                        oscillatory_efficiency=0.0,
                        immune_system_health=0.0,
                        error_message=str(e)
                    )
                
                # Wait before retrying
                await asyncio.sleep(self.config.retry_delay * (attempt + 1))
        
        # Should not reach here
        return AutobahnResponse(
            success=False,
            result={},
            quality_score=0.0,
            consciousness_level=0.0,
            atp_consumption=0.0,
            membrane_coherence=0.0,
            entropy_optimization=0.0,
            processing_time=0.0,
            oscillatory_efficiency=0.0,
            immune_system_health=0.0,
            error_message="Maximum retries exceeded"
        )
    
    def _update_statistics(self, response: AutobahnResponse):
        """Update performance statistics."""
        self.request_count += 1
        self.total_processing_time += response.processing_time
        
        # Running average for quality and consciousness
        alpha = 1.0 / self.request_count
        self.average_quality_score = (1 - alpha) * self.average_quality_score + alpha * response.quality_score
        self.average_consciousness_level = (1 - alpha) * self.average_consciousness_level + alpha * response.consciousness_level
    
    # Core Probabilistic Reasoning Methods
    
    async def bayesian_inference(self, request: BayesianInferenceRequest) -> AutobahnResponse:
        """Perform Bayesian inference using Autobahn's biological intelligence."""
        data = {
            "evidence_data": request.evidence_data,
            "prior_beliefs": request.prior_beliefs,
            "hypothesis_space": request.hypothesis_space,
            "inference_method": request.inference_method,
            "confidence_threshold": request.confidence_threshold,
            "metabolic_mode": request.metabolic_mode.value,
            "hierarchy_level": request.hierarchy_level.value,
            "enable_consciousness": self.config.enable_consciousness_modeling,
            "enable_biological": self.config.enable_biological_processing,
            "atp_budget": self.config.atp_budget_per_query
        }
        
        return await self._make_request("bayesian_inference", data)
    
    async def fuzzy_logic_processing(self, request: FuzzyLogicRequest) -> AutobahnResponse:
        """Process fuzzy logic using Autobahn's oscillatory dynamics."""
        data = {
            "fuzzy_sets": request.fuzzy_sets,
            "rules": request.rules,
            "input_variables": request.input_variables,
            "defuzzification_method": request.defuzzification_method,
            "t_norm": request.t_norm,
            "s_norm": request.s_norm,
            "linguistic_hedges": request.linguistic_hedges or {},
            "oscillatory_optimization": self.config.enable_oscillatory_dynamics,
            "coherence_threshold": self.config.coherence_threshold,
            "target_entropy": self.config.target_entropy
        }
        
        return await self._make_request("fuzzy_logic", data)
    
    async def evidence_network_processing(self, request: EvidenceNetworkRequest) -> AutobahnResponse:
        """Process evidence networks using Autobahn's membrane intelligence."""
        data = {
            "network_structure": request.network_structure,
            "evidence_updates": request.evidence_updates,
            "query_nodes": request.query_nodes,
            "propagation_algorithm": request.propagation_algorithm,
            "temporal_decay_factor": request.temporal_decay_factor,
            "uncertainty_modeling": request.uncertainty_modeling,
            "membrane_coherence": self.config.enable_biological_processing,
            "consciousness_integration": self.config.enable_consciousness_modeling,
            "immune_protection": True
        }
        
        return await self._make_request("evidence_network", data)
    
    async def metacognitive_optimization(self, request: MetacognitiveOptimizationRequest) -> AutobahnResponse:
        """Perform metacognitive optimization using Autobahn's consciousness emergence."""
        data = {
            "decision_context": request.decision_context,
            "available_strategies": request.available_strategies,
            "optimization_objectives": request.optimization_objectives,
            "constraints": request.constraints,
            "learning_enabled": request.learning_enabled,
            "consciousness_integration": request.consciousness_integration,
            "consciousness_threshold": self.config.consciousness_emergence_threshold,
            "metabolic_mode": self.config.default_metabolic_mode.value,
            "hierarchy_level": self.config.default_hierarchy_level.value,
            "fire_circle_communication": True,
            "dual_proximity_signaling": True
        }
        
        return await self._make_request("metacognitive_optimization", data)
    
    async def consciousness_emergence_modeling(self, 
                                             integrated_information: Dict[str, Any],
                                             workspace_activity: Dict[str, float],
                                             self_awareness_level: float = 0.5,
                                             metacognition_level: float = 0.5) -> AutobahnResponse:
        """Model consciousness emergence using Autobahn's IIT implementation."""
        data = {
            "integrated_information": integrated_information,
            "workspace_activity": workspace_activity,
            "self_awareness_level": self_awareness_level,
            "metacognition_level": metacognition_level,
            "calculate_phi": True,
            "global_workspace_integration": True,
            "agency_illusion": True,
            "persistence_illusion": True,
            "biological_membrane_coherence": self.config.enable_biological_processing,
            "oscillatory_dynamics": self.config.enable_oscillatory_dynamics
        }
        
        return await self._make_request("consciousness_emergence", data)
    
    async def biological_immune_analysis(self, 
                                       input_data: Dict[str, Any],
                                       threat_sensitivity: float = None) -> AutobahnResponse:
        """Analyze threats using Autobahn's biological immune system."""
        data = {
            "input_data": input_data,
            "threat_sensitivity": threat_sensitivity or self.config.immune_sensitivity,
            "t_cell_simulation": True,
            "b_cell_simulation": True,
            "memory_cell_learning": True,
            "adaptive_threat_detection": True,
            "coherence_interference_detection": True,
            "metabolic_attack_prevention": True
        }
        
        return await self._make_request("immune_analysis", data)
    
    async def entropy_optimization(self, 
                                 data_input: Dict[str, Any],
                                 optimization_strategy: str = "predictive_ml") -> AutobahnResponse:
        """Optimize entropy using Autobahn's ML-enhanced optimization."""
        data = {
            "data_input": data_input,
            "optimization_strategy": optimization_strategy,
            "target_entropy": self.config.target_entropy,
            "cross_hierarchy_correlation": True,
            "emergence_pattern_detection": True,
            "gradient_descent_optimization": True,
            "predictive_termination": True,
            "consciousness_integration": self.config.enable_consciousness_modeling
        }
        
        return await self._make_request("entropy_optimization", data)
    
    # High-level Integration Methods
    
    async def process_probabilistic_query(self, request: ProbabilisticReasoningRequest) -> AutobahnResponse:
        """Process a general probabilistic reasoning query."""
        # Route to appropriate specialized method based on query type
        if request.query_type == "bayesian":
            bayesian_request = BayesianInferenceRequest(
                evidence_data=request.input_data.get("evidence_data", {}),
                prior_beliefs=request.input_data.get("prior_beliefs", {}),
                hypothesis_space=request.input_data.get("hypothesis_space", []),
                inference_method=request.processing_parameters.get("inference_method", "belief_propagation")
            )
            return await self.bayesian_inference(bayesian_request)
        
        elif request.query_type == "fuzzy":
            fuzzy_request = FuzzyLogicRequest(
                fuzzy_sets=request.input_data.get("fuzzy_sets", []),
                rules=request.input_data.get("rules", []),
                input_variables=request.input_data.get("input_variables", {}),
                defuzzification_method=request.processing_parameters.get("defuzzification_method", "centroid")
            )
            return await self.fuzzy_logic_processing(fuzzy_request)
        
        elif request.query_type == "evidence_network":
            network_request = EvidenceNetworkRequest(
                network_structure=request.input_data.get("network_structure", {}),
                evidence_updates=request.input_data.get("evidence_updates", []),
                query_nodes=request.input_data.get("query_nodes", []),
                propagation_algorithm=request.processing_parameters.get("propagation_algorithm", "belief_propagation")
            )
            return await self.evidence_network_processing(network_request)
        
        elif request.query_type == "metacognitive":
            metacognitive_request = MetacognitiveOptimizationRequest(
                decision_context=request.input_data.get("decision_context", {}),
                available_strategies=request.input_data.get("available_strategies", []),
                optimization_objectives=request.input_data.get("optimization_objectives", []),
                constraints=request.input_data.get("constraints", [])
            )
            return await self.metacognitive_optimization(metacognitive_request)
        
        elif request.query_type == "consciousness":
            return await self.consciousness_emergence_modeling(
                integrated_information=request.input_data.get("integrated_information", {}),
                workspace_activity=request.input_data.get("workspace_activity", {}),
                self_awareness_level=request.input_data.get("self_awareness_level", 0.5),
                metacognition_level=request.input_data.get("metacognition_level", 0.5)
            )
        
        else:
            # Generic processing
            data = {
                "query_type": request.query_type,
                "input_data": request.input_data,
                "processing_parameters": request.processing_parameters,
                "quality_requirements": request.quality_requirements,
                "resource_constraints": request.resource_constraints,
                "consciousness_integration": self.config.enable_consciousness_modeling,
                "biological_processing": self.config.enable_biological_processing,
                "oscillatory_dynamics": self.config.enable_oscillatory_dynamics
            }
            
            return await self._make_request("general_probabilistic", data)
    
    async def optimize_four_sided_triangle_pipeline(self, 
                                                  pipeline_context: Dict[str, Any],
                                                  stage_performance_data: Dict[str, float],
                                                  quality_requirements: Dict[str, float],
                                                  resource_constraints: Dict[str, float]) -> AutobahnResponse:
        """Optimize the Four-Sided Triangle pipeline using Autobahn's metacognitive capabilities."""
        
        # Prepare optimization request for the 8-stage pipeline
        strategies = [
            {"id": "query_complexity_adaptation", "type": "query_optimization", "stage": 0},
            {"id": "semantic_retrieval_optimization", "type": "retrieval_strategy", "stage": 1},
            {"id": "domain_knowledge_selection", "type": "knowledge_strategy", "stage": 2},
            {"id": "reasoning_optimization", "type": "reasoning_strategy", "stage": 3},
            {"id": "solution_generation_optimization", "type": "generation_strategy", "stage": 4},
            {"id": "quality_scoring_optimization", "type": "scoring_strategy", "stage": 5},
            {"id": "response_comparison_optimization", "type": "comparison_strategy", "stage": 6},
            {"id": "verification_optimization", "type": "verification_strategy", "stage": 7}
        ]
        
        objectives = [
            {"name": "output_quality", "weight": 0.4, "target": quality_requirements.get("quality", 0.9)},
            {"name": "processing_efficiency", "weight": 0.3, "target": quality_requirements.get("efficiency", 0.8)},
            {"name": "user_satisfaction", "weight": 0.2, "target": quality_requirements.get("satisfaction", 0.9)},
            {"name": "resource_efficiency", "weight": 0.1, "target": 0.8}
        ]
        
        constraints = [
            {"variable": "processing_time", "type": "upper_bound", "value": resource_constraints.get("time", 10.0)},
            {"variable": "memory_usage", "type": "upper_bound", "value": resource_constraints.get("memory", 0.8)},
            {"variable": "cpu_usage", "type": "upper_bound", "value": resource_constraints.get("cpu", 0.8)}
        ]
        
        request = MetacognitiveOptimizationRequest(
            decision_context=pipeline_context,
            available_strategies=strategies,
            optimization_objectives=objectives,
            constraints=constraints,
            learning_enabled=True,
            consciousness_integration=True
        )
        
        return await self.metacognitive_optimization(request)
    
    # System Status and Statistics
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and performance metrics."""
        try:
            if self.connection_status != AutobahnConnectionStatus.CONNECTED:
                return {
                    "connection_status": self.connection_status.value,
                    "error": "Not connected to Autobahn system"
                }
            
            response = await self._make_request("system/status", {})
            
            if response.success:
                return {
                    "connection_status": self.connection_status.value,
                    "autobahn_status": response.result,
                    "interface_statistics": {
                        "request_count": self.request_count,
                        "average_processing_time": self.total_processing_time / max(1, self.request_count),
                        "average_quality_score": self.average_quality_score,
                        "average_consciousness_level": self.average_consciousness_level,
                        "circuit_breaker_failures": self.circuit_breaker_failures
                    }
                }
            else:
                return {
                    "connection_status": self.connection_status.value,
                    "error": response.error_message
                }
        
        except Exception as e:
            return {
                "connection_status": "error",
                "error": str(e)
            }
    
    def get_interface_statistics(self) -> Dict[str, Any]:
        """Get interface performance statistics."""
        return {
            "request_count": self.request_count,
            "total_processing_time": self.total_processing_time,
            "average_processing_time": self.total_processing_time / max(1, self.request_count),
            "average_quality_score": self.average_quality_score,
            "average_consciousness_level": self.average_consciousness_level,
            "connection_status": self.connection_status.value,
            "circuit_breaker_failures": self.circuit_breaker_failures,
            "circuit_breaker_open": self._is_circuit_breaker_open()
        }
    
    def reset_statistics(self):
        """Reset performance statistics."""
        self.request_count = 0
        self.total_processing_time = 0.0
        self.average_quality_score = 0.0
        self.average_consciousness_level = 0.0
        self.circuit_breaker_failures = 0
        self.last_failure_time = 0.0


# Global instance for easy access
autobahn_interface = AutobahnInterface()


# Convenience functions for direct access
async def initialize_autobahn(config: Optional[AutobahnConfiguration] = None) -> bool:
    """Initialize connection to Autobahn system."""
    global autobahn_interface
    if config:
        autobahn_interface = AutobahnInterface(config)
    return await autobahn_interface.connect()


async def shutdown_autobahn():
    """Shutdown connection to Autobahn system."""
    global autobahn_interface
    await autobahn_interface.disconnect()


async def process_bayesian_inference(evidence_data: Dict[str, Any], 
                                   prior_beliefs: Dict[str, float],
                                   hypothesis_space: List[str],
                                   method: str = "belief_propagation") -> AutobahnResponse:
    """Direct access to Bayesian inference processing."""
    request = BayesianInferenceRequest(
        evidence_data=evidence_data,
        prior_beliefs=prior_beliefs,
        hypothesis_space=hypothesis_space,
        inference_method=method
    )
    return await autobahn_interface.bayesian_inference(request)


async def process_fuzzy_logic(fuzzy_sets: List[Dict[str, Any]],
                            rules: List[Dict[str, Any]], 
                            input_variables: Dict[str, float]) -> AutobahnResponse:
    """Direct access to fuzzy logic processing."""
    request = FuzzyLogicRequest(
        fuzzy_sets=fuzzy_sets,
        rules=rules,
        input_variables=input_variables
    )
    return await autobahn_interface.fuzzy_logic_processing(request)


async def process_evidence_network(network_structure: Dict[str, Any],
                                 evidence_updates: List[Dict[str, Any]],
                                 query_nodes: List[str],
                                 algorithm: str = "belief_propagation") -> AutobahnResponse:
    """Direct access to evidence network processing."""
    request = EvidenceNetworkRequest(
        network_structure=network_structure,
        evidence_updates=evidence_updates,
        query_nodes=query_nodes,
        propagation_algorithm=algorithm
    )
    return await autobahn_interface.evidence_network_processing(request)


async def optimize_metacognitive_decision(decision_context: Dict[str, Any],
                                        strategies: List[Dict[str, Any]],
                                        objectives: List[Dict[str, Any]],
                                        constraints: List[Dict[str, Any]]) -> AutobahnResponse:
    """Direct access to metacognitive optimization."""
    request = MetacognitiveOptimizationRequest(
        decision_context=decision_context,
        available_strategies=strategies,
        optimization_objectives=objectives,
        constraints=constraints
    )
    return await autobahn_interface.metacognitive_optimization(request)


async def model_consciousness_emergence(integrated_info: Dict[str, Any],
                                      workspace_activity: Dict[str, float]) -> AutobahnResponse:
    """Direct access to consciousness emergence modeling."""
    return await autobahn_interface.consciousness_emergence_modeling(
        integrated_information=integrated_info,
        workspace_activity=workspace_activity
    )