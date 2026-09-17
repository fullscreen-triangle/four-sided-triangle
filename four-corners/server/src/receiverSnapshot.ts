/**
 * Server-side counterpart to sdk-ts's JsonFilePersistAdapter (four-sided-
 * triangle/sdk-ts/src/index.ts) — a PersistAdapter implemented over HTTP
 * instead of a local file, so a worker can push/pull the same
 * ReceiverSnapshot shape. Writes are optimistically versioned: a push
 * carrying a version older than what's stored is rejected rather than
 * silently overwriting newer state, matching Thm 8.9 (monotone history,
 * never rolled back) at the storage layer too.
 */

import type { Db } from './db/index.js';
import type { ReceiverSnapshotRecord } from './types.js';

interface SnapshotRow {
  user_id: string;
  device_id: string;
  snapshot_json: string;
  version: number;
  updated_at: string;
}

function rowToRecord(row: SnapshotRow): ReceiverSnapshotRecord {
  const parsed = JSON.parse(row.snapshot_json) as { receiverId: string; committedCount: number; claims: string[]; edges: ReceiverSnapshotRecord['edges'] };
  return {
    userId: row.user_id,
    deviceId: row.device_id,
    receiverId: parsed.receiverId,
    committedCount: parsed.committedCount,
    claims: parsed.claims,
    edges: parsed.edges,
    version: row.version,
    updatedAt: row.updated_at
  };
}

export function getSnapshot(db: Db, userId: string, deviceId: string): ReceiverSnapshotRecord | undefined {
  const row = db
    .prepare(`SELECT * FROM receiver_snapshots WHERE user_id = ? AND device_id = ?`)
    .get(userId, deviceId) as SnapshotRow | undefined;
  return row ? rowToRecord(row) : undefined;
}

export type PutSnapshotResult = { ok: true; version: number } | { ok: false; reason: 'stale-version'; currentVersion: number };

/**
 * Writes a snapshot. If `expectedVersion` is provided and doesn't match the
 * stored version, the write is refused (optimistic concurrency) rather than
 * clobbering newer state — the caller should re-fetch and reapply.
 */
export function putSnapshot(
  db: Db,
  userId: string,
  deviceId: string,
  snapshot: { receiverId: string; committedCount: number; claims: string[]; edges: ReceiverSnapshotRecord['edges'] },
  expectedVersion?: number
): PutSnapshotResult {
  const existing = db
    .prepare(`SELECT version FROM receiver_snapshots WHERE user_id = ? AND device_id = ?`)
    .get(userId, deviceId) as { version: number } | undefined;

  if (existing && expectedVersion !== undefined && existing.version !== expectedVersion) {
    return { ok: false, reason: 'stale-version', currentVersion: existing.version };
  }

  const nextVersion = (existing?.version ?? 0) + 1;
  const now = new Date().toISOString();
  const json = JSON.stringify(snapshot);

  db.prepare(
    `INSERT INTO receiver_snapshots (user_id, device_id, snapshot_json, version, updated_at)
     VALUES (?, ?, ?, ?, ?)
     ON CONFLICT(user_id, device_id) DO UPDATE SET snapshot_json = excluded.snapshot_json, version = excluded.version, updated_at = excluded.updated_at`
  ).run(userId, deviceId, json, nextVersion, now);

  return { ok: true, version: nextVersion };
}
