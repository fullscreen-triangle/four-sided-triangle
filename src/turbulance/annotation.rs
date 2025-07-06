//! Turbulance DSL Annotation Engine
//! 
//! Annotates original Turbulance scripts with execution results, embedding outputs and statistics
//! at appropriate locations to create comprehensive documented execution traces.

use crate::error::{FourSidedTriangleError, Result};
use crate::{validation_error};
use super::parser::{TurbulanceScript, TurbulanceNode, TurbulanceValue};
use super::orchestrator::{ExecutionResult, StepResult, QualityMetrics, ExecutionStatistics};
use super::compiler::CompiledProtocol;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use regex::Regex;

/// Annotated script with embedded execution results
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnnotatedScript {
    pub original_script: String,
    pub annotated_script: String,
    pub annotation_summary: AnnotationSummary,
    pub execution_metadata: ExecutionMetadata,
}

/// Summary of annotations added to the script
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnnotationSummary {
    pub total_annotations: usize,
    pub result_annotations: usize,
    pub quality_annotations: usize,
    pub performance_annotations: usize,
    pub error_annotations: usize,
    pub auxiliary_file_annotations: usize,
}

/// Metadata about the execution and annotation process
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionMetadata {
    pub protocol_name: String,
    pub execution_timestamp: String,
    pub total_execution_time: f64,
    pub overall_success: bool,
    pub steps_completed: usize,
    pub steps_failed: usize,
    pub average_quality_score: f64,
    pub resource_efficiency: f64,
}

/// Types of annotations that can be added
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum AnnotationType {
    ExecutionResult,
    QualityMetrics,
    PerformanceStats,
    ErrorMessage,
    AuxiliaryFileReference,
    Summary,
}

/// Individual annotation entry
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Annotation {
    pub annotation_type: AnnotationType,
    pub line_number: usize,
    pub content: String,
    pub metadata: HashMap<String, serde_json::Value>,
}

/// High-performance Turbulance annotation engine
pub struct TurbulanceAnnotator {
    // Annotation formatting options
    pub compact_mode: bool,
    pub include_debug_info: bool,
    pub max_output_length: usize,
    pub indent_style: String,
    
    // Statistics
    scripts_annotated: usize,
    total_annotations_added: usize,
    average_annotation_density: f64,
}

impl Default for TurbulanceAnnotator {
    fn default() -> Self {
        Self::new()
    }
}

impl TurbulanceAnnotator {
    pub fn new() -> Self {
        Self {
            compact_mode: false,
            include_debug_info: true,
            max_output_length: 2000,
            indent_style: "  ".to_string(),
            scripts_annotated: 0,
            total_annotations_added: 0,
            average_annotation_density: 0.0,
        }
    }

    pub fn with_compact_mode(mut self, compact: bool) -> Self {
        self.compact_mode = compact;
        self
    }

    pub fn with_debug_info(mut self, debug: bool) -> Self {
        self.include_debug_info = debug;
        self
    }

    pub fn with_max_output_length(mut self, length: usize) -> Self {
        self.max_output_length = length;
        self
    }

    /// Annotate a script with execution results
    pub fn annotate_script(
        &mut self,
        original_script: &str,
        execution_result: &ExecutionResult,
        compiled_protocol: &CompiledProtocol,
    ) -> Result<AnnotatedScript> {
        // Parse the original script to understand its structure
        let script_lines: Vec<&str> = original_script.lines().collect();
        let mut annotated_lines: Vec<String> = Vec::new();
        let mut annotations: Vec<Annotation> = Vec::new();

        // Create execution metadata
        let execution_metadata = ExecutionMetadata {
            protocol_name: execution_result.protocol_name.clone(),
            execution_timestamp: chrono::Utc::now().to_rfc3339(),
            total_execution_time: execution_result.total_execution_time_seconds,
            overall_success: execution_result.overall_status == super::orchestrator::ExecutionStatus::Completed,
            steps_completed: execution_result.execution_statistics.steps_completed,
            steps_failed: execution_result.execution_statistics.steps_failed,
            average_quality_score: execution_result.execution_statistics.average_step_quality,
            resource_efficiency: execution_result.execution_statistics.resource_utilization_efficiency,
        };

        // Add header annotation
        let header_annotation = self.create_header_annotation(execution_result, compiled_protocol)?;
        annotated_lines.push(header_annotation.content.clone());
        annotated_lines.push("".to_string());
        annotations.push(header_annotation);

        // Process each line of the original script
        for (line_idx, line) in script_lines.iter().enumerate() {
            let line_number = line_idx + 1;
            annotated_lines.push(line.to_string());

            // Check if this line contains a pipeline stage call
            if let Some(stage_annotation) = self.find_stage_annotation(line, line_number, execution_result, compiled_protocol)? {
                // Add execution result annotation
                let result_annotation = self.create_result_annotation(&stage_annotation, execution_result)?;
                annotated_lines.push("".to_string());
                annotated_lines.push(result_annotation.content.clone());
                annotated_lines.push("".to_string());
                annotations.push(result_annotation);

                // Add quality metrics annotation
                if let Some(quality_annotation) = self.create_quality_annotation(&stage_annotation, execution_result)? {
                    annotated_lines.push(quality_annotation.content.clone());
                    annotated_lines.push("".to_string());
                    annotations.push(quality_annotation);
                }

                // Add performance annotation
                if let Some(perf_annotation) = self.create_performance_annotation(&stage_annotation, execution_result)? {
                    annotated_lines.push(perf_annotation.content.clone());
                    annotated_lines.push("".to_string());
                    annotations.push(perf_annotation);
                }
            }
        }

        // Add auxiliary file annotations
        let aux_annotations = self.create_auxiliary_file_annotations(compiled_protocol)?;
        if !aux_annotations.is_empty() {
            annotated_lines.push("".to_string());
            annotated_lines.push("# ═══════════════════════════════════════════════════════════════════════════════".to_string());
            annotated_lines.push("# AUXILIARY FILES GENERATED".to_string());
            annotated_lines.push("# ═══════════════════════════════════════════════════════════════════════════════".to_string());
            annotated_lines.push("".to_string());
            
            for aux_annotation in aux_annotations {
                annotated_lines.push(aux_annotation.content.clone());
                annotated_lines.push("".to_string());
                annotations.push(aux_annotation);
            }
        }

        // Add summary annotation
        let summary_annotation = self.create_summary_annotation(execution_result, &annotations)?;
        annotated_lines.push("".to_string());
        annotated_lines.push(summary_annotation.content.clone());
        annotations.push(summary_annotation);

        // Create annotation summary
        let annotation_summary = AnnotationSummary {
            total_annotations: annotations.len(),
            result_annotations: annotations.iter().filter(|a| matches!(a.annotation_type, AnnotationType::ExecutionResult)).count(),
            quality_annotations: annotations.iter().filter(|a| matches!(a.annotation_type, AnnotationType::QualityMetrics)).count(),
            performance_annotations: annotations.iter().filter(|a| matches!(a.annotation_type, AnnotationType::PerformanceStats)).count(),
            error_annotations: annotations.iter().filter(|a| matches!(a.annotation_type, AnnotationType::ErrorMessage)).count(),
            auxiliary_file_annotations: annotations.iter().filter(|a| matches!(a.annotation_type, AnnotationType::AuxiliaryFileReference)).count(),
        };

        // Update statistics
        self.scripts_annotated += 1;
        self.total_annotations_added += annotations.len();
        self.average_annotation_density = self.total_annotations_added as f64 / self.scripts_annotated as f64;

        Ok(AnnotatedScript {
            original_script: original_script.to_string(),
            annotated_script: annotated_lines.join("\n"),
            annotation_summary,
            execution_metadata,
        })
    }

    /// Create header annotation with execution overview
    fn create_header_annotation(&self, execution_result: &ExecutionResult, compiled_protocol: &CompiledProtocol) -> Result<Annotation> {
        let success_indicator = if execution_result.overall_status == super::orchestrator::ExecutionStatus::Completed {
            "✓ SUCCESS"
        } else {
            "✗ FAILED"
        };

        let content = format!(
            "# ═══════════════════════════════════════════════════════════════════════════════
# TURBULANCE EXECUTION RESULTS - {}
# ═══════════════════════════════════════════════════════════════════════════════
# Protocol: {}
# Execution Time: {:.2}s
# Steps Completed: {}/{}
# Overall Quality: {:.2}
# Resource Efficiency: {:.2}%
# Execution Mode: {:?}
# ═══════════════════════════════════════════════════════════════════════════════",
            success_indicator,
            execution_result.protocol_name,
            execution_result.total_execution_time_seconds,
            execution_result.execution_statistics.steps_completed,
            execution_result.step_results.len(),
            execution_result.execution_statistics.average_step_quality,
            execution_result.execution_statistics.resource_utilization_efficiency * 100.0,
            compiled_protocol.execution_mode,
        );

        Ok(Annotation {
            annotation_type: AnnotationType::Summary,
            line_number: 0,
            content,
            metadata: HashMap::new(),
        })
    }

    /// Find stage annotation for a given line
    fn find_stage_annotation(&self, line: &str, line_number: usize, execution_result: &ExecutionResult, compiled_protocol: &CompiledProtocol) -> Result<Option<String>> {
        // Look for pipeline stage calls using regex
        let stage_regex = Regex::new(r"(\w+)\s*=\s*pipeline\.(\w+)\s*\(").unwrap();
        
        if let Some(captures) = stage_regex.captures(line) {
            let variable_name = captures.get(1).unwrap().as_str();
            let stage_name = captures.get(2).unwrap().as_str();
            
            // Find corresponding execution step
            let step_id = format!("{}_{}", execution_result.protocol_name, variable_name);
            
            return Ok(Some(step_id));
        }
        
        Ok(None)
    }

    /// Create result annotation for a stage
    fn create_result_annotation(&self, step_id: &str, execution_result: &ExecutionResult) -> Result<Annotation> {
        let step_result = execution_result.step_results.iter()
            .find(|r| r.step_id == step_id)
            .ok_or_else(|| validation_error!(format!("Step result not found: {}", step_id)))?;

        let status_indicator = match step_result.status {
            super::orchestrator::ExecutionStatus::Completed => "✓",
            super::orchestrator::ExecutionStatus::Failed => "✗",
            super::orchestrator::ExecutionStatus::Timeout => "⏱",
            _ => "?",
        };

        let output_preview = self.format_output_preview(&step_result.output)?;
        
        let content = format!(
            "{}# {} EXECUTION RESULT: {}
{}# Time: {:.2}s | CPU: {:.1} cores | Memory: {:.1} GB | Status: {}
{}# Output Preview:
{}{}",
            self.indent_style,
            status_indicator,
            step_result.step_id,
            self.indent_style,
            step_result.execution_time_seconds,
            step_result.resource_usage.cpu_cores_used,
            step_result.resource_usage.memory_gb_used,
            format!("{:?}", step_result.status),
            self.indent_style,
            self.indent_style,
            output_preview,
        );

        let mut metadata = HashMap::new();
        metadata.insert("execution_time".to_string(), serde_json::Value::Number(serde_json::Number::from_f64(step_result.execution_time_seconds).unwrap()));
        metadata.insert("status".to_string(), serde_json::Value::String(format!("{:?}", step_result.status)));

        Ok(Annotation {
            annotation_type: AnnotationType::ExecutionResult,
            line_number: 0,
            content,
            metadata,
        })
    }

    /// Create quality metrics annotation
    fn create_quality_annotation(&self, step_id: &str, execution_result: &ExecutionResult) -> Result<Option<Annotation>> {
        let step_result = execution_result.step_results.iter()
            .find(|r| r.step_id == step_id)
            .ok_or_else(|| validation_error!(format!("Step result not found: {}", step_id)))?;

        if self.compact_mode {
            return Ok(None);
        }

        let quality = &step_result.quality_metrics;
        let avg_quality = (quality.accuracy + quality.completeness + quality.relevance + 
                          quality.confidence + quality.novelty + quality.coherence) / 6.0;

        let content = format!(
            "{}# QUALITY METRICS (Average: {:.2})
{}# Accuracy: {:.2} | Completeness: {:.2} | Relevance: {:.2}
{}# Confidence: {:.2} | Novelty: {:.2} | Coherence: {:.2}",
            self.indent_style,
            avg_quality,
            self.indent_style,
            quality.accuracy,
            quality.completeness,
            quality.relevance,
            self.indent_style,
            quality.confidence,
            quality.novelty,
            quality.coherence,
        );

        Ok(Some(Annotation {
            annotation_type: AnnotationType::QualityMetrics,
            line_number: 0,
            content,
            metadata: HashMap::new(),
        }))
    }

    /// Create performance annotation
    fn create_performance_annotation(&self, step_id: &str, execution_result: &ExecutionResult) -> Result<Option<Annotation>> {
        let step_result = execution_result.step_results.iter()
            .find(|r| r.step_id == step_id)
            .ok_or_else(|| validation_error!(format!("Step result not found: {}", step_id)))?;

        if self.compact_mode {
            return Ok(None);
        }

        let usage = &step_result.resource_usage;
        let content = format!(
            "{}# RESOURCE USAGE
{}# CPU: {:.1} cores | Memory: {:.1} GB | GPU: {:.1} units
{}# Network: {:.1} Mbps | Storage: {:.1} GB",
            self.indent_style,
            self.indent_style,
            usage.cpu_cores_used,
            usage.memory_gb_used,
            usage.gpu_units_used,
            self.indent_style,
            usage.network_bandwidth_mbps_used,
            usage.storage_gb_used,
        );

        Ok(Some(Annotation {
            annotation_type: AnnotationType::PerformanceStats,
            line_number: 0,
            content,
            metadata: HashMap::new(),
        }))
    }

    /// Create auxiliary file annotations
    fn create_auxiliary_file_annotations(&self, compiled_protocol: &CompiledProtocol) -> Result<Vec<Annotation>> {
        let mut annotations = Vec::new();

        // .fs file annotation
        let fs_annotation = Annotation {
            annotation_type: AnnotationType::AuxiliaryFileReference,
            line_number: 0,
            content: format!(
                "# 📊 NETWORK GRAPH STATE (.fs)
# Consciousness levels and processing flow analysis
# Nodes: {} | Parallel Capacity: {} | Complexity Score: {:.2}
# Preview: {}",
                compiled_protocol.execution_steps.len(),
                compiled_protocol.parallel_groups.len(),
                compiled_protocol.total_resource_requirements.cpu_cores + compiled_protocol.total_resource_requirements.memory_gb,
                self.format_json_preview(&compiled_protocol.auxiliary_files.fs_content)?
            ),
            metadata: HashMap::new(),
        };
        annotations.push(fs_annotation);

        // .ghd file annotation
        let ghd_annotation = Annotation {
            annotation_type: AnnotationType::AuxiliaryFileReference,
            line_number: 0,
            content: format!(
                "# 🔧 RESOURCE ORCHESTRATION (.ghd)
# Resource allocation and orchestration planning
# CPU: {:.1} cores | Memory: {:.1} GB | Estimated Duration: {:.1}s
# Preview: {}",
                compiled_protocol.total_resource_requirements.cpu_cores,
                compiled_protocol.total_resource_requirements.memory_gb,
                compiled_protocol.total_resource_requirements.estimated_duration_seconds,
                self.format_json_preview(&compiled_protocol.auxiliary_files.ghd_content)?
            ),
            metadata: HashMap::new(),
        };
        annotations.push(ghd_annotation);

        // .hre file annotation
        let hre_annotation = Annotation {
            annotation_type: AnnotationType::AuxiliaryFileReference,
            line_number: 0,
            content: format!(
                "# 🧠 METACOGNITIVE MEMORY (.hre)
# Decision memory and optimization insights
# Optimization Hints: {} | Critical Stages: {}
# Preview: {}",
                compiled_protocol.optimization_hints.len(),
                compiled_protocol.execution_steps.iter().filter(|s| s.resource_requirements.cpu_cores > 3.0).count(),
                self.format_json_preview(&compiled_protocol.auxiliary_files.hre_content)?
            ),
            metadata: HashMap::new(),
        };
        annotations.push(hre_annotation);

        Ok(annotations)
    }

    /// Create summary annotation
    fn create_summary_annotation(&self, execution_result: &ExecutionResult, annotations: &[Annotation]) -> Result<Annotation> {
        let content = format!(
            "# ═══════════════════════════════════════════════════════════════════════════════
# EXECUTION SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
# Total Annotations: {}
# Execution Success Rate: {:.1}%
# Average Step Quality: {:.2}
# Resource Efficiency: {:.1}%
# Bottleneck Stages: {}
# ═══════════════════════════════════════════════════════════════════════════════",
            annotations.len(),
            if execution_result.execution_statistics.steps_completed > 0 { 
                100.0 * execution_result.execution_statistics.steps_completed as f64 / 
                (execution_result.execution_statistics.steps_completed + execution_result.execution_statistics.steps_failed) as f64 
            } else { 0.0 },
            execution_result.execution_statistics.average_step_quality,
            execution_result.execution_statistics.resource_utilization_efficiency * 100.0,
            execution_result.execution_statistics.bottleneck_stages.len(),
        );

        Ok(Annotation {
            annotation_type: AnnotationType::Summary,
            line_number: 0,
            content,
            metadata: HashMap::new(),
        })
    }

    /// Format output preview with length limit
    fn format_output_preview(&self, output: &serde_json::Value) -> Result<String> {
        let json_str = serde_json::to_string_pretty(output)?;
        let preview = if json_str.len() > self.max_output_length {
            format!("{}{}...", &json_str[..self.max_output_length], self.indent_style)
        } else {
            json_str
        };

        // Add indentation to each line
        let indented_lines: Vec<String> = preview.lines()
            .map(|line| format!("{}{}", self.indent_style, line))
            .collect();

        Ok(indented_lines.join("\n"))
    }

    /// Format JSON preview with length limit
    fn format_json_preview(&self, json_str: &str) -> Result<String> {
        let preview = if json_str.len() > 200 {
            format!("{}...", &json_str[..200])
        } else {
            json_str.to_string()
        };

        // Extract key fields for preview
        if let Ok(json_value) = serde_json::from_str::<serde_json::Value>(&preview) {
            if let Some(obj) = json_value.as_object() {
                let key_fields: Vec<String> = obj.keys().take(3).cloned().collect();
                return Ok(format!("Fields: [{}]", key_fields.join(", ")));
            }
        }

        Ok(preview.replace('\n', " "))
    }

    /// Get annotation statistics
    pub fn get_statistics(&self) -> HashMap<String, f64> {
        let mut stats = HashMap::new();
        stats.insert("scripts_annotated".to_string(), self.scripts_annotated as f64);
        stats.insert("total_annotations_added".to_string(), self.total_annotations_added as f64);
        stats.insert("average_annotation_density".to_string(), self.average_annotation_density);
        stats
    }
}

// Python FFI functions

#[pyfunction]
pub fn py_annotate_turbulance_script(
    original_script: &str,
    execution_result_json: &str,
    compiled_protocol_json: &str,
    compact_mode: Option<bool>,
    include_debug_info: Option<bool>,
) -> PyResult<String> {
    let execution_result: ExecutionResult = serde_json::from_str(execution_result_json)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid execution result JSON: {}", e)))?;
    
    let compiled_protocol: CompiledProtocol = serde_json::from_str(compiled_protocol_json)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid compiled protocol JSON: {}", e)))?;
    
    let mut annotator = TurbulanceAnnotator::new()
        .with_compact_mode(compact_mode.unwrap_or(false))
        .with_debug_info(include_debug_info.unwrap_or(true));
    
    let annotated_script = annotator.annotate_script(original_script, &execution_result, &compiled_protocol)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    serde_json::to_string(&annotated_script)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Serialization failed: {}", e)))
}

#[pyfunction]
pub fn py_get_annotator_statistics() -> PyResult<String> {
    let annotator = TurbulanceAnnotator::new();
    let stats = annotator.get_statistics();
    
    serde_json::to_string(&stats)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Serialization failed: {}", e)))
}