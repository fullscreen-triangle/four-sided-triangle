use crate::error::{FourSidedTriangleError, Result};
use crate::{quality_error, validation_error};
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QualityAssessment {
    pub accuracy: f64,
    pub completeness: f64,
    pub consistency: f64,
    pub relevance: f64,
    pub novelty: f64,
    pub overall_score: f64,
    pub uncertainty_metrics: UncertaintyMetrics,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UncertaintyMetrics {
    pub confidence_bounds: (f64, f64),
    pub variance_estimate: f64,
    pub uncertainty_dimensions: HashMap<String, f64>,
}

/// Assess quality across multiple dimensions
pub fn assess_quality_dimensions(
    solution: &str,
    domain_knowledge: &str,
    query_intent: &str,
    bayesian_metrics: &str,
) -> Result<QualityAssessment> {
    if solution.is_empty() {
        return Err(quality_error!("Solution cannot be empty"));
    }

    // Parse inputs
    let domain_knowledge: serde_json::Value = serde_json::from_str(domain_knowledge)?;
    let query_intent: serde_json::Value = serde_json::from_str(query_intent)?;
    let bayesian_metrics: serde_json::Value = serde_json::from_str(bayesian_metrics)?;

    let accuracy = assess_accuracy(solution, &domain_knowledge)?;
    let completeness = assess_completeness(solution, &query_intent)?;
    let consistency = assess_consistency(solution)?;
    let relevance = assess_relevance(solution, &query_intent)?;
    let novelty = assess_novelty(solution, &domain_knowledge)?;

    // Weighted overall score
    let overall_score = 0.25 * accuracy + 0.25 * completeness + 0.20 * consistency + 0.20 * relevance + 0.10 * novelty;

    let uncertainty_metrics = quantify_uncertainty(solution, overall_score)?;

    Ok(QualityAssessment {
        accuracy,
        completeness,
        consistency,
        relevance,
        novelty,
        overall_score,
        uncertainty_metrics,
    })
}

fn assess_accuracy(solution: &str, domain_knowledge: &serde_json::Value) -> Result<f64> {
    // Check factual alignment with domain knowledge
    let facts = domain_knowledge.get("facts").and_then(|f| f.as_array()).unwrap_or(&vec![]);
    
    if facts.is_empty() {
        return Ok(0.5); // Neutral score when no facts available
    }

    let mut accuracy_score = 0.0;
    let mut fact_count = 0;

    for fact in facts {
        if let Some(fact_str) = fact.as_str() {
            let similarity = calculate_semantic_overlap(solution, fact_str)?;
            accuracy_score += similarity;
            fact_count += 1;
        }
    }

    if fact_count > 0 {
        Ok(accuracy_score / fact_count as f64)
    } else {
        Ok(0.5)
    }
}

fn assess_completeness(solution: &str, query_intent: &serde_json::Value) -> Result<f64> {
    let intent_type = query_intent.get("intent_type").and_then(|i| i.as_str()).unwrap_or("unknown");
    let complexity = query_intent.get("complexity").and_then(|c| c.as_f64()).unwrap_or(0.5);

    // Expected elements based on query type
    let expected_elements = match intent_type {
        "computational" => vec!["calculation", "result", "formula", "method"],
        "informational" => vec!["explanation", "background", "details", "context"],
        "comparison" => vec!["differences", "similarities", "advantages", "disadvantages"],
        _ => vec!["information", "details"],
    };

    let mut completeness_score = 0.0;
    for element in &expected_elements {
        if solution.to_lowercase().contains(element) {
            completeness_score += 1.0;
        }
    }

    completeness_score /= expected_elements.len() as f64;

    // Adjust for complexity
    let length_factor = (solution.len() as f64 / (200.0 * (1.0 + complexity))).min(1.0);
    completeness_score = (completeness_score + length_factor) / 2.0;

    Ok(completeness_score)
}

fn assess_consistency(solution: &str) -> Result<f64> {
    let sentences: Vec<&str> = solution.split(['.', '!', '?']).filter(|s| !s.trim().is_empty()).collect();
    
    if sentences.len() < 2 {
        return Ok(1.0); // Single sentence is always consistent
    }

    let mut consistency_score = 0.0;
    let mut comparison_count = 0;

    // Compare adjacent sentences for consistency
    for window in sentences.windows(2) {
        let similarity = calculate_semantic_overlap(window[0], window[1])?;
        consistency_score += similarity;
        comparison_count += 1;
    }

    if comparison_count > 0 {
        Ok(consistency_score / comparison_count as f64)
    } else {
        Ok(1.0)
    }
}

fn assess_relevance(solution: &str, query_intent: &serde_json::Value) -> Result<f64> {
    let intent_type = query_intent.get("intent_type").and_then(|i| i.as_str()).unwrap_or("unknown");
    let domain_specificity = query_intent.get("domain_specificity").and_then(|d| d.as_f64()).unwrap_or(0.5);

    // Check for intent-specific keywords
    let intent_keywords = match intent_type {
        "computational" => vec!["calculate", "compute", "result", "equation", "formula"],
        "informational" => vec!["explain", "describe", "information", "details", "background"],
        "comparison" => vec!["compare", "contrast", "difference", "similar", "versus"],
        _ => vec!["relevant", "appropriate"],
    };

    let mut relevance_score = 0.0;
    for keyword in &intent_keywords {
        if solution.to_lowercase().contains(keyword) {
            relevance_score += 1.0;
        }
    }

    relevance_score /= intent_keywords.len() as f64;

    // Adjust for domain specificity
    relevance_score = relevance_score * (0.5 + 0.5 * domain_specificity);

    Ok(relevance_score.min(1.0))
}

fn assess_novelty(solution: &str, domain_knowledge: &serde_json::Value) -> Result<f64> {
    let facts = domain_knowledge.get("facts").and_then(|f| f.as_array()).unwrap_or(&vec![]);
    
    if facts.is_empty() {
        return Ok(0.5); // Neutral novelty when no baseline
    }

    let solution_words: std::collections::HashSet<String> = solution
        .split_whitespace()
        .map(|w| w.to_lowercase())
        .collect();

    let mut domain_words = std::collections::HashSet::new();
    for fact in facts {
        if let Some(fact_str) = fact.as_str() {
            for word in fact_str.split_whitespace() {
                domain_words.insert(word.to_lowercase());
            }
        }
    }

    let unique_words = solution_words.difference(&domain_words).count();
    let total_words = solution_words.len();

    if total_words > 0 {
        Ok(unique_words as f64 / total_words as f64)
    } else {
        Ok(0.0)
    }
}

fn calculate_semantic_overlap(text1: &str, text2: &str) -> Result<f64> {
    let words1: std::collections::HashSet<String> = text1
        .split_whitespace()
        .map(|w| w.to_lowercase())
        .collect();
    let words2: std::collections::HashSet<String> = text2
        .split_whitespace()
        .map(|w| w.to_lowercase())
        .collect();

    let intersection = words1.intersection(&words2).count();
    let union = words1.union(&words2).count();

    if union > 0 {
        Ok(intersection as f64 / union as f64)
    } else {
        Ok(0.0)
    }
}

/// Quantify uncertainty in quality assessment
pub fn quantify_uncertainty(solution: &str, quality_score: f64) -> Result<UncertaintyMetrics> {
    let solution_length = solution.len() as f64;
    let complexity_factor = (solution_length / 1000.0).min(1.0);
    
    // Estimate variance based on solution characteristics
    let variance_estimate = (1.0 - quality_score) * (1.0 - complexity_factor) * 0.1;
    
    // Calculate confidence bounds
    let margin = 1.96 * variance_estimate.sqrt(); // 95% confidence interval
    let lower_bound = (quality_score - margin).max(0.0);
    let upper_bound = (quality_score + margin).min(1.0);
    
    let mut uncertainty_dimensions = HashMap::new();
    uncertainty_dimensions.insert("solution_length".to_string(), 1.0 - complexity_factor);
    uncertainty_dimensions.insert("quality_variance".to_string(), variance_estimate);
    
    Ok(UncertaintyMetrics {
        confidence_bounds: (lower_bound, upper_bound),
        variance_estimate,
        uncertainty_dimensions,
    })
}

// Python FFI functions

#[pyfunction]
pub fn py_assess_quality_dimensions(
    solution: &str,
    domain_knowledge: &str,
    query_intent: &str,
    bayesian_metrics: &str,
) -> PyResult<String> {
    let result = assess_quality_dimensions(solution, domain_knowledge, query_intent, bayesian_metrics)?;
    let json_result = serde_json::to_string(&result)?;
    Ok(json_result)
}

#[pyfunction]
pub fn py_quantify_uncertainty(solution: &str, quality_score: f64) -> PyResult<String> {
    let result = quantify_uncertainty(solution, quality_score)?;
    let json_result = serde_json::to_string(&result)?;
    Ok(json_result)
} 