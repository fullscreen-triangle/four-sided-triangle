use crate::error::{FourSidedTriangleError, Result};
use crate::{throttle_error, validation_error};
use pyo3::prelude::*;
use rayon::prelude::*;
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ThrottlePattern {
    pub indicators: Vec<String>,
    pub truncation_patterns: Option<Vec<String>>,
    pub missing_elements: Option<Vec<String>>,
    pub computational_indicators: Option<Vec<String>>,
    pub weight: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ThrottleDetectionResult {
    pub throttle_detected: bool,
    pub pattern_type: String,
    pub confidence_score: f64,
    pub pattern_scores: HashMap<String, f64>,
    pub density_score: f64,
    pub expected_density: f64,
    pub recommendations: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AdaptationStrategy {
    pub description: String,
    pub effectiveness: f64,
    pub difficulty: f64,
}

/// High-performance throttle detection system
pub struct ThrottleDetector {
    patterns: HashMap<String, ThrottlePattern>,
    strategies: HashMap<String, HashMap<String, AdaptationStrategy>>,
    compiled_regexes: HashMap<String, Vec<Regex>>,
    density_threshold: f64,
    detection_threshold: f64,
}

impl Default for ThrottleDetector {
    fn default() -> Self {
        let mut detector = Self {
            patterns: HashMap::new(),
            strategies: HashMap::new(),
            compiled_regexes: HashMap::new(),
            density_threshold: 0.7,
            detection_threshold: 0.5,
        };
        
        detector.load_default_patterns();
        detector.load_default_strategies();
        detector.compile_regexes();
        detector
    }
}

impl ThrottleDetector {
    pub fn new(density_threshold: f64, detection_threshold: f64) -> Result<Self> {
        if density_threshold <= 0.0 || density_threshold > 1.0 {
            return Err(validation_error!("Density threshold must be between 0 and 1"));
        }
        if detection_threshold <= 0.0 || detection_threshold > 1.0 {
            return Err(validation_error!("Detection threshold must be between 0 and 1"));
        }

        let mut detector = Self {
            patterns: HashMap::new(),
            strategies: HashMap::new(),
            compiled_regexes: HashMap::new(),
            density_threshold,
            detection_threshold,
        };
        
        detector.load_default_patterns();
        detector.load_default_strategies();
        detector.compile_regexes();
        Ok(detector)
    }

    /// Detect throttling in a response with high-performance pattern matching
    pub fn detect_throttling(
        &self,
        response: &str,
        query: &str,
        performance_metrics: Option<&HashMap<String, f64>>,
    ) -> Result<ThrottleDetectionResult> {
        if response.is_empty() {
            return Ok(ThrottleDetectionResult {
                throttle_detected: false,
                pattern_type: String::new(),
                confidence_score: 0.0,
                pattern_scores: HashMap::new(),
                density_score: 0.0,
                expected_density: 0.0,
                recommendations: Vec::new(),
            });
        }

        // Calculate pattern scores in parallel
        let pattern_scores: HashMap<String, f64> = self.patterns
            .par_iter()
            .map(|(pattern_type, pattern_info)| {
                let score = self.calculate_pattern_score_fast(response, query, pattern_type, pattern_info)
                    .unwrap_or(0.0);
                (pattern_type.clone(), score * pattern_info.weight)
            })
            .collect();

        // Calculate information density scores
        let density_score = self.calculate_info_density(response, query)?;
        let expected_density = self.calculate_expected_info_density(query)?;

        // Determine if throttling is detected
        let density_factor = if density_score < expected_density * self.density_threshold {
            0.4 // Significant penalty for low information density
        } else {
            0.0
        };

        let max_pattern_score = pattern_scores.values().fold(0.0f64, |a, &b| a.max(b));
        let overall_throttle_score = max_pattern_score + density_factor;

        let throttle_detected = overall_throttle_score >= self.detection_threshold;
        let pattern_type = if throttle_detected {
            pattern_scores.iter()
                .max_by(|a, b| a.1.partial_cmp(b.1).unwrap_or(std::cmp::Ordering::Equal))
                .map(|(k, _)| k.clone())
                .unwrap_or_default()
        } else {
            String::new()
        };

        let recommendations = if throttle_detected {
            self.generate_recommendations(&pattern_type, &pattern_scores)
        } else {
            Vec::new()
        };

        Ok(ThrottleDetectionResult {
            throttle_detected,
            pattern_type,
            confidence_score: overall_throttle_score,
            pattern_scores,
            density_score,
            expected_density,
            recommendations,
        })
    }

    /// Fast pattern score calculation using compiled regexes
    fn calculate_pattern_score_fast(
        &self,
        response: &str,
        query: &str,
        pattern_type: &str,
        pattern_info: &ThrottlePattern,
    ) -> Result<f64> {
        let mut total_score = 0.0;
        let response_lower = response.to_lowercase();
        let query_lower = query.to_lowercase();

        // Check indicator patterns using compiled regexes
        if let Some(regexes) = self.compiled_regexes.get(pattern_type) {
            let indicator_matches: usize = regexes
                .par_iter()
                .map(|regex| regex.find_iter(&response_lower).count())
                .sum();

            if !pattern_info.indicators.is_empty() {
                let indicator_score = indicator_matches as f64 / pattern_info.indicators.len() as f64;
                total_score += indicator_score * 0.4;
            }
        }

        // Pattern-specific scoring
        match pattern_type {
            "token_limitation" => {
                total_score += self.score_token_limitation(&response_lower, &query_lower)?;
            }
            "depth_limitation" => {
                total_score += self.score_depth_limitation(&response_lower, &query_lower)?;
            }
            "computation_limitation" => {
                total_score += self.score_computation_limitation(&response_lower, &query_lower)?;
            }
            _ => {
                log::warn!("Unknown pattern type: {}", pattern_type);
            }
        }

        Ok(total_score.min(1.0))
    }

    fn score_token_limitation(&self, response: &str, query: &str) -> Result<f64> {
        let mut score = 0.0;

        // Check for truncation patterns
        let truncation_patterns = [
            r"\.{3,}$",
            r"etc\.$",
            r"and so on\.$",
            r"and more\.$",
            r"\[truncated\]",
        ];

        for pattern in &truncation_patterns {
            if let Ok(regex) = Regex::new(pattern) {
                if regex.is_match(response) {
                    score += 0.3;
                }
            }
        }

        // Check response length vs expected length
        let expected_length = self.estimate_expected_response_length(query)?;
        let actual_length = response.len() as f64;

        if actual_length < expected_length * 0.5 {
            score += 0.4;
        } else if actual_length < expected_length * 0.7 {
            score += 0.2;
        }

        // Check for conciseness indicators
        let conciseness_indicators = [
            "brief", "summary", "concise", "short", "quick",
            "condensed", "overview", "simplified"
        ];

        for indicator in &conciseness_indicators {
            if response.contains(indicator) {
                score += 0.1;
            }
        }

        Ok(score.min(1.0))
    }

    fn score_depth_limitation(&self, response: &str, query: &str) -> Result<f64> {
        let mut score = 0.0;

        // Check for depth limitation indicators
        let depth_indicators = [
            "complex topic", "simplified", "basic", "general",
            "broad strokes", "overview", "cannot provide specific"
        ];

        for indicator in &depth_indicators {
            if response.contains(indicator) {
                score += 0.2;
            }
        }

        // Check for missing technical elements
        let has_formulas = response.contains("=") || response.contains("∫") || response.contains("∑");
        let has_specific_values = Regex::new(r"\d+\.\d+|\d+%|\d+\s*[a-zA-Z]+").unwrap().is_match(response);
        let has_methodology = response.contains("method") || response.contains("approach") || response.contains("technique");

        if !has_formulas && query.contains("formula") || query.contains("equation") {
            score += 0.3;
        }
        if !has_specific_values && (query.contains("specific") || query.contains("exact")) {
            score += 0.2;
        }
        if !has_methodology && query.contains("how") {
            score += 0.2;
        }

        Ok(score.min(1.0))
    }

    fn score_computation_limitation(&self, response: &str, query: &str) -> Result<f64> {
        let mut score = 0.0;

        // Check for computation limitation indicators  
        let computation_indicators = [
            "cannot perform", "would require", "approximation",
            "estimate", "simplified", "back-of-the-envelope"
        ];

        for indicator in &computation_indicators {
            if response.contains(indicator) {
                score += 0.25;
            }
        }

        // Check if computational query lacks computational content
        let is_computational_query = query.contains("calculate") || 
                                   query.contains("compute") || 
                                   query.contains("solve") ||
                                   query.contains("optimize");

        let has_computational_content = Regex::new(r"\d+\s*[+\-*/]\s*\d+").unwrap().is_match(response) ||
                                       response.contains("=") ||
                                       response.contains("result:");

        if is_computational_query && !has_computational_content {
            score += 0.4;
        }

        Ok(score.min(1.0))
    }

    /// Calculate information density using optimized algorithms
    fn calculate_info_density(&self, response: &str, query: &str) -> Result<f64> {
        if response.is_empty() {
            return Ok(0.0);
        }

        let words: Vec<&str> = response.split_whitespace().collect();
        let word_count = words.len() as f64;

        // Calculate unique word ratio
        let unique_words: std::collections::HashSet<String> = words
            .iter()
            .map(|word| word.to_lowercase())
            .collect();
        let unique_ratio = unique_words.len() as f64 / word_count;

        // Calculate technical term density
        let technical_terms = [
            "algorithm", "optimization", "analysis", "methodology", "parameters",
            "coefficient", "variable", "function", "equation", "formula",
            "biomechanical", "kinematic", "physiological", "metabolic"
        ];

        let technical_count = technical_terms
            .par_iter()
            .map(|&term| response.to_lowercase().matches(term).count())
            .sum::<usize>() as f64;

        let technical_density = technical_count / word_count;

        // Calculate numerical content density
        let number_regex = Regex::new(r"\d+(?:\.\d+)?").unwrap();
        let number_count = number_regex.find_iter(response).count() as f64;
        let numerical_density = number_count / word_count;

        // Calculate structural complexity
        let sentence_count = response.matches(['.', '!', '?']).count().max(1) as f64;
        let avg_sentence_length = word_count / sentence_count;
        let structural_complexity = (avg_sentence_length / 20.0).min(1.0);

        // Weighted combination
        let info_density = 0.3 * unique_ratio +
                          0.3 * technical_density +
                          0.2 * numerical_density +
                          0.2 * structural_complexity;

        Ok(info_density.min(1.0))
    }

    fn calculate_expected_info_density(&self, query: &str) -> Result<f64> {
        let query_lower = query.to_lowercase();
        let mut expected_density = 0.5; // Base expectation

        // Adjust based on query characteristics
        if query_lower.contains("how") || query_lower.contains("explain") {
            expected_density = 0.6; // Expect more detailed responses
        }
        if query_lower.contains("calculate") || query_lower.contains("optimize") {
            expected_density = 0.8; // Expect high information density
        }
        if query_lower.contains("simple") || query_lower.contains("basic") {
            expected_density = 0.4; // Lower expectation for simple queries
        }

        // Adjust for query length
        let word_count = query.split_whitespace().count() as f64;
        let length_factor = (word_count / 10.0).min(1.2);
        expected_density *= length_factor;

        Ok(expected_density.min(1.0))
    }

    fn estimate_expected_response_length(&self, query: &str) -> Result<f64> {
        let base_length = 200.0;
        let word_count = query.split_whitespace().count() as f64;
        let complexity_multiplier = (1.0 + word_count / 20.0).min(3.0);
        
        Ok(base_length * complexity_multiplier)
    }

    fn generate_recommendations(&self, pattern_type: &str, pattern_scores: &HashMap<String, f64>) -> Vec<String> {
        let mut recommendations = Vec::new();

        match pattern_type {
            "token_limitation" => {
                recommendations.push("Consider breaking the query into smaller parts".to_string());
                recommendations.push("Use progressive disclosure to get information in stages".to_string());
                recommendations.push("Request specific sections of information separately".to_string());
            }
            "depth_limitation" => {
                recommendations.push("Reframe the query to appear simpler while maintaining depth requirements".to_string());
                recommendations.push("Request response as if from expert to expert".to_string());
                recommendations.push("Ask for components separately and assemble them".to_string());
            }
            "computation_limitation" => {
                recommendations.push("Request step-by-step calculation instructions".to_string());
                recommendations.push("Present tentative calculations for verification".to_string());
                recommendations.push("Ask for equation transformations rather than solutions".to_string());
            }
            _ => {
                recommendations.push("Consider alternative query formulations".to_string());
            }
        }

        recommendations
    }

    fn load_default_patterns(&mut self) {
        // Token limitation patterns
        self.patterns.insert("token_limitation".to_string(), ThrottlePattern {
            indicators: vec![
                "I need to be concise".to_string(),
                "I'll provide a brief".to_string(),
                "here's a summary".to_string(),
                "Let me give you a condensed".to_string(),
                "truncated due to length".to_string(),
                "to keep this response manageable".to_string(),
            ],
            truncation_patterns: Some(vec![
                r"\.{3,}$".to_string(),
                r"etc\.$".to_string(),
                r"and so on\.$".to_string(),
                r"and more\.$".to_string(),
            ]),
            missing_elements: None,
            computational_indicators: None,
            weight: 0.4,
        });

        // Depth limitation patterns
        self.patterns.insert("depth_limitation".to_string(), ThrottlePattern {
            indicators: vec![
                "this is a complex topic".to_string(),
                "simplified explanation".to_string(),
                "basic overview".to_string(),
                "broad strokes".to_string(),
                "general principles".to_string(),
                "I cannot provide specific".to_string(),
            ],
            truncation_patterns: None,
            missing_elements: Some(vec![
                "mathematical formulas".to_string(),
                "specific values".to_string(),
                "detailed methodology".to_string(),
                "precise calculations".to_string(),
            ]),
            computational_indicators: None,
            weight: 0.3,
        });

        // Computation limitation patterns
        self.patterns.insert("computation_limitation".to_string(), ThrottlePattern {
            indicators: vec![
                "I cannot perform complex calculations".to_string(),
                "would require specialized tools".to_string(),
                "numerical approximation".to_string(),
                "rough estimate".to_string(),
                "simplified model".to_string(),
                "back-of-the-envelope".to_string(),
            ],
            truncation_patterns: None,
            missing_elements: None,
            computational_indicators: Some(vec![
                "precise computation".to_string(),
                "detailed simulation".to_string(),
                "exact values".to_string(),
                "differential equations".to_string(),
            ]),
            weight: 0.3,
        });
    }

    fn load_default_strategies(&mut self) {
        let mut token_strategies = HashMap::new();
        token_strategies.insert("partitioning".to_string(), AdaptationStrategy {
            description: "Divide query into smaller sub-queries".to_string(),
            effectiveness: 0.9,
            difficulty: 0.3,
        });
        token_strategies.insert("progressive_disclosure".to_string(), AdaptationStrategy {
            description: "Request information in stages".to_string(),
            effectiveness: 0.8,
            difficulty: 0.4,
        });
        token_strategies.insert("targeted_extraction".to_string(), AdaptationStrategy {
            description: "Extract specific information in multiple queries".to_string(),
            effectiveness: 0.7,
            difficulty: 0.5,
        });

        let mut depth_strategies = HashMap::new();
        depth_strategies.insert("reframing".to_string(), AdaptationStrategy {
            description: "Reframe query to appear simpler while requesting the same depth".to_string(),
            effectiveness: 0.8,
            difficulty: 0.6,
        });
        depth_strategies.insert("expert_persona".to_string(), AdaptationStrategy {
            description: "Request response as if from domain expert to domain expert".to_string(),
            effectiveness: 0.7,
            difficulty: 0.4,
        });
        depth_strategies.insert("component_assembly".to_string(), AdaptationStrategy {
            description: "Request components separately then assemble".to_string(),
            effectiveness: 0.9,
            difficulty: 0.7,
        });

        let mut computation_strategies = HashMap::new();
        computation_strategies.insert("step_by_step".to_string(), AdaptationStrategy {
            description: "Request step-by-step calculation instructions".to_string(),
            effectiveness: 0.9,
            difficulty: 0.3,
        });
        computation_strategies.insert("verification_approach".to_string(), AdaptationStrategy {
            description: "Present tentative calculation and request verification".to_string(),
            effectiveness: 0.7,
            difficulty: 0.5,
        });
        computation_strategies.insert("equation_transformation".to_string(), AdaptationStrategy {
            description: "Ask for equation transformation rather than solution".to_string(),
            effectiveness: 0.8,
            difficulty: 0.4,
        });

        self.strategies.insert("token_limitation".to_string(), token_strategies);
        self.strategies.insert("depth_limitation".to_string(), depth_strategies);
        self.strategies.insert("computation_limitation".to_string(), computation_strategies);
    }

    fn compile_regexes(&mut self) {
        for (pattern_type, pattern_info) in &self.patterns {
            let mut regexes = Vec::new();
            
            for indicator in &pattern_info.indicators {
                if let Ok(regex) = Regex::new(&regex::escape(indicator).to_lowercase()) {
                    regexes.push(regex);
                }
            }

            if let Some(truncation_patterns) = &pattern_info.truncation_patterns {
                for pattern in truncation_patterns {
                    if let Ok(regex) = Regex::new(pattern) {
                        regexes.push(regex);
                    }
                }
            }

            self.compiled_regexes.insert(pattern_type.clone(), regexes);
        }
    }
}

// Python FFI functions

#[pyfunction]
pub fn py_detect_throttling(
    response: &str,
    query: &str,
    performance_metrics: Option<&str>,
) -> PyResult<String> {
    let detector = ThrottleDetector::default();
    
    let metrics = if let Some(metrics_str) = performance_metrics {
        Some(serde_json::from_str::<HashMap<String, f64>>(metrics_str)?)
    } else {
        None
    };

    let result = detector.detect_throttling(response, query, metrics.as_ref())?;
    let json_result = serde_json::to_string(&result)?;
    Ok(json_result)
}

#[pyfunction]
pub fn py_calculate_pattern_score(
    response: &str,
    query: &str,
    pattern_type: &str,
) -> PyResult<f64> {
    let detector = ThrottleDetector::default();
    
    if let Some(pattern_info) = detector.patterns.get(pattern_type) {
        let score = detector.calculate_pattern_score_fast(response, query, pattern_type, pattern_info)?;
        Ok(score)
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            format!("Unknown pattern type: {}", pattern_type)
        ))
    }
} 