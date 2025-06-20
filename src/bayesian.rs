use crate::error::{FourSidedTriangleError, Result};
use crate::{bayesian_error, validation_error};
use nalgebra::{DMatrix, DVector};
use pyo3::prelude::*;
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use statrs::distribution::{Beta, Continuous, Normal};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BayesianMetrics {
    pub posterior_probability: f64,
    pub likelihood: f64,
    pub prior: f64,
    pub evidence: f64,
    pub information_gain: f64,
    pub mutual_information: f64,
    pub confidence_interval: (f64, f64),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DomainKnowledge {
    pub facts: Vec<String>,
    pub formulas: Vec<String>,
    pub confidence_scores: Vec<f64>,
    pub relationships: Vec<(String, String, f64)>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QueryIntent {
    pub intent_type: String,
    pub complexity: f64,
    pub domain_specificity: f64,
    pub parameters: HashMap<String, f64>,
}

/// High-performance Bayesian evaluator using Rust's mathematical libraries
pub struct BayesianEvaluator {
    alpha_prior: f64,
    beta_prior: f64,
    confidence_level: f64,
}

impl Default for BayesianEvaluator {
    fn default() -> Self {
        Self {
            alpha_prior: 1.0,
            beta_prior: 1.0,
            confidence_level: 0.95,
        }
    }
}

impl BayesianEvaluator {
    pub fn new(alpha_prior: f64, beta_prior: f64, confidence_level: f64) -> Result<Self> {
        if alpha_prior <= 0.0 || beta_prior <= 0.0 {
            return Err(validation_error!("Prior parameters must be positive"));
        }
        if confidence_level <= 0.0 || confidence_level >= 1.0 {
            return Err(validation_error!("Confidence level must be between 0 and 1"));
        }
        
        Ok(Self {
            alpha_prior,
            beta_prior,
            confidence_level,
        })
    }

    /// Calculate posterior probability P(R|D,Q) using Bayesian inference
    pub fn calculate_posterior_probability(
        &self,
        solution: &str,
        domain_knowledge: &DomainKnowledge,
        query_intent: &QueryIntent,
    ) -> Result<f64> {
        let prior = self.calculate_prior_probability(solution, query_intent)?;
        let likelihood = self.calculate_likelihood(solution, domain_knowledge, query_intent)?;
        let evidence = self.calculate_evidence_factor(domain_knowledge, query_intent)?;

        if evidence == 0.0 {
            return Err(bayesian_error!("Evidence factor cannot be zero"));
        }

        let posterior = (likelihood * prior) / evidence;
        
        // Ensure posterior is within valid bounds
        if posterior < 0.0 || posterior > 1.0 {
            log::warn!("Posterior probability {} is outside valid bounds, clamping", posterior);
            Ok(posterior.clamp(0.0, 1.0))
        } else {
            Ok(posterior)
        }
    }

    /// Calculate prior probability P(R|Q) based on query characteristics
    pub fn calculate_prior_probability(&self, solution: &str, query_intent: &QueryIntent) -> Result<f64> {
        let solution_length = solution.len() as f64;
        let expected_length = self.estimate_expected_length(query_intent)?;
        
        // Length-based prior
        let length_factor = if expected_length > 0.0 {
            (-((solution_length - expected_length) / expected_length).powi(2) / 2.0).exp()
        } else {
            0.5
        };

        // Complexity-based prior
        let complexity_factor = match query_intent.intent_type.as_str() {
            "computational" => 0.3 + 0.4 * query_intent.complexity,
            "informational" => 0.7 - 0.2 * query_intent.complexity,
            "comparison" => 0.5,
            _ => 0.5,
        };

        // Domain specificity factor
        let domain_factor = 0.3 + 0.4 * query_intent.domain_specificity;

        let prior = length_factor * complexity_factor * domain_factor;
        Ok(prior.clamp(0.001, 0.999)) // Avoid extreme values
    }

    /// Calculate likelihood P(D|R,Q) using domain knowledge alignment
    pub fn calculate_likelihood(
        &self,
        solution: &str,
        domain_knowledge: &DomainKnowledge,
        query_intent: &QueryIntent,
    ) -> Result<f64> {
        if domain_knowledge.facts.is_empty() {
            return Ok(0.5); // Neutral likelihood when no domain knowledge
        }

        // Parallel computation for performance
        let fact_alignments: Vec<f64> = domain_knowledge.facts
            .par_iter()
            .zip(domain_knowledge.confidence_scores.par_iter())
            .map(|(fact, &confidence)| {
                let alignment = self.calculate_text_alignment(solution, fact);
                alignment * confidence
            })
            .collect();

        let formula_alignments: Vec<f64> = domain_knowledge.formulas
            .par_iter()
            .map(|formula| self.calculate_formula_alignment(solution, formula))
            .collect();

        let relationship_alignments: Vec<f64> = domain_knowledge.relationships
            .par_iter()
            .map(|(source, target, &strength)| {
                let source_presence = solution.contains(source) as i32 as f64;
                let target_presence = solution.contains(target) as i32 as f64;
                source_presence * target_presence * strength
            })
            .collect();

        // Weighted average of alignments
        let fact_weight = 0.5;
        let formula_weight = 0.3;
        let relationship_weight = 0.2;

        let avg_fact_alignment = fact_alignments.iter().sum::<f64>() / fact_alignments.len().max(1) as f64;
        let avg_formula_alignment = formula_alignments.iter().sum::<f64>() / formula_alignments.len().max(1) as f64;
        let avg_relationship_alignment = relationship_alignments.iter().sum::<f64>() / relationship_alignments.len().max(1) as f64;

        let likelihood = fact_weight * avg_fact_alignment
            + formula_weight * avg_formula_alignment
            + relationship_weight * avg_relationship_alignment;

        Ok(likelihood.clamp(0.001, 0.999))
    }

    /// Calculate evidence factor P(D|Q) for normalization
    pub fn calculate_evidence_factor(
        &self,
        domain_knowledge: &DomainKnowledge,
        query_intent: &QueryIntent,
    ) -> Result<f64> {
        let knowledge_relevance = domain_knowledge.confidence_scores.iter().sum::<f64>() 
            / domain_knowledge.confidence_scores.len().max(1) as f64;
        
        let query_specificity = query_intent.domain_specificity;
        let complexity_factor = (1.0 + query_intent.complexity) / 2.0;
        
        let evidence = knowledge_relevance * query_specificity * complexity_factor;
        Ok(evidence.clamp(0.001, 1.0))
    }

    /// Calculate information gain of the solution
    pub fn calculate_information_gain(
        &self,
        solution: &str,
        domain_knowledge: &DomainKnowledge,
        query_intent: &QueryIntent,
    ) -> Result<f64> {
        let solution_entropy = self.calculate_text_entropy(solution)?;
        let domain_entropy = self.calculate_domain_entropy(domain_knowledge)?;
        let query_entropy = self.calculate_query_entropy(query_intent)?;

        // Information gain = H(S) - H(S|D,Q)
        let conditional_entropy = solution_entropy * (1.0 - (domain_entropy + query_entropy) / 2.0);
        let information_gain = solution_entropy - conditional_entropy;

        Ok(information_gain.max(0.0))
    }

    /// Calculate mutual information between solution and query intent
    pub fn calculate_mutual_information(
        &self,
        solution: &str,
        domain_knowledge: &DomainKnowledge,
        query_intent: &QueryIntent,
    ) -> Result<f64> {
        let solution_entropy = self.calculate_text_entropy(solution)?;
        let query_entropy = self.calculate_query_entropy(query_intent)?;
        
        // Estimate joint entropy
        let joint_entropy = solution_entropy + query_entropy - self.calculate_correlation(solution, query_intent)?;
        
        // Mutual information = H(S) + H(Q) - H(S,Q)
        let mutual_info = solution_entropy + query_entropy - joint_entropy;
        
        Ok(mutual_info.max(0.0))
    }

    /// Calculate confidence interval for the posterior probability
    pub fn calculate_confidence_interval(&self, posterior: f64, sample_size: f64) -> Result<(f64, f64)> {
        if sample_size <= 0.0 {
            return Err(bayesian_error!("Sample size must be positive"));
        }

        let alpha = 1.0 - self.confidence_level;
        let z_score = Normal::new(0.0, 1.0).unwrap().inverse_cdf(1.0 - alpha / 2.0);
        
        let standard_error = (posterior * (1.0 - posterior) / sample_size).sqrt();
        let margin_of_error = z_score * standard_error;
        
        let lower_bound = (posterior - margin_of_error).max(0.0);
        let upper_bound = (posterior + margin_of_error).min(1.0);
        
        Ok((lower_bound, upper_bound))
    }

    // Helper methods

    fn estimate_expected_length(&self, query_intent: &QueryIntent) -> Result<f64> {
        let base_length = match query_intent.intent_type.as_str() {
            "computational" => 200.0,
            "informational" => 500.0,
            "comparison" => 300.0,
            _ => 350.0,
        };

        let complexity_multiplier = 1.0 + query_intent.complexity;
        let domain_multiplier = 1.0 + query_intent.domain_specificity * 0.5;

        Ok(base_length * complexity_multiplier * domain_multiplier)
    }

    fn calculate_text_alignment(&self, text1: &str, text2: &str) -> f64 {
        let words1: Vec<&str> = text1.split_whitespace().collect();
        let words2: Vec<&str> = text2.split_whitespace().collect();
        
        if words1.is_empty() || words2.is_empty() {
            return 0.0;
        }

        let common_words = words1.iter()
            .filter(|word| words2.contains(word))
            .count();

        common_words as f64 / (words1.len() + words2.len() - common_words) as f64
    }

    fn calculate_formula_alignment(&self, solution: &str, formula: &str) -> f64 {
        // Simple heuristic: check for mathematical symbols and patterns
        let math_symbols = ["=", "+", "-", "*", "/", "^", "(", ")", "∫", "∑", "∆"];
        let solution_math_count = math_symbols.iter()
            .map(|&symbol| solution.matches(symbol).count())
            .sum::<usize>();
        let formula_math_count = math_symbols.iter()
            .map(|&symbol| formula.matches(symbol).count())
            .sum::<usize>();

        if solution_math_count == 0 && formula_math_count == 0 {
            return 0.0;
        }

        let alignment = (solution_math_count.min(formula_math_count) as f64) 
            / (solution_math_count.max(formula_math_count) as f64);

        alignment * self.calculate_text_alignment(solution, formula)
    }

    fn calculate_text_entropy(&self, text: &str) -> Result<f64> {
        let words: Vec<&str> = text.split_whitespace().collect();
        if words.is_empty() {
            return Ok(0.0);
        }

        let mut word_counts = HashMap::new();
        for word in &words {
            *word_counts.entry(word.to_lowercase()).or_insert(0) += 1;
        }

        let total_words = words.len() as f64;
        let entropy = word_counts.values()
            .map(|&count| {
                let prob = count as f64 / total_words;
                -prob * prob.log2()
            })
            .sum::<f64>();

        Ok(entropy)
    }

    fn calculate_domain_entropy(&self, domain_knowledge: &DomainKnowledge) -> Result<f64> {
        if domain_knowledge.facts.is_empty() {
            return Ok(0.0);
        }

        let avg_confidence = domain_knowledge.confidence_scores.iter().sum::<f64>() 
            / domain_knowledge.confidence_scores.len() as f64;

        // Entropy based on confidence distribution
        let entropy = domain_knowledge.confidence_scores.iter()
            .map(|&conf| {
                if conf > 0.0 {
                    -conf * conf.log2()
                } else {
                    0.0
                }
            })
            .sum::<f64>();

        Ok(entropy / domain_knowledge.confidence_scores.len() as f64)
    }

    fn calculate_query_entropy(&self, query_intent: &QueryIntent) -> Result<f64> {
        let complexity_entropy = if query_intent.complexity > 0.0 {
            -query_intent.complexity * query_intent.complexity.log2()
        } else {
            0.0
        };

        let specificity_entropy = if query_intent.domain_specificity > 0.0 {
            -query_intent.domain_specificity * query_intent.domain_specificity.log2()
        } else {
            0.0
        };

        Ok((complexity_entropy + specificity_entropy) / 2.0)
    }

    fn calculate_correlation(&self, solution: &str, query_intent: &QueryIntent) -> Result<f64> {
        let solution_length = solution.len() as f64;
        let expected_length = self.estimate_expected_length(query_intent)?;
        
        // Simple correlation based on length alignment
        let length_correlation = if expected_length > 0.0 {
            1.0 - ((solution_length - expected_length) / expected_length).abs()
        } else {
            0.0
        };

        Ok(length_correlation.clamp(0.0, 1.0))
    }
}

/// Perform complete Bayesian evaluation
pub fn bayesian_evaluate(
    solution: &str,
    domain_knowledge: &DomainKnowledge,
    query_intent: &QueryIntent,
    evaluator: &BayesianEvaluator,
) -> Result<BayesianMetrics> {
    let prior = evaluator.calculate_prior_probability(solution, query_intent)?;
    let likelihood = evaluator.calculate_likelihood(solution, domain_knowledge, query_intent)?;
    let evidence = evaluator.calculate_evidence_factor(domain_knowledge, query_intent)?;
    let posterior = evaluator.calculate_posterior_probability(solution, domain_knowledge, query_intent)?;
    let information_gain = evaluator.calculate_information_gain(solution, domain_knowledge, query_intent)?;
    let mutual_information = evaluator.calculate_mutual_information(solution, domain_knowledge, query_intent)?;
    
    let sample_size = solution.split_whitespace().count() as f64;
    let confidence_interval = evaluator.calculate_confidence_interval(posterior, sample_size)?;

    Ok(BayesianMetrics {
        posterior_probability: posterior,
        likelihood,
        prior,
        evidence,
        information_gain,
        mutual_information,
        confidence_interval,
    })
}

// Python FFI functions

#[pyfunction]
pub fn py_calculate_posterior_probability(
    solution: &str,
    domain_knowledge: &str,
    query_intent: &str,
) -> PyResult<f64> {
    let domain_knowledge: DomainKnowledge = serde_json::from_str(domain_knowledge)?;
    let query_intent: QueryIntent = serde_json::from_str(query_intent)?;
    let evaluator = BayesianEvaluator::default();
    
    let result = evaluator.calculate_posterior_probability(solution, &domain_knowledge, &query_intent)?;
    Ok(result)
}

#[pyfunction]
pub fn py_calculate_information_gain(
    solution: &str,
    domain_knowledge: &str,
    query_intent: &str,
) -> PyResult<f64> {
    let domain_knowledge: DomainKnowledge = serde_json::from_str(domain_knowledge)?;
    let query_intent: QueryIntent = serde_json::from_str(query_intent)?;
    let evaluator = BayesianEvaluator::default();
    
    let result = evaluator.calculate_information_gain(solution, &domain_knowledge, &query_intent)?;
    Ok(result)
}

#[pyfunction]
pub fn py_calculate_mutual_information(
    solution: &str,
    domain_knowledge: &str,
    query_intent: &str,
) -> PyResult<f64> {
    let domain_knowledge: DomainKnowledge = serde_json::from_str(domain_knowledge)?;
    let query_intent: QueryIntent = serde_json::from_str(query_intent)?;
    let evaluator = BayesianEvaluator::default();
    
    let result = evaluator.calculate_mutual_information(solution, &domain_knowledge, &query_intent)?;
    Ok(result)
}

#[pyfunction]
pub fn py_bayesian_evaluate(
    solution: &str,
    domain_knowledge: &str,
    query_intent: &str,
) -> PyResult<String> {
    let domain_knowledge: DomainKnowledge = serde_json::from_str(domain_knowledge)?;
    let query_intent: QueryIntent = serde_json::from_str(query_intent)?;
    let evaluator = BayesianEvaluator::default();
    
    let result = bayesian_evaluate(solution, &domain_knowledge, &query_intent, &evaluator)?;
    let json_result = serde_json::to_string(&result)?;
    Ok(json_result)
} 