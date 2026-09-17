//! Integration test for LocalFileSource against a real temp directory —
//! mirrors sdk-ts's LocalFileSource behavior (paragraph chunking, min/max
//! chunk size, extension filtering, skipping hidden/node_modules dirs).
//!
//! Test paragraphs are padded to comfortably clear the default 80-char
//! min_chunk_chars threshold — anything shorter is correctly (and
//! silently) dropped as noise, which is the intended behavior, not a bug.

use four_corners_worker::source_adapter::SourceAdapter;
use four_corners_worker::sources::local_file::LocalFileSource;
use std::fs;

/// Repeats `text` until it exceeds `min_len` characters — a cheap way to
/// guarantee a paragraph clears min_chunk_chars regardless of its content.
fn padded(text: &str, min_len: usize) -> String {
    let mut out = text.to_string();
    while out.len() < min_len {
        out.push_str(" ");
        out.push_str(text);
    }
    out
}

#[tokio::test]
async fn merges_short_paragraphs_under_the_default_max_chunk_size_into_one_chunk() {
    let dir = tempfile::tempdir().unwrap();
    let p1 = padded("First paragraph.", 90);
    let p2 = padded("Second paragraph.", 90);
    fs::write(dir.path().join("doc.md"), format!("{p1}\n\n{p2}")).unwrap();

    let source = LocalFileSource::new(dir.path());
    let chunks = source.list().await.unwrap();

    // Both paragraphs comfortably fit under the default 2000-char max, so
    // they are merged into a single chunk — this is the intended behavior
    // (a claim should be a genuine multi-paragraph passage when the source
    // paragraphs are short, not one claim per short paragraph).
    assert_eq!(chunks.len(), 1);
    assert!(chunks[0].text.contains("First paragraph"));
    assert!(chunks[0].text.contains("Second paragraph"));
    assert_eq!(chunks[0].origin, "doc.md");
}

#[tokio::test]
async fn splits_when_a_single_paragraph_alone_exceeds_the_default_max_chunk_size() {
    let dir = tempfile::tempdir().unwrap();
    let long_para = padded("A very long paragraph that keeps repeating itself.", 2100);
    let short_para = padded("A short second paragraph.", 90);
    fs::write(dir.path().join("doc.md"), format!("{long_para}\n\n{short_para}")).unwrap();

    let source = LocalFileSource::new(dir.path());
    let chunks = source.list().await.unwrap();

    assert_eq!(chunks.len(), 2);
    assert!(chunks[0].text.contains("very long paragraph"));
    assert!(chunks[1].text.contains("short second paragraph"));
}

#[tokio::test]
async fn skips_files_outside_the_configured_extensions() {
    let dir = tempfile::tempdir().unwrap();
    fs::write(dir.path().join("doc.md"), padded("A paragraph long enough to be kept.", 90)).unwrap();
    fs::write(dir.path().join("ignored.bin"), padded("binary-ish content that should never surface.", 90)).unwrap();

    let source = LocalFileSource::new(dir.path());
    let chunks = source.list().await.unwrap();

    assert_eq!(chunks.len(), 1);
    assert_eq!(chunks[0].origin, "doc.md");
}

#[tokio::test]
async fn skips_hidden_and_node_modules_directories() {
    let dir = tempfile::tempdir().unwrap();
    fs::create_dir_all(dir.path().join(".git")).unwrap();
    fs::write(dir.path().join(".git").join("secret.md"), padded("This should never surface from a hidden directory.", 90)).unwrap();
    fs::create_dir_all(dir.path().join("node_modules")).unwrap();
    fs::write(dir.path().join("node_modules").join("dep.md"), padded("This should never surface from node_modules.", 90)).unwrap();
    fs::write(dir.path().join("real.md"), padded("This is the only paragraph that should be surfaced.", 90)).unwrap();

    let source = LocalFileSource::new(dir.path());
    let chunks = source.list().await.unwrap();

    assert_eq!(chunks.len(), 1);
    assert_eq!(chunks[0].origin, "real.md");
}

#[tokio::test]
async fn respects_custom_extensions() {
    let dir = tempfile::tempdir().unwrap();
    fs::write(dir.path().join("notes.tex"), padded("A LaTeX-flavored paragraph long enough to be kept.", 90)).unwrap();

    let source = LocalFileSource::new(dir.path()).with_extensions(vec!["tex".to_string()]);
    let chunks = source.list().await.unwrap();

    assert_eq!(chunks.len(), 1);
    assert_eq!(chunks[0].origin, "notes.tex");
}
