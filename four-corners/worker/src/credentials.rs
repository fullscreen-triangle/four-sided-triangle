//! Device credential storage. The worker holds a long-lived secret issued
//! at pairing time (four-corners/server's `POST /api/pairing-tokens/redeem`)
//! and uses it as a Bearer token on every subsequent request. Stored in the
//! OS keychain via the `keyring` crate rather than a plaintext file where
//! possible; if the keychain is unavailable (e.g. a headless CI box), fall
//! back to a permissioned local file under the OS data directory.

use std::fs;
use std::path::PathBuf;

use directories::ProjectDirs;

const SERVICE: &str = "four-corners-worker";
const USERNAME: &str = "device-credential";

pub struct StoredCredential {
    pub server_url: String,
    pub device_id: String,
    pub secret: String,
}

fn config_dir() -> anyhow::Result<PathBuf> {
    let dirs = ProjectDirs::from("dev", "four-sided-triangle", "four-corners-worker")
        .ok_or_else(|| anyhow::anyhow!("could not determine a config directory for this platform"))?;
    let dir = dirs.config_dir().to_path_buf();
    fs::create_dir_all(&dir)?;
    Ok(dir)
}

fn fallback_credential_path() -> anyhow::Result<PathBuf> {
    Ok(config_dir()?.join("credential.json"))
}

#[derive(serde::Serialize, serde::Deserialize)]
struct CredentialFile {
    server_url: String,
    device_id: String,
    secret: String,
}

/// Persists the device credential. Tries the OS keychain first; falls back
/// to a local file (best-effort 0600 permissions on Unix) if the keychain
/// backend is unavailable.
pub fn save(server_url: &str, device_id: &str, secret: &str) -> anyhow::Result<()> {
    let payload = serde_json::to_string(&CredentialFile {
        server_url: server_url.to_string(),
        device_id: device_id.to_string(),
        secret: secret.to_string(),
    })?;

    match keyring::Entry::new(SERVICE, USERNAME).and_then(|entry| entry.set_password(&payload)) {
        Ok(()) => Ok(()),
        Err(_) => {
            let path = fallback_credential_path()?;
            fs::write(&path, payload)?;
            #[cfg(unix)]
            {
                use std::os::unix::fs::PermissionsExt;
                fs::set_permissions(&path, fs::Permissions::from_mode(0o600))?;
            }
            Ok(())
        }
    }
}

pub fn load() -> anyhow::Result<Option<StoredCredential>> {
    let payload = match keyring::Entry::new(SERVICE, USERNAME).and_then(|entry| entry.get_password()) {
        Ok(payload) => Some(payload),
        Err(keyring::Error::NoEntry) => None,
        Err(_) => {
            let path = fallback_credential_path()?;
            if path.exists() {
                Some(fs::read_to_string(&path)?)
            } else {
                None
            }
        }
    };

    let Some(payload) = payload else { return Ok(None) };
    let parsed: CredentialFile = serde_json::from_str(&payload)?;
    Ok(Some(StoredCredential { server_url: parsed.server_url, device_id: parsed.device_id, secret: parsed.secret }))
}

pub fn clear() -> anyhow::Result<()> {
    let _ = keyring::Entry::new(SERVICE, USERNAME).and_then(|entry| entry.delete_password());
    let path = fallback_credential_path()?;
    if path.exists() {
        fs::remove_file(path)?;
    }
    Ok(())
}
