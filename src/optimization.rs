use crate::error::{FourSidedTriangleError, Result};
use crate::{optimization_error, validation_error};
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResourceAllocation {
    pub total_resources: f64,
    pub allocations: HashMap<String, f64>,
    pub expected_roi: HashMap<String, f64>,
    pub risk_factors: HashMap<String, f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ROICalculation {
    pub investment: f64,
    pub expected_return: f64,
    pub roi_percentage: f64,
    pub risk_adjusted_roi: f64,
    pub confidence_level: f64,
}

/// Optimize resource allocation using ROI-based approach
pub fn optimize_resource_allocation(
    available_resources: f64,
    component_requirements: &str,
    historical_performance: &str,
) -> Result<ResourceAllocation> {
    if available_resources <= 0.0 {
        return Err(optimization_error!("Available resources must be positive"));
    }

    let requirements: HashMap<String, f64> = serde_json::from_str(component_requirements)?;
    let performance: HashMap<String, f64> = serde_json::from_str(historical_performance)?;

    let mut allocations = HashMap::new();
    let mut expected_roi = HashMap::new();
    let mut risk_factors = HashMap::new();

    let total_requirement: f64 = requirements.values().sum();
    if total_requirement == 0.0 {
        return Err(optimization_error!("Total requirements cannot be zero"));
    }

    // Calculate base allocation proportions
    for (component, requirement) in &requirements {
        let base_proportion = requirement / total_requirement;
        
        // Adjust based on historical performance
        let performance_factor = performance.get(component).unwrap_or(&1.0);
        let adjusted_proportion = base_proportion * performance_factor;
        
        let allocation = available_resources * adjusted_proportion;
        allocations.insert(component.clone(), allocation);
        
        // Calculate expected ROI
        let roi = calculate_component_roi(allocation, *performance_factor)?;
        expected_roi.insert(component.clone(), roi);
        
        // Estimate risk factor
        let risk = estimate_risk_factor(component, *performance_factor)?;
        risk_factors.insert(component.clone(), risk);
    }

    // Normalize allocations to ensure they sum to available resources
    let total_allocated: f64 = allocations.values().sum();
    if total_allocated > 0.0 {
        for allocation in allocations.values_mut() {
            *allocation = (*allocation / total_allocated) * available_resources;
        }
    }

    Ok(ResourceAllocation {
        total_resources: available_resources,
        allocations,
        expected_roi,
        risk_factors,
    })
}

fn calculate_component_roi(investment: f64, performance_factor: f64) -> Result<f64> {
    if investment <= 0.0 {
        return Ok(0.0);
    }

    // Simple ROI calculation based on performance factor
    let expected_return = investment * performance_factor;
    let roi = (expected_return - investment) / investment;
    
    Ok(roi)
}

fn estimate_risk_factor(component: &str, performance_factor: f64) -> Result<f64> {
    // Risk estimation based on component type and performance variance
    let base_risk = match component {
        comp if comp.contains("bayesian") => 0.2,  // Lower risk for mathematical components
        comp if comp.contains("throttle") => 0.4,  // Medium risk for detection systems
        comp if comp.contains("quality") => 0.3,   // Medium-low risk for assessment
        comp if comp.contains("memory") => 0.1,    // Low risk for storage
        _ => 0.35, // Default medium risk
    };

    // Adjust risk based on performance factor
    let performance_risk = if performance_factor < 0.5 {
        0.5 // High risk for poor performance
    } else if performance_factor > 1.5 {
        0.1 // Low risk for excellent performance
    } else {
        1.0 - performance_factor // Inverse relationship
    };

    let combined_risk = (base_risk + performance_risk) / 2.0;
    Ok(combined_risk.clamp(0.0, 1.0))
}

/// Calculate ROI for a specific investment
pub fn calculate_roi(
    investment: f64,
    expected_return: f64,
    risk_factor: f64,
) -> Result<ROICalculation> {
    if investment <= 0.0 {
        return Err(optimization_error!("Investment must be positive"));
    }

    if risk_factor < 0.0 || risk_factor > 1.0 {
        return Err(validation_error!("Risk factor must be between 0 and 1"));
    }

    let roi_percentage = ((expected_return - investment) / investment) * 100.0;
    
    // Risk-adjusted ROI
    let risk_adjusted_roi = roi_percentage * (1.0 - risk_factor);
    
    // Confidence level based on investment size and risk
    let confidence_level = calculate_confidence_level(investment, risk_factor)?;

    Ok(ROICalculation {
        investment,
        expected_return,
        roi_percentage,
        risk_adjusted_roi,
        confidence_level,
    })
}

fn calculate_confidence_level(investment: f64, risk_factor: f64) -> Result<f64> {
    // Higher investment and lower risk lead to higher confidence
    let investment_factor = (investment / 1000.0).min(1.0); // Normalize to reasonable scale
    let risk_adjustment = 1.0 - risk_factor;
    
    let confidence = (investment_factor * 0.3 + risk_adjustment * 0.7) * 0.95; // Max 95% confidence
    Ok(confidence.clamp(0.1, 0.95))
}

/// Multi-objective optimization for competing priorities
pub fn multi_objective_optimization(
    objectives: &str,
    constraints: &str,
    weights: &str,
) -> Result<HashMap<String, f64>> {
    let objectives: HashMap<String, f64> = serde_json::from_str(objectives)?;
    let constraints: HashMap<String, f64> = serde_json::from_str(constraints)?;
    let weights: HashMap<String, f64> = serde_json::from_str(weights)?;

    let mut solution = HashMap::new();

    // Simple weighted sum approach
    let total_weight: f64 = weights.values().sum();
    if total_weight == 0.0 {
        return Err(optimization_error!("Total weights cannot be zero"));
    }

    for (objective, value) in &objectives {
        let weight = weights.get(objective).unwrap_or(&1.0);
        let normalized_weight = weight / total_weight;
        
        // Apply constraints
        let constrained_value = if let Some(constraint) = constraints.get(objective) {
            value.min(*constraint)
        } else {
            *value
        };

        let optimized_value = constrained_value * normalized_weight;
        solution.insert(objective.clone(), optimized_value);
    }

    Ok(solution)
}

// Python FFI functions

#[pyfunction]
pub fn py_optimize_resource_allocation(
    available_resources: f64,
    component_requirements: &str,
    historical_performance: &str,
) -> PyResult<String> {
    let result = optimize_resource_allocation(available_resources, component_requirements, historical_performance)?;
    let json_result = serde_json::to_string(&result)?;
    Ok(json_result)
}

#[pyfunction]
pub fn py_calculate_roi(
    investment: f64,
    expected_return: f64,
    risk_factor: f64,
) -> PyResult<String> {
    let result = calculate_roi(investment, expected_return, risk_factor)?;
    let json_result = serde_json::to_string(&result)?;
    Ok(json_result)
} 