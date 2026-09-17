//! Receiver graphs (paper §4.3, Def 4.7) and monotone agent history (§8.2,
//! Thm 8.9). Thm 8.9: the committed count strictly increases under every
//! committed act and is never restored, including by "rollback." Every
//! `register_cell` call is a fresh walk against the *current* graph, never a
//! cached value.
//!
//! Direct Rust port of `sdk-ts/src/receiver.ts`. `ReceiverSnapshot` is
//! serde-serializable to the exact JSON shape the four-corners server's
//! `receiver_snapshots` table stores (four-corners/server/src/types.ts),
//! so this worker can push/pull state to/from that HTTP endpoint directly.

use serde::{Deserialize, Serialize};

use crate::graph::{ContactGraph, GraphError, VertexId};

#[derive(Debug, Clone)]
pub struct RegisteredCell {
    pub claim: String,
    /// The claim's resting cut in this receiver, i.e. its meaning here — never "the" relevance.
    pub separation_cost: f64,
    /// This receiver's own floor at the moment of registration.
    pub floor: f64,
    /// Monotone act count at which this registration was computed (Thm 8.9).
    pub committed_count: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnapshotEdge {
    pub a: String,
    pub b: String,
    pub weight: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReceiverSnapshot {
    #[serde(rename = "receiverId")]
    pub receiver_id: String,
    #[serde(rename = "committedCount")]
    pub committed_count: u64,
    pub claims: Vec<String>,
    pub edges: Vec<SnapshotEdge>,
}

const MEDIUM_MARKER: &str = "__medium__";

pub struct ReceiverGraph {
    pub receiver_id: String,
    graph: ContactGraph,
    committed_count: u64,
}

impl ReceiverGraph {
    pub fn new(receiver_id: &str, snapshot: Option<ReceiverSnapshot>) -> Result<Self, GraphError> {
        let mut graph = ContactGraph::new();
        let mut committed_count = 0;

        if let Some(snapshot) = snapshot {
            if snapshot.receiver_id != receiver_id {
                return Err(GraphError::ReceiverIdMismatch {
                    expected: receiver_id.to_string(),
                    found: snapshot.receiver_id,
                });
            }
            committed_count = snapshot.committed_count;
            for c in &snapshot.claims {
                graph.add_claim(c, 1.0)?;
            }
            for e in &snapshot.edges {
                if e.b == MEDIUM_MARKER {
                    graph.add_claim(&e.a, e.weight)?;
                } else {
                    let a = VertexId::Claim(e.a.clone());
                    let b = VertexId::Claim(e.b.clone());
                    graph.add_contact(&a, &b, e.weight)?;
                }
            }
        }

        Ok(ReceiverGraph { receiver_id: receiver_id.to_string(), graph, committed_count })
    }

    /// Every mutation is a committed act: the count only ever increases (Thm 8.9).
    fn commit(&mut self) {
        self.committed_count += 1;
    }

    /// Fix a distinction the receiver already holds: a new claim. This is
    /// how prior queries and project context accrete into the receiver's
    /// own graph over a session (Principle 9.2).
    pub fn fix_distinction(&mut self, claim: &str, medium_weight: f64) -> Result<(), GraphError> {
        let is_new = !self.graph.has(&VertexId::Claim(claim.to_string()));
        self.graph.add_claim(claim, medium_weight)?;
        if is_new {
            self.commit();
        }
        Ok(())
    }

    pub fn fix_contact(&mut self, a: &str, b: &str, weight: f64) -> Result<(), GraphError> {
        let va = VertexId::Claim(a.to_string());
        let vb = VertexId::Claim(b.to_string());
        self.graph.add_contact(&va, &vb, weight)?;
        self.commit();
        Ok(())
    }

    /// An explicit "undo" is itself a further committed act — it never lowers the count (Thm 8.9 proof).
    pub fn acknowledge_rollback_attempt(&mut self) {
        self.commit();
    }

    pub fn committed_count(&self) -> u64 {
        self.committed_count
    }

    /// Def 4.7 / Thm 4.9: register the cell a claim occupies *in this
    /// receiver*. Always a fresh walk against the current graph, never a
    /// cached fetch — the committed_count on the result proves it was
    /// computed now.
    pub fn register_cell(&mut self, claim: &str, medium_weight: f64) -> Result<RegisteredCell, GraphError> {
        self.fix_distinction(claim, medium_weight)?;
        Ok(RegisteredCell {
            claim: claim.to_string(),
            separation_cost: self.graph.separation_cost(claim)?,
            floor: self.graph.floor(),
            committed_count: self.committed_count,
        })
    }

    pub fn floor(&self) -> f64 {
        self.graph.floor()
    }

    pub fn snapshot(&self) -> ReceiverSnapshot {
        // edges() can return either endpoint as `a` or `b` (HashMap iteration
        // order is not insertion order in Rust, unlike sdk-ts's JS Map), so
        // normalize: whichever side is the medium always becomes `b` in the
        // exported shape, and the claim side always becomes `a`.
        let edges = self
            .graph
            .edges()
            .into_iter()
            .map(|e| match (e.a, e.b) {
                (VertexId::Medium, VertexId::Claim(claim)) => SnapshotEdge { a: claim, b: MEDIUM_MARKER.to_string(), weight: e.weight },
                (VertexId::Claim(claim), VertexId::Medium) => SnapshotEdge { a: claim, b: MEDIUM_MARKER.to_string(), weight: e.weight },
                (VertexId::Claim(a), VertexId::Claim(b)) => SnapshotEdge { a, b, weight: e.weight },
                (VertexId::Medium, VertexId::Medium) => unreachable!("a graph never contains a medium-to-medium self-loop"),
            })
            .collect();

        ReceiverSnapshot {
            receiver_id: self.receiver_id.clone(),
            committed_count: self.committed_count,
            claims: self.graph.claims(),
            edges,
        }
    }
}
