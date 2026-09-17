//! Catalytic composition and coherence (paper §6, Def 6.1–6.3, Thm 6.2, 6.4).
//!
//! Direct Rust port of `sdk-ts/src/catalysis.ts`. A claim can only be marked
//! "grounded" once a real strongly-connected triangle of >=3 independent,
//! mutually-supporting catalysts exists (Thm 6.4) — one passage is never a
//! grounded answer, and neither are two (Remark 6.5).

use std::collections::{HashMap, HashSet};

#[derive(Debug, Clone)]
pub struct Catalyst {
    pub id: String,
    /// Independent evidentiary channel this catalyst draws from — a file, a model, a record store.
    pub source: String,
    /// power ∈ [0,1]: fraction of the above-floor alignment gap this catalyst closes (Def 6.1).
    pub power: f64,
}

/// Thm 6.2: composite power of catalysts applied in sequence, 1 - Π(1 - power_i).
pub fn composite_power(catalysts: &[Catalyst]) -> f64 {
    1.0 - catalysts.iter().fold(1.0, |acc, c| acc * (1.0 - c.power))
}

#[derive(Debug, Clone)]
pub struct SupportEdge {
    pub from: String,
    pub to: String,
    /// Degree to which `from`'s result reinforces `to`'s alignment shift, in (0,1].
    pub degree: f64,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum GroundingStatus {
    SingleSourced,
    TwoSourced,
    Grounded,
}

#[derive(Debug, Clone)]
pub struct GroundingResult {
    pub status: GroundingStatus,
    pub catalysts: Vec<Catalyst>,
    pub active_support: Vec<SupportEdge>,
    /// True only for status Grounded: a strongly-connected triangle survives single-member removal (Thm 6.4(iii)).
    pub robust_to_single_removal: bool,
}

const DEFAULT_THETA: f64 = 0.5;

/// Thm 6.4: never silently promote a claim to "grounded" on fewer than three
/// independently sourced, mutually supporting catalysts.
pub fn assess_grounding(catalysts: &[Catalyst], support: &[SupportEdge], theta: Option<f64>) -> GroundingResult {
    let theta = theta.unwrap_or(DEFAULT_THETA);
    let unique_sources: HashSet<&str> = catalysts.iter().map(|c| c.source.as_str()).collect();
    let active: Vec<SupportEdge> = support.iter().filter(|e| e.degree >= theta && e.degree > 0.5).cloned().collect();

    if catalysts.len() <= 1 {
        return GroundingResult {
            status: GroundingStatus::SingleSourced,
            catalysts: catalysts.to_vec(),
            active_support: active,
            robust_to_single_removal: false,
        };
    }
    if catalysts.len() == 2 || unique_sources.len() < 3 {
        // Thm 6.4(ii): a 2-cycle fails the majority condition θ>1/2 — removing
        // either leaves exactly one, unsupported, voter.
        return GroundingResult {
            status: GroundingStatus::TwoSourced,
            catalysts: catalysts.to_vec(),
            active_support: active,
            robust_to_single_removal: false,
        };
    }

    let ids: Vec<String> = catalysts.iter().map(|c| c.id.clone()).collect();
    let robust = is_strongly_connected_robust(&ids, &active);
    GroundingResult {
        status: if robust { GroundingStatus::Grounded } else { GroundingStatus::TwoSourced },
        catalysts: catalysts.to_vec(),
        active_support: active,
        robust_to_single_removal: robust,
    }
}

/// Thm 6.4(iii): each catalyst supported by >=2 others at θ, and removal of any one leaves the rest mutually supporting.
fn is_strongly_connected_robust(ids: &[String], support: &[SupportEdge]) -> bool {
    if ids.len() < 3 {
        return false;
    }
    let mut incoming: HashMap<&str, HashSet<&str>> = ids.iter().map(|id| (id.as_str(), HashSet::new())).collect();
    for edge in support {
        if let Some(set) = incoming.get_mut(edge.to.as_str()) {
            set.insert(edge.from.as_str());
        }
    }

    for id in ids {
        if incoming.get(id.as_str()).map(|s| s.len()).unwrap_or(0) < 2 {
            return false;
        }
    }

    for removed in ids {
        for id in ids {
            if id == removed {
                continue;
            }
            let supporters = incoming.get(id.as_str()).map(|s| s.iter().filter(|&&s| s != removed.as_str()).count()).unwrap_or(0);
            if supporters < 1 {
                return false;
            }
        }
    }
    true
}
