//! Turbulance DSL Processing System
//! 
//! This module provides comprehensive Turbulance DSL processing capabilities:
//! - Script parsing and AST generation
//! - Compilation to Four-Sided Triangle execution plans
//! - Orchestrated execution through pipeline stages
//! - Result annotation back to original scripts
//! - Integration with Rust-based evidence networks, fuzzy logic, and metacognitive optimization

pub mod parser;
pub mod compiler;
pub mod orchestrator;
pub mod annotation;

// Re-export main types for convenience
pub use parser::{TurbulanceParser, TurbulanceScript, TurbulanceNode, NodeType};
pub use compiler::{TurbulanceCompiler, CompiledProtocol, ExecutionStep};
pub use orchestrator::{TurbulanceOrchestrator, ExecutionResult, ProtocolResult};
pub use annotation::{AnnotationEngine, AnnotatedScript, ResultAnnotation};

use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use crate::error::Result;

/// Configuration for Turbulance processing
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TurbulanceConfig {
    pub enable_rust_acceleration: bool,
    pub enable_fuzzy_inference: bool,
    pub enable_bayesian_evaluation: bool,
    pub enable_evidence_networks: bool,
    pub enable_metacognitive_optimization: bool,
    pub max_execution_time_seconds: f64,
    pub confidence_threshold: f64,
    pub resource_limits: HashMap<String, f64>,
}

impl Default for TurbulanceConfig {
    fn default() -> Self {
        Self {
            enable_rust_acceleration: true,
            enable_fuzzy_inference: true,
            enable_bayesian_evaluation: true,
            enable_evidence_networks: true,
            enable_metacognitive_optimization: true,
            max_execution_time_seconds: 300.0,
            confidence_threshold: 0.8,
            resource_limits: [
                ("cpu_cores".to_string(), 8.0),
                ("memory_gb".to_string(), 32.0),
                ("gpu_units".to_string(), 2.0),
            ].iter().cloned().collect(),
        }
    }
}

/// Main Turbulance processor that coordinates all components
pub struct TurbulanceProcessor {
    parser: TurbulanceParser,
    compiler: TurbulanceCompiler,
    orchestrator: TurbulanceOrchestrator,
    annotation_engine: AnnotationEngine,
    config: TurbulanceConfig,
}

impl Default for TurbulanceProcessor {
    fn default() -> Self {
        Self::new()
    }
}

impl TurbulanceProcessor {
    pub fn new() -> Self {
        let config = TurbulanceConfig::default();
        
        Self {
            parser: TurbulanceParser::new(),
            compiler: TurbulanceCompiler::new(),
            orchestrator: TurbulanceOrchestrator::new(&config),
            annotation_engine: AnnotationEngine::new(),
            config,
        }
    }

    pub fn new_with_config(config: TurbulanceConfig) -> Self {
        Self {
            parser: TurbulanceParser::new(),
            compiler: TurbulanceCompiler::new(),
            orchestrator: TurbulanceOrchestrator::new(&config),
            annotation_engine: AnnotationEngine::new(),
            config,
        }
    }

    /// Process a complete Turbulance protocol from script to annotated results
    pub async fn process_protocol(&mut self, script_content: &str, protocol_name: &str) -> Result<AnnotatedScript> {
        // Parse the script
        let script = self.parser.parse_script(script_content, protocol_name)?;
        
        // Compile to execution plan
        let compiled_protocol = self.compiler.compile_protocol(&script)?;
        
        // Execute through Four-Sided Triangle pipeline
        let execution_result = self.orchestrator.execute_protocol(compiled_protocol).await?;
        
        // Annotate original script with results
        let annotated_script = self.annotation_engine.annotate_script(
            script_content,
            &execution_result,
            &script
        )?;
        
        Ok(annotated_script)
    }

    /// Get processing statistics
    pub fn get_statistics(&self) -> HashMap<String, f64> {
        let mut stats = HashMap::new();
        
        // Merge statistics from all components
        let parser_stats = self.parser.get_statistics();
        let compiler_stats = self.compiler.get_statistics();
        let orchestrator_stats = self.orchestrator.get_statistics();
        let annotation_stats = self.annotation_engine.get_statistics();
        
        for (key, value) in parser_stats {
            stats.insert(format!("parser_{}", key), value);
        }
        for (key, value) in compiler_stats {
            stats.insert(format!("compiler_{}", key), value);
        }
        for (key, value) in orchestrator_stats {
            stats.insert(format!("orchestrator_{}", key), value);
        }
        for (key, value) in annotation_stats {
            stats.insert(format!("annotation_{}", key), value);
        }
        
        stats
    }
}

// Python FFI functions

/// Generate a unique processor ID
fn generate_processor_id() -> String {
    format!("turbulance_{}", rand::random::<u64>())
}

#[pyfunction]
pub fn py_create_turbulance_processor(config_json: Option<&str>) -> PyResult<String> {
    let config = if let Some(config_str) = config_json {
        serde_json::from_str::<TurbulanceConfig>(config_str)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid config: {}", e)))?
    } else {
        TurbulanceConfig::default()
    };
    
    let processor = TurbulanceProcessor::new_with_config(config);
    let processor_id = generate_processor_id();
    
    let mut processors = crate::TURBULANCE_PROCESSORS.lock().unwrap();
    processors.insert(processor_id.clone(), processor);
    
    Ok(processor_id)
}

#[pyfunction]
pub fn py_process_turbulance_protocol(
    processor_id: &str,
    script_content: &str,
    protocol_name: &str,
) -> PyResult<String> {
    let runtime = tokio::runtime::Runtime::new()
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to create runtime: {}", e)))?;
    
    let mut processors = crate::TURBULANCE_PROCESSORS.lock().unwrap();
    if let Some(processor) = processors.get_mut(processor_id) {
        let result = runtime.block_on(processor.process_protocol(script_content, protocol_name))
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        
        serde_json::to_string(&result)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Serialization failed: {}", e)))
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>("Processor not found"))
    }
}

#[pyfunction]
pub fn py_get_turbulance_statistics(processor_id: &str) -> PyResult<String> {
    let processors = crate::TURBULANCE_PROCESSORS.lock().unwrap();
    if let Some(processor) = processors.get(processor_id) {
        let stats = processor.get_statistics();
        serde_json::to_string(&stats)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Serialization failed: {}", e)))
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>("Processor not found"))
    }
} 