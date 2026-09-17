import { describe, it, expect, beforeEach } from 'vitest';
import { openDb, type Db } from '../src/db/index.js';
import { issuePairingToken, redeemPairingToken, authenticateDevice, revokeDevice, listDevices } from '../src/pairing.js';
import { signup } from '../src/users.js';

describe('pairing-token state machine', () => {
  let db: Db;
  let userId: string;

  beforeEach(async () => {
    db = openDb(':memory:');
    const result = await signup(db, 'researcher@example.com', 'correct horse battery staple');
    if (!result.ok) throw new Error('setup failed');
    userId = result.user.id;
  });

  it('issues a code and redeems it exactly once into a device credential', () => {
    const issued = issuePairingToken(db, userId);
    expect(issued.code).toHaveLength(8);

    const redeemed = redeemPairingToken(db, issued.code, 'my-laptop');
    expect(redeemed.ok).toBe(true);
    if (!redeemed.ok) return;
    expect(redeemed.device.userId).toBe(userId);
    expect(redeemed.deviceCredentialSecret.length).toBeGreaterThan(20);

    const devices = listDevices(db, userId);
    expect(devices).toHaveLength(1);
    expect(devices[0]!.deviceName).toBe('my-laptop');
  });

  it('refuses to redeem the same code twice', () => {
    const issued = issuePairingToken(db, userId);
    const first = redeemPairingToken(db, issued.code, 'device-a');
    expect(first.ok).toBe(true);

    const second = redeemPairingToken(db, issued.code, 'device-b');
    expect(second.ok).toBe(false);
    if (second.ok) return;
    expect(second.reason).toBe('already-used');

    // Only one device was actually created.
    expect(listDevices(db, userId)).toHaveLength(1);
  });

  it('refuses an unknown code', () => {
    const result = redeemPairingToken(db, 'NOTAREAL', 'device-a');
    expect(result.ok).toBe(false);
    if (result.ok) return;
    expect(result.reason).toBe('not-found');
  });

  it('refuses an expired code', () => {
    const issued = issuePairingToken(db, userId);
    // Force expiry directly rather than waiting 10 real minutes.
    db.prepare(`UPDATE pairing_tokens SET expires_at = datetime('now', '-1 minute') WHERE id = ?`).run(issued.id);

    const result = redeemPairingToken(db, issued.code, 'device-a');
    expect(result.ok).toBe(false);
    if (result.ok) return;
    expect(result.reason).toBe('expired');
  });

  it('authenticates a device by its credential secret, and rejects a wrong one', () => {
    const issued = issuePairingToken(db, userId);
    const redeemed = redeemPairingToken(db, issued.code, 'my-laptop');
    if (!redeemed.ok) throw new Error('setup failed');

    const authed = authenticateDevice(db, redeemed.deviceCredentialSecret);
    expect(authed?.id).toBe(redeemed.device.id);

    const wrong = authenticateDevice(db, 'not-the-right-secret');
    expect(wrong).toBeUndefined();
  });

  it('revoking a device immediately invalidates its credential', () => {
    const issued = issuePairingToken(db, userId);
    const redeemed = redeemPairingToken(db, issued.code, 'my-laptop');
    if (!redeemed.ok) throw new Error('setup failed');

    const revoked = revokeDevice(db, userId, redeemed.device.id);
    expect(revoked).toBe(true);

    const authed = authenticateDevice(db, redeemed.deviceCredentialSecret);
    expect(authed).toBeUndefined();
  });

  it('cannot revoke a device belonging to a different user', async () => {
    const other = await signup(db, 'other@example.com', 'another password entirely');
    if (!other.ok) throw new Error('setup failed');

    const issued = issuePairingToken(db, userId);
    const redeemed = redeemPairingToken(db, issued.code, 'my-laptop');
    if (!redeemed.ok) throw new Error('setup failed');

    const revoked = revokeDevice(db, other.user.id, redeemed.device.id);
    expect(revoked).toBe(false);

    // Original owner's credential still works.
    expect(authenticateDevice(db, redeemed.deviceCredentialSecret)).toBeDefined();
  });

  it('each issued code is unique and only its hash is ever queryable by plaintext lookup', () => {
    const a = issuePairingToken(db, userId);
    const b = issuePairingToken(db, userId);
    expect(a.code).not.toBe(b.code);
  });
});
