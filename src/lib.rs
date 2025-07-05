use pyo3::prelude::*;
use std::sync::Mutex;
use std::collections::HashMap;
use once_cell::sync::Lazy;

// Core modules
pub mod bayesian;
pub mod text_processing;
pub mod memory;
pub mod throttle_detection;
pub mod quality_assessment;
pub mod optimization;
pub mod utils;

// Enhanced fuzzy evidence system modules
pub mod fuzzy_evidence;
pub mod evidence_network;
pub mod metacognitive_optimizer;

// Autobahn integration module
pub mod autobahn_bridge;

// Error types
pub mod error;

// Turbulance DSL processing modules
pub mod turbulance;

// Re-exports for convenience
pub use error::{FourSidedTriangleError, Result};

// Global registries for managing instances
static EVIDENCE_NETWORKS: Lazy<Mutex<HashMap<String, evidence_network::EvidenceNetwork>>> = 
    Lazy::new(|| Mutex::new(HashMap::new()));

static METACOGNITIVE_OPTIMIZERS: Lazy<Mutex<HashMap<String, metacognitive_optimizer::MetacognitiveOptimizer>>> = 
    Lazy::new(|| Mutex::new(HashMap::new()));

static FUZZY_ENGINES: Lazy<Mutex<HashMap<String, fuzzy_evidence::FuzzyInferenceEngine>>> = 
    Lazy::new(|| Mutex::new(HashMap::new()));

/// Python module initialization
#[pymodule]
fn four_sided_triangle_core(_py: Python, m: &PyModule) -> PyResult<()> {
    // Initialize logging
    env_logger::init();
    
    // Register Bayesian evaluation functions
    m.add_function(wrap_pyfunction!(bayesian::py_calculate_posterior_probability, m)?)?;
    m.add_function(wrap_pyfunction!(bayesian::py_calculate_information_gain, m)?)?;
    m.add_function(wrap_pyfunction!(bayesian::py_calculate_mutual_information, m)?)?;
    m.add_function(wrap_pyfunction!(bayesian::py_bayesian_evaluate, m)?)?;
    
    // Register text processing functions
    m.add_function(wrap_pyfunction!(text_processing::py_calculate_text_similarity, m)?)?;
    m.add_function(wrap_pyfunction!(text_processing::py_extract_entities, m)?)?;
    m.add_function(wrap_pyfunction!(text_processing::py_tokenize_advanced, m)?)?;
    m.add_function(wrap_pyfunction!(text_processing::py_calculate_information_density, m)?)?;
    
    // Register throttle detection functions
    m.add_function(wrap_pyfunction!(throttle_detection::py_detect_throttling, m)?)?;
    m.add_function(wrap_pyfunction!(throttle_detection::py_calculate_pattern_score, m)?)?;
    
    // Register quality assessment functions
    m.add_function(wrap_pyfunction!(quality_assessment::py_assess_quality_dimensions, m)?)?;
    m.add_function(wrap_pyfunction!(quality_assessment::py_quantify_uncertainty, m)?)?;
    
    // Register memory management functions
    m.add_function(wrap_pyfunction!(memory::py_create_session, m)?)?;
    m.add_function(wrap_pyfunction!(memory::py_update_session, m)?)?;
    m.add_function(wrap_pyfunction!(memory::py_get_session, m)?)?;
    
    // Register optimization functions
    m.add_function(wrap_pyfunction!(optimization::py_optimize_resource_allocation, m)?)?;
    m.add_function(wrap_pyfunction!(optimization::py_calculate_roi, m)?)?;
    
    // Register fuzzy evidence system functions
    m.add_function(wrap_pyfunction!(fuzzy_evidence::py_create_fuzzy_set, m)?)?;
    m.add_function(wrap_pyfunction!(fuzzy_evidence::py_calculate_membership, m)?)?;
    m.add_function(wrap_pyfunction!(fuzzy_evidence::py_fuzzy_inference, m)?)?;
    m.add_function(wrap_pyfunction!(fuzzy_evidence::py_defuzzify, m)?)?;
    m.add_function(wrap_pyfunction!(fuzzy_evidence::py_combine_evidence, m)?)?;
    
    // Register evidence network functions  
    m.add_function(wrap_pyfunction!(evidence_network::py_create_evidence_network, m)?)?;
    m.add_function(wrap_pyfunction!(evidence_network::py_add_node, m)?)?;
    m.add_function(wrap_pyfunction!(evidence_network::py_add_edge, m)?)?;
    m.add_function(wrap_pyfunction!(evidence_network::py_update_node_evidence, m)?)?;  
    m.add_function(wrap_pyfunction!(evidence_network::py_propagate_evidence, m)?)?;
    m.add_function(wrap_pyfunction!(evidence_network::py_query_network, m)?)?;
    m.add_function(wrap_pyfunction!(evidence_network::py_get_network_statistics, m)?)?;
    
    // Register metacognitive optimizer functions
    m.add_function(wrap_pyfunction!(metacognitive_optimizer::py_create_optimizer, m)?)?;
    m.add_function(wrap_pyfunction!(metacognitive_optimizer::py_optimize_pipeline, m)?)?;
    m.add_function(wrap_pyfunction!(metacognitive_optimizer::py_evaluate_decision, m)?)?;
    m.add_function(wrap_pyfunction!(metacognitive_optimizer::py_update_strategy, m)?)?;
    m.add_function(wrap_pyfunction!(metacognitive_optimizer::py_get_optimizer_statistics, m)?)?;
    
    // Register Autobahn bridge functions
    m.add_function(wrap_pyfunction!(autobahn_bridge::py_initialize_autobahn_bridge, m)?)?;
    m.add_function(wrap_pyfunction!(autobahn_bridge::py_is_autobahn_available, m)?)?;
    m.add_function(wrap_pyfunction!(autobahn_bridge::py_autobahn_bayesian_inference, m)?)?;
    m.add_function(wrap_pyfunction!(autobahn_bridge::py_autobahn_fuzzy_logic, m)?)?;
    m.add_function(wrap_pyfunction!(autobahn_bridge::py_autobahn_evidence_network, m)?)?;
    m.add_function(wrap_pyfunction!(autobahn_bridge::py_autobahn_metacognitive_optimization, m)?)?;
    m.add_function(wrap_pyfunction!(autobahn_bridge::py_autobahn_optimize_pipeline, m)?)?;
    m.add_function(wrap_pyfunction!(autobahn_bridge::py_autobahn_get_status, m)?)?;
    
    // Register Turbulance DSL functions
    m.add_function(wrap_pyfunction!(turbulance::parser::py_parse_turbulance_script, m)?)?;
    m.add_function(wrap_pyfunction!(turbulance::parser::py_get_parser_statistics, m)?)?;
    m.add_function(wrap_pyfunction!(turbulance::compiler::py_compile_turbulance_protocol, m)?)?;
    m.add_function(wrap_pyfunction!(turbulance::orchestrator::py_execute_turbulance_protocol, m)?)?;
    m.add_function(wrap_pyfunction!(turbulance::orchestrator::py_get_orchestrator_statistics, m)?)?;
    m.add_function(wrap_pyfunction!(turbulance::annotation::py_annotate_turbulance_script, m)?)?;
    m.add_function(wrap_pyfunction!(turbulance::annotation::py_get_annotator_statistics, m)?)?;
    m.add_function(wrap_pyfunction!(turbulance::processor::py_create_turbulance_processor, m)?)?;
    m.add_function(wrap_pyfunction!(turbulance::processor::py_process_turbulance_script, m)?)?;
    m.add_function(wrap_pyfunction!(turbulance::processor::py_get_processor_statistics, m)?)?;
    m.add_function(wrap_pyfunction!(turbulance::processor::py_update_processor_config, m)?)?;
    m.add_function(wrap_pyfunction!(turbulance::processor::py_remove_processor, m)?)?;
    
    Ok(())
} 