//! Turbulance DSL Compiler
//! 
//! Compiles parsed Turbulance scripts into executable Four-Sided Triangle pipeline plans.
//! Handles dependency resolution, resource allocation, and optimization.

use crate::error::{FourSidedTriangleError, Result};
use crate::{validation_error};
use super::parser::{TurbulanceScript, TurbulanceNode, NodeType, TurbulanceValue};
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};

/// Execution mode for compiled protocols
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ExecutionMode {
    Sequential,
    Parallel,
    Adaptive,
    Optimized,
}

/// Individual execution step in compiled protocol
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionStep {
    pub step_id: String,
    pub stage_name: String,
    pub variable_name: String,
    pub parameters: HashMap<String, TurbulanceValue>,
    pub dependencies: Vec<String>,
    pub resource_requirements: ResourceRequirements,
    pub line_number: usize,
    pub priority: f64,
    pub timeout_seconds: f64,
}

/// Resource requirements for execution steps
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResourceRequirements {
    pub cpu_cores: f64,
    pub memory_gb: f64,
    pub gpu_units: f64,
    pub network_bandwidth_mbps: f64,
    pub estimated_duration_seconds: f64,
    pub storage_gb: f64,
}

/// Compiled Turbulance protocol ready for execution
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CompiledProtocol {
    pub protocol_name: String,
    pub execution_steps: Vec<ExecutionStep>,
    pub execution_mode: ExecutionMode,
    pub total_resource_requirements: ResourceRequirements,
    pub dependency_graph: HashMap<String, Vec<String>>,
    pub execution_order: Vec<String>,
    pub parallel_groups: Vec<Vec<String>>,
    pub auxiliary_files: AuxiliaryFiles,
    pub optimization_hints: Vec<OptimizationHint>,
}

/// Generated auxiliary files for Turbulance protocols
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuxiliaryFiles {
    pub fs_content: String,  // Network graph consciousness state
    pub ghd_content: String, // Resource orchestration dependencies
    pub hre_content: String, // Metacognitive decision memory
}

/// Optimization hint for execution
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OptimizationHint {
    pub hint_type: OptimizationType,
    pub target_step: String,
    pub description: String,
    pub priority: f64,
}

/// Types of optimizations
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum OptimizationType {
    Parallelization,
    Caching,
    ResourceBalancing,
    DependencyMinimization,
    QualityBoost,
    EfficiencyImprovement,
}

/// High-performance Turbulance compiler
pub struct TurbulanceCompiler {
    // Stage mapping to actual Four-Sided Triangle stages
    stage_mappings: HashMap<String, String>,
    
    // Resource estimation models
    resource_models: HashMap<String, ResourceRequirements>,
    
    // Compilation statistics
    protocols_compiled: usize,
    total_steps_generated: usize,
    optimization_hits: usize,
}

impl Default for TurbulanceCompiler {
    fn default() -> Self {
        Self::new()
    }
}

impl TurbulanceCompiler {
    pub fn new() -> Self {
        let mut compiler = Self {
            stage_mappings: HashMap::new(),
            resource_models: HashMap::new(),
            protocols_compiled: 0,
            total_steps_generated: 0,
            optimization_hits: 0,
        };
        
        compiler.initialize_stage_mappings();
        compiler.initialize_resource_models();
        compiler
    }

    fn initialize_stage_mappings(&mut self) {
        self.stage_mappings.insert("query_processor".to_string(), "stage0_query_processor".to_string());
        self.stage_mappings.insert("semantic_atdb".to_string(), "stage1_semantic_atdb".to_string());
        self.stage_mappings.insert("domain_knowledge".to_string(), "stage2_domain_knowledge".to_string());
        self.stage_mappings.insert("reasoning_optimization".to_string(), "stage3_reasoning_optimization".to_string());
        self.stage_mappings.insert("solution_generation".to_string(), "stage4_solution".to_string());
        self.stage_mappings.insert("response_scoring".to_string(), "stage5_scoring".to_string());
        self.stage_mappings.insert("response_comparison".to_string(), "stage6_comparison".to_string());
        self.stage_mappings.insert("threshold_verification".to_string(), "stage7_verification".to_string());
    }

    fn initialize_resource_models(&mut self) {
        let models = vec![
            ("stage0_query_processor", ResourceRequirements {
                cpu_cores: 1.0, memory_gb: 2.0, gpu_units: 0.0, network_bandwidth_mbps: 10.0,
                estimated_duration_seconds: 5.0, storage_gb: 0.1,
            }),
            ("stage1_semantic_atdb", ResourceRequirements {
                cpu_cores: 2.0, memory_gb: 4.0, gpu_units: 0.0, network_bandwidth_mbps: 20.0,
                estimated_duration_seconds: 15.0, storage_gb: 0.2,
            }),
            ("stage2_domain_knowledge", ResourceRequirements {
                cpu_cores: 4.0, memory_gb: 8.0, gpu_units: 1.0, network_bandwidth_mbps: 50.0,
                estimated_duration_seconds: 30.0, storage_gb: 0.5,
            }),
            ("stage3_reasoning_optimization", ResourceRequirements {
                cpu_cores: 3.0, memory_gb: 6.0, gpu_units: 0.5, network_bandwidth_mbps: 30.0,
                estimated_duration_seconds: 25.0, storage_gb: 0.3,
            }),
            ("stage4_solution", ResourceRequirements {
                cpu_cores: 2.0, memory_gb: 4.0, gpu_units: 0.0, network_bandwidth_mbps: 25.0,
                estimated_duration_seconds: 20.0, storage_gb: 0.2,
            }),
            ("stage5_scoring", ResourceRequirements {
                cpu_cores: 1.0, memory_gb: 2.0, gpu_units: 0.0, network_bandwidth_mbps: 15.0,
                estimated_duration_seconds: 10.0, storage_gb: 0.1,
            }),
            ("stage6_comparison", ResourceRequirements {
                cpu_cores: 2.0, memory_gb: 4.0, gpu_units: 0.0, network_bandwidth_mbps: 20.0,
                estimated_duration_seconds: 15.0, storage_gb: 0.2,
            }),
            ("stage7_verification", ResourceRequirements {
                cpu_cores: 1.0, memory_gb: 2.0, gpu_units: 0.0, network_bandwidth_mbps: 10.0,
                estimated_duration_seconds: 8.0, storage_gb: 0.1,
            }),
        ];

        for (stage, requirements) in models {
            self.resource_models.insert(stage.to_string(), requirements);
        }
    }

    /// Compile a parsed Turbulance script into executable protocol
    pub fn compile_protocol(&mut self, script: &TurbulanceScript) -> Result<CompiledProtocol> {
        // Extract execution steps from pipeline calls
        let execution_steps = self.extract_execution_steps(script)?;
        
        // Build dependency graph
        let dependency_graph = self.build_dependency_graph(&execution_steps)?;
        
        // Determine optimal execution mode
        let execution_mode = self.determine_execution_mode(&execution_steps, &dependency_graph)?;
        
        // Calculate execution order and parallel groups
        let (execution_order, parallel_groups) = self.calculate_execution_plan(&execution_steps, &dependency_graph)?;
        
        // Calculate total resource requirements
        let total_resource_requirements = self.calculate_total_resources(&execution_steps, &execution_mode)?;
        
        // Generate auxiliary files
        let auxiliary_files = self.generate_auxiliary_files(script, &execution_steps)?;
        
        // Generate optimization hints
        let optimization_hints = self.generate_optimization_hints(&execution_steps, &dependency_graph)?;

        self.protocols_compiled += 1;
        self.total_steps_generated += execution_steps.len();

        Ok(CompiledProtocol {
            protocol_name: script.protocol_name.clone(),
            execution_steps,
            execution_mode,
            total_resource_requirements,
            dependency_graph,
            execution_order,
            parallel_groups,
            auxiliary_files,
            optimization_hints,
        })
    }

    /// Extract execution steps from pipeline calls
    fn extract_execution_steps(&self, script: &TurbulanceScript) -> Result<Vec<ExecutionStep>> {
        let mut steps = Vec::new();

        for node in &script.pipeline_calls {
            if node.node_type != NodeType::PipelineStage {
                continue;
            }

            let variable_name = node.name.as_ref()
                .ok_or_else(|| validation_error!("Pipeline stage missing variable name"))?;

            let stage_name = node.parameters.get("stage")
                .and_then(|v| if let TurbulanceValue::String(s) = v { Some(s) } else { None })
                .ok_or_else(|| validation_error!("Pipeline stage missing stage name"))?;

            // Map to actual stage name
            let actual_stage = self.stage_mappings.get(stage_name)
                .unwrap_or(stage_name)
                .clone();

            // Get resource requirements
            let resource_requirements = self.resource_models.get(&actual_stage)
                .cloned()
                .unwrap_or_else(|| ResourceRequirements {
                    cpu_cores: 1.0, memory_gb: 2.0, gpu_units: 0.0, network_bandwidth_mbps: 10.0,
                    estimated_duration_seconds: 15.0, storage_gb: 0.1,
                });

            // Extract configuration and adjust resources
            let mut adjusted_requirements = resource_requirements.clone();
            if let Some(TurbulanceValue::Object(config)) = node.parameters.get("config") {
                self.adjust_resource_requirements(&mut adjusted_requirements, config);
            }

            let step = ExecutionStep {
                step_id: format!("{}_{}", script.protocol_name, variable_name),
                stage_name: actual_stage,
                variable_name: variable_name.clone(),
                parameters: node.parameters.clone(),
                dependencies: node.dependencies.clone(),
                resource_requirements: adjusted_requirements,
                line_number: node.line_number,
                priority: 1.0,
                timeout_seconds: resource_requirements.estimated_duration_seconds * 3.0, // 3x buffer
            };

            steps.push(step);
        }

        Ok(steps)
    }

    /// Adjust resource requirements based on configuration
    fn adjust_resource_requirements(&self, requirements: &mut ResourceRequirements, config: &HashMap<String, TurbulanceValue>) {
        // Adjust based on common configuration parameters
        if let Some(TurbulanceValue::Array(expert_models)) = config.get("expert_models") {
            let model_count = expert_models.len() as f64;
            requirements.cpu_cores *= 1.0 + (model_count - 1.0) * 0.5;
            requirements.memory_gb *= 1.0 + (model_count - 1.0) * 0.3;
            requirements.estimated_duration_seconds *= 1.0 + (model_count - 1.0) * 0.2;
        }

        if let Some(TurbulanceValue::String(priority)) = config.get("resource_priority") {
            let multiplier = match priority.as_str() {
                "high" => 1.5,
                "critical" => 2.0,
                "low" => 0.7,
                _ => 1.0,
            };
            requirements.cpu_cores *= multiplier;
            requirements.memory_gb *= multiplier;
        }

        if let Some(TurbulanceValue::Number(quality_threshold)) = config.get("minimum_confidence") {
            if *quality_threshold > 0.9 {
                requirements.estimated_duration_seconds *= 1.5;
                requirements.cpu_cores *= 1.2;
            }
        }
    }

    /// Build dependency graph from execution steps
    fn build_dependency_graph(&self, steps: &[ExecutionStep]) -> Result<HashMap<String, Vec<String>>> {
        let mut graph = HashMap::new();

        // Create mapping from variable names to step IDs
        let var_to_step: HashMap<String, String> = steps.iter()
            .map(|step| (step.variable_name.clone(), step.step_id.clone()))
            .collect();

        for step in steps {
            let mut resolved_deps = Vec::new();

            for dep in &step.dependencies {
                if let Some(dep_step_id) = var_to_step.get(dep) {
                    resolved_deps.push(dep_step_id.clone());
                }
            }

            graph.insert(step.step_id.clone(), resolved_deps);
        }

        Ok(graph)
    }

    /// Determine optimal execution mode
    fn determine_execution_mode(&self, steps: &[ExecutionStep], dependency_graph: &HashMap<String, Vec<String>>) -> Result<ExecutionMode> {
        let total_steps = steps.len();
        
        // Count independent steps (no dependencies)
        let independent_steps = steps.iter()
            .filter(|step| dependency_graph.get(&step.step_id).map_or(true, |deps| deps.is_empty()))
            .count();

        // Analyze dependency complexity
        let max_depth = self.calculate_max_dependency_depth(dependency_graph)?;
        let avg_dependencies = dependency_graph.values()
            .map(|deps| deps.len())
            .sum::<usize>() as f64 / total_steps as f64;

        // Decision logic
        if independent_steps == total_steps {
            Ok(ExecutionMode::Parallel)
        } else if independent_steps == 0 {
            Ok(ExecutionMode::Sequential)
        } else if max_depth <= 3 && avg_dependencies < 2.0 {
            Ok(ExecutionMode::Adaptive)
        } else {
            Ok(ExecutionMode::Optimized)
        }
    }

    /// Calculate maximum dependency depth
    fn calculate_max_dependency_depth(&self, dependency_graph: &HashMap<String, Vec<String>>) -> Result<usize> {
        let mut max_depth = 0;
        let mut visited = HashSet::new();

        for step_id in dependency_graph.keys() {
            if !visited.contains(step_id) {
                let depth = self.calculate_depth_dfs(step_id, dependency_graph, &mut visited, &mut HashSet::new())?;
                max_depth = max_depth.max(depth);
            }
        }

        Ok(max_depth)
    }

    /// DFS helper for depth calculation
    fn calculate_depth_dfs(
        &self,
        step_id: &str,
        dependency_graph: &HashMap<String, Vec<String>>,
        visited: &mut HashSet<String>,
        path: &mut HashSet<String>,
    ) -> Result<usize> {
        if path.contains(step_id) {
            return Err(validation_error!("Circular dependency detected"));
        }

        if visited.contains(step_id) {
            return Ok(0);
        }

        visited.insert(step_id.to_string());
        path.insert(step_id.to_string());

        let mut max_child_depth = 0;
        if let Some(dependencies) = dependency_graph.get(step_id) {
            for dep in dependencies {
                let child_depth = self.calculate_depth_dfs(dep, dependency_graph, visited, path)?;
                max_child_depth = max_child_depth.max(child_depth);
            }
        }

        path.remove(step_id);
        Ok(max_child_depth + 1)
    }

    /// Calculate execution order and parallel groups
    fn calculate_execution_plan(&self, steps: &[ExecutionStep], dependency_graph: &HashMap<String, Vec<String>>) -> Result<(Vec<String>, Vec<Vec<String>>)> {
        let mut execution_order = Vec::new();
        let mut parallel_groups = Vec::new();
        let mut completed = HashSet::new();
        let mut remaining: HashSet<String> = steps.iter().map(|s| s.step_id.clone()).collect();

        while !remaining.is_empty() {
            // Find steps that can run now (all dependencies completed)
            let ready_steps: Vec<String> = remaining.iter()
                .filter(|step_id| {
                    if let Some(deps) = dependency_graph.get(*step_id) {
                        deps.iter().all(|dep| completed.contains(dep))
                    } else {
                        true
                    }
                })
                .cloned()
                .collect();

            if ready_steps.is_empty() {
                return Err(validation_error!("Deadlock in dependency graph"));
            }

            // Add to execution order and parallel group
            for step_id in &ready_steps {
                execution_order.push(step_id.clone());
                completed.insert(step_id.clone());
                remaining.remove(step_id);
            }

            if ready_steps.len() > 1 {
                parallel_groups.push(ready_steps);
            }
        }

        Ok((execution_order, parallel_groups))
    }

    /// Calculate total resource requirements
    fn calculate_total_resources(&self, steps: &[ExecutionStep], execution_mode: &ExecutionMode) -> Result<ResourceRequirements> {
        match execution_mode {
            ExecutionMode::Parallel => {
                // Sum of maximum requirements across all steps
                Ok(ResourceRequirements {
                    cpu_cores: steps.iter().map(|s| s.resource_requirements.cpu_cores).fold(0.0, f64::max),
                    memory_gb: steps.iter().map(|s| s.resource_requirements.memory_gb).fold(0.0, f64::max),
                    gpu_units: steps.iter().map(|s| s.resource_requirements.gpu_units).fold(0.0, f64::max),
                    network_bandwidth_mbps: steps.iter().map(|s| s.resource_requirements.network_bandwidth_mbps).fold(0.0, f64::max),
                    estimated_duration_seconds: steps.iter().map(|s| s.resource_requirements.estimated_duration_seconds).fold(0.0, f64::max),
                    storage_gb: steps.iter().map(|s| s.resource_requirements.storage_gb).sum(),
                })
            }
            ExecutionMode::Sequential => {
                // Average requirements, sum of durations
                let step_count = steps.len() as f64;
                Ok(ResourceRequirements {
                    cpu_cores: steps.iter().map(|s| s.resource_requirements.cpu_cores).sum::<f64>() / step_count,
                    memory_gb: steps.iter().map(|s| s.resource_requirements.memory_gb).sum::<f64>() / step_count,
                    gpu_units: steps.iter().map(|s| s.resource_requirements.gpu_units).sum::<f64>() / step_count,
                    network_bandwidth_mbps: steps.iter().map(|s| s.resource_requirements.network_bandwidth_mbps).sum::<f64>() / step_count,
                    estimated_duration_seconds: steps.iter().map(|s| s.resource_requirements.estimated_duration_seconds).sum(),
                    storage_gb: steps.iter().map(|s| s.resource_requirements.storage_gb).sum(),
                })
            }
            _ => {
                // Adaptive/Optimized: somewhere between parallel and sequential
                let parallel_reqs = self.calculate_total_resources(steps, &ExecutionMode::Parallel)?;
                let sequential_reqs = self.calculate_total_resources(steps, &ExecutionMode::Sequential)?;
                
                Ok(ResourceRequirements {
                    cpu_cores: (parallel_reqs.cpu_cores + sequential_reqs.cpu_cores) / 2.0,
                    memory_gb: (parallel_reqs.memory_gb + sequential_reqs.memory_gb) / 2.0,
                    gpu_units: (parallel_reqs.gpu_units + sequential_reqs.gpu_units) / 2.0,
                    network_bandwidth_mbps: (parallel_reqs.network_bandwidth_mbps + sequential_reqs.network_bandwidth_mbps) / 2.0,
                    estimated_duration_seconds: (parallel_reqs.estimated_duration_seconds + sequential_reqs.estimated_duration_seconds) / 2.0,
                    storage_gb: parallel_reqs.storage_gb,
                })
            }
        }
    }

    /// Generate auxiliary files (.fs, .ghd, .hre)
    fn generate_auxiliary_files(&self, script: &TurbulanceScript, steps: &[ExecutionStep]) -> Result<AuxiliaryFiles> {
        // Generate .fs file (network graph consciousness state)
        let fs_content = self.generate_fs_file(script, steps)?;
        
        // Generate .ghd file (resource orchestration dependencies)
        let ghd_content = self.generate_ghd_file(script, steps)?;
        
        // Generate .hre file (metacognitive decision memory)
        let hre_content = self.generate_hre_file(script, steps)?;

        Ok(AuxiliaryFiles {
            fs_content,
            ghd_content,
            hre_content,
        })
    }

    fn generate_fs_file(&self, script: &TurbulanceScript, steps: &[ExecutionStep]) -> Result<String> {
        let mut fs_data = serde_json::json!({
            "protocol_name": script.protocol_name,
            "network_topology": {
                "nodes": [],
                "edges": [],
                "consciousness_levels": {}
            },
            "processing_flow": {
                "stages": steps.len(),
                "parallel_capacity": steps.iter().filter(|s| s.dependencies.is_empty()).count(),
                "complexity_score": steps.iter().map(|s| s.resource_requirements.cpu_cores).sum::<f64>()
            }
        });

        // Add nodes for each step
        for step in steps {
            let node = serde_json::json!({
                "id": step.step_id,
                "stage": step.stage_name,
                "consciousness_level": self.calculate_consciousness_level(&step.stage_name),
                "resource_intensity": step.resource_requirements.cpu_cores + step.resource_requirements.memory_gb / 4.0
            });
            fs_data["network_topology"]["nodes"].as_array_mut().unwrap().push(node);
        }

        Ok(serde_json::to_string_pretty(&fs_data)?)
    }

    fn generate_ghd_file(&self, script: &TurbulanceScript, steps: &[ExecutionStep]) -> Result<String> {
        let total_resources = self.calculate_total_resources(steps, &ExecutionMode::Adaptive)?;
        
        let ghd_data = serde_json::json!({
            "protocol_name": script.protocol_name,
            "resource_allocation": {
                "cpu_cores": total_resources.cpu_cores,
                "memory_gb": total_resources.memory_gb,
                "gpu_units": total_resources.gpu_units,
                "network_bandwidth_mbps": total_resources.network_bandwidth_mbps,
                "storage_gb": total_resources.storage_gb
            },
            "orchestration_plan": {
                "execution_mode": "adaptive",
                "estimated_duration": total_resources.estimated_duration_seconds,
                "steps": steps.iter().map(|s| serde_json::json!({
                    "id": s.step_id,
                    "stage": s.stage_name,
                    "priority": s.priority,
                    "dependencies": s.dependencies
                })).collect::<Vec<_>>()
            }
        });

        Ok(serde_json::to_string_pretty(&ghd_data)?)
    }

    fn generate_hre_file(&self, script: &TurbulanceScript, steps: &[ExecutionStep]) -> Result<String> {
        let hre_data = serde_json::json!({
            "protocol_name": script.protocol_name,
            "metacognitive_profile": {
                "complexity_assessment": self.assess_protocol_complexity(steps),
                "uncertainty_factors": self.identify_uncertainty_factors(steps),
                "optimization_opportunities": self.identify_optimization_opportunities(steps)
            },
            "decision_memory": {
                "critical_stages": steps.iter()
                    .filter(|s| s.resource_requirements.cpu_cores > 3.0)
                    .map(|s| s.stage_name.clone())
                    .collect::<Vec<_>>(),
                "fallback_strategies": self.generate_fallback_strategies(steps)
            }
        });

        Ok(serde_json::to_string_pretty(&hre_data)?)
    }

    /// Generate optimization hints
    fn generate_optimization_hints(&mut self, steps: &[ExecutionStep], dependency_graph: &HashMap<String, Vec<String>>) -> Result<Vec<OptimizationHint>> {
        let mut hints = Vec::new();

        // Parallelization opportunities
        let parallel_groups = self.identify_parallelization_opportunities(steps, dependency_graph);
        for group in parallel_groups {
            if group.len() > 1 {
                self.optimization_hits += 1;
                hints.push(OptimizationHint {
                    hint_type: OptimizationType::Parallelization,
                    target_step: group.join(","),
                    description: format!("Steps {} can be executed in parallel", group.join(", ")),
                    priority: 0.8,
                });
            }
        }

        // Resource balancing
        let (underutilized, overutilized) = self.identify_resource_imbalances(steps);
        if !underutilized.is_empty() || !overutilized.is_empty() {
            hints.push(OptimizationHint {
                hint_type: OptimizationType::ResourceBalancing,
                target_step: "protocol".to_string(),
                description: "Resource allocation can be balanced across stages".to_string(),
                priority: 0.6,
            });
        }

        Ok(hints)
    }

    // Helper methods for optimization analysis
    fn calculate_consciousness_level(&self, stage_name: &str) -> f64 {
        match stage_name {
            "stage2_domain_knowledge" => 0.9,
            "stage3_reasoning_optimization" => 0.85,
            "stage5_scoring" => 0.8,
            "stage7_verification" => 0.75,
            _ => 0.7,
        }
    }

    fn assess_protocol_complexity(&self, steps: &[ExecutionStep]) -> f64 {
        let step_count = steps.len() as f64;
        let avg_dependencies = steps.iter().map(|s| s.dependencies.len()).sum::<usize>() as f64 / step_count;
        let resource_intensity = steps.iter().map(|s| s.resource_requirements.cpu_cores).sum::<f64>() / step_count;
        
        (step_count.ln() + avg_dependencies + resource_intensity) / 3.0
    }

    fn identify_uncertainty_factors(&self, steps: &[ExecutionStep]) -> Vec<String> {
        let mut factors = Vec::new();
        
        for step in steps {
            if step.resource_requirements.estimated_duration_seconds > 30.0 {
                factors.push(format!("Long duration step: {}", step.stage_name));
            }
            if step.resource_requirements.gpu_units > 0.0 && step.resource_requirements.gpu_units < 1.0 {
                factors.push(format!("Partial GPU utilization: {}", step.stage_name));
            }
        }
        
        factors
    }

    fn identify_optimization_opportunities(&self, steps: &[ExecutionStep]) -> Vec<String> {
        let mut opportunities = Vec::new();
        
        let total_duration: f64 = steps.iter().map(|s| s.resource_requirements.estimated_duration_seconds).sum();
        if total_duration > 120.0 {
            opportunities.push("Consider parallelization to reduce total execution time".to_string());
        }
        
        let gpu_steps = steps.iter().filter(|s| s.resource_requirements.gpu_units > 0.0).count();
        if gpu_steps > 0 && gpu_steps < steps.len() {
            opportunities.push("Mixed GPU/CPU workload detected, consider resource scheduling".to_string());
        }
        
        opportunities
    }

    fn generate_fallback_strategies(&self, steps: &[ExecutionStep]) -> Vec<String> {
        let mut strategies = Vec::new();
        
        for step in steps {
            if step.resource_requirements.cpu_cores > 4.0 {
                strategies.push(format!("Reduce parallel processing for {}", step.stage_name));
            }
            if step.resource_requirements.memory_gb > 8.0 {
                strategies.push(format!("Use memory streaming for {}", step.stage_name));
            }
        }
        
        strategies
    }

    fn identify_parallelization_opportunities(&self, steps: &[ExecutionStep], dependency_graph: &HashMap<String, Vec<String>>) -> Vec<Vec<String>> {
        let mut groups = Vec::new();
        let mut processed = HashSet::new();

        for step in steps {
            if processed.contains(&step.step_id) {
                continue;
            }

            let mut group = vec![step.step_id.clone()];
            processed.insert(step.step_id.clone());

            // Find other steps with same dependencies
            for other_step in steps {
                if processed.contains(&other_step.step_id) {
                    continue;
                }

                let step_deps = dependency_graph.get(&step.step_id).cloned().unwrap_or_default();
                let other_deps = dependency_graph.get(&other_step.step_id).cloned().unwrap_or_default();

                if step_deps == other_deps {
                    group.push(other_step.step_id.clone());
                    processed.insert(other_step.step_id.clone());
                }
            }

            groups.push(group);
        }

        groups
    }

    fn identify_resource_imbalances(&self, steps: &[ExecutionStep]) -> (Vec<String>, Vec<String>) {
        let avg_cpu = steps.iter().map(|s| s.resource_requirements.cpu_cores).sum::<f64>() / steps.len() as f64;
        let avg_memory = steps.iter().map(|s| s.resource_requirements.memory_gb).sum::<f64>() / steps.len() as f64;

        let mut underutilized = Vec::new();
        let mut overutilized = Vec::new();

        for step in steps {
            if step.resource_requirements.cpu_cores < avg_cpu * 0.5 && step.resource_requirements.memory_gb < avg_memory * 0.5 {
                underutilized.push(step.step_id.clone());
            }
            if step.resource_requirements.cpu_cores > avg_cpu * 2.0 || step.resource_requirements.memory_gb > avg_memory * 2.0 {
                overutilized.push(step.step_id.clone());
            }
        }

        (underutilized, overutilized)
    }

    pub fn get_statistics(&self) -> HashMap<String, f64> {
        let mut stats = HashMap::new();
        stats.insert("protocols_compiled".to_string(), self.protocols_compiled as f64);
        stats.insert("total_steps_generated".to_string(), self.total_steps_generated as f64);
        stats.insert("optimization_hits".to_string(), self.optimization_hits as f64);
        
        let avg_steps = if self.protocols_compiled > 0 {
            self.total_steps_generated as f64 / self.protocols_compiled as f64
        } else {
            0.0
        };
        stats.insert("avg_steps_per_protocol".to_string(), avg_steps);
        
        stats
    }
}

// Python FFI functions

#[pyfunction]
pub fn py_compile_turbulance_protocol(script_json: &str) -> PyResult<String> {
    let script: TurbulanceScript = serde_json::from_str(script_json)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid script JSON: {}", e)))?;
    
    let mut compiler = TurbulanceCompiler::new();
    let compiled_protocol = compiler.compile_protocol(&script)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    serde_json::to_string(&compiled_protocol)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Serialization failed: {}", e)))
}