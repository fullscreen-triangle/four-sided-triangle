//! Contact graphs (paper §2). A finite weighted graph with a distinguished
//! "medium" vertex adjacent to every other vertex. Vertices other than the
//! medium are "claims" — candidate individuated units of information. An
//! edge's weight is the cost of the distinction separating its endpoints.
//!
//! Direct Rust port of `sdk-ts/src/graph.ts` — same theorem-to-code mapping,
//! same algorithm (Edmonds–Karp max-flow / min-cut), different host language.

use std::collections::{HashMap, HashSet, VecDeque};
use std::fmt;

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum VertexId {
    Medium,
    Claim(String),
}

impl fmt::Display for VertexId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            VertexId::Medium => write!(f, "<medium>"),
            VertexId::Claim(id) => write!(f, "{id}"),
        }
    }
}

#[derive(Debug, Clone)]
pub struct Edge {
    pub a: VertexId,
    pub b: VertexId,
    pub weight: f64,
}

/// Violates Theorem 2.7 (resolution floor > 0): a contact graph has no zero-cost contacts.
#[derive(Debug, thiserror::Error)]
pub enum GraphError {
    #[error("edge weight must be > 0 (got {0}); a contact graph has no zero-cost contacts (Thm 2.7)")]
    NonPositiveWeight(f64),
    #[error("both endpoints must already be claims in the graph (Def 2.1): {0}, {1}")]
    UnknownEndpoint(String, String),
    #[error("unknown claim: {0}")]
    UnknownClaim(String),
    #[error("minCut: unknown vertex {0} or {1}")]
    UnknownVertex(String, String),
    #[error("snapshot receiverId \"{found}\" does not match \"{expected}\"; refusing to load another receiver's state")]
    ReceiverIdMismatch { expected: String, found: String },
}

pub struct ContactGraph {
    vertices: HashSet<VertexId>,
    adjacency: HashMap<VertexId, HashMap<VertexId, f64>>,
}

impl Default for ContactGraph {
    fn default() -> Self {
        Self::new()
    }
}

impl ContactGraph {
    pub fn new() -> Self {
        let mut vertices = HashSet::new();
        vertices.insert(VertexId::Medium);
        let mut adjacency = HashMap::new();
        adjacency.insert(VertexId::Medium, HashMap::new());
        ContactGraph { vertices, adjacency }
    }

    /// Add a claim vertex, contacted to the medium at the given weight if not already present.
    pub fn add_claim(&mut self, id: &str, medium_weight: f64) -> Result<(), GraphError> {
        if medium_weight <= 0.0 {
            return Err(GraphError::NonPositiveWeight(medium_weight));
        }
        let vertex = VertexId::Claim(id.to_string());
        if !self.vertices.contains(&vertex) {
            self.vertices.insert(vertex.clone());
            self.adjacency.insert(vertex.clone(), HashMap::new());
        }
        self.set_edge(vertex, VertexId::Medium, medium_weight);
        Ok(())
    }

    /// Add or update a contact (edge) between two claims already in the graph.
    pub fn add_contact(&mut self, a: &VertexId, b: &VertexId, weight: f64) -> Result<(), GraphError> {
        if weight <= 0.0 {
            return Err(GraphError::NonPositiveWeight(weight));
        }
        if !self.vertices.contains(a) || !self.vertices.contains(b) {
            return Err(GraphError::UnknownEndpoint(a.to_string(), b.to_string()));
        }
        self.set_edge(a.clone(), b.clone(), weight);
        Ok(())
    }

    fn set_edge(&mut self, a: VertexId, b: VertexId, weight: f64) {
        self.adjacency.get_mut(&a).unwrap().insert(b.clone(), weight);
        self.adjacency.get_mut(&b).unwrap().insert(a, weight);
    }

    pub fn has(&self, id: &VertexId) -> bool {
        self.vertices.contains(id)
    }

    pub fn claims(&self) -> Vec<String> {
        self.vertices
            .iter()
            .filter_map(|v| match v {
                VertexId::Claim(id) => Some(id.clone()),
                VertexId::Medium => None,
            })
            .collect()
    }

    pub fn neighbors(&self, id: &VertexId) -> HashMap<VertexId, f64> {
        self.adjacency.get(id).cloned().unwrap_or_default()
    }

    pub fn edges(&self) -> Vec<Edge> {
        let mut seen = HashSet::new();
        let mut out = Vec::new();
        for (a, nbrs) in &self.adjacency {
            for (b, weight) in nbrs {
                let mut key = [a.to_string(), b.to_string()];
                key.sort();
                let key = key.join(" ");
                if seen.contains(&key) {
                    continue;
                }
                seen.insert(key);
                out.push(Edge { a: a.clone(), b: b.clone(), weight: *weight });
            }
        }
        out
    }

    /// Total edge weight, Ω in the paper — used to normalize alignment scores.
    pub fn total_weight(&self) -> f64 {
        self.edges().iter().map(|e| e.weight).sum()
    }

    /// Minimum s-t cut weight via Edmonds–Karp max-flow (max-flow min-cut theorem,
    /// Ford–Fulkerson 1956 / Menger 1927 — cited directly in the paper's Method §1.5).
    /// Treats the graph as its own capacity network (undirected: capacity both ways).
    pub fn min_cut(&self, source: &VertexId, sink: &VertexId) -> Result<f64, GraphError> {
        if !self.vertices.contains(source) || !self.vertices.contains(sink) {
            return Err(GraphError::UnknownVertex(source.to_string(), sink.to_string()));
        }
        if source == sink {
            return Ok(0.0);
        }

        let mut residual: HashMap<VertexId, HashMap<VertexId, f64>> = HashMap::new();
        for v in &self.vertices {
            residual.insert(v.clone(), HashMap::new());
        }
        for edge in self.edges() {
            *residual.get_mut(&edge.a).unwrap().entry(edge.b.clone()).or_insert(0.0) += edge.weight;
            *residual.get_mut(&edge.b).unwrap().entry(edge.a.clone()).or_insert(0.0) += edge.weight;
        }

        let mut max_flow = 0.0;
        loop {
            let parent = Self::bfs_augmenting_path(&residual, source, sink);
            let Some(parent) = parent else { break };

            let mut path_flow = f64::INFINITY;
            let mut v = sink.clone();
            while &v != source {
                let u = parent.get(&v).unwrap().clone();
                path_flow = path_flow.min(*residual.get(&u).unwrap().get(&v).unwrap());
                v = u;
            }

            let mut v = sink.clone();
            while &v != source {
                let u = parent.get(&v).unwrap().clone();
                *residual.get_mut(&u).unwrap().get_mut(&v).unwrap() -= path_flow;
                *residual.get_mut(&v).unwrap().entry(u.clone()).or_insert(0.0) += path_flow;
                v = u;
            }

            max_flow += path_flow;
        }

        Ok(max_flow)
    }

    fn bfs_augmenting_path(
        residual: &HashMap<VertexId, HashMap<VertexId, f64>>,
        source: &VertexId,
        sink: &VertexId,
    ) -> Option<HashMap<VertexId, VertexId>> {
        let mut parent: HashMap<VertexId, VertexId> = HashMap::new();
        let mut visited: HashSet<VertexId> = HashSet::new();
        visited.insert(source.clone());
        let mut queue: VecDeque<VertexId> = VecDeque::new();
        queue.push_back(source.clone());

        while let Some(u) = queue.pop_front() {
            if let Some(neighbors) = residual.get(&u) {
                for (v, cap) in neighbors {
                    if !visited.contains(v) && *cap > 1e-12 {
                        visited.insert(v.clone());
                        parent.insert(v.clone(), u.clone());
                        if v == sink {
                            return Some(parent);
                        }
                        queue.push_back(v.clone());
                    }
                }
            }
        }
        None
    }

    /// Def 2.2: separation cost σ(v) = min cut separating v from the medium.
    pub fn separation_cost(&self, claim: &str) -> Result<f64, GraphError> {
        let vertex = VertexId::Claim(claim.to_string());
        if !self.vertices.contains(&vertex) {
            return Err(GraphError::UnknownClaim(claim.to_string()));
        }
        self.min_cut(&vertex, &VertexId::Medium)
    }

    /// Thm 2.7 resolution floor β: the infimum separation cost over all claims,
    /// equal to the minimum edge weight in a connected graph (proof in the paper
    /// shows the floor is attained exactly, confirmed by validation Experiment 1).
    pub fn floor(&self) -> f64 {
        let claims = self.claims();
        if claims.is_empty() {
            return f64::INFINITY;
        }
        claims
            .iter()
            .map(|c| self.separation_cost(c).unwrap())
            .fold(f64::INFINITY, f64::min)
    }
}
