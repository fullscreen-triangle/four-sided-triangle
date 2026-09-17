/**
 * Pairing-token state machine: pending -> paired | expired | revoked.
 *
 * A token is a short, human-typeable one-time code the web UI shows and the
 * user types into the downloaded worker binary. Only its hash is ever
 * stored — the plaintext code is returned once, at issue time, and never
 * persisted. Redeeming a valid token creates a `devices` row (the worker's
 * long-lived credential) and consumes the token so it cannot be reused.
 */

import { randomBytes, createHash, randomUUID } from 'node:crypto';
import type { Db } from './db/index.js';
import type { Device, PairingToken } from './types.js';

const CODE_ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; // no 0/O/1/I — human-typeable
const CODE_LENGTH = 8;
const TOKEN_TTL_MS = 10 * 60 * 1000; // 10 minutes

export function generatePairingCode(): string {
  const bytes = randomBytes(CODE_LENGTH);
  let code = '';
  for (let i = 0; i < CODE_LENGTH; i++) {
    code += CODE_ALPHABET[bytes[i]! % CODE_ALPHABET.length];
  }
  return code;
}

function hashCode(code: string): string {
  return createHash('sha256').update(code).digest('hex');
}

export interface IssuedToken {
  id: string;
  code: string;
  expiresAt: string;
}

/** Issues a new pairing token for `userId`. Returns the plaintext code once — the server never stores it. */
export function issuePairingToken(db: Db, userId: string): IssuedToken {
  const code = generatePairingCode();
  const id = randomUUID();
  const expiresAt = new Date(Date.now() + TOKEN_TTL_MS).toISOString();

  db.prepare(
    `INSERT INTO pairing_tokens (id, user_id, code_hash, status, expires_at) VALUES (?, ?, ?, 'pending', ?)`
  ).run(id, userId, hashCode(code), expiresAt);

  return { id, code, expiresAt };
}

export type RedeemResult =
  | { ok: true; device: Device; deviceCredentialSecret: string }
  | { ok: false; reason: 'not-found' | 'expired' | 'already-used' | 'revoked' };

/**
 * Redeems a pairing code: validates it is pending and unexpired, creates a
 * `devices` row bound to a fresh device credential, marks the token
 * consumed. The plaintext device credential secret is returned once — only
 * its hash is stored, mirroring the pairing code itself.
 */
export function redeemPairingToken(db: Db, code: string, deviceName: string): RedeemResult {
  const codeHash = hashCode(code);
  const token = db
    .prepare(`SELECT * FROM pairing_tokens WHERE code_hash = ?`)
    .get(codeHash) as PairingTokenRow | undefined;

  if (!token) return { ok: false, reason: 'not-found' };
  if (token.status === 'revoked') return { ok: false, reason: 'revoked' };
  if (token.status === 'paired') return { ok: false, reason: 'already-used' };
  if (token.status === 'expired' || new Date(token.expires_at).getTime() < Date.now()) {
    if (token.status !== 'expired') {
      db.prepare(`UPDATE pairing_tokens SET status = 'expired' WHERE id = ?`).run(token.id);
    }
    return { ok: false, reason: 'expired' };
  }

  const deviceCredentialSecret = randomBytes(32).toString('base64url');
  const deviceId = randomUUID();
  const now = new Date().toISOString();

  const tx = db.transaction(() => {
    db.prepare(
      `INSERT INTO devices (id, user_id, device_name, device_key_hash, paired_at) VALUES (?, ?, ?, ?, ?)`
    ).run(deviceId, token.user_id, deviceName, hashCode(deviceCredentialSecret), now);

    db.prepare(`UPDATE pairing_tokens SET status = 'paired', redeemed_at = ? WHERE id = ?`).run(now, token.id);
  });
  tx();

  const device: Device = {
    id: deviceId,
    userId: token.user_id,
    deviceName,
    deviceKeyHash: hashCode(deviceCredentialSecret),
    pairedAt: now,
    lastSeenAt: null,
    revokedAt: null
  };

  return { ok: true, device, deviceCredentialSecret };
}

/** Looks up the device bound to a presented credential secret; returns undefined if unknown or revoked. */
export function authenticateDevice(db: Db, deviceCredentialSecret: string): Device | undefined {
  const row = db
    .prepare(`SELECT * FROM devices WHERE device_key_hash = ? AND revoked_at IS NULL`)
    .get(hashCode(deviceCredentialSecret)) as DeviceRow | undefined;
  if (!row) return undefined;

  db.prepare(`UPDATE devices SET last_seen_at = ? WHERE id = ?`).run(new Date().toISOString(), row.id);

  return {
    id: row.id,
    userId: row.user_id,
    deviceName: row.device_name,
    deviceKeyHash: row.device_key_hash,
    pairedAt: row.paired_at,
    lastSeenAt: row.last_seen_at,
    revokedAt: row.revoked_at
  };
}

export function revokeDevice(db: Db, userId: string, deviceId: string): boolean {
  const result = db
    .prepare(`UPDATE devices SET revoked_at = ? WHERE id = ? AND user_id = ? AND revoked_at IS NULL`)
    .run(new Date().toISOString(), deviceId, userId);
  return result.changes > 0;
}

export function listDevices(db: Db, userId: string): Device[] {
  const rows = db.prepare(`SELECT * FROM devices WHERE user_id = ? ORDER BY paired_at DESC`).all(userId) as DeviceRow[];
  return rows.map((row) => ({
    id: row.id,
    userId: row.user_id,
    deviceName: row.device_name,
    deviceKeyHash: row.device_key_hash,
    pairedAt: row.paired_at,
    lastSeenAt: row.last_seen_at,
    revokedAt: row.revoked_at
  }));
}

interface PairingTokenRow {
  id: string;
  user_id: string;
  code_hash: string;
  status: 'pending' | 'paired' | 'expired' | 'revoked';
  created_at: string;
  expires_at: string;
  redeemed_at: string | null;
}

interface DeviceRow {
  id: string;
  user_id: string;
  device_name: string;
  device_key_hash: string;
  paired_at: string;
  last_seen_at: string | null;
  revoked_at: string | null;
}
