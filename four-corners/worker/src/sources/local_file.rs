//! Reference SourceAdapter: local filesystem, plain text (.md/.txt/.mdx).
//! Chunks by paragraph (blank-line-delimited) with a minimum size, so a
//! claim is a genuine passage rather than a single sentence fragment or an
//! entire document. PDF support is deferred to a later pass (sdk-ts's
//! equivalent uses an optional peer dependency; the worker's first pass
//! covers the text-source path needed to prove the pairing + compute
//! pipeline end-to-end).
//!
//! Rust port of `sdk-ts/src/sources/localFile.ts` (text path only).

use std::future::Future;
use std::path::{Path, PathBuf};
use std::pin::Pin;

use tokio::fs;

use crate::source_adapter::{SourceAdapter, SourceChunk};

pub struct LocalFileSource {
    root: PathBuf,
    extensions: Vec<String>,
    min_chunk_chars: usize,
    max_chunk_chars: usize,
}

const DEFAULT_EXTENSIONS: &[&str] = &["md", "txt", "mdx"];
const DEFAULT_MIN_CHARS: usize = 80;
const DEFAULT_MAX_CHARS: usize = 2000;

impl LocalFileSource {
    pub fn new(root: impl Into<PathBuf>) -> Self {
        LocalFileSource {
            root: root.into(),
            extensions: DEFAULT_EXTENSIONS.iter().map(|s| s.to_string()).collect(),
            min_chunk_chars: DEFAULT_MIN_CHARS,
            max_chunk_chars: DEFAULT_MAX_CHARS,
        }
    }

    pub fn with_extensions(mut self, extensions: Vec<String>) -> Self {
        self.extensions = extensions;
        self
    }

    async fn walk(&self, dir: &Path) -> anyhow::Result<Vec<PathBuf>> {
        let mut out = Vec::new();
        let mut entries = fs::read_dir(dir).await?;
        while let Some(entry) = entries.next_entry().await? {
            let path = entry.path();
            let file_type = entry.file_type().await?;
            let name = entry.file_name();
            let name = name.to_string_lossy();

            if file_type.is_dir() {
                if name == "node_modules" || name.starts_with('.') {
                    continue;
                }
                out.extend(Box::pin(self.walk(&path)).await?);
            } else if let Some(ext) = path.extension().and_then(|e| e.to_str()) {
                if self.extensions.iter().any(|allowed| allowed.eq_ignore_ascii_case(ext)) {
                    out.push(path);
                }
            }
        }
        Ok(out)
    }

    fn chunk_paragraphs(&self, text: &str) -> Vec<String> {
        let paragraphs: Vec<&str> = text.split("\n\n").map(|p| p.trim()).filter(|p| !p.is_empty()).collect();

        let mut chunks = Vec::new();
        let mut buffer = String::new();
        for para in paragraphs {
            let candidate = if buffer.is_empty() { para.to_string() } else { format!("{buffer}\n\n{para}") };
            if candidate.len() > self.max_chunk_chars && buffer.len() >= self.min_chunk_chars {
                chunks.push(buffer.clone());
                buffer = para.to_string();
            } else {
                buffer = candidate;
            }
        }
        if buffer.len() >= self.min_chunk_chars {
            chunks.push(buffer);
        }
        chunks
    }
}

impl SourceAdapter for LocalFileSource {
    fn name(&self) -> &str {
        "local-file"
    }

    fn list(&self) -> Pin<Box<dyn Future<Output = anyhow::Result<Vec<SourceChunk>>> + Send + '_>> {
        Box::pin(async move {
            let files = self.walk(&self.root).await?;
            let mut chunks = Vec::new();
            for file in files {
                let info = fs::metadata(&file).await?;
                if info.len() == 0 {
                    continue;
                }
                let text = fs::read_to_string(&file).await?;
                let rel = file.strip_prefix(&self.root).unwrap_or(&file).to_string_lossy().replace('\\', "/");

                for (index, para) in self.chunk_paragraphs(&text).into_iter().enumerate() {
                    chunks.push(SourceChunk { id: format!("{rel}#{index}"), text: para, origin: rel.clone() });
                }
            }
            Ok(chunks)
        })
    }
}
