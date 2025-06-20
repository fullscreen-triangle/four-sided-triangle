use crate::error::{FourSidedTriangleError, Result};
use crate::{text_processing_error, validation_error};
use pyo3::prelude::*;
use rayon::prelude::*;
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use unicode_segmentation::UnicodeSegmentation;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TextSimilarityResult {
    pub jaccard_similarity: f64,
    pub cosine_similarity: f64,
    pub semantic_similarity: f64,
    pub overall_similarity: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Entity {
    pub text: String,
    pub entity_type: String,
    pub start_pos: usize,
    pub end_pos: usize,
    pub confidence: f64,
}

/// Calculate text similarity using multiple algorithms
pub fn calculate_text_similarity(text1: &str, text2: &str) -> Result<TextSimilarityResult> {
    if text1.is_empty() || text2.is_empty() {
        return Ok(TextSimilarityResult {
            jaccard_similarity: 0.0,
            cosine_similarity: 0.0,
            semantic_similarity: 0.0,
            overall_similarity: 0.0,
        });
    }

    let jaccard = calculate_jaccard_similarity(text1, text2)?;
    let cosine = calculate_cosine_similarity(text1, text2)?;
    let semantic = calculate_semantic_similarity(text1, text2)?;
    
    // Weighted average
    let overall = 0.4 * jaccard + 0.4 * cosine + 0.2 * semantic;

    Ok(TextSimilarityResult {
        jaccard_similarity: jaccard,
        cosine_similarity: cosine,
        semantic_similarity: semantic,
        overall_similarity: overall,
    })
}

fn calculate_jaccard_similarity(text1: &str, text2: &str) -> Result<f64> {
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

    if union == 0 {
        Ok(0.0)
    } else {
        Ok(intersection as f64 / union as f64)
    }
}

fn calculate_cosine_similarity(text1: &str, text2: &str) -> Result<f64> {
    let words1: Vec<&str> = text1.split_whitespace().collect();
    let words2: Vec<&str> = text2.split_whitespace().collect();

    if words1.is_empty() || words2.is_empty() {
        return Ok(0.0);
    }

    // Create word frequency vectors
    let mut vocab: std::collections::HashSet<String> = std::collections::HashSet::new();
    for word in &words1 {
        vocab.insert(word.to_lowercase());
    }
    for word in &words2 {
        vocab.insert(word.to_lowercase());
    }

    let vocab: Vec<String> = vocab.into_iter().collect();
    let mut vec1 = vec![0.0; vocab.len()];
    let mut vec2 = vec![0.0; vocab.len()];

    for (i, word) in vocab.iter().enumerate() {
        vec1[i] = words1.iter().filter(|w| w.to_lowercase() == *word).count() as f64;
        vec2[i] = words2.iter().filter(|w| w.to_lowercase() == *word).count() as f64;
    }

    // Calculate cosine similarity
    let dot_product: f64 = vec1.iter().zip(vec2.iter()).map(|(a, b)| a * b).sum();
    let norm1: f64 = vec1.iter().map(|x| x * x).sum::<f64>().sqrt();
    let norm2: f64 = vec2.iter().map(|x| x * x).sum::<f64>().sqrt();

    if norm1 == 0.0 || norm2 == 0.0 {
        Ok(0.0)
    } else {
        Ok(dot_product / (norm1 * norm2))
    }
}

fn calculate_semantic_similarity(text1: &str, text2: &str) -> Result<f64> {
    // Simplified semantic similarity based on common patterns
    let technical_terms = [
        "algorithm", "optimization", "analysis", "methodology", "parameters",
        "coefficient", "variable", "function", "equation", "formula",
        "biomechanical", "kinematic", "physiological", "metabolic"
    ];

    let count1: usize = technical_terms
        .iter()
        .map(|&term| text1.to_lowercase().matches(term).count())
        .sum();
    let count2: usize = technical_terms
        .iter()
        .map(|&term| text2.to_lowercase().matches(term).count())
        .sum();

    let similarity = if count1.max(count2) == 0 {
        0.5 // Neutral similarity when no technical terms
    } else {
        count1.min(count2) as f64 / count1.max(count2) as f64
    };

    Ok(similarity)
}

/// Extract entities from text using pattern matching
pub fn extract_entities(text: &str) -> Result<Vec<Entity>> {
    let mut entities = Vec::new();

    // Extract numbers with units
    let number_regex = Regex::new(r"\b(\d+(?:\.\d+)?)\s*([a-zA-Z]+)\b")?;
    for captures in number_regex.captures_iter(text) {
        if let Some(m) = captures.get(0) {
            entities.push(Entity {
                text: m.as_str().to_string(),
                entity_type: "MEASUREMENT".to_string(),
                start_pos: m.start(),
                end_pos: m.end(),
                confidence: 0.9,
            });
        }
    }

    // Extract percentages
    let percent_regex = Regex::new(r"\b(\d+(?:\.\d+)?)\s*%")?;
    for captures in percent_regex.captures_iter(text) {
        if let Some(m) = captures.get(0) {
            entities.push(Entity {
                text: m.as_str().to_string(),
                entity_type: "PERCENTAGE".to_string(),
                start_pos: m.start(),
                end_pos: m.end(),
                confidence: 0.95,
            });
        }
    }

    // Extract time expressions
    let time_regex = Regex::new(r"\b(\d+)\s*(seconds?|minutes?|hours?|days?|weeks?|months?|years?)\b")?;
    for captures in time_regex.captures_iter(text) {
        if let Some(m) = captures.get(0) {
            entities.push(Entity {
                text: m.as_str().to_string(),
                entity_type: "TIME".to_string(),
                start_pos: m.start(),
                end_pos: m.end(),
                confidence: 0.85,
            });
        }
    }

    Ok(entities)
}

/// Advanced tokenization with stemming and normalization
pub fn tokenize_advanced(text: &str) -> Result<Vec<String>> {
    let mut tokens = Vec::new();
    
    // Split into words and normalize
    for word in text.unicode_words() {
        let normalized = word.to_lowercase();
        
        // Remove punctuation
        let cleaned: String = normalized.chars()
            .filter(|c| c.is_alphanumeric())
            .collect();
        
        if !cleaned.is_empty() && cleaned.len() > 2 {
            tokens.push(cleaned);
        }
    }

    Ok(tokens)
}

/// Calculate information density of text
pub fn calculate_information_density(text: &str, domain_context: Option<&str>) -> Result<f64> {
    if text.is_empty() {
        return Ok(0.0);
    }

    let words: Vec<&str> = text.split_whitespace().collect();
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
        .map(|&term| text.to_lowercase().matches(term).count())
        .sum::<usize>() as f64;

    let technical_density = technical_count / word_count;

    // Calculate numerical content density
    let number_regex = Regex::new(r"\d+(?:\.\d+)?").unwrap();
    let number_count = number_regex.find_iter(text).count() as f64;
    let numerical_density = number_count / word_count;

    // Weighted combination
    let info_density = 0.4 * unique_ratio + 0.4 * technical_density + 0.2 * numerical_density;

    Ok(info_density.min(1.0))
}

// Python FFI functions

#[pyfunction]
pub fn py_calculate_text_similarity(text1: &str, text2: &str) -> PyResult<String> {
    let result = calculate_text_similarity(text1, text2)?;
    let json_result = serde_json::to_string(&result)?;
    Ok(json_result)
}

#[pyfunction]
pub fn py_extract_entities(text: &str) -> PyResult<String> {
    let result = extract_entities(text)?;
    let json_result = serde_json::to_string(&result)?;
    Ok(json_result)
}

#[pyfunction]
pub fn py_tokenize_advanced(text: &str) -> PyResult<Vec<String>> {
    let result = tokenize_advanced(text)?;
    Ok(result)
}

#[pyfunction]
pub fn py_calculate_information_density(text: &str, domain_context: Option<&str>) -> PyResult<f64> {
    let result = calculate_information_density(text, domain_context)?;
    Ok(result)
} 