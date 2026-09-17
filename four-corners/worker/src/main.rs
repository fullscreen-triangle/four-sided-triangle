use clap::{Parser, Subcommand};
use four_corners_worker::{credentials, server_client::ServerClient};

#[derive(Parser)]
#[command(name = "four-corners-worker", version, about = "Local compute worker for four-corners")]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand)]
enum Command {
    /// Redeem a one-time pairing code shown in the four-corners web UI.
    Pair {
        /// The 8-character code shown by "Connect a device" in the web UI.
        #[arg(long)]
        code: String,
        /// Base URL of the four-corners server, e.g. https://four-corners.example.com.
        #[arg(long)]
        server: String,
        /// A name for this device, shown in the web UI's device list.
        #[arg(long, default_value_t = default_device_name())]
        name: String,
    },
    /// Show whether this machine is currently paired, and to which server.
    Status,
    /// Forget this device's stored credential (does not revoke it server-side — use the web UI to revoke).
    Unpair,
    /// Run the worker: watches configured local sources and serves individuation requests. (Not yet implemented — pairing must land first.)
    Run,
}

fn default_device_name() -> String {
    hostname_or_fallback()
}

fn hostname_or_fallback() -> String {
    std::env::var("COMPUTERNAME")
        .or_else(|_| std::env::var("HOSTNAME"))
        .unwrap_or_else(|_| "unnamed-device".to_string())
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Command::Pair { code, server, name } => pair(&code, &server, &name).await,
        Command::Status => status(),
        Command::Unpair => unpair(),
        Command::Run => {
            println!("four-corners-worker run: not yet implemented (pairing lands first — see plan Phase 3/4).");
            Ok(())
        }
    }
}

async fn pair(code: &str, server: &str, device_name: &str) -> anyhow::Result<()> {
    let client = ServerClient::new(server);
    let response = client.redeem_pairing_token(code, device_name).await?;

    credentials::save(server, &response.device_id, &response.device_credential)?;

    println!("Paired as \"{device_name}\" (device id {}).", response.device_id);
    println!("Credential stored locally. Run `four-corners-worker run` to start.");
    Ok(())
}

fn status() -> anyhow::Result<()> {
    match credentials::load()? {
        Some(cred) => {
            println!("Paired to {} as device {}.", cred.server_url, cred.device_id);
        }
        None => {
            println!("Not paired. Run `four-corners-worker pair --code <CODE> --server <URL>` to connect.");
        }
    }
    Ok(())
}

fn unpair() -> anyhow::Result<()> {
    credentials::clear()?;
    println!("Local credential cleared. This device may still show as paired in the web UI until you revoke it there.");
    Ok(())
}
