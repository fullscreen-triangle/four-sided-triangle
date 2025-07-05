//! Turbulance DSL Integration Module
//! 
//! Provides complete Turbulance DSL support for Four-Sided Triangle, including parsing,
//! compilation, orchestration, and result annotation.

pub mod parser;
pub mod compiler;
pub mod orchestrator;
pub mod annotation;
pub mod processor;

// Re-export key types for convenient access
pub use parser::{TurbulanceParser, TurbulanceScript, TurbulanceValue, TurbulanceNode};
pub use compiler::{TurbulanceCompiler, CompiledProtocol, ExecutionStep, ExecutionMode};
pub use orchestrator::{TurbulanceOrchestrator, ExecutionResult, StepResult, QualityMetrics};
pub use annotation::{TurbulanceAnnotator, AnnotatedScript, AnnotationSummary};
pub use processor::{TurbulanceProcessor, ProcessingConfig, ProcessingResult};

// Python FFI function exports
use pyo3::prelude::*;

/// Python module for Turbulance DSL functionality
#[pymodule]
pub fn turbulance_dsl(_py: Python, m: &PyModule) -> PyResult<()> {
    // Parser functions
    m.add_function(wrap_pyfunction!(parser::py_parse_turbulance_script, m)?)?;
    m.add_function(wrap_pyfunction!(parser::py_get_parser_statistics, m)?)?;
    
    // Compiler functions
    m.add_function(wrap_pyfunction!(compiler::py_compile_turbulance_protocol, m)?)?;
    
    // Orchestrator functions
    m.add_function(wrap_pyfunction!(orchestrator::py_execute_turbulance_protocol, m)?)?;
    m.add_function(wrap_pyfunction!(orchestrator::py_get_orchestrator_statistics, m)?)?;
    
    // Annotation functions
    m.add_function(wrap_pyfunction!(annotation::py_annotate_turbulance_script, m)?)?;
    m.add_function(wrap_pyfunction!(annotation::py_get_annotator_statistics, m)?)?;
    
    // Main processor functions
    m.add_function(wrap_pyfunction!(processor::py_process_turbulance_script, m)?)?;
    m.add_function(wrap_pyfunction!(processor::py_get_processor_statistics, m)?)?;
    
    Ok(())
} 