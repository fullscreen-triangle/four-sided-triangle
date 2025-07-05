//! Turbulance DSL Orchestrator
//! 
//! Orchestrates the execution of compiled Turbulance protocols through the Four-Sided Triangle pipeline.
//! Manages async execution, resource allocation, and result collection.

use crate::error::{FourSidedTriangleError, Result};
use crate::{validation_error, computational_error};
use super::compiler::{CompiledProtocol, ExecutionStep, ExecutionMode, ResourceRequirements};
use super::parser::TurbulanceValue;
use crate::fuzzy_evidence::FuzzyEvidenceNetwork;
use crate::evidence_network::EvidenceNetwork;
use crate::bayesian::BayesianEvaluator;
use crate::metacognitive_optimizer::MetacognitiveOptimizer;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};
use std::sync::Arc;
use tokio::sync::{RwLock, Semaphore};
use std::time::{Duration, Instant};

/// Result of executing a single step
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StepResult {
    pub step_id: String,
    pub status: ExecutionStatus,
    pub output: serde_json::Value,
    pub execution_time_seconds: f64,
    pub resource_usage: ResourceUsage,
    pub quality_metrics: QualityMetrics,
    pub error_message: Option<String>,
}

/// Status of execution step
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ExecutionStatus {
    Pending,
    Running,
    Completed,
    Failed,
    Cancelled,
    Timeout,
}

/// Actual resource usage during execution
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResourceUsage {
    pub cpu_cores_used: f64,
    pub memory_gb_used: f64,
    pub gpu_units_used: f64,
    pub network_bandwidth_mbps_used: f64,
    pub storage_gb_used: f64,
}

/// Quality metrics for execution results
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QualityMetrics {
    pub accuracy: f64,
    pub completeness: f64,
    pub relevance: f64,
    pub confidence: f64,
    pub novelty: f64,
    pub coherence: f64,
}

/// Complete execution result for a protocol
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionResult {
    pub protocol_name: String,
    pub overall_status: ExecutionStatus,
    pub step_results: Vec<StepResult>,
    pub total_execution_time_seconds: f64,
    pub total_resource_usage: ResourceUsage,
    pub overall_quality_metrics: QualityMetrics,
    pub execution_statistics: ExecutionStatistics,
}

/// Execution statistics and telemetry
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionStatistics {
    pub steps_completed: usize,
    pub steps_failed: usize,
    pub parallelization_efficiency: f64,
    pub resource_utilization_efficiency: f64,
    pub average_step_quality: f64,
    pub bottleneck_stages: Vec<String>,
}

/// Resource pool for managing execution resources
#[derive(Debug)]
pub struct ResourcePool {
    pub cpu_semaphore: Arc<Semaphore>,
    pub memory_semaphore: Arc<Semaphore>,
    pub gpu_semaphore: Arc<Semaphore>,
    pub network_semaphore: Arc<Semaphore>,
    pub storage_semaphore: Arc<Semaphore>,
}

/// High-performance Turbulance orchestrator
pub struct TurbulanceOrchestrator {
    // Resource management
    resource_pool: ResourcePool,
    
    // Execution state
    running_protocols: Arc<RwLock<HashMap<String, ExecutionResult>>>,
    
    // Four-Sided Triangle integration
    fuzzy_evidence: Arc<RwLock<FuzzyEvidenceNetwork>>,
    evidence_network: Arc<RwLock<EvidenceNetwork>>,
    bayesian_evaluator: Arc<RwLock<BayesianEvaluator>>,
    metacognitive_optimizer: Arc<RwLock<MetacognitiveOptimizer>>,
    
    // Execution statistics
    protocols_executed: usize,
    total_steps_executed: usize,
    total_execution_time: Duration,
    successful_protocols: usize,
}

impl TurbulanceOrchestrator {
    pub fn new() -> Self {
        let resource_pool = ResourcePool {
            cpu_semaphore: Arc::new(Semaphore::new(16)),   // 16 CPU cores
            memory_semaphore: Arc::new(Semaphore::new(32)),  // 32 GB memory
            gpu_semaphore: Arc::new(Semaphore::new(4)),     // 4 GPU units
            network_semaphore: Arc::new(Semaphore::new(1000)), // 1000 Mbps
            storage_semaphore: Arc::new(Semaphore::new(100)), // 100 GB storage
        };

        Self {
            resource_pool,
            running_protocols: Arc::new(RwLock::new(HashMap::new())),
            fuzzy_evidence: Arc::new(RwLock::new(FuzzyEvidenceNetwork::new())),
            evidence_network: Arc::new(RwLock::new(EvidenceNetwork::new())),
            bayesian_evaluator: Arc::new(RwLock::new(BayesianEvaluator::new())),
            metacognitive_optimizer: Arc::new(RwLock::new(MetacognitiveOptimizer::new())),
            protocols_executed: 0,
            total_steps_executed: 0,
            total_execution_time: Duration::new(0, 0),
            successful_protocols: 0,
        }
    }

    /// Execute a compiled protocol
    pub async fn execute_protocol(&mut self, protocol: CompiledProtocol) -> Result<ExecutionResult> {
        let start_time = Instant::now();
        
        // Initialize execution result
        let mut result = ExecutionResult {
            protocol_name: protocol.protocol_name.clone(),
            overall_status: ExecutionStatus::Running,
            step_results: Vec::new(),
            total_execution_time_seconds: 0.0,
            total_resource_usage: ResourceUsage {
                cpu_cores_used: 0.0,
                memory_gb_used: 0.0,
                gpu_units_used: 0.0,
                network_bandwidth_mbps_used: 0.0,
                storage_gb_used: 0.0,
            },
            overall_quality_metrics: QualityMetrics {
                accuracy: 0.0,
                completeness: 0.0,
                relevance: 0.0,
                confidence: 0.0,
                novelty: 0.0,
                coherence: 0.0,
            },
            execution_statistics: ExecutionStatistics {
                steps_completed: 0,
                steps_failed: 0,
                parallelization_efficiency: 0.0,
                resource_utilization_efficiency: 0.0,
                average_step_quality: 0.0,
                bottleneck_stages: Vec::new(),
            },
        };

        // Register protocol as running
        {
            let mut running = self.running_protocols.write().await;
            running.insert(protocol.protocol_name.clone(), result.clone());
        }

        // Execute based on execution mode
        match protocol.execution_mode {
            ExecutionMode::Sequential => {
                result = self.execute_sequential(&protocol).await?;
            }
            ExecutionMode::Parallel => {
                result = self.execute_parallel(&protocol).await?;
            }
            ExecutionMode::Adaptive => {
                result = self.execute_adaptive(&protocol).await?;
            }
            ExecutionMode::Optimized => {
                result = self.execute_optimized(&protocol).await?;
            }
        }

        // Finalize execution
        let execution_time = start_time.elapsed();
        result.total_execution_time_seconds = execution_time.as_secs_f64();
        result.overall_status = if result.step_results.iter().all(|r| r.status == ExecutionStatus::Completed) {
            ExecutionStatus::Completed
        } else {
            ExecutionStatus::Failed
        };

        // Update statistics
        self.protocols_executed += 1;
        self.total_steps_executed += result.step_results.len();
        self.total_execution_time += execution_time;
        if result.overall_status == ExecutionStatus::Completed {
            self.successful_protocols += 1;
        }

        // Compute overall quality metrics
        result.overall_quality_metrics = self.compute_overall_quality_metrics(&result.step_results);

        // Compute execution statistics
        result.execution_statistics = self.compute_execution_statistics(&result.step_results, &protocol);

        // Remove from running protocols
        {
            let mut running = self.running_protocols.write().await;
            running.remove(&protocol.protocol_name);
        }

        Ok(result)
    }

    /// Execute protocol steps sequentially
    async fn execute_sequential(&self, protocol: &CompiledProtocol) -> Result<ExecutionResult> {
        let mut result = ExecutionResult {
            protocol_name: protocol.protocol_name.clone(),
            overall_status: ExecutionStatus::Running,
            step_results: Vec::new(),
            total_execution_time_seconds: 0.0,
            total_resource_usage: ResourceUsage {
                cpu_cores_used: 0.0,
                memory_gb_used: 0.0,
                gpu_units_used: 0.0,
                network_bandwidth_mbps_used: 0.0,
                storage_gb_used: 0.0,
            },
            overall_quality_metrics: QualityMetrics {
                accuracy: 0.0,
                completeness: 0.0,
                relevance: 0.0,
                confidence: 0.0,
                novelty: 0.0,
                coherence: 0.0,
            },
            execution_statistics: ExecutionStatistics {
                steps_completed: 0,
                steps_failed: 0,
                parallelization_efficiency: 0.0,
                resource_utilization_efficiency: 0.0,
                average_step_quality: 0.0,
                bottleneck_stages: Vec::new(),
            },
        };

        // Execute steps in order
        for step_id in &protocol.execution_order {
            let step = protocol.execution_steps.iter()
                .find(|s| s.step_id == *step_id)
                .ok_or_else(|| computational_error!("Step not found: {}", step_id))?;

            let step_result = self.execute_step(step).await?;
            
            // Accumulate resource usage
            result.total_resource_usage.cpu_cores_used += step_result.resource_usage.cpu_cores_used;
            result.total_resource_usage.memory_gb_used += step_result.resource_usage.memory_gb_used;
            result.total_resource_usage.gpu_units_used += step_result.resource_usage.gpu_units_used;
            result.total_resource_usage.network_bandwidth_mbps_used += step_result.resource_usage.network_bandwidth_mbps_used;
            result.total_resource_usage.storage_gb_used += step_result.resource_usage.storage_gb_used;

            result.step_results.push(step_result.clone());

            // Stop on failure
            if step_result.status == ExecutionStatus::Failed {
                break;
            }
        }

        Ok(result)
    }

    /// Execute protocol steps in parallel where possible
    async fn execute_parallel(&self, protocol: &CompiledProtocol) -> Result<ExecutionResult> {
        let mut result = ExecutionResult {
            protocol_name: protocol.protocol_name.clone(),
            overall_status: ExecutionStatus::Running,
            step_results: Vec::new(),
            total_execution_time_seconds: 0.0,
            total_resource_usage: ResourceUsage {
                cpu_cores_used: 0.0,
                memory_gb_used: 0.0,
                gpu_units_used: 0.0,
                network_bandwidth_mbps_used: 0.0,
                storage_gb_used: 0.0,
            },
            overall_quality_metrics: QualityMetrics {
                accuracy: 0.0,
                completeness: 0.0,
                relevance: 0.0,
                confidence: 0.0,
                novelty: 0.0,
                coherence: 0.0,
            },
            execution_statistics: ExecutionStatistics {
                steps_completed: 0,
                steps_failed: 0,
                parallelization_efficiency: 0.0,
                resource_utilization_efficiency: 0.0,
                average_step_quality: 0.0,
                bottleneck_stages: Vec::new(),
            },
        };

        // Execute parallel groups
        for group in &protocol.parallel_groups {
            let mut group_tasks = Vec::new();
            
            for step_id in group {
                let step = protocol.execution_steps.iter()
                    .find(|s| s.step_id == *step_id)
                    .ok_or_else(|| computational_error!("Step not found: {}", step_id))?;

                let step_task = self.execute_step(step);
                group_tasks.push(step_task);
            }

            // Wait for all tasks in group to complete
            let group_results = futures::future::join_all(group_tasks).await;
            
            for step_result in group_results {
                let step_result = step_result?;
                
                // Accumulate resource usage
                result.total_resource_usage.cpu_cores_used += step_result.resource_usage.cpu_cores_used;
                result.total_resource_usage.memory_gb_used += step_result.resource_usage.memory_gb_used;
                result.total_resource_usage.gpu_units_used += step_result.resource_usage.gpu_units_used;
                result.total_resource_usage.network_bandwidth_mbps_used += step_result.resource_usage.network_bandwidth_mbps_used;
                result.total_resource_usage.storage_gb_used += step_result.resource_usage.storage_gb_used;

                result.step_results.push(step_result);
            }
        }

        Ok(result)
    }

    /// Execute protocol adaptively based on runtime conditions
    async fn execute_adaptive(&self, protocol: &CompiledProtocol) -> Result<ExecutionResult> {
        // Start with parallel execution but switch to sequential if resources become constrained
        let resource_threshold = 0.8; // 80% resource utilization threshold
        
        let mut result = self.execute_parallel(protocol).await?;
        
        // Check if resource utilization was too high
        let cpu_util = result.total_resource_usage.cpu_cores_used / protocol.total_resource_requirements.cpu_cores;
        let memory_util = result.total_resource_usage.memory_gb_used / protocol.total_resource_requirements.memory_gb;
        
        if cpu_util > resource_threshold || memory_util > resource_threshold {
            // Re-execute sequentially
            result = self.execute_sequential(protocol).await?;
        }

        Ok(result)
    }

    /// Execute protocol with optimization strategies
    async fn execute_optimized(&self, protocol: &CompiledProtocol) -> Result<ExecutionResult> {
        // Use metacognitive optimization to determine best execution strategy
        let optimizer = self.metacognitive_optimizer.read().await;
        let strategy = optimizer.select_execution_strategy(
            protocol.execution_steps.len(),
            &protocol.total_resource_requirements,
            &protocol.optimization_hints,
        );

        match strategy.strategy_type.as_str() {
            "parallel" => self.execute_parallel(protocol).await,
            "sequential" => self.execute_sequential(protocol).await,
            "adaptive" => self.execute_adaptive(protocol).await,
            _ => self.execute_adaptive(protocol).await,
        }
    }

    /// Execute a single step
    async fn execute_step(&self, step: &ExecutionStep) -> Result<StepResult> {
        let start_time = Instant::now();

        // Acquire resources
        let _cpu_permit = self.resource_pool.cpu_semaphore.acquire_many(step.resource_requirements.cpu_cores as u32).await
            .map_err(|_| computational_error!("Failed to acquire CPU resources"))?;
        let _memory_permit = self.resource_pool.memory_semaphore.acquire_many(step.resource_requirements.memory_gb as u32).await
            .map_err(|_| computational_error!("Failed to acquire memory resources"))?;
        let _gpu_permit = if step.resource_requirements.gpu_units > 0.0 {
            Some(self.resource_pool.gpu_semaphore.acquire_many(step.resource_requirements.gpu_units as u32).await
                .map_err(|_| computational_error!("Failed to acquire GPU resources"))?)
        } else {
            None
        };

        // Execute the step
        let result = self.execute_stage(&step.stage_name, &step.parameters).await?;

        // Calculate execution time
        let execution_time = start_time.elapsed().as_secs_f64();

        // Estimate resource usage based on execution time and requirements
        let resource_usage = ResourceUsage {
            cpu_cores_used: step.resource_requirements.cpu_cores * (execution_time / step.resource_requirements.estimated_duration_seconds),
            memory_gb_used: step.resource_requirements.memory_gb * (execution_time / step.resource_requirements.estimated_duration_seconds),
            gpu_units_used: step.resource_requirements.gpu_units * (execution_time / step.resource_requirements.estimated_duration_seconds),
            network_bandwidth_mbps_used: step.resource_requirements.network_bandwidth_mbps * (execution_time / step.resource_requirements.estimated_duration_seconds),
            storage_gb_used: step.resource_requirements.storage_gb,
        };

        // Evaluate quality metrics
        let quality_metrics = self.evaluate_step_quality(&result, &step.stage_name).await?;

        Ok(StepResult {
            step_id: step.step_id.clone(),
            status: ExecutionStatus::Completed,
            output: result,
            execution_time_seconds: execution_time,
            resource_usage,
            quality_metrics,
            error_message: None,
        })
    }

    /// Execute a specific Four-Sided Triangle stage
    async fn execute_stage(&self, stage_name: &str, parameters: &HashMap<String, TurbulanceValue>) -> Result<serde_json::Value> {
        match stage_name {
            "stage0_query_processor" => {
                self.execute_query_processor(parameters).await
            }
            "stage1_semantic_atdb" => {
                self.execute_semantic_atdb(parameters).await
            }
            "stage2_domain_knowledge" => {
                self.execute_domain_knowledge(parameters).await
            }
            "stage3_reasoning_optimization" => {
                self.execute_reasoning_optimization(parameters).await
            }
            "stage4_solution" => {
                self.execute_solution_generation(parameters).await
            }
            "stage5_scoring" => {
                self.execute_response_scoring(parameters).await
            }
            "stage6_comparison" => {
                self.execute_response_comparison(parameters).await
            }
            "stage7_verification" => {
                self.execute_threshold_verification(parameters).await
            }
            _ => Err(computational_error!("Unknown stage: {}", stage_name)),
        }
    }

    /// Stage execution implementations
    async fn execute_query_processor(&self, _parameters: &HashMap<String, TurbulanceValue>) -> Result<serde_json::Value> {
        // Simulate query processing
        Ok(serde_json::json!({
            "processed_query": "Sample processed query",
            "intent": "information_retrieval",
            "entities": ["sample", "entity"],
            "confidence": 0.9
        }))
    }

    async fn execute_semantic_atdb(&self, _parameters: &HashMap<String, TurbulanceValue>) -> Result<serde_json::Value> {
        // Simulate semantic search
        Ok(serde_json::json!({
            "retrieved_documents": [
                {"id": "doc1", "score": 0.95, "content": "Sample document 1"},
                {"id": "doc2", "score": 0.87, "content": "Sample document 2"}
            ],
            "total_retrieved": 2
        }))
    }

    async fn execute_domain_knowledge(&self, _parameters: &HashMap<String, TurbulanceValue>) -> Result<serde_json::Value> {
        // Use fuzzy evidence network for domain knowledge processing
        let fuzzy_network = self.fuzzy_evidence.read().await;
        let knowledge_result = fuzzy_network.process_domain_knowledge(&[0.8, 0.9, 0.7]);
        
        Ok(serde_json::json!({
            "domain_insights": knowledge_result,
            "expert_models": ["model1", "model2"],
            "confidence": 0.85
        }))
    }

    async fn execute_reasoning_optimization(&self, _parameters: &HashMap<String, TurbulanceValue>) -> Result<serde_json::Value> {
        // Use metacognitive optimizer
        let optimizer = self.metacognitive_optimizer.read().await;
        let strategy = optimizer.select_reasoning_strategy(0.8, 0.9, 0.7);
        
        Ok(serde_json::json!({
            "reasoning_strategy": strategy.strategy_type,
            "optimization_applied": true,
            "performance_gain": strategy.expected_improvement
        }))
    }

    async fn execute_solution_generation(&self, _parameters: &HashMap<String, TurbulanceValue>) -> Result<serde_json::Value> {
        Ok(serde_json::json!({
            "generated_solutions": [
                {"solution_id": "sol1", "content": "Solution 1", "confidence": 0.92},
                {"solution_id": "sol2", "content": "Solution 2", "confidence": 0.88}
            ],
            "best_solution": "sol1"
        }))
    }

    async fn execute_response_scoring(&self, _parameters: &HashMap<String, TurbulanceValue>) -> Result<serde_json::Value> {
        // Use Bayesian evaluator
        let evaluator = self.bayesian_evaluator.read().await;
        let scores = evaluator.evaluate_responses(&[0.9, 0.8, 0.7]);
        
        Ok(serde_json::json!({
            "response_scores": scores,
            "ranking": [0, 1, 2],
            "confidence": 0.85
        }))
    }

    async fn execute_response_comparison(&self, _parameters: &HashMap<String, TurbulanceValue>) -> Result<serde_json::Value> {
        Ok(serde_json::json!({
            "comparison_matrix": [[1.0, 0.8, 0.6], [0.8, 1.0, 0.7], [0.6, 0.7, 1.0]],
            "diversity_score": 0.75,
            "quality_score": 0.85
        }))
    }

    async fn execute_threshold_verification(&self, _parameters: &HashMap<String, TurbulanceValue>) -> Result<serde_json::Value> {
        // Use evidence network for verification
        let evidence_network = self.evidence_network.read().await;
        let verification_result = evidence_network.verify_threshold(0.8, 0.9);
        
        Ok(serde_json::json!({
            "verification_passed": verification_result,
            "threshold_met": 0.85,
            "confidence": 0.9
        }))
    }

    /// Evaluate quality metrics for a step result
    async fn evaluate_step_quality(&self, result: &serde_json::Value, stage_name: &str) -> Result<QualityMetrics> {
        // Use Bayesian evaluator to assess quality
        let evaluator = self.bayesian_evaluator.read().await;
        let quality_scores = evaluator.evaluate_quality(result, stage_name);

        Ok(QualityMetrics {
            accuracy: quality_scores.get("accuracy").unwrap_or(&0.8).clone(),
            completeness: quality_scores.get("completeness").unwrap_or(&0.85).clone(),
            relevance: quality_scores.get("relevance").unwrap_or(&0.9).clone(),
            confidence: quality_scores.get("confidence").unwrap_or(&0.85).clone(),
            novelty: quality_scores.get("novelty").unwrap_or(&0.7).clone(),
            coherence: quality_scores.get("coherence").unwrap_or(&0.88).clone(),
        })
    }

    /// Compute overall quality metrics from step results
    fn compute_overall_quality_metrics(&self, step_results: &[StepResult]) -> QualityMetrics {
        if step_results.is_empty() {
            return QualityMetrics {
                accuracy: 0.0,
                completeness: 0.0,
                relevance: 0.0,
                confidence: 0.0,
                novelty: 0.0,
                coherence: 0.0,
            };
        }

        let count = step_results.len() as f64;
        QualityMetrics {
            accuracy: step_results.iter().map(|r| r.quality_metrics.accuracy).sum::<f64>() / count,
            completeness: step_results.iter().map(|r| r.quality_metrics.completeness).sum::<f64>() / count,
            relevance: step_results.iter().map(|r| r.quality_metrics.relevance).sum::<f64>() / count,
            confidence: step_results.iter().map(|r| r.quality_metrics.confidence).sum::<f64>() / count,
            novelty: step_results.iter().map(|r| r.quality_metrics.novelty).sum::<f64>() / count,
            coherence: step_results.iter().map(|r| r.quality_metrics.coherence).sum::<f64>() / count,
        }
    }

    /// Compute execution statistics
    fn compute_execution_statistics(&self, step_results: &[StepResult], protocol: &CompiledProtocol) -> ExecutionStatistics {
        let steps_completed = step_results.iter().filter(|r| r.status == ExecutionStatus::Completed).count();
        let steps_failed = step_results.iter().filter(|r| r.status == ExecutionStatus::Failed).count();

        let parallelization_efficiency = if protocol.parallel_groups.is_empty() {
            0.0
        } else {
            let parallel_steps: usize = protocol.parallel_groups.iter().map(|g| g.len()).sum();
            let total_steps = protocol.execution_steps.len();
            parallel_steps as f64 / total_steps as f64
        };

        let resource_utilization_efficiency = {
            let total_estimated_time: f64 = protocol.execution_steps.iter()
                .map(|s| s.resource_requirements.estimated_duration_seconds)
                .sum();
            let total_actual_time: f64 = step_results.iter()
                .map(|r| r.execution_time_seconds)
                .sum();
            if total_actual_time > 0.0 {
                total_estimated_time / total_actual_time
            } else {
                0.0
            }
        };

        let average_step_quality = if step_results.is_empty() {
            0.0
        } else {
            let total_quality: f64 = step_results.iter()
                .map(|r| {
                    (r.quality_metrics.accuracy + r.quality_metrics.completeness + 
                     r.quality_metrics.relevance + r.quality_metrics.confidence + 
                     r.quality_metrics.novelty + r.quality_metrics.coherence) / 6.0
                })
                .sum();
            total_quality / step_results.len() as f64
        };

        let bottleneck_stages = step_results.iter()
            .filter(|r| r.execution_time_seconds > 30.0) // Steps taking more than 30 seconds
            .map(|r| r.step_id.clone())
            .collect();

        ExecutionStatistics {
            steps_completed,
            steps_failed,
            parallelization_efficiency,
            resource_utilization_efficiency,
            average_step_quality,
            bottleneck_stages,
        }
    }

    /// Get orchestrator statistics
    pub fn get_statistics(&self) -> HashMap<String, f64> {
        let mut stats = HashMap::new();
        stats.insert("protocols_executed".to_string(), self.protocols_executed as f64);
        stats.insert("total_steps_executed".to_string(), self.total_steps_executed as f64);
        stats.insert("successful_protocols".to_string(), self.successful_protocols as f64);
        stats.insert("total_execution_time_seconds".to_string(), self.total_execution_time.as_secs_f64());
        
        let success_rate = if self.protocols_executed > 0 {
            self.successful_protocols as f64 / self.protocols_executed as f64
        } else {
            0.0
        };
        stats.insert("success_rate".to_string(), success_rate);
        
        let avg_execution_time = if self.protocols_executed > 0 {
            self.total_execution_time.as_secs_f64() / self.protocols_executed as f64
        } else {
            0.0
        };
        stats.insert("avg_execution_time_seconds".to_string(), avg_execution_time);
        
        stats
    }
}

// Python FFI functions

#[pyfunction]
pub fn py_execute_turbulance_protocol(protocol_json: &str) -> PyResult<String> {
    let protocol: CompiledProtocol = serde_json::from_str(protocol_json)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid protocol JSON: {}", e)))?;
    
    let rt = tokio::runtime::Runtime::new()
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to create runtime: {}", e)))?;
    
    let result = rt.block_on(async {
        let mut orchestrator = TurbulanceOrchestrator::new();
        orchestrator.execute_protocol(protocol).await
    });
    
    let execution_result = result
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    serde_json::to_string(&execution_result)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Serialization failed: {}", e)))
}

#[pyfunction]
pub fn py_get_orchestrator_statistics() -> PyResult<String> {
    let orchestrator = TurbulanceOrchestrator::new();
    let stats = orchestrator.get_statistics();
    
    serde_json::to_string(&stats)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Serialization failed: {}", e)))
}