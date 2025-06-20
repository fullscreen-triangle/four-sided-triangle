use pyo3::prelude::*;

// Core modules
pub mod bayesian;
pub mod text_processing;
pub mod memory;
pub mod throttle_detection;
pub mod quality_assessment;
pub mod optimization;
pub mod utils;

// Error types
pub mod error;

// Re-exports for convenience
pub use error::{FourSidedTriangleError, Result};

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
    
    Ok(())
} 