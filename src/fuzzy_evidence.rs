use crate::error::{FourSidedTriangleError, Result};
use crate::{validation_error};
use ordered_float::OrderedFloat;
use pyo3::prelude::*;
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use rand;

/// Fuzzy membership function types
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MembershipFunction {
    Triangular { left: f64, center: f64, right: f64 },
    Trapezoidal { left: f64, left_top: f64, right_top: f64, right: f64 },
    Gaussian { center: f64, sigma: f64 },
    Sigmoid { center: f64, slope: f64 },
    Custom { points: Vec<(f64, f64)> },
}

/// Fuzzy set representation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FuzzySet {
    pub name: String,
    pub universe_min: f64,
    pub universe_max: f64,
    pub membership_function: MembershipFunction,
}

/// Fuzzy evidence with uncertainty quantification
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FuzzyEvidence {
    pub value: f64,
    pub membership_degree: f64,
    pub confidence: f64,
    pub source_reliability: f64,
    pub temporal_decay: f64,
    pub context_relevance: f64,
}

/// Fuzzy rule for inference
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FuzzyRule {
    pub id: String,
    pub antecedents: Vec<FuzzyCondition>,
    pub consequent: FuzzyConsequent,
    pub weight: f64,
    pub confidence: f64,
}

/// Fuzzy condition in rule antecedent
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FuzzyCondition {
    pub variable: String,
    pub fuzzy_set: String,
    pub operator: FuzzyOperator,
}

/// Fuzzy operators
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum FuzzyOperator {
    Is,
    IsNot,
    VeryMuch,
    Somewhat,
    Extremely,
}

/// Fuzzy consequent in rule
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FuzzyConsequent {
    pub variable: String,
    pub fuzzy_set: String,
    pub certainty_factor: f64,
}

/// Fuzzy inference engine
pub struct FuzzyInferenceEngine {
    fuzzy_sets: HashMap<String, FuzzySet>,
    rules: Vec<FuzzyRule>,
    variables: HashMap<String, f64>,
    evidence_history: Vec<FuzzyEvidence>,
}

impl Default for FuzzyInferenceEngine {
    fn default() -> Self {
        Self::new()
    }
}

impl FuzzyInferenceEngine {
    pub fn new() -> Self {
        Self {
            fuzzy_sets: HashMap::new(),
            rules: Vec::new(),
            variables: HashMap::new(),
            evidence_history: Vec::new(),
        }
    }

    /// Add a fuzzy set to the system
    pub fn add_fuzzy_set(&mut self, fuzzy_set: FuzzySet) -> Result<()> {
        if fuzzy_set.universe_min >= fuzzy_set.universe_max {
            return Err(validation_error!("Universe min must be less than max"));
        }
        
        self.fuzzy_sets.insert(fuzzy_set.name.clone(), fuzzy_set);
        Ok(())
    }

    /// Calculate membership degree for a value in a fuzzy set
    pub fn calculate_membership(&self, value: f64, set_name: &str) -> Result<f64> {
        let fuzzy_set = self.fuzzy_sets.get(set_name)
            .ok_or_else(|| validation_error!("Fuzzy set not found"))?;

        // Clamp value to universe
        let clamped_value = value.clamp(fuzzy_set.universe_min, fuzzy_set.universe_max);

        let membership = match &fuzzy_set.membership_function {
            MembershipFunction::Triangular { left, center, right } => {
                self.triangular_membership(clamped_value, *left, *center, *right)
            }
            MembershipFunction::Trapezoidal { left, left_top, right_top, right } => {
                self.trapezoidal_membership(clamped_value, *left, *left_top, *right_top, *right)
            }
            MembershipFunction::Gaussian { center, sigma } => {
                self.gaussian_membership(clamped_value, *center, *sigma)
            }
            MembershipFunction::Sigmoid { center, slope } => {
                self.sigmoid_membership(clamped_value, *center, *slope)
            }
            MembershipFunction::Custom { points } => {
                self.custom_membership(clamped_value, points)
            }
        };

        Ok(membership.clamp(0.0, 1.0))
    }

    /// Triangular membership function
    fn triangular_membership(&self, x: f64, left: f64, center: f64, right: f64) -> f64 {
        if x <= left || x >= right {
            0.0
        } else if x <= center {
            (x - left) / (center - left)
        } else {
            (right - x) / (right - center)
        }
    }

    /// Trapezoidal membership function
    fn trapezoidal_membership(&self, x: f64, left: f64, left_top: f64, right_top: f64, right: f64) -> f64 {
        if x <= left || x >= right {
            0.0
        } else if x <= left_top {
            (x - left) / (left_top - left)
        } else if x <= right_top {
            1.0
        } else {
            (right - x) / (right - right_top)
        }
    }

    /// Gaussian membership function
    fn gaussian_membership(&self, x: f64, center: f64, sigma: f64) -> f64 {
        (-0.5 * ((x - center) / sigma).powi(2)).exp()
    }

    /// Sigmoid membership function
    fn sigmoid_membership(&self, x: f64, center: f64, slope: f64) -> f64 {
        1.0 / (1.0 + (-slope * (x - center)).exp())
    }

    /// Custom membership function using linear interpolation
    fn custom_membership(&self, x: f64, points: &[(f64, f64)]) -> f64 {
        if points.is_empty() {
            return 0.0;
        }

        // Find the two points to interpolate between
        for window in points.windows(2) {
            let (x1, y1) = window[0];
            let (x2, y2) = window[1];
            
            if x >= x1 && x <= x2 {
                if (x2 - x1).abs() < f64::EPSILON {
                    return y1;
                }
                // Linear interpolation
                return y1 + (y2 - y1) * (x - x1) / (x2 - x1);
            }
        }

        // Outside the range
        if x < points[0].0 {
            points[0].1
        } else {
            points[points.len() - 1].1
        }
    }

    /// Add evidence to the system
    pub fn add_evidence(&mut self, evidence: FuzzyEvidence) -> Result<()> {
        // Apply temporal decay to existing evidence
        let current_time = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs_f64();

        for existing_evidence in &mut self.evidence_history {
            existing_evidence.temporal_decay *= 0.95; // Decay factor
        }

        // Add new evidence
        self.evidence_history.push(evidence);

        // Limit history size
        if self.evidence_history.len() > 1000 {
            self.evidence_history.remove(0);
        }

        Ok(())
    }

    /// Perform fuzzy inference using Mamdani method
    pub fn fuzzy_inference(&self, input_variables: &HashMap<String, f64>) -> Result<HashMap<String, f64>> {
        let mut output_aggregations: HashMap<String, Vec<f64>> = HashMap::new();

        // Evaluate each rule
        for rule in &self.rules {
            let activation_strength = self.evaluate_rule_antecedent(rule, input_variables)?;
            
            if activation_strength > 0.0 {
                // Apply rule weight and confidence
                let weighted_activation = activation_strength * rule.weight * rule.confidence;
                
                // Add to output aggregation
                output_aggregations
                    .entry(rule.consequent.variable.clone())
                    .or_default()
                    .push(weighted_activation * rule.consequent.certainty_factor);
            }
        }

        // Aggregate outputs using maximum method
        let mut results = HashMap::new();
        for (variable, activations) in output_aggregations {
            let max_activation = activations.into_iter()
                .fold(0.0f64, |acc, x| acc.max(x));
            results.insert(variable, max_activation);
        }

        Ok(results)
    }

    /// Evaluate rule antecedent
    fn evaluate_rule_antecedent(&self, rule: &FuzzyRule, variables: &HashMap<String, f64>) -> Result<f64> {
        let mut activation_degrees = Vec::new();

        for condition in &rule.antecedents {
            let variable_value = variables.get(&condition.variable)
                .ok_or_else(|| validation_error!("Variable not found in input"))?;

            let membership = self.calculate_membership(*variable_value, &condition.fuzzy_set)?;
            
            // Apply fuzzy operator modifiers
            let modified_membership = match condition.operator {
                FuzzyOperator::Is => membership,
                FuzzyOperator::IsNot => 1.0 - membership,
                FuzzyOperator::VeryMuch => membership.powi(2), // Concentration
                FuzzyOperator::Somewhat => membership.sqrt(), // Dilation
                FuzzyOperator::Extremely => membership.powi(3), // More concentration
            };

            activation_degrees.push(modified_membership);
        }

        // Use minimum for AND operation (T-norm)
        Ok(activation_degrees.into_iter().fold(1.0f64, |acc, x| acc.min(x)))
    }

    /// Defuzzify output using centroid method
    pub fn defuzzify(&self, variable: &str, activation_level: f64) -> Result<f64> {
        let fuzzy_set = self.fuzzy_sets.get(variable)
            .ok_or_else(|| validation_error!("Output fuzzy set not found"))?;

        let min_val = fuzzy_set.universe_min;
        let max_val = fuzzy_set.universe_max;
        let step = (max_val - min_val) / 1000.0; // Resolution

        let mut numerator = 0.0;
        let mut denominator = 0.0;

        let mut x = min_val;
        while x <= max_val {
            let membership = self.calculate_membership(x, variable)?;
            let clipped_membership = membership.min(activation_level);
            
            numerator += x * clipped_membership;
            denominator += clipped_membership;
            
            x += step;
        }

        if denominator > 0.0 {
            Ok(numerator / denominator)
        } else {
            Ok((min_val + max_val) / 2.0) // Default to center
        }
    }

    /// Calculate evidence strength combining multiple factors
    pub fn calculate_evidence_strength(&self, evidence: &FuzzyEvidence) -> f64 {
        let base_strength = evidence.membership_degree * evidence.confidence;
        let reliability_factor = evidence.source_reliability;
        let temporal_factor = evidence.temporal_decay;
        let context_factor = evidence.context_relevance;

        // Weighted combination of factors
        base_strength * (0.4 * reliability_factor + 0.3 * temporal_factor + 0.3 * context_factor)
    }

    /// Combine multiple pieces of evidence using Dempster-Shafer theory
    pub fn combine_evidence(&self, evidences: &[FuzzyEvidence]) -> Result<f64> {
        if evidences.is_empty() {
            return Ok(0.0);
        }

        let mut combined_belief = 0.0;
        let mut combined_plausibility = 0.0;

        for evidence in evidences {
            let strength = self.calculate_evidence_strength(evidence);
            let uncertainty = 1.0 - evidence.confidence;

            // Dempster's rule of combination (simplified)
            let new_belief = combined_belief + strength * (1.0 - combined_belief);
            let new_plausibility = combined_plausibility + strength * uncertainty;

            combined_belief = new_belief;
            combined_plausibility = new_plausibility;
        }

        // Normalize
        let total_mass = combined_belief + combined_plausibility;
        if total_mass > 0.0 {
            Ok(combined_belief / total_mass)
        } else {
            Ok(0.5) // Maximum uncertainty
        }
    }
}

/// Create default fuzzy sets for common linguistic variables
pub fn create_default_fuzzy_sets() -> Vec<FuzzySet> {
    vec![
        // Confidence levels
        FuzzySet {
            name: "low_confidence".to_string(),
            universe_min: 0.0,
            universe_max: 1.0,
            membership_function: MembershipFunction::Triangular {
                left: 0.0,
                center: 0.0,
                right: 0.5,
            },
        },
        FuzzySet {
            name: "medium_confidence".to_string(),
            universe_min: 0.0,
            universe_max: 1.0,
            membership_function: MembershipFunction::Triangular {
                left: 0.2,
                center: 0.5,
                right: 0.8,
            },
        },
        FuzzySet {
            name: "high_confidence".to_string(),
            universe_min: 0.0,
            universe_max: 1.0,
            membership_function: MembershipFunction::Triangular {
                left: 0.5,
                center: 1.0,
                right: 1.0,
            },
        },
        // Quality levels
        FuzzySet {
            name: "poor_quality".to_string(),
            universe_min: 0.0,
            universe_max: 1.0,
            membership_function: MembershipFunction::Trapezoidal {
                left: 0.0,
                left_top: 0.0,
                right_top: 0.3,
                right: 0.5,
            },
        },
        FuzzySet {
            name: "good_quality".to_string(),
            universe_min: 0.0,
            universe_max: 1.0,
            membership_function: MembershipFunction::Triangular {
                left: 0.3,
                center: 0.6,
                right: 0.9,
            },
        },
        FuzzySet {
            name: "excellent_quality".to_string(),
            universe_min: 0.0,
            universe_max: 1.0,
            membership_function: MembershipFunction::Trapezoidal {
                left: 0.7,
                left_top: 0.9,
                right_top: 1.0,
                right: 1.0,
            },
        },
        // Urgency levels
        FuzzySet {
            name: "low_urgency".to_string(),
            universe_min: 0.0,
            universe_max: 10.0,
            membership_function: MembershipFunction::Gaussian {
                center: 2.0,
                sigma: 1.5,
            },
        },
        FuzzySet {
            name: "medium_urgency".to_string(),
            universe_min: 0.0,
            universe_max: 10.0,
            membership_function: MembershipFunction::Gaussian {
                center: 5.0,
                sigma: 1.5,
            },
        },
        FuzzySet {
            name: "high_urgency".to_string(),
            universe_min: 0.0,
            universe_max: 10.0,
            membership_function: MembershipFunction::Gaussian {
                center: 8.0,
                sigma: 1.5,
            },
        },
    ]
}

// Python FFI functions

/// Generate a unique fuzzy engine ID
fn generate_fuzzy_engine_id() -> String {
    format!("fuzzy_{}", rand::random::<u64>())
}

#[pyfunction]
pub fn py_create_fuzzy_set(
    name: &str,
    universe_min: f64,
    universe_max: f64,
    membership_function_json: &str,
) -> PyResult<String> {
    let membership_function: MembershipFunction = serde_json::from_str(membership_function_json)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid membership function: {}", e)))?;
    
    let fuzzy_set = FuzzySet {
        name: name.to_string(),
        universe_min,
        universe_max,
        membership_function,
    };
    
    let engine_id = generate_fuzzy_engine_id();
    let mut engine = FuzzyInferenceEngine::new();
    engine.add_fuzzy_set(fuzzy_set)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    let mut engines = crate::FUZZY_ENGINES.lock().unwrap();
    engines.insert(engine_id.clone(), engine);
    
    Ok(engine_id)
}

#[pyfunction]
pub fn py_calculate_membership(
    value: f64,
    fuzzy_set_json: &str,
) -> PyResult<f64> {
    let fuzzy_set: FuzzySet = serde_json::from_str(fuzzy_set_json)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid fuzzy set: {}", e)))?;
    
    let engine = FuzzyInferenceEngine::new();
    let membership = engine.calculate_membership(value, &fuzzy_set.name)
        .unwrap_or(0.0);
    
    Ok(membership)
}

#[pyfunction]
pub fn py_fuzzy_inference(
    rules_json: &str,
    fuzzy_sets_json: &str,
    input_variables_json: &str,
) -> PyResult<String> {
    let rules: Vec<FuzzyRule> = serde_json::from_str(rules_json)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid rules: {}", e)))?;
    
    let fuzzy_sets: Vec<FuzzySet> = serde_json::from_str(fuzzy_sets_json)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid fuzzy sets: {}", e)))?;
    
    let input_variables: HashMap<String, f64> = serde_json::from_str(input_variables_json)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid input variables: {}", e)))?;
    
    let mut engine = FuzzyInferenceEngine::new();
    
    // Add fuzzy sets to engine
    for fuzzy_set in fuzzy_sets {
        engine.add_fuzzy_set(fuzzy_set)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    }
    
    // Set the rules
    engine.rules = rules;
    
    // Perform inference
    let result = engine.fuzzy_inference(&input_variables)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    serde_json::to_string(&result)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Serialization failed: {}", e)))
}

#[pyfunction]
pub fn py_defuzzify(
    variable: &str,
    activation_level: f64,
    fuzzy_set_json: &str,
) -> PyResult<f64> {
    let fuzzy_set: FuzzySet = serde_json::from_str(fuzzy_set_json)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid fuzzy set: {}", e)))?;
    
    let mut engine = FuzzyInferenceEngine::new();
    engine.add_fuzzy_set(fuzzy_set)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    let result = engine.defuzzify(variable, activation_level)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    Ok(result)
}

#[pyfunction]
pub fn py_combine_evidence(evidence_list_json: &str) -> PyResult<String> {
    let evidence_list: Vec<FuzzyEvidence> = serde_json::from_str(evidence_list_json)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid evidence list: {}", e)))?;
    
    let engine = FuzzyInferenceEngine::new();
    let combined_evidence = engine.combine_evidence(&evidence_list)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    serde_json::to_string(&combined_evidence)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Serialization failed: {}", e)))
} 