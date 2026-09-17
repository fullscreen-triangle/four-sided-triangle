import { describe, it, expect, beforeEach } from 'vitest';
import { openDb, type Db } from '../src/db/index.js';
import { getSnapshot, putSnapshot } from '../src/receiverSnapshot.js';
import { signup } from '../src/users.js';
import { issuePairingToken, redeemPairingToken } from '../src/pairing.js';

/**
 * Thm 8.9 (monotone history) at the storage layer: a stale write (an older
 * version than what's stored) must be refused, never silently applied —
 * otherwise a second device or a retried request could roll back a
 * receiver graph that has already moved forward.
 */
describe('receiver snapshot optimistic versioning', () => {
  let db: Db;
  let userId: string;
  let deviceId: string;

  beforeEach(async () => {
    db = openDb(':memory:');
    const user = await signup(db, 'researcher@example.com', 'correct horse battery staple');
    if (!user.ok) throw new Error('setup failed');
    userId = user.user.id;

    const issued = issuePairingToken(db, userId);
    const redeemed = redeemPairingToken(db, issued.code, 'laptop');
    if (!redeemed.ok) throw new Error('setup failed');
    deviceId = redeemed.device.id;
  });

  it('first write has no expected version and starts at version 1', () => {
    const result = putSnapshot(db, userId, deviceId, { receiverId: 'r1', committedCount: 1, claims: ['a'], edges: [] });
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.version).toBe(1);
  });

  it('a write with the correct expected version succeeds and advances the version', () => {
    putSnapshot(db, userId, deviceId, { receiverId: 'r1', committedCount: 1, claims: ['a'], edges: [] });
    const result = putSnapshot(db, userId, deviceId, { receiverId: 'r1', committedCount: 2, claims: ['a', 'b'], edges: [] }, 1);
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.version).toBe(2);
  });

  it('a write with a stale expected version is refused, never silently overwriting', () => {
    putSnapshot(db, userId, deviceId, { receiverId: 'r1', committedCount: 1, claims: ['a'], edges: [] });
    putSnapshot(db, userId, deviceId, { receiverId: 'r1', committedCount: 2, claims: ['a', 'b'], edges: [] }, 1);

    // Retry using the now-stale version 1 — must be refused, not applied.
    const stale = putSnapshot(db, userId, deviceId, { receiverId: 'r1', committedCount: 99, claims: ['rolled-back'], edges: [] }, 1);
    expect(stale.ok).toBe(false);
    if (stale.ok) return;
    expect(stale.reason).toBe('stale-version');
    expect(stale.currentVersion).toBe(2);

    // Confirm the newer state is still intact.
    const current = getSnapshot(db, userId, deviceId);
    expect(current?.committedCount).toBe(2);
    expect(current?.claims).toEqual(['a', 'b']);
  });

  it('getSnapshot returns undefined before any write', () => {
    expect(getSnapshot(db, userId, deviceId)).toBeUndefined();
  });
});
