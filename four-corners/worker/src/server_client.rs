//! Thin HTTP client for the four-corners server's device-facing endpoints
//! (four-corners/server/src/routes/pairing.ts, receiverSnapshot.ts). The
//! worker only ever calls the device-authenticated (`Authorization: Bearer
//! <secret>`) or unauthenticated (redeem) endpoints — never the user-session
//! cookie endpoints, which belong to the web frontend.

use serde::{Deserialize, Serialize};

use crate::receiver::ReceiverSnapshot;

pub struct ServerClient {
    base_url: String,
    http: reqwest::Client,
}

#[derive(Debug, Serialize)]
struct RedeemRequest<'a> {
    code: &'a str,
    #[serde(rename = "deviceName")]
    device_name: &'a str,
}

#[derive(Debug, Deserialize)]
pub struct RedeemResponse {
    #[serde(rename = "deviceId")]
    pub device_id: String,
    #[serde(rename = "deviceCredential")]
    pub device_credential: String,
}

#[derive(Debug, Deserialize)]
struct ErrorBody {
    error: String,
}

#[derive(Debug, Serialize)]
struct PutSnapshotRequest<'a> {
    #[serde(rename = "receiverId")]
    receiver_id: &'a str,
    #[serde(rename = "committedCount")]
    committed_count: u64,
    claims: &'a [String],
    edges: &'a [crate::receiver::SnapshotEdge],
    #[serde(rename = "expectedVersion", skip_serializing_if = "Option::is_none")]
    expected_version: Option<u64>,
}

#[derive(Debug, Deserialize)]
pub struct PutSnapshotResponse {
    pub version: u64,
}

impl ServerClient {
    pub fn new(base_url: &str) -> Self {
        ServerClient { base_url: base_url.trim_end_matches('/').to_string(), http: reqwest::Client::new() }
    }

    /// Redeems a pairing code typed by the user, as the worker (no prior auth needed for this call).
    pub async fn redeem_pairing_token(&self, code: &str, device_name: &str) -> anyhow::Result<RedeemResponse> {
        let res = self
            .http
            .post(format!("{}/api/pairing-tokens/redeem", self.base_url))
            .json(&RedeemRequest { code, device_name })
            .send()
            .await?;

        if !res.status().is_success() {
            let status = res.status();
            let body: Result<ErrorBody, _> = res.json().await;
            let reason = body.map(|b| b.error).unwrap_or_else(|_| status.to_string());
            anyhow::bail!("pairing redeem failed ({status}): {reason}");
        }

        Ok(res.json().await?)
    }

    /// Pulls the last snapshot this device pushed, if any.
    pub async fn get_snapshot(&self, device_secret: &str) -> anyhow::Result<Option<ReceiverSnapshot>> {
        let res = self.http.get(format!("{}/api/receiver-snapshot", self.base_url)).bearer_auth(device_secret).send().await?;

        if res.status() == reqwest::StatusCode::NOT_FOUND {
            return Ok(None);
        }
        if !res.status().is_success() {
            anyhow::bail!("get snapshot failed: {}", res.status());
        }
        Ok(Some(res.json().await?))
    }

    /// Pushes a snapshot, optimistically versioned against `expected_version` (mirrors server's optimistic-concurrency PersistAdapter contract).
    pub async fn put_snapshot(&self, device_secret: &str, snapshot: &ReceiverSnapshot, expected_version: Option<u64>) -> anyhow::Result<PutSnapshotResponse> {
        let body = PutSnapshotRequest {
            receiver_id: &snapshot.receiver_id,
            committed_count: snapshot.committed_count,
            claims: &snapshot.claims,
            edges: &snapshot.edges,
            expected_version,
        };

        let res = self.http.put(format!("{}/api/receiver-snapshot", self.base_url)).bearer_auth(device_secret).json(&body).send().await?;

        if !res.status().is_success() {
            let status = res.status();
            let body: Result<ErrorBody, _> = res.json().await;
            let reason = body.map(|b| b.error).unwrap_or_else(|_| status.to_string());
            anyhow::bail!("put snapshot failed ({status}): {reason}");
        }
        Ok(res.json().await?)
    }
}
