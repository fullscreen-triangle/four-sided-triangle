use crate::error::{FourSidedTriangleError, Result};
use crate::fuzzy_evidence::{FuzzyEvidence, FuzzyInferenceEngine};
use crate::{validation_error};
use indexmap::IndexMap;
use petgraph::graph::{DiGraph, NodeIndex};
use petgraph::Graph;
use pyo3::prelude::*;
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet, VecDeque};
use std::sync::{Arc, Mutex};

/// Node in the Bayesian evidence network
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EvidenceNode {
    pub id: String,
    pub name: String,
    pub node_type: NodeType,
    pub prior_probability: f64,
    pub current_belief: f64,
    pub evidence_strength: f64,
    pub uncertainty: f64,
    pub fuzzy_evidence: Vec<FuzzyEvidence>,
    pub conditional_probabilities: HashMap<String, f64>,
    pub temporal_weight: f64,
    pub context_relevance: f64,
}

/// Types of nodes in the evidence network
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum NodeType {
    Query,          // User query/request
    Context,        // Context information
    Domain,         // Domain knowledge
    Strategy,       // Processing strategy
    Quality,        // Quality assessment
    Resource,       // Resource allocation
    Output,         // Final output
    Meta,           // Metacognitive control
}

/// Edge in the evidence network representing causal relationships
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EvidenceEdge {
    pub source: String,
    pub target: String,
    pub relationship_type: RelationshipType,
    pub strength: f64,
    pub confidence: f64,
    pub causal_direction: CausalDirection,
    pub temporal_lag: f64,
}

/// Types of relationships between nodes
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum RelationshipType {
    Causal,         // A causes B
    Correlational,  // A correlates with B
    Inhibitory,     // A inhibits B
    Supportive,     // A supports B
    Conditional,    // A is conditional on B
    Temporal,       // A precedes B
}

/// Direction of causal influence
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum CausalDirection {
    Forward,    // Source influences target
    Backward,   // Target influences source
    Bidirectional, // Mutual influence
}

/// Bayesian evidence network
pub struct EvidenceNetwork {
    graph: DiGraph<EvidenceNode, EvidenceEdge>,
    node_indices: HashMap<String, NodeIndex>,
    fuzzy_engine: FuzzyInferenceEngine,
    propagation_history: Vec<PropagationStep>,
    convergence_threshold: f64,
    max_iterations: usize,
}

/// Step in evidence propagation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PropagationStep {
    pub iteration: usize,
    pub node_id: String,
    pub old_belief: f64,
    pub new_belief: f64,
    pub evidence_sources: Vec<String>,
    pub timestamp: f64,
}

/// Evidence propagation algorithm
#[derive(Debug, Clone)]
pub enum PropagationAlgorithm {
    BeliefPropagation,
    VariationalBayes,
    MarkovChainMonteCarlo,
    ParticleFilter,
}

/// Query result from the evidence network
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NetworkQuery {
    pub target_nodes: Vec<String>,
    pub evidence_nodes: HashMap<String, f64>,
    pub query_type: QueryType,
    pub confidence_threshold: f64,
}

/// Types of network queries
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum QueryType {
    MarginalProbability,
    ConditionalProbability,
    MostProbableExplanation,
    SensitivityAnalysis,
    WhatIfScenario,
}

/// Network query result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QueryResult {
    pub probabilities: HashMap<String, f64>,
    pub confidence_intervals: HashMap<String, (f64, f64)>,
    pub explanation: String,
    pub uncertainty_measures: HashMap<String, f64>,
    pub sensitivity_scores: HashMap<String, f64>,
}

impl Default for EvidenceNetwork {
    fn default() -> Self {
        Self::new()
    }
}

impl EvidenceNetwork {
    pub fn new() -> Self {
        Self {
            graph: DiGraph::new(),
            node_indices: HashMap::new(),
            fuzzy_engine: FuzzyInferenceEngine::new(),
            propagation_history: Vec::new(),
            convergence_threshold: 0.001,
            max_iterations: 100,
        }
    }

    /// Add a node to the evidence network
    pub fn add_node(&mut self, node: EvidenceNode) -> Result<()> {
        if self.node_indices.contains_key(&node.id) {
            return Err(validation_error!("Node already exists"));
        }

        let node_index = self.graph.add_node(node.clone());
        self.node_indices.insert(node.id.clone(), node_index);
        
        Ok(())
    }

    /// Add an edge to the evidence network
    pub fn add_edge(&mut self, edge: EvidenceEdge) -> Result<()> {
        let source_idx = self.node_indices.get(&edge.source)
            .ok_or_else(|| validation_error!("Source node not found"))?;
        let target_idx = self.node_indices.get(&edge.target)
            .ok_or_else(|| validation_error!("Target node not found"))?;

        self.graph.add_edge(*source_idx, *target_idx, edge);
        Ok(())
    }

    /// Update evidence for a specific node
    pub fn update_node_evidence(&mut self, node_id: &str, evidence: FuzzyEvidence) -> Result<()> {
        let node_idx = self.node_indices.get(node_id)
            .ok_or_else(|| validation_error!("Node not found"))?;

        if let Some(node) = self.graph.node_weight_mut(*node_idx) {
            node.fuzzy_evidence.push(evidence.clone());
            
            // Update evidence strength using fuzzy inference
            let combined_strength = self.fuzzy_engine.calculate_evidence_strength(&evidence);
            node.evidence_strength = (node.evidence_strength + combined_strength) / 2.0;
            
            // Update uncertainty
            node.uncertainty = 1.0 - (evidence.confidence * evidence.source_reliability);
            
            // Limit evidence history
            if node.fuzzy_evidence.len() > 50 {
                node.fuzzy_evidence.remove(0);
            }
        }

        Ok(())
    }

    /// Propagate evidence through the network using belief propagation
    pub fn propagate_evidence(&mut self, algorithm: PropagationAlgorithm) -> Result<()> {
        match algorithm {
            PropagationAlgorithm::BeliefPropagation => self.belief_propagation(),
            PropagationAlgorithm::VariationalBayes => self.variational_bayes(),
            PropagationAlgorithm::MarkovChainMonteCarlo => self.mcmc_propagation(),
            PropagationAlgorithm::ParticleFilter => self.particle_filter(),
        }
    }

    /// Belief propagation algorithm
    fn belief_propagation(&mut self) -> Result<()> {
        let mut iteration = 0;
        let mut converged = false;

        while !converged && iteration < self.max_iterations {
            let mut max_change = 0.0;
            let node_ids: Vec<String> = self.node_indices.keys().cloned().collect();

            for node_id in &node_ids {
                let old_belief = self.get_node_belief(node_id)?;
                let new_belief = self.calculate_node_belief(node_id)?;
                
                self.update_node_belief(node_id, new_belief)?;
                
                let change = (new_belief - old_belief).abs();
                max_change = max_change.max(change);

                // Record propagation step
                self.propagation_history.push(PropagationStep {
                    iteration,
                    node_id: node_id.clone(),
                    old_belief,
                    new_belief,
                    evidence_sources: self.get_evidence_sources(node_id)?,
                    timestamp: std::time::SystemTime::now()
                        .duration_since(std::time::UNIX_EPOCH)
                        .unwrap()
                        .as_secs_f64(),
                });
            }

            converged = max_change < self.convergence_threshold;
            iteration += 1;
        }

        Ok(())
    }

    /// Calculate belief for a node based on its parents and evidence
    fn calculate_node_belief(&self, node_id: &str) -> Result<f64> {
        let node_idx = self.node_indices.get(node_id)
            .ok_or_else(|| validation_error!("Node not found"))?;

        let node = self.graph.node_weight(*node_idx)
            .ok_or_else(|| validation_error!("Node weight not found"))?;

        // Start with prior probability
        let mut belief = node.prior_probability;

        // Collect evidence from parent nodes
        let parents = self.graph.neighbors_directed(*node_idx, petgraph::Direction::Incoming);
        let mut parent_influences = Vec::new();

        for parent_idx in parents {
            if let Some(parent_node) = self.graph.node_weight(parent_idx) {
                if let Some(edge) = self.graph.find_edge(parent_idx, *node_idx) {
                    if let Some(edge_weight) = self.graph.edge_weight(edge) {
                        let influence = self.calculate_parent_influence(
                            parent_node,
                            node,
                            edge_weight,
                        )?;
                        parent_influences.push(influence);
                    }
                }
            }
        }

        // Combine parent influences using fuzzy aggregation
        if !parent_influences.is_empty() {
            let combined_influence = self.combine_influences(&parent_influences)?;
            belief = self.bayesian_update(belief, combined_influence, node.evidence_strength)?;
        }

        // Apply fuzzy evidence
        if !node.fuzzy_evidence.is_empty() {
            let fuzzy_belief = self.fuzzy_engine.combine_evidence(&node.fuzzy_evidence)?;
            belief = self.weighted_combination(belief, fuzzy_belief, 0.7)?;
        }

        // Apply temporal and context weights
        belief *= node.temporal_weight * node.context_relevance;

        Ok(belief.clamp(0.0, 1.0))
    }

    /// Calculate influence from parent node
    fn calculate_parent_influence(
        &self,
        parent: &EvidenceNode,
        child: &EvidenceNode,
        edge: &EvidenceEdge,
    ) -> Result<f64> {
        let base_influence = parent.current_belief * edge.strength * edge.confidence;
        
        // Apply relationship type modifiers
        let modified_influence = match edge.relationship_type {
            RelationshipType::Causal => base_influence,
            RelationshipType::Correlational => base_influence * 0.8,
            RelationshipType::Inhibitory => -base_influence,
            RelationshipType::Supportive => base_influence * 1.2,
            RelationshipType::Conditional => {
                if parent.current_belief > 0.5 {
                    base_influence
                } else {
                    base_influence * 0.3
                }
            }
            RelationshipType::Temporal => {
                // Apply temporal decay
                let decay_factor = (-edge.temporal_lag * 0.1).exp();
                base_influence * decay_factor
            }
        };

        // Apply causal direction
        let directional_influence = match edge.causal_direction {
            CausalDirection::Forward => modified_influence,
            CausalDirection::Backward => modified_influence * 0.5,
            CausalDirection::Bidirectional => modified_influence * 0.8,
        };

        Ok(directional_influence)
    }

    /// Combine multiple influences using fuzzy aggregation
    fn combine_influences(&self, influences: &[f64]) -> Result<f64> {
        if influences.is_empty() {
            return Ok(0.0);
        }

        // Use ordered weighted averaging (OWA)
        let mut sorted_influences: Vec<f64> = influences.iter().cloned().collect();
        sorted_influences.sort_by(|a, b| b.partial_cmp(a).unwrap());

        let n = sorted_influences.len() as f64;
        let mut weighted_sum = 0.0;
        let mut weight_sum = 0.0;

        for (i, influence) in sorted_influences.iter().enumerate() {
            // Decreasing weights for OWA
            let weight = (n - i as f64) / (n * (n + 1.0) / 2.0);
            weighted_sum += influence * weight;
            weight_sum += weight;
        }

        if weight_sum > 0.0 {
            Ok(weighted_sum / weight_sum)
        } else {
            Ok(0.0)
        }
    }

    /// Bayesian update of belief
    fn bayesian_update(&self, prior: f64, likelihood: f64, evidence_strength: f64) -> Result<f64> {
        let likelihood_pos = likelihood * evidence_strength;
        let likelihood_neg = (1.0 - likelihood) * (1.0 - evidence_strength);
        
        let posterior = (prior * likelihood_pos) / 
            (prior * likelihood_pos + (1.0 - prior) * likelihood_neg);
        
        Ok(posterior)
    }

    /// Weighted combination of beliefs
    fn weighted_combination(&self, belief1: f64, belief2: f64, weight: f64) -> Result<f64> {
        Ok(weight * belief1 + (1.0 - weight) * belief2)
    }

    /// Get current belief for a node
    fn get_node_belief(&self, node_id: &str) -> Result<f64> {
        let node_idx = self.node_indices.get(node_id)
            .ok_or_else(|| validation_error!("Node not found"))?;

        let node = self.graph.node_weight(*node_idx)
            .ok_or_else(|| validation_error!("Node weight not found"))?;

        Ok(node.current_belief)
    }

    /// Update belief for a node
    fn update_node_belief(&mut self, node_id: &str, new_belief: f64) -> Result<()> {
        let node_idx = self.node_indices.get(node_id)
            .ok_or_else(|| validation_error!("Node not found"))?;

        if let Some(node) = self.graph.node_weight_mut(*node_idx) {
            node.current_belief = new_belief.clamp(0.0, 1.0);
        }

        Ok(())
    }

    /// Get evidence sources for a node
    fn get_evidence_sources(&self, node_id: &str) -> Result<Vec<String>> {
        let node_idx = self.node_indices.get(node_id)
            .ok_or_else(|| validation_error!("Node not found"))?;

        let parents = self.graph.neighbors_directed(*node_idx, petgraph::Direction::Incoming);
        let mut sources = Vec::new();

        for parent_idx in parents {
            if let Some(parent_node) = self.graph.node_weight(parent_idx) {
                sources.push(parent_node.id.clone());
            }
        }

        Ok(sources)
    }

    /// Variational Bayes propagation (simplified implementation)
    fn variational_bayes(&mut self) -> Result<()> {
        // Simplified variational inference
        let mut iteration = 0;
        let mut converged = false;

        while !converged && iteration < self.max_iterations {
            let mut max_change = 0.0;
            let node_ids: Vec<String> = self.node_indices.keys().cloned().collect();

            for node_id in &node_ids {
                let old_belief = self.get_node_belief(node_id)?;
                
                // Variational update (simplified)
                let new_belief = self.variational_update(node_id)?;
                self.update_node_belief(node_id, new_belief)?;
                
                let change = (new_belief - old_belief).abs();
                max_change = max_change.max(change);
            }

            converged = max_change < self.convergence_threshold;
            iteration += 1;
        }

        Ok(())
    }

    /// Variational update for a node
    fn variational_update(&self, node_id: &str) -> Result<f64> {
        // Simplified variational update
        let current_belief = self.get_node_belief(node_id)?;
        let evidence_influence = self.calculate_node_belief(node_id)?;
        
        // Variational approximation
        let alpha = 2.0; // Concentration parameter
        let beta = 2.0;  // Concentration parameter
        
        let updated_belief = (alpha * current_belief + evidence_influence) / (alpha + beta);
        Ok(updated_belief)
    }

    /// MCMC propagation (simplified implementation)
    fn mcmc_propagation(&mut self) -> Result<()> {
        // Simplified MCMC sampling
        let num_samples = 1000;
        let burn_in = 100;
        
        for iteration in 0..num_samples {
            if iteration > burn_in {
                // Sample from posterior
                let node_ids: Vec<String> = self.node_indices.keys().cloned().collect();
                
                for node_id in &node_ids {
                    let sample = self.mcmc_sample(node_id)?;
                    if iteration == num_samples - 1 {
                        // Use final sample as belief
                        self.update_node_belief(node_id, sample)?;
                    }
                }
            }
        }

        Ok(())
    }

    /// MCMC sample for a node
    fn mcmc_sample(&self, node_id: &str) -> Result<f64> {
        use rand::Rng;
        let mut rng = rand::thread_rng();
        
        // Simplified Gibbs sampling
        let current_belief = self.get_node_belief(node_id)?;
        let proposal = current_belief + rng.gen_range(-0.1..0.1);
        let clamped_proposal = proposal.clamp(0.0, 1.0);
        
        // Accept/reject based on likelihood
        let likelihood_current = self.calculate_likelihood(node_id, current_belief)?;
        let likelihood_proposal = self.calculate_likelihood(node_id, clamped_proposal)?;
        
        let acceptance_ratio = likelihood_proposal / likelihood_current.max(1e-10);
        
        if rng.gen::<f64>() < acceptance_ratio.min(1.0) {
            Ok(clamped_proposal)
        } else {
            Ok(current_belief)
        }
    }

    /// Calculate likelihood for MCMC
    fn calculate_likelihood(&self, node_id: &str, belief: f64) -> Result<f64> {
        let node_idx = self.node_indices.get(node_id)
            .ok_or_else(|| validation_error!("Node not found"))?;

        let node = self.graph.node_weight(*node_idx)
            .ok_or_else(|| validation_error!("Node weight not found"))?;

        // Simplified likelihood calculation
        let prior_likelihood = if belief > 0.0 && belief < 1.0 {
            belief.ln() + (1.0 - belief).ln()
        } else {
            -1000.0 // Very low likelihood for boundary values
        };

        let evidence_likelihood = node.evidence_strength * belief;
        
        Ok((prior_likelihood + evidence_likelihood).exp())
    }

    /// Particle filter propagation
    fn particle_filter(&mut self) -> Result<()> {
        let num_particles = 1000;
        
        // Initialize particles
        let mut particles = self.initialize_particles(num_particles)?;
        
        // Propagate particles
        for _ in 0..10 { // Number of time steps
            particles = self.propagate_particles(particles)?;
            particles = self.resample_particles(particles)?;
        }
        
        // Update beliefs based on particles
        self.update_beliefs_from_particles(&particles)?;
        
        Ok(())
    }

    /// Initialize particles for particle filter
    fn initialize_particles(&self, num_particles: usize) -> Result<Vec<HashMap<String, f64>>> {
        use rand::Rng;
        let mut rng = rand::thread_rng();
        let mut particles = Vec::new();
        
        for _ in 0..num_particles {
            let mut particle = HashMap::new();
            
            for (node_id, node_idx) in &self.node_indices {
                if let Some(node) = self.graph.node_weight(*node_idx) {
                    // Sample from prior
                    let sample = rng.gen::<f64>() * node.prior_probability;
                    particle.insert(node_id.clone(), sample);
                }
            }
            
            particles.push(particle);
        }
        
        Ok(particles)
    }

    /// Propagate particles through network dynamics
    fn propagate_particles(&self, particles: Vec<HashMap<String, f64>>) -> Result<Vec<HashMap<String, f64>>> {
        use rand::Rng;
        let mut rng = rand::thread_rng();
        let mut new_particles = Vec::new();
        
        for particle in particles {
            let mut new_particle = HashMap::new();
            
            for (node_id, &current_value) in &particle {
                // Add noise and propagate
                let noise = rng.gen_range(-0.05..0.05);
                let new_value = (current_value + noise).clamp(0.0, 1.0);
                new_particle.insert(node_id.clone(), new_value);
            }
            
            new_particles.push(new_particle);
        }
        
        Ok(new_particles)
    }

    /// Resample particles based on weights
    fn resample_particles(&self, particles: Vec<HashMap<String, f64>>) -> Result<Vec<HashMap<String, f64>>> {
        use rand::Rng;
        let mut rng = rand::thread_rng();
        
        // Calculate weights
        let weights: Vec<f64> = particles.iter()
            .map(|particle| self.calculate_particle_weight(particle).unwrap_or(0.0))
            .collect();
        
        let total_weight: f64 = weights.iter().sum();
        if total_weight <= 0.0 {
            return Ok(particles);
        }
        
        // Systematic resampling
        let mut resampled = Vec::new();
        let num_particles = particles.len();
        let step = total_weight / num_particles as f64;
        let mut cumulative_weight = 0.0;
        let mut i = 0;
        
        for j in 0..num_particles {
            let target = step * (j as f64 + rng.gen::<f64>());
            
            while cumulative_weight < target && i < weights.len() {
                cumulative_weight += weights[i];
                i += 1;
            }
            
            if i > 0 {
                resampled.push(particles[i - 1].clone());
            }
        }
        
        Ok(resampled)
    }

    /// Calculate weight for a particle
    fn calculate_particle_weight(&self, particle: &HashMap<String, f64>) -> Result<f64> {
        let mut weight = 1.0;
        
        for (node_id, &value) in particle {
            if let Some(node_idx) = self.node_indices.get(node_id) {
                if let Some(node) = self.graph.node_weight(*node_idx) {
                    // Weight based on evidence
                    let evidence_weight = node.evidence_strength * value;
                    weight *= evidence_weight;
                }
            }
        }
        
        Ok(weight)
    }

    /// Update node beliefs from particle distribution
    fn update_beliefs_from_particles(&mut self, particles: &[HashMap<String, f64>]) -> Result<()> {
        for (node_id, _) in &self.node_indices {
            let values: Vec<f64> = particles.iter()
                .filter_map(|p| p.get(node_id).copied())
                .collect();
            
            if !values.is_empty() {
                let mean_belief = values.iter().sum::<f64>() / values.len() as f64;
                self.update_node_belief(node_id, mean_belief)?;
            }
        }
        
        Ok(())
    }

    /// Query the network for specific information
    pub fn query_network(&self, query: &NetworkQuery) -> Result<QueryResult> {
        match query.query_type {
            QueryType::MarginalProbability => self.marginal_probability_query(query),
            QueryType::ConditionalProbability => self.conditional_probability_query(query),
            QueryType::MostProbableExplanation => self.mpe_query(query),
            QueryType::SensitivityAnalysis => self.sensitivity_analysis_query(query),
            QueryType::WhatIfScenario => self.what_if_query(query),
        }
    }

    /// Marginal probability query
    fn marginal_probability_query(&self, query: &NetworkQuery) -> Result<QueryResult> {
        let mut probabilities = HashMap::new();
        let mut confidence_intervals = HashMap::new();
        let mut uncertainty_measures = HashMap::new();

        for target_node in &query.target_nodes {
            let belief = self.get_node_belief(target_node)?;
            let uncertainty = self.calculate_node_uncertainty(target_node)?;
            
            probabilities.insert(target_node.clone(), belief);
            
            // Calculate confidence interval
            let margin = 1.96 * uncertainty.sqrt(); // 95% CI
            confidence_intervals.insert(
                target_node.clone(),
                ((belief - margin).max(0.0), (belief + margin).min(1.0)),
            );
            
            uncertainty_measures.insert(target_node.clone(), uncertainty);
        }

        Ok(QueryResult {
            probabilities,
            confidence_intervals,
            explanation: "Marginal probabilities calculated".to_string(),
            uncertainty_measures,
            sensitivity_scores: HashMap::new(),
        })
    }

    /// Calculate uncertainty for a node
    fn calculate_node_uncertainty(&self, node_id: &str) -> Result<f64> {
        let node_idx = self.node_indices.get(node_id)
            .ok_or_else(|| validation_error!("Node not found"))?;

        let node = self.graph.node_weight(*node_idx)
            .ok_or_else(|| validation_error!("Node weight not found"))?;

        // Combine various uncertainty sources
        let belief_uncertainty = node.current_belief * (1.0 - node.current_belief); // Variance of Bernoulli
        let evidence_uncertainty = node.uncertainty;
        let fuzzy_uncertainty = if !node.fuzzy_evidence.is_empty() {
            1.0 - node.fuzzy_evidence.iter().map(|e| e.confidence).sum::<f64>() / node.fuzzy_evidence.len() as f64
        } else {
            0.5
        };

        Ok((belief_uncertainty + evidence_uncertainty + fuzzy_uncertainty) / 3.0)
    }

    /// Conditional probability query
    fn conditional_probability_query(&self, query: &NetworkQuery) -> Result<QueryResult> {
        // Simplified conditional probability calculation
        // In a full implementation, this would use exact inference algorithms
        
        let mut probabilities = HashMap::new();
        let mut confidence_intervals = HashMap::new();
        
        for target_node in &query.target_nodes {
            let marginal_prob = self.get_node_belief(target_node)?;
            
            // Adjust based on evidence
            let mut conditional_prob = marginal_prob;
            for (evidence_node, evidence_value) in &query.evidence_nodes {
                let evidence_belief = self.get_node_belief(evidence_node)?;
                let adjustment = evidence_value * evidence_belief;
                conditional_prob = self.bayesian_update(conditional_prob, adjustment, 0.8)?;
            }
            
            probabilities.insert(target_node.clone(), conditional_prob);
            
            let uncertainty = self.calculate_node_uncertainty(target_node)?;
            let margin = 1.96 * uncertainty.sqrt();
            confidence_intervals.insert(
                target_node.clone(),
                ((conditional_prob - margin).max(0.0), (conditional_prob + margin).min(1.0)),
            );
        }

        Ok(QueryResult {
            probabilities,
            confidence_intervals,
            explanation: "Conditional probabilities calculated".to_string(),
            uncertainty_measures: HashMap::new(),
            sensitivity_scores: HashMap::new(),
        })
    }

    /// Most probable explanation query
    fn mpe_query(&self, query: &NetworkQuery) -> Result<QueryResult> {
        // Find the most probable assignment to all variables
        let mut best_assignment = HashMap::new();
        let mut best_probability = 0.0;
        
        // Simplified: use current beliefs as MPE
        for (node_id, node_idx) in &self.node_indices {
            if let Some(node) = self.graph.node_weight(*node_idx) {
                best_assignment.insert(node_id.clone(), node.current_belief);
                best_probability += node.current_belief;
            }
        }
        
        // Normalize probability
        best_probability /= self.node_indices.len() as f64;

        Ok(QueryResult {
            probabilities: best_assignment,
            confidence_intervals: HashMap::new(),
            explanation: format!("Most probable explanation with probability {:.4}", best_probability),
            uncertainty_measures: HashMap::new(),
            sensitivity_scores: HashMap::new(),
        })
    }

    /// Sensitivity analysis query
    fn sensitivity_analysis_query(&self, query: &NetworkQuery) -> Result<QueryResult> {
        let mut sensitivity_scores = HashMap::new();
        
        for target_node in &query.target_nodes {
            let baseline_belief = self.get_node_belief(target_node)?;
            
            // Test sensitivity to each evidence node
            for (evidence_node, _) in &query.evidence_nodes {
                let sensitivity = self.calculate_sensitivity(target_node, evidence_node)?;
                sensitivity_scores.insert(
                    format!("{}_{}", target_node, evidence_node),
                    sensitivity,
                );
            }
        }

        Ok(QueryResult {
            probabilities: HashMap::new(),
            confidence_intervals: HashMap::new(),
            explanation: "Sensitivity analysis completed".to_string(),
            uncertainty_measures: HashMap::new(),
            sensitivity_scores,
        })
    }

    /// Calculate sensitivity between two nodes
    fn calculate_sensitivity(&self, target_node: &str, evidence_node: &str) -> Result<f64> {
        let baseline_target = self.get_node_belief(target_node)?;
        let baseline_evidence = self.get_node_belief(evidence_node)?;
        
        // Small perturbation
        let delta = 0.01;
        let perturbed_evidence = (baseline_evidence + delta).min(1.0);
        
        // Calculate change in target (simplified)
        let evidence_influence = self.calculate_direct_influence(evidence_node, target_node)?;
        let perturbed_target = baseline_target + evidence_influence * delta;
        
        let sensitivity = (perturbed_target - baseline_target) / delta;
        Ok(sensitivity.abs())
    }

    /// Calculate direct influence between nodes
    fn calculate_direct_influence(&self, source_node: &str, target_node: &str) -> Result<f64> {
        let source_idx = self.node_indices.get(source_node)
            .ok_or_else(|| validation_error!("Source node not found"))?;
        let target_idx = self.node_indices.get(target_node)
            .ok_or_else(|| validation_error!("Target node not found"))?;

        if let Some(edge_idx) = self.graph.find_edge(*source_idx, *target_idx) {
            if let Some(edge) = self.graph.edge_weight(edge_idx) {
                return Ok(edge.strength * edge.confidence);
            }
        }

        // No direct edge, calculate indirect influence
        Ok(0.1) // Default small influence
    }

    /// What-if scenario query
    fn what_if_query(&self, query: &NetworkQuery) -> Result<QueryResult> {
        // Simulate what happens if evidence nodes are set to specific values
        let mut scenario_probabilities = HashMap::new();
        
        for target_node in &query.target_nodes {
            let mut scenario_belief = self.get_node_belief(target_node)?;
            
            // Apply what-if evidence
            for (evidence_node, evidence_value) in &query.evidence_nodes {
                let influence = self.calculate_direct_influence(evidence_node, target_node)?;
                scenario_belief += influence * (evidence_value - self.get_node_belief(evidence_node)?);
            }
            
            scenario_belief = scenario_belief.clamp(0.0, 1.0);
            scenario_probabilities.insert(target_node.clone(), scenario_belief);
        }

        Ok(QueryResult {
            probabilities: scenario_probabilities,
            confidence_intervals: HashMap::new(),
            explanation: "What-if scenario analysis completed".to_string(),
            uncertainty_measures: HashMap::new(),
            sensitivity_scores: HashMap::new(),
        })
    }

    /// Get network statistics
    pub fn get_network_statistics(&self) -> HashMap<String, f64> {
        let mut stats = HashMap::new();
        
        stats.insert("num_nodes".to_string(), self.graph.node_count() as f64);
        stats.insert("num_edges".to_string(), self.graph.edge_count() as f64);
        
        // Average belief
        let total_belief: f64 = self.graph.node_weights()
            .map(|node| node.current_belief)
            .sum();
        stats.insert("average_belief".to_string(), total_belief / self.graph.node_count() as f64);
        
        // Average uncertainty
        let total_uncertainty: f64 = self.graph.node_weights()
            .map(|node| node.uncertainty)
            .sum();
        stats.insert("average_uncertainty".to_string(), total_uncertainty / self.graph.node_count() as f64);
        
        // Network density
        let max_edges = self.graph.node_count() * (self.graph.node_count() - 1);
        let density = if max_edges > 0 {
            self.graph.edge_count() as f64 / max_edges as f64
        } else {
            0.0
        };
        stats.insert("network_density".to_string(), density);
        
        stats
    }
}

// Python FFI functions

/// Generate a unique network ID
fn generate_network_id() -> String {
    format!("network_{}", rand::random::<u64>())
}

/// Get network from global registry
fn get_network(network_id: &str) -> Result<EvidenceNetwork> {
    let networks = crate::EVIDENCE_NETWORKS.lock().unwrap();
    networks.get(network_id)
        .cloned()
        .ok_or_else(|| validation_error!("Network not found"))
}

/// Update network in global registry
fn update_network(network_id: &str, network: EvidenceNetwork) -> Result<()> {
    let mut networks = crate::EVIDENCE_NETWORKS.lock().unwrap();
    networks.insert(network_id.to_string(), network);
    Ok(())
}

#[pyfunction]
pub fn py_create_evidence_network() -> PyResult<String> {
    let network = EvidenceNetwork::new();
    let network_id = generate_network_id();
    
    let mut networks = crate::EVIDENCE_NETWORKS.lock().unwrap();
    networks.insert(network_id.clone(), network);
    
    Ok(network_id)
}

#[pyfunction]
pub fn py_add_node(
    network_id: &str,
    node_json: &str,
) -> PyResult<()> {
    let node: EvidenceNode = serde_json::from_str(node_json)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid node JSON: {}", e)))?;
    
    let mut networks = crate::EVIDENCE_NETWORKS.lock().unwrap();
    if let Some(network) = networks.get_mut(network_id) {
        network.add_node(node)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        Ok(())
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>("Network not found"))
    }
}

#[pyfunction]
pub fn py_add_edge(
    network_id: &str,
    edge_json: &str,
) -> PyResult<()> {
    let edge: EvidenceEdge = serde_json::from_str(edge_json)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid edge JSON: {}", e)))?;
    
    let mut networks = crate::EVIDENCE_NETWORKS.lock().unwrap();
    if let Some(network) = networks.get_mut(network_id) {
        network.add_edge(edge)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        Ok(())
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>("Network not found"))
    }
}

#[pyfunction]
pub fn py_update_node_evidence(
    network_id: &str,
    node_id: &str,
    evidence_json: &str,
) -> PyResult<()> {
    let evidence: FuzzyEvidence = serde_json::from_str(evidence_json)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid evidence JSON: {}", e)))?;
    
    let mut networks = crate::EVIDENCE_NETWORKS.lock().unwrap();
    if let Some(network) = networks.get_mut(network_id) {
        network.update_node_evidence(node_id, evidence)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        Ok(())
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>("Network not found"))
    }
}

#[pyfunction]
pub fn py_propagate_evidence(
    network_id: &str,
    algorithm: &str,
) -> PyResult<()> {
    let propagation_algorithm = match algorithm {
        "belief_propagation" => PropagationAlgorithm::BeliefPropagation,
        "variational_bayes" => PropagationAlgorithm::VariationalBayes,
        "mcmc" => PropagationAlgorithm::MarkovChainMonteCarlo,
        "particle_filter" => PropagationAlgorithm::ParticleFilter,
        _ => return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Unknown propagation algorithm")),
    };
    
    let mut networks = crate::EVIDENCE_NETWORKS.lock().unwrap();
    if let Some(network) = networks.get_mut(network_id) {
        network.propagate_evidence(propagation_algorithm)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        Ok(())
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>("Network not found"))
    }
}

#[pyfunction]
pub fn py_query_network(
    network_id: &str,
    query_json: &str,
) -> PyResult<String> {
    let query: NetworkQuery = serde_json::from_str(query_json)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid query JSON: {}", e)))?;
    
    let networks = crate::EVIDENCE_NETWORKS.lock().unwrap();
    if let Some(network) = networks.get(network_id) {
        let result = network.query(&query)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        
        serde_json::to_string(&result)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Serialization failed: {}", e)))
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>("Network not found"))
    }
}

#[pyfunction]
pub fn py_get_network_statistics(network_id: &str) -> PyResult<String> {
    let networks = crate::EVIDENCE_NETWORKS.lock().unwrap();
    if let Some(network) = networks.get(network_id) {
        let stats = network.get_network_statistics();
        serde_json::to_string(&stats)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Serialization failed: {}", e)))
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>("Network not found"))
    }
} 