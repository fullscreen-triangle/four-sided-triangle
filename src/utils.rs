use crate::error::{FourSidedTriangleError, Result};
use std::time::{Duration, Instant};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PerformanceMetrics {
    pub execution_time_ms: u64,
    pub memory_usage_bytes: usize,
    pub cpu_usage_percent: f64,
    pub throughput_ops_per_sec: f64,
}

#[derive(Debug)]
pub struct Timer {
    start: Instant,
    name: String,
}

impl Timer {
    pub fn new(name: &str) -> Self {
        Self {
            start: Instant::now(),
            name: name.to_string(),
        }
    }

    pub fn elapsed(&self) -> Duration {
        self.start.elapsed()
    }

    pub fn elapsed_ms(&self) -> u64 {
        self.elapsed().as_millis() as u64
    }
}

impl Drop for Timer {
    fn drop(&mut self) {
        let elapsed = self.elapsed_ms();
        log::debug!("Timer '{}' completed in {}ms", self.name, elapsed);
    }
}

/// Macro for timing code blocks
#[macro_export]
macro_rules! time_it {
    ($name:expr, $code:block) => {{
        let _timer = $crate::utils::Timer::new($name);
        $code
    }};
}

/// Calculate statistical measures
pub fn calculate_statistics(values: &[f64]) -> Result<(f64, f64, f64, f64)> {
    if values.is_empty() {
        return Err(FourSidedTriangleError::ValidationError {
            message: "Cannot calculate statistics for empty array".to_string(),
        });
    }

    let n = values.len() as f64;
    let mean = values.iter().sum::<f64>() / n;
    
    let variance = values.iter()
        .map(|x| (x - mean).powi(2))
        .sum::<f64>() / n;
    
    let std_dev = variance.sqrt();
    
    let mut sorted = values.to_vec();
    sorted.sort_by(|a, b| a.partial_cmp(b).unwrap());
    
    let median = if sorted.len() % 2 == 0 {
        let mid = sorted.len() / 2;
        (sorted[mid - 1] + sorted[mid]) / 2.0
    } else {
        sorted[sorted.len() / 2]
    };

    Ok((mean, median, std_dev, variance))
}

/// Normalize values to 0-1 range
pub fn normalize_values(values: &[f64]) -> Result<Vec<f64>> {
    if values.is_empty() {
        return Ok(Vec::new());
    }

    let min_val = values.iter().fold(f64::INFINITY, |a, &b| a.min(b));
    let max_val = values.iter().fold(f64::NEG_INFINITY, |a, &b| a.max(b));
    
    if (max_val - min_val).abs() < f64::EPSILON {
        // All values are the same
        return Ok(vec![0.5; values.len()]);
    }

    let normalized = values.iter()
        .map(|&x| (x - min_val) / (max_val - min_val))
        .collect();

    Ok(normalized)
}

/// Calculate moving average
pub fn moving_average(values: &[f64], window_size: usize) -> Result<Vec<f64>> {
    if window_size == 0 || window_size > values.len() {
        return Err(FourSidedTriangleError::ValidationError {
            message: "Invalid window size for moving average".to_string(),
        });
    }

    let mut averages = Vec::new();
    
    for i in 0..=(values.len() - window_size) {
        let window = &values[i..(i + window_size)];
        let avg = window.iter().sum::<f64>() / window_size as f64;
        averages.push(avg);
    }

    Ok(averages)
}

/// Exponential moving average
pub fn exponential_moving_average(values: &[f64], alpha: f64) -> Result<Vec<f64>> {
    if alpha <= 0.0 || alpha > 1.0 {
        return Err(FourSidedTriangleError::ValidationError {
            message: "Alpha must be between 0 and 1".to_string(),
        });
    }

    if values.is_empty() {
        return Ok(Vec::new());
    }

    let mut ema = Vec::with_capacity(values.len());
    ema.push(values[0]); // First value is the starting point

    for &value in &values[1..] {
        let last_ema = ema.last().unwrap();
        let new_ema = alpha * value + (1.0 - alpha) * last_ema;
        ema.push(new_ema);
    }

    Ok(ema)
}

/// Calculate correlation coefficient between two series
pub fn correlation_coefficient(x: &[f64], y: &[f64]) -> Result<f64> {
    if x.len() != y.len() || x.is_empty() {
        return Err(FourSidedTriangleError::ValidationError {
            message: "Arrays must have the same non-zero length".to_string(),
        });
    }

    let n = x.len() as f64;
    let mean_x = x.iter().sum::<f64>() / n;
    let mean_y = y.iter().sum::<f64>() / n;

    let numerator: f64 = x.iter().zip(y.iter())
        .map(|(&xi, &yi)| (xi - mean_x) * (yi - mean_y))
        .sum();

    let sum_sq_x: f64 = x.iter().map(|&xi| (xi - mean_x).powi(2)).sum();
    let sum_sq_y: f64 = y.iter().map(|&yi| (yi - mean_y).powi(2)).sum();

    let denominator = (sum_sq_x * sum_sq_y).sqrt();

    if denominator == 0.0 {
        Ok(0.0) // No correlation if either series has no variance
    } else {
        Ok(numerator / denominator)
    }
}

/// Clamp value to range
pub fn clamp(value: f64, min: f64, max: f64) -> f64 {
    if value < min {
        min
    } else if value > max {
        max
    } else {
        value
    }
}

/// Linear interpolation
pub fn lerp(a: f64, b: f64, t: f64) -> f64 {
    a + t * (b - a)
}

/// Check if value is within tolerance of target
pub fn within_tolerance(value: f64, target: f64, tolerance: f64) -> bool {
    (value - target).abs() <= tolerance
}

/// Round to specified decimal places
pub fn round_to_decimal_places(value: f64, decimal_places: u32) -> f64 {
    let multiplier = 10_f64.powi(decimal_places as i32);
    (value * multiplier).round() / multiplier
}

/// Generate a simple hash for string content
pub fn simple_hash(content: &str) -> u64 {
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};
    
    let mut hasher = DefaultHasher::new();
    content.hash(&mut hasher);
    hasher.finish()
}

/// Performance monitoring utilities
pub struct PerformanceMonitor {
    timers: std::collections::HashMap<String, Timer>,
}

impl Default for PerformanceMonitor {
    fn default() -> Self {
        Self::new()
    }
}

impl PerformanceMonitor {
    pub fn new() -> Self {
        Self {
            timers: std::collections::HashMap::new(),
        }
    }

    pub fn start_timer(&mut self, name: &str) {
        self.timers.insert(name.to_string(), Timer::new(name));
    }

    pub fn stop_timer(&mut self, name: &str) -> Option<u64> {
        self.timers.remove(name).map(|timer| timer.elapsed_ms())
    }

    pub fn get_metrics(&self, name: &str) -> Option<u64> {
        self.timers.get(name).map(|timer| timer.elapsed_ms())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_calculate_statistics() {
        let values = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let (mean, median, std_dev, variance) = calculate_statistics(&values).unwrap();
        
        assert!((mean - 3.0).abs() < f64::EPSILON);
        assert!((median - 3.0).abs() < f64::EPSILON);
        assert!(std_dev > 0.0);
        assert!(variance > 0.0);
    }

    #[test]
    fn test_normalize_values() {
        let values = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let normalized = normalize_values(&values).unwrap();
        
        assert!((normalized[0] - 0.0).abs() < f64::EPSILON);
        assert!((normalized[4] - 1.0).abs() < f64::EPSILON);
    }

    #[test]
    fn test_correlation_coefficient() {
        let x = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let y = vec![2.0, 4.0, 6.0, 8.0, 10.0]; // Perfect positive correlation
        
        let correlation = correlation_coefficient(&x, &y).unwrap();
        assert!((correlation - 1.0).abs() < 1e-10);
    }
} 