//! Turbulance DSL Main Processor
//! 
//! Coordinates all Turbulance components to provide a complete script processing pipeline
//! from original script to annotated results with execution outputs.

use crate::error::{FourSidedTriangleError, Result};
use crate::{validation_error};
use super::parser::{TurbulanceParser, TurbulanceScript};
use super::compiler::TurbulanceCompiler;
use super::orchestrator::TurbulanceOrchestrator;
use super::annotation::TurbulanceAnnotator;
use super::annotation::AnnotatedScript;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use once_cell::sync::Lazy;

/// Configuration for Turbulance processing
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProcessingConfig {
    pub enable_rust_acceleration: bool,
    pub enable_fuzzy_inference: bool,
    pub enable_bayesian_evaluation: bool,
    pub enable_evidence_networks: bool,
    pub enable_metacognitive_optimization: bool,
    pub max_execution_time_seconds: f64,
    pub confidence_threshold: f64,
    pub resource_limits: HashMap<String, f64>,
    pub compact_annotation: bool,
    pub include_debug_info: bool,
}

impl Default for ProcessingConfig {
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
            compact_annotation: false,
            include_debug_info: true,
        }
    }
}

/// Complete processing result including all intermediate products
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProcessingResult {
    pub protocol_name: String,
    pub original_script: String,
    pub parsed_script: TurbulanceScript,
    pub compiled_protocol: super::compiler::CompiledProtocol,
    pub execution_result: super::orchestrator::ExecutionResult,
    pub annotated_script: AnnotatedScript,
    pub processing_statistics: ProcessingStatistics,
    pub auxiliary_files: HashMap<String, String>,
}

/// Processing statistics across all components
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProcessingStatistics {
    pub total_processing_time_seconds: f64,
    pub parsing_time_seconds: f64,
    pub compilation_time_seconds: f64,
    pub execution_time_seconds: f64,
    pub annotation_time_seconds: f64,
    pub success: bool,
    pub steps_processed: usize,
    pub annotations_added: usize,
    pub optimization_hits: usize,
}

/// Main Turbulance processor that coordinates all components
pub struct TurbulanceProcessor {
    parser: TurbulanceParser,
    compiler: TurbulanceCompiler,
    orchestrator: TurbulanceOrchestrator,
    annotator: TurbulanceAnnotator,
    config: ProcessingConfig,
    
    // Processing statistics
    protocols_processed: usize,
    total_processing_time: f64,
    successful_protocols: usize,
}

impl Default for TurbulanceProcessor {
    fn default() -> Self {
        Self::new()
    }
}

impl TurbulanceProcessor {
    pub fn new() -> Self {
        let config = ProcessingConfig::default();
        
        Self {
            parser: TurbulanceParser::new(),
            compiler: TurbulanceCompiler::new(),
            orchestrator: TurbulanceOrchestrator::new(),
            annotator: TurbulanceAnnotator::new(),
            config,
            protocols_processed: 0,
            total_processing_time: 0.0,
            successful_protocols: 0,
        }
    }

    pub fn new_with_config(config: ProcessingConfig) -> Self {
        let annotator = TurbulanceAnnotator::new()
            .with_compact_mode(config.compact_annotation)
            .with_debug_info(config.include_debug_info);
        
        Self {
            parser: TurbulanceParser::new(),
            compiler: TurbulanceCompiler::new(),
            orchestrator: TurbulanceOrchestrator::new(),
            annotator,
            config,
            protocols_processed: 0,
            total_processing_time: 0.0,
            successful_protocols: 0,
        }
    }

    /// Process a complete Turbulance protocol from script to annotated results
    pub async fn process_protocol(&mut self, script_content: &str, protocol_name: &str) -> Result<ProcessingResult> {
        let start_time = std::time::Instant::now();
        
        // Step 1: Parse the script
        let parse_start = std::time::Instant::now();
        let parsed_script = self.parser.parse_script(script_content, protocol_name)?;
        let parsing_time = parse_start.elapsed().as_secs_f64();
        
        // Step 2: Compile to execution plan
        let compile_start = std::time::Instant::now();
        let compiled_protocol = self.compiler.compile_protocol(&parsed_script)?;
        let compilation_time = compile_start.elapsed().as_secs_f64();
        
        // Step 3: Execute through Four-Sided Triangle pipeline
        let execution_start = std::time::Instant::now();
        let execution_result = self.orchestrator.execute_protocol(compiled_protocol.clone()).await?;
        let execution_time = execution_start.elapsed().as_secs_f64();
        
        // Step 4: Annotate original script with results
        let annotation_start = std::time::Instant::now();
        let annotated_script = self.annotator.annotate_script(
            script_content,
            &execution_result,
            &compiled_protocol
        )?;
        let annotation_time = annotation_start.elapsed().as_secs_f64();
        
        // Step 5: Generate auxiliary files
        let auxiliary_files = self.generate_auxiliary_files(&compiled_protocol)?;
        
        // Calculate total processing time
        let total_time = start_time.elapsed().as_secs_f64();
        
        // Create processing statistics
        let processing_statistics = ProcessingStatistics {
            total_processing_time_seconds: total_time,
            parsing_time_seconds: parsing_time,
            compilation_time_seconds: compilation_time,
            execution_time_seconds: execution_time,
            annotation_time_seconds: annotation_time,
            success: execution_result.overall_status == super::orchestrator::ExecutionStatus::Completed,
            steps_processed: execution_result.step_results.len(),
            annotations_added: annotated_script.annotation_summary.total_annotations,
            optimization_hits: compiled_protocol.optimization_hints.len(),
        };
        
        // Update processor statistics
        self.protocols_processed += 1;
        self.total_processing_time += total_time;
        if processing_statistics.success {
            self.successful_protocols += 1;
        }
        
        Ok(ProcessingResult {
            protocol_name: protocol_name.to_string(),
            original_script: script_content.to_string(),
            parsed_script,
            compiled_protocol,
            execution_result,
            annotated_script,
            processing_statistics,
            auxiliary_files,
        })
    }

    /// Generate auxiliary files from compiled protocol
    fn generate_auxiliary_files(&self, compiled_protocol: &super::compiler::CompiledProtocol) -> Result<HashMap<String, String>> {
        let mut files = HashMap::new();
        
        // .fs file (network graph consciousness state)
        files.insert("fs".to_string(), compiled_protocol.auxiliary_files.fs_content.clone());
        
        // .ghd file (resource orchestration dependencies)
        files.insert("ghd".to_string(), compiled_protocol.auxiliary_files.ghd_content.clone());
        
        // .hre file (metacognitive decision memory)
        files.insert("hre".to_string(), compiled_protocol.auxiliary_files.hre_content.clone());
        
        // .trb file (original script for reference)
        files.insert("trb".to_string(), format!(
            "# Original Turbulance Script
# Protocol: {}
# Generated: {}
# Execution Mode: {:?}
# Steps: {}

# This file contains the original Turbulance script for reference
# See .fs, .ghd, and .hre files for compiled analysis",
            compiled_protocol.protocol_name,
            chrono::Utc::now().to_rfc3339(),
            compiled_protocol.execution_mode,
            compiled_protocol.execution_steps.len()
        ));
        
        Ok(files)
    }

    /// Get comprehensive processing statistics
    pub fn get_statistics(&self) -> HashMap<String, f64> {
        let mut stats = HashMap::new();
        
        // Overall processor statistics
        stats.insert("protocols_processed".to_string(), self.protocols_processed as f64);
        stats.insert("total_processing_time_seconds".to_string(), self.total_processing_time);
        stats.insert("successful_protocols".to_string(), self.successful_protocols as f64);
        
        let success_rate = if self.protocols_processed > 0 {
            self.successful_protocols as f64 / self.protocols_processed as f64
        } else {
            0.0
        };
        stats.insert("success_rate".to_string(), success_rate);
        
        let avg_processing_time = if self.protocols_processed > 0 {
            self.total_processing_time / self.protocols_processed as f64
        } else {
            0.0
        };
        stats.insert("avg_processing_time_seconds".to_string(), avg_processing_time);
        
        // Component statistics
        let parser_stats = self.parser.get_statistics();
        let compiler_stats = self.compiler.get_statistics();
        let orchestrator_stats = self.orchestrator.get_statistics();
        let annotator_stats = self.annotator.get_statistics();
        
        // Merge component statistics with prefixes
        for (key, value) in parser_stats {
            stats.insert(format!("parser_{}", key), value);
        }
        for (key, value) in compiler_stats {
            stats.insert(format!("compiler_{}", key), value);
        }
        for (key, value) in orchestrator_stats {
            stats.insert(format!("orchestrator_{}", key), value);
        }
        for (key, value) in annotator_stats {
            stats.insert(format!("annotator_{}", key), value);
        }
        
        stats
    }

    /// Update processing configuration
    pub fn update_config(&mut self, config: ProcessingConfig) -> Result<()> {
        self.config = config.clone();
        
        // Update annotator configuration
        self.annotator = TurbulanceAnnotator::new()
            .with_compact_mode(config.compact_annotation)
            .with_debug_info(config.include_debug_info);
        
        Ok(())
    }
}

// Global registry for processor instances (for Python FFI)
static PROCESSOR_REGISTRY: Lazy<Arc<Mutex<HashMap<String, TurbulanceProcessor>>>> = 
    Lazy::new(|| Arc::new(Mutex::new(HashMap::new())));

/// Generate a unique processor ID
fn generate_processor_id() -> String {
    format!("turbulance_processor_{}", chrono::Utc::now().timestamp_nanos())
}

// Python FFI functions

#[pyfunction]
pub fn py_create_turbulance_processor(config_json: Option<&str>) -> PyResult<String> {
    let config = if let Some(config_str) = config_json {
        serde_json::from_str::<ProcessingConfig>(config_str)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid config JSON: {}", e)))?
    } else {
        ProcessingConfig::default()
    };
    
    let processor = TurbulanceProcessor::new_with_config(config);
    let processor_id = generate_processor_id();
    
    let mut registry = PROCESSOR_REGISTRY.lock().unwrap();
    registry.insert(processor_id.clone(), processor);
    
    Ok(processor_id)
}

#[pyfunction]
pub fn py_process_turbulance_script(
    processor_id: &str,
    script_content: &str,
    protocol_name: &str,
) -> PyResult<String> {
    let runtime = tokio::runtime::Runtime::new()
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to create runtime: {}", e)))?;
    
    let mut registry = PROCESSOR_REGISTRY.lock().unwrap();
    let processor = registry.get_mut(processor_id)
        .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyKeyError, _>("Processor not found"))?;
    
    let result = runtime.block_on(processor.process_protocol(script_content, protocol_name))
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    serde_json::to_string(&result)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Serialization failed: {}", e)))
}

#[pyfunction]
pub fn py_get_processor_statistics(processor_id: &str) -> PyResult<String> {
    let registry = PROCESSOR_REGISTRY.lock().unwrap();
    let processor = registry.get(processor_id)
        .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyKeyError, _>("Processor not found"))?;
    
    let stats = processor.get_statistics();
    serde_json::to_string(&stats)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Serialization failed: {}", e)))
}

#[pyfunction]
pub fn py_update_processor_config(processor_id: &str, config_json: &str) -> PyResult<()> {
    let config: ProcessingConfig = serde_json::from_str(config_json)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid config JSON: {}", e)))?;
    
    let mut registry = PROCESSOR_REGISTRY.lock().unwrap();
    let processor = registry.get_mut(processor_id)
        .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyKeyError, _>("Processor not found"))?;
    
    processor.update_config(config)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    Ok(())
}

#[pyfunction]
pub fn py_remove_processor(processor_id: &str) -> PyResult<()> {
    let mut registry = PROCESSOR_REGISTRY.lock().unwrap();
    registry.remove(processor_id)
        .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyKeyError, _>("Processor not found"))?;
    
    Ok(())
}