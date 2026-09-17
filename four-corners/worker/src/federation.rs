//! Federation (paper §8.1, Def 8.1, Thm 8.2). A federation unions several
//! SourceAdapters' claims into one contact graph, exactly the union
//! construction Remark 8.3 distinguishes from ensembling-by-vote.
//!
//! Direct Rust port of `sdk-ts/src/federation.ts`.

use crate::source_adapter::{SourceAdapter, SourceChunk};

#[derive(Debug, Clone)]
pub struct FederatedClaim {
    pub id: String,
    pub text: String,
    pub origin: String,
    /// Which adapter this claim came from — the catalyst `source` field downstream (Def 6.1).
    pub source_name: String,
}

pub struct Federation {
    adapters: Vec<Box<dyn SourceAdapter>>,
}

impl Federation {
    pub fn new(adapters: Vec<Box<dyn SourceAdapter>>) -> anyhow::Result<Self> {
        if adapters.is_empty() {
            anyhow::bail!("Federation requires at least one SourceAdapter (Def 8.1: a federation of zero receivers is not a receiver)");
        }
        Ok(Federation { adapters })
    }

    /// Union construction (Remark 8.3): every adapter's claims are pooled, none filtered by the others' agreement.
    pub async fn list_all(&self) -> anyhow::Result<Vec<FederatedClaim>> {
        let mut out = Vec::new();
        for adapter in &self.adapters {
            let chunks: Vec<SourceChunk> = adapter.list().await?;
            out.extend(chunks.into_iter().map(|c| FederatedClaim {
                id: c.id,
                text: c.text,
                origin: c.origin,
                source_name: adapter.name().to_string(),
            }));
        }
        Ok(out)
    }

    /// Number of distinct adapters federated — used by catalysis.rs to check source independence (Cor 6.3).
    pub fn member_count(&self) -> usize {
        self.adapters.len()
    }

    pub fn member_names(&self) -> Vec<String> {
        self.adapters.iter().map(|a| a.name().to_string()).collect()
    }
}
