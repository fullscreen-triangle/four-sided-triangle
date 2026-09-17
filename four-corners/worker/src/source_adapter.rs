//! Source adapters (paper Remark 2.2: no boundary between local, remote, and
//! learned — all are computationally uniform contents of the medium prior
//! to individuation). A `SourceAdapter` yields claims as chunks of text
//! with a stable id.
//!
//! Direct Rust port of `sdk-ts/src/sourceAdapter.ts`.

use std::future::Future;
use std::pin::Pin;

#[derive(Debug, Clone)]
pub struct SourceChunk {
    /// Stable id, unique within this adapter — becomes the claim id in the contact graph.
    pub id: String,
    pub text: String,
    /// Human-readable origin, e.g. a file path — never shown as "the answer," only as provenance.
    pub origin: String,
}

pub trait SourceAdapter: Send + Sync {
    /// A name for this adapter, used as the catalyst `source` field (Def 6.1) for independence checks.
    fn name(&self) -> &str;
    /// Yield every claim this source can currently offer. Called once per federation build.
    fn list(&self) -> Pin<Box<dyn Future<Output = anyhow::Result<Vec<SourceChunk>>> + Send + '_>>;
}
