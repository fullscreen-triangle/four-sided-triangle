//! four-corners-worker: the downloadable local compute worker.
//!
//! Pairs to a four-corners account via a one-time token (see
//! `credentials.rs` and `server_client.rs`), then runs the paper's
//! individuation primitives (`graph.rs`, `receiver.rs`, `catalysis.rs`,
//! `closure.rs`, `waterfill.rs`, `federation.rs`) against local sources —
//! a mechanical Rust port of `sdk-ts/src/*.ts`, module for module.

pub mod catalysis;
pub mod closure;
pub mod credentials;
pub mod federation;
pub mod graph;
pub mod receiver;
pub mod server_client;
pub mod source_adapter;
pub mod sources {
    pub mod local_file;
}
pub mod waterfill;
