//! Closure (paper §6.4, Def 6.5, Thm 6.6–6.7): the correct stopping rule for
//! a search, replacing a confidence threshold. A search is closed once no
//! further *available but not-yet-invoked* source can add a new answer
//! class. There is deliberately no early-exit-on-confidence path, since
//! Thm 6.6 constructs a case where that would stop too early.
//!
//! Direct Rust port of `sdk-ts/src/closure.ts`.

use std::collections::HashMap;
use std::future::Future;
use std::pin::Pin;

#[derive(Debug, Clone)]
pub struct AnswerClass {
    /// Stable key identifying this equivalence class of reachable answers (Def 6.5: endpoint-indistinguishable).
    pub key: String,
    pub representative: String,
    pub supporting_catalyst_ids: Vec<String>,
}

pub type InvokeFuture = Pin<Box<dyn Future<Output = Option<AnswerClass>> + Send>>;

pub struct AvailableSource {
    pub id: String,
    pub invoke: Box<dyn Fn() -> InvokeFuture + Send + Sync>,
}

#[derive(Debug, Clone)]
pub enum ClosureResult {
    Closed { class: AnswerClass },
    Contested { classes: Vec<AnswerClass> },
    Declined { reason: String },
}

/// Runs every available source to exhaustion against the registry (Def 6.5)
/// and classifies the outcome per Thm 6.7 — convergent closure (one class),
/// contested closure (>1 class, reported as a first-class output, Remark
/// 6.8, never silently resolved), or declined (nothing reached).
pub async fn run_to_closure(sources: &[AvailableSource]) -> ClosureResult {
    if sources.is_empty() {
        return ClosureResult::Declined { reason: "no available sources were registered for this query".to_string() };
    }

    let mut classes_by_key: HashMap<String, AnswerClass> = HashMap::new();
    for source in sources {
        let Some(result) = (source.invoke)().await else { continue };
        classes_by_key
            .entry(result.key.clone())
            .and_modify(|existing| existing.supporting_catalyst_ids.extend(result.supporting_catalyst_ids.clone()))
            .or_insert(result);
    }

    let classes: Vec<AnswerClass> = classes_by_key.into_values().collect();
    match classes.len() {
        0 => ClosureResult::Declined { reason: "every available source was exhausted and none reached an answer class".to_string() },
        1 => ClosureResult::Closed { class: classes.into_iter().next().unwrap() },
        _ => ClosureResult::Contested { classes },
    }
}
